import React, { useState, useEffect, useCallback } from 'react';
import DashboardHeader from './components/DashboardHeader';
import OverviewCards from './components/OverviewCards';
import AnalyticsCharts from './components/AnalyticsCharts';
import ThreatHotspots from './components/ThreatHotspots';
import AlertsTable from './components/AlertsTable';
import AlertDetailSidebar from './components/AlertDetailSidebar';
import AICopilot from './components/AICopilot';
import {
  getOverview,
  getSeverityDistribution,
  getTimeline,
  getTopSources,
  getGeoData,
  getAlerts,
  getAlertDetail,
  respondToAlert,
  sendChatMessage,
  trainModel,
  verifyAlert,
} from './utils/api';
import { Shield, TrendingUp, Cpu, X, BookOpen, AlertOctagon, Terminal } from 'lucide-react';
import './App.css';

function App() {
  // Navigation active tab
  const [activeTab, setActiveTab] = useState('triage'); // 'triage', 'analytics', 'copilot'

  // Real-time Feed & Pagination States
  const [alerts, setAlerts] = useState([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(12); // Show 12 per page for clean multi-pane layout
  const [filters, setFilters] = useState({
    search: '',
    severity: '',
    eventType: '',
  });

  // Selected Triage Alert & Playbook States
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isResponding, setIsResponding] = useState(null);
  const [responseLogs, setResponseLogs] = useState({});

  // Analytics & Stats States
  const [stats, setStats] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [severityDist, setSeverityDist] = useState([]);
  const [topSources, setTopSources] = useState([]);
  const [geoData, setGeoData] = useState([]);

  // System status & WebSocket connection
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [systemHealth, setSystemHealth] = useState(null);

  // Chat Copilot States
  const [chatHistory, setChatHistory] = useState([]);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // 1. Fetch initial statistics and analytics charts
  const fetchDashboardStats = useCallback(async () => {
    try {
      const [overviewData, sevData, timeData, srcData, mapData] = await Promise.all([
        getOverview(),
        getSeverityDistribution(),
        getTimeline(),
        getTopSources(),
        getGeoData(),
      ]);
      setStats(overviewData);
      setSeverityDist(sevData.distribution);
      setTimeline(timeData.timeline);
      setTopSources(srcData.sources);
      setGeoData(mapData.geo_threats);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  }, []);

  // 2. Fetch paginated alerts list based on page/filters
  const fetchAlertsList = useCallback(async () => {
    try {
      const params = {
        page,
        per_page: perPage,
        severity: filters.severity || undefined,
        event_type: filters.eventType || undefined,
      };
      
      const data = await getAlerts(params);
      
      // Client-side local filtering for search query to make search instantaneous
      let fetchedAlerts = data.alerts;
      if (filters.search) {
        const query = filters.search.toLowerCase();
        fetchedAlerts = fetchedAlerts.filter(
          (alert) =>
            alert.src_ip?.toLowerCase().includes(query) ||
            alert.dest_ip?.toLowerCase().includes(query) ||
            alert.user?.toLowerCase().includes(query) ||
            alert.event_type?.toLowerCase().includes(query) ||
            alert.raw_log?.toLowerCase().includes(query)
        );
      }
      
      setAlerts(fetchedAlerts);
      setTotalAlerts(data.total);
    } catch (err) {
      console.error('Error loading alerts list:', err);
    }
  }, [page, perPage, filters]);

  // Load server status & system config initially
  const fetchSystemHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setSystemHealth(data);
      }
    } catch (err) {
      console.error('System health check failed:', err);
      setSystemHealth({ status: 'offline', service: 'SOC API unreachable' });
    }
  };

  // Sync initial render parameters
  useEffect(() => {
    fetchSystemHealth();
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // Sync alerts when page or filters change
  useEffect(() => {
    fetchAlertsList();
  }, [fetchAlertsList]);

  // 3. Connect to real-time WebSocket threat stream
  useEffect(() => {
    let socket = null;
    let reconnectTimeout = null;

    const connectWS = () => {
      setWsStatus('connecting');
      // Create WebSocket URI relative to hostname
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        console.log('[WebSocket] Connection established.');
        setWsStatus('connected');
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          
          if (payload.type === 'NEW_ALERT') {
            const newAlert = payload.data;
            
            // Append visual glow attribute
            newAlert.isNew = true;

            // Prepend new alert to alerts list (only if it fits current filters / page 1)
            setAlerts((prev) => {
              const updated = [newAlert, ...prev.slice(0, perPage - 1)];
              return updated;
            });
            setTotalAlerts((prev) => prev + 1);

            // Re-sync counters and charts automatically to display live changes
            fetchDashboardStats();

            // Clear glow highlight after 4 seconds
            setTimeout(() => {
              setAlerts((prev) =>
                prev.map((a) => (a.id === newAlert.id ? { ...a, isNew: false } : a))
              );
            }, 4000);
          }
        } catch (e) {
          // Ignores text responses like echoes
        }
      };

      socket.onclose = () => {
        console.warn('[WebSocket] Connection dropped. Reconnecting in 3 seconds...');
        setWsStatus('disconnected');
        reconnectTimeout = setTimeout(connectWS, 3000);
      };

      socket.onerror = (err) => {
        console.error('[WebSocket] Error caught:', err);
        socket.close();
      };
    };

    connectWS();

    return () => {
      if (socket) socket.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [perPage, fetchDashboardStats]);

  // 4. Alert detail selection handler
  const handleAlertSelect = async (alertSummary) => {
    try {
      const detail = await getAlertDetail(alertSummary.id);
      setSelectedAlert(detail);
    } catch (err) {
      console.error('Error fetching alert details:', err);
      // Fallback to list details if server fails
      setSelectedAlert(alertSummary);
    }
  };

  // 5. Automated incident response action trigger
  const handleRespondAction = async (action) => {
    if (!selectedAlert) return;
    setIsResponding(action);
    try {
      const result = await respondToAlert(selectedAlert.id, action);
      
      // Save result in execution log dictionary
      setResponseLogs((prev) => ({
        ...prev,
        [selectedAlert.id]: result,
      }));
      
      // Reload details to capture updated auto-response fields
      const updatedDetail = await getAlertDetail(selectedAlert.id);
      setSelectedAlert(updatedDetail);
    } catch (err) {
      console.error('Playbook execution failed:', err);
    } finally {
      setIsResponding(null);
    }
  };

  // 6. RAG AI Copilot communication handler
  const handleSendChatMessage = async (msgText) => {
    if (!msgText.trim()) return;
    
    // Push user message to history
    const userMsg = { sender: 'user', text: msgText };
    setChatHistory((prev) => [...prev, userMsg]);
    setIsSendingMessage(true);

    try {
      const res = await sendChatMessage(msgText);
      const botMsg = {
        sender: 'bot',
        text: res.response,
        context_alerts_used: res.context_alerts_used,
      };
      setChatHistory((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('AI chat copilot error:', err);
      setChatHistory((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'I apologize, but I encountered an error communicating with the Aegis AI orchestrator core.',
        },
      ]);
    } finally {
      setIsSendingMessage(false);
    }
  };

  // Handle manual dashboard data refresh
  const handleManualRefresh = () => {
    fetchSystemHealth();
    fetchDashboardStats();
    fetchAlertsList();
  };

  const handleTrainModel = async () => {
    try {
      const data = await trainModel();
      fetchSystemHealth();
      fetchDashboardStats();
      fetchAlertsList();
      return data;
    } catch (err) {
      console.error('Error training model:', err);
      return { success: false, message: 'API error occurred.' };
    }
  };

  const handleVerifyAlert = async (alertId, status) => {
    try {
      const res = await verifyAlert(alertId, status);
      if (res && res.success) {
        setSelectedAlert((prev) => {
          if (prev && prev.id === alertId) {
            return { ...prev, analyst_verification: status };
          }
          return prev;
        });
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, analyst_verification: status } : a))
        );
      }
    } catch (err) {
      console.error('Error verifying alert:', err);
    }
  };

  const handlePreCannedPromptClick = (promptText) => {
    handleSendChatMessage(promptText);
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid-bg text-zinc-200 font-sans flex flex-col antialiased">
      {/* ── HUD Header ── */}
      <DashboardHeader
        wsStatus={wsStatus}
        systemHealth={systemHealth}
        onRefresh={handleManualRefresh}
        onTrainModel={handleTrainModel}
      />

      {/* ── Modern Segmented Navigation Tabs ── */}
      <div className="px-6 py-3 border-b border-zinc-800 bg-zinc-950/80 flex flex-wrap gap-2 text-xs z-10">
        <div className="flex bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80">
          <button
            onClick={() => setActiveTab('triage')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'triage'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Shield className="w-3.5 h-3.5" />
            Incident Triage
          </button>

          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'analytics'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5" />
            Analytics & Trends
          </button>

          <button
            onClick={() => setActiveTab('copilot')}
            className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
              activeTab === 'copilot'
                ? 'bg-zinc-800 text-zinc-100 shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            AI Copilot Lab
          </button>
        </div>
      </div>

      {/* ── Active View Rendering ── */}
      {activeTab === 'triage' && (
        <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
          {/* Column 1: Live Alert Feed (Col-span 8) */}
          <div className="xl:col-span-8 flex flex-col min-h-0">
            <AlertsTable
              alerts={alerts}
              total={totalAlerts}
              page={page}
              perPage={perPage}
              filters={filters}
              onFilterChange={(newFilters) => {
                setFilters(newFilters);
                setPage(newFilters.page || 1);
              }}
              onAlertSelect={handleAlertSelect}
              selectedAlertId={selectedAlert?.id}
            />
          </div>

          {/* Column 2: Threat Map OR Incident Playbook Inspector (Col-span 4) */}
          <div className="xl:col-span-4 flex flex-col min-h-0">
            {selectedAlert ? (
              <AlertDetailSidebar
                alert={selectedAlert}
                onRespond={handleRespondAction}
                responseLogs={responseLogs}
                isResponding={isResponding}
                onClose={() => setSelectedAlert(null)}
                onVerifyAlert={handleVerifyAlert}
              />
            ) : (
              <div className="flex flex-col h-full gap-6">
                <ThreatHotspots geoData={geoData} />
                
                <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-6 flex flex-col items-center justify-center text-center gap-3 py-8">
                  <Shield className="w-6 h-6 text-emerald-500/80" />
                  <h3 className="text-sm font-semibold text-zinc-200 tracking-wide">Aegis Telemetry Active</h3>
                  <p className="text-xs text-zinc-400 max-w-[280px] leading-relaxed">
                    Live security incident streaming is running. Click any alert row on the left to analyze payloads, map MITRE ATT&CK vectors, and execute mitigation playbooks.
                  </p>
                </div>
              </div>
            )}
          </div>
        </main>
      )}

      {activeTab === 'analytics' && (
        <main className="flex-grow flex flex-col py-2 min-h-0">
          {/* Overview KPI Cards */}
          <OverviewCards stats={stats} />
          
          {/* Charts visualizations */}
          <div className="px-6 pb-6 flex-grow">
            <AnalyticsCharts
              timeline={timeline}
              severity={severityDist}
              sources={topSources}
            />
          </div>
        </main>
      )}

      {activeTab === 'copilot' && (
        <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
          {/* Column 1: Aegis Chat Assistant (Col-span 8) */}
          <div className="xl:col-span-8 flex flex-col min-h-[500px]">
            <AICopilot
              onSendMessage={handleSendChatMessage}
              chatHistory={chatHistory}
              isSendingMessage={isSendingMessage}
            />
          </div>

          {/* Column 2: Aegis AI Guide and Cheatsheet (Col-span 4) */}
          <div className="xl:col-span-4 flex flex-col min-h-0 gap-6">
            <div className="glassmorphism rounded-xl border border-cyber-card-border p-5 flex flex-col h-full">
              <div className="flex items-center gap-2 border-b border-cyber-card-border/30 pb-3 mb-4">
                <Terminal className="w-5 h-5 text-cyber-purple animate-pulse" />
                <h2 className="text-sm font-bold font-cyber tracking-wider text-slate-200 uppercase">
                  Aegis AI Copilot Lab
                </h2>
              </div>

              <p className="text-[11px] text-slate-400 font-mono mb-4 leading-relaxed">
                The Aegis AI Copilot leverages large language model (LLM) intelligence to inspect your entire security logs catalog, explain attack methodologies, and design remediation actions.
              </p>

              <div className="flex-1 flex flex-col gap-3 font-mono text-[10px] overflow-y-auto">
                <div className="text-slate-500 font-bold uppercase tracking-wider flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-cyber-blue" />
                  Suggested Threat Queries
                </div>

                {[
                  {
                    label: "Summarize High-Risk Incidents",
                    prompt: "Summarize all high and critical risk alerts currently stored in our system and tell me the primary threat source."
                  },
                  {
                    label: "Identify Malware Activity",
                    prompt: "Have there been any malware detections? Explain their impact and map them to MITRE ATT&CK techniques."
                  },
                  {
                    label: "Investigate SSH Brute Force",
                    prompt: "Review SSH brute force incidents in the logs and write a custom iptables firewall script to block the source IPs."
                  },
                  {
                    label: "Explain System Risk Scoring",
                    prompt: "How does the risk scorer weigh CVSS base metrics versus real-time anomaly scores? Explain in detail."
                  },
                  {
                    label: "Draft Incident Report Summary",
                    prompt: "Write a high-level executive cybersecurity incident summary report for the SOC team covering today's threat landscape."
                  }
                ].map((item, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePreCannedPromptClick(item.prompt)}
                    className="text-left w-full p-2.5 rounded border border-cyber-card-border hover:border-cyber-purple/50 bg-cyber-card/10 hover:bg-cyber-purple/5 text-slate-300 hover:text-white transition-all duration-200"
                  >
                    <div className="font-bold text-[11px] text-cyber-purple uppercase mb-1">{item.label}</div>
                    <div className="text-[10px] text-slate-400 italic line-clamp-2">"{item.prompt}"</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </main>
      )}
    </div>
  );
}

export default App;