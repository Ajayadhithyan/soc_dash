import React, { useState, useEffect, useCallback, useMemo, Suspense, lazy } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardHeader from './components/DashboardHeader';
import OverviewCards from './components/OverviewCards';
import ThreatHotspots from './components/ThreatHotspots';
import AlertsTable from './components/AlertsTable';
import AlertDetailSidebar from './components/AlertDetailSidebar';
import ErrorBoundary from './components/ErrorBoundary';
import { useToast } from './components/Toast';
import {
  getOverview, getSeverityDistribution, getTimeline, getTopSources, getGeoData,
  getAlerts, getAlertDetail, respondToAlert, sendChatMessage, trainModel,
  verifyAlert, checkHealth,
} from './utils/api';
import { Shield, TrendingUp, Cpu, Terminal } from 'lucide-react';
import type { AlertEvent, ChatMessage, SystemHealth } from './types';

const AnalyticsCharts = lazy(() => import('./components/AnalyticsCharts'));
const AICopilot = lazy(() => import('./components/AICopilot'));
const SOARAuditLogs = lazy(() => import('./components/SOARAuditLogs'));

const TABS = [
  { id: 'triage' as const, label: 'Incident Triage', icon: Shield },
  { id: 'analytics' as const, label: 'Analytics & Trends', icon: TrendingUp },
  { id: 'copilot' as const, label: 'AI Copilot Lab', icon: Cpu },
  { id: 'audit' as const, label: 'SOAR Audit Trail', icon: Terminal },
];

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const { addToast } = useToast();
  const tabFromPath = location.pathname.replace('/', '') || 'triage';
  const validTab = TABS.find(t => t.id === tabFromPath)?.id || 'triage';
  const [activeTab, setActiveTab] = useState(validTab);

  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [totalAlerts, setTotalAlerts] = useState(0);
  const [page, setPage] = useState(1);
  const perPage = 15;
  const [filters, setFilters] = useState({ search: '', severity: '', eventType: '' });

  const [selectedAlert, setSelectedAlert] = useState<AlertEvent | null>(null);
  const [isResponding, setIsResponding] = useState<string | null>(null);
  const [responseLogs, setResponseLogs] = useState<Record<string, unknown>>({});

  const [stats, setStats] = useState<Record<string, unknown> | null>(null);
  const [timeline, setTimeline] = useState<{ time: string; count: number }[]>([]);
  const [severityDist, setSeverityDist] = useState<{ severity: string; count: number }[]>([]);
  const [topSources, setTopSources] = useState<{ ip: string; count: number; last_seen: string; primary_attack: string }[]>([]);
  const [geoData, setGeoData] = useState<{ country: string; count: number; lat: number; lng: number }[]>([]);
  const [selectedRange, setSelectedRange] = useState('6h');

  const [wsStatus, setWsStatus] = useState('disconnected');
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  const fetchDashboardStats = useCallback(async () => {
    try {
      const [overviewData, sevData, timeData, srcData, mapData] = await Promise.all([
        getOverview(), getSeverityDistribution(), getTimeline(selectedRange),
        getTopSources(), getGeoData(),
      ]);
      setStats(overviewData);
      setSeverityDist(sevData.distribution);
      setTimeline(timeData.timeline);
      setTopSources(srcData.sources);
      setGeoData(mapData.geo_threats);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  }, [selectedRange]);

  const fetchAlertsList = useCallback(async () => {
    try {
      const params: Record<string, unknown> = {
        page, per_page: perPage,
        severity: filters.severity || undefined,
        event_type: filters.eventType || undefined,
      };
      const data = await getAlerts(params);
      let fetchedAlerts = data.alerts;
      if (filters.search) {
        const query = filters.search.toLowerCase();
        fetchedAlerts = fetchedAlerts.filter((a: AlertEvent) =>
          a.src_ip?.toLowerCase().includes(query) ||
          a.dest_ip?.toLowerCase().includes(query) ||
          a.user?.toLowerCase().includes(query) ||
          a.event_type?.toLowerCase().includes(query)
        );
      }
      setAlerts(fetchedAlerts);
      setTotalAlerts(data.total);
    } catch (err) {
      console.error('Error loading alerts list:', err);
    }
  }, [page, perPage, filters]);

  const fetchSystemHealth = useCallback(async () => {
    try {
      const data = await checkHealth();
      setSystemHealth(data);
    } catch {
      setSystemHealth({ status: 'offline', service: 'SOC API unreachable', database: '', gemini_api: '', anomaly_detector: '' });
    }
  }, []);

  useEffect(() => {
    setActiveTab(tabFromPath);
  }, [location.pathname]);

  const handleTabChange = useCallback((tabId: string) => {
    setActiveTab(tabId);
    navigate(tabId === 'triage' ? '/' : `/${tabId}`);
  }, [navigate]);

  useEffect(() => {
    fetchSystemHealth();
    fetchDashboardStats();
  }, [fetchDashboardStats, fetchSystemHealth]);

  useEffect(() => {
    fetchAlertsList();
  }, [fetchAlertsList]);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
    let reconnectAttempts = 0;

    const connectWS = () => {
      setWsStatus('connecting');
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws`;
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setWsStatus('connected');
        reconnectAttempts = 0;
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'NEW_ALERT') {
            const newAlert: AlertEvent = payload.data;
            newAlert.isNew = true;
            setAlerts((prev) => {
              const filtered = prev.filter((a) => a.id !== newAlert.id);
              return [newAlert, ...filtered.slice(0, perPage - 1)];
            });
            setTotalAlerts((prev) => prev + 1);
            fetchDashboardStats();
            setTimeout(() => {
              setAlerts((prev) => prev.map((a) => (a.id === newAlert.id ? { ...a, isNew: false } : a)));
            }, 4000);
          }
        } catch { /* ignore non-JSON */ }
      };

      socket.onclose = () => {
        setWsStatus('disconnected');
        if (reconnectAttempts < 10) {
          const delay = Math.min(3000 * Math.pow(1.5, reconnectAttempts), 30000);
          reconnectTimeout = setTimeout(connectWS, delay);
          reconnectAttempts++;
        }
      };

      socket.onerror = () => { socket?.close(); };
    };

    connectWS();
    return () => {
      if (socket) { socket.onclose = null; socket.onerror = null; socket.close(); }
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [perPage, fetchDashboardStats]);

  const handleAlertSelect = useCallback(async (alertSummary: AlertEvent) => {
    try {
      const detail = await getAlertDetail(alertSummary.id);
      setSelectedAlert(detail);
    } catch {
      setSelectedAlert(alertSummary);
    }
  }, []);

  const handleRespondAction = useCallback(async (action: string) => {
    if (!selectedAlert) return;
    setIsResponding(action);
    try {
      const result = await respondToAlert(selectedAlert.id, action);
      setResponseLogs((prev) => ({ ...prev, [selectedAlert.id]: result }));
      addToast({ type: 'success', title: 'Action Executed', message: `${action} completed successfully.` });
      const updatedDetail = await getAlertDetail(selectedAlert.id);
      setSelectedAlert(updatedDetail);
    } catch (err) {
      console.error('Playbook execution failed:', err);
      addToast({ type: 'error', title: 'Action Failed', message: `Failed to execute ${action}.` });
    } finally {
      setIsResponding(null);
    }
  }, [selectedAlert, addToast]);

  const handleSendChatMessage = useCallback(async (msgText: string) => {
    if (!msgText.trim()) return;
    const userMsg: ChatMessage = { sender: 'user', text: msgText };
    setChatHistory((prev) => [...prev, userMsg]);
    setIsSendingMessage(true);
    try {
      const res = await sendChatMessage(msgText);
      const botMsg: ChatMessage = { sender: 'bot', text: res.response, context_alerts_used: res.context_alerts_used };
      setChatHistory((prev) => [...prev, botMsg]);
    } catch {
      setChatHistory((prev) => [...prev, { sender: 'bot', text: 'I encountered an error communicating with the Zenith AI orchestrator core.' }]);
    } finally {
      setIsSendingMessage(false);
    }
  }, []);

  const handleManualRefresh = useCallback(() => {
    fetchSystemHealth();
    fetchDashboardStats();
    fetchAlertsList();
    addToast({ type: 'info', title: 'Refreshing', message: 'Dashboard data syncing...' });
  }, [fetchSystemHealth, fetchDashboardStats, fetchAlertsList, addToast]);

  const handleTrainModel = useCallback(async () => {
    try {
      const data = await trainModel();
      fetchSystemHealth();
      fetchDashboardStats();
      fetchAlertsList();
      addToast({ type: 'success', title: 'Model Trained', message: 'Anomaly detector retrained successfully.' });
      return data;
    } catch {
      addToast({ type: 'error', title: 'Training Failed', message: 'API error occurred during training.' });
      return { success: false, message: 'API error occurred.' };
    }
  }, [fetchSystemHealth, fetchDashboardStats, fetchAlertsList, addToast]);

  const handleVerifyAlert = useCallback(async (alertId: string, status: string) => {
    try {
      const res = await verifyAlert(alertId, status);
      if (res?.success) {
        setSelectedAlert((prev) => {
          if (prev && prev.id === alertId) {
            return { ...prev, analyst_verification: status as 'TRUE_POSITIVE' | 'FALSE_POSITIVE' };
          }
          return prev;
        });
        setAlerts((prev) =>
          prev.map((a) => (a.id === alertId ? { ...a, analyst_verification: status as 'TRUE_POSITIVE' | 'FALSE_POSITIVE' } : a))
        );
        addToast({ type: 'success', title: 'Alert Verified', message: `Marked as ${status.replace('_', ' ')}.` });
      }
    } catch (err) {
      console.error('Error verifying alert:', err);
    }
  }, [addToast]);

  const handleFilterChange = useCallback((newFilters: { search: string; severity: string; eventType: string; page?: number }) => {
    setFilters(newFilters);
    setPage(newFilters.page || 1);
  }, []);

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-cyber-bg cyber-grid-bg text-zinc-200 font-sans flex flex-col antialiased">
        <DashboardHeader
          wsStatus={wsStatus}
          systemHealth={systemHealth}
          onRefresh={handleManualRefresh}
          onTrainModel={handleTrainModel}
        />

        <div className="px-6 py-3 border-b border-zinc-800 bg-zinc-950/80 flex flex-wrap gap-2 text-xs z-10">
          <div className="flex bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80">
            {TABS.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-md transition-all font-medium cursor-pointer ${
                    activeTab === tab.id ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {activeTab === 'triage' && (
          <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
            <div className="xl:col-span-8 flex flex-col min-h-0">
              <AlertsTable
                alerts={alerts}
                total={totalAlerts}
                page={page}
                perPage={perPage}
                filters={filters}
                onFilterChange={handleFilterChange}
                onAlertSelect={handleAlertSelect}
                selectedAlertId={selectedAlert?.id}
              />
            </div>
            <div className="xl:col-span-4 flex flex-col min-h-0">
              <ErrorBoundary>
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
                      <h3 className="text-sm font-semibold text-zinc-200 tracking-wide">Zenith Telemetry Active</h3>
                      <p className="text-xs text-zinc-400 max-w-[280px] leading-relaxed">
                        Live security incident streaming is running. Click any alert row on the left to analyze payloads, map MITRE ATT&CK vectors, and execute mitigation playbooks.
                      </p>
                    </div>
                  </div>
                )}
              </ErrorBoundary>
            </div>
          </main>
        )}

        {activeTab === 'analytics' && (
          <main className="flex-grow flex flex-col py-2 min-h-0">
            <OverviewCards stats={stats as any} />
            <div className="px-6 pb-6 flex-grow">
              <Suspense fallback={<div className="flex-grow flex items-center justify-center py-20"><div className="text-zinc-500 text-xs font-mono">LOADING...</div></div>}>
                <AnalyticsCharts
                  timeline={timeline}
                  severity={severityDist}
                  sources={topSources}
                  selectedRange={selectedRange}
                  onRangeChange={setSelectedRange}
                />
              </Suspense>
            </div>
          </main>
        )}

        {activeTab === 'copilot' && (
          <main className="flex-grow px-6 py-6 grid grid-cols-1 xl:grid-cols-12 gap-6 min-h-0">
            <div className="xl:col-span-8 flex flex-col min-h-[500px]">
              <ErrorBoundary>
                <Suspense fallback={<div className="flex-grow flex items-center justify-center py-20"><div className="text-zinc-500 text-xs font-mono">LOADING...</div></div>}>
                  <AICopilot
                    onSendMessage={handleSendChatMessage}
                    chatHistory={chatHistory}
                    isSendingMessage={isSendingMessage}
                  />
                </Suspense>
              </ErrorBoundary>
            </div>
            <div className="xl:col-span-4 flex flex-col min-h-0 gap-6">
              <div className="glassmorphism rounded-xl border border-cyber-card-border p-5 flex flex-col h-full">
                <div className="flex items-center gap-2 border-b border-cyber-card-border/30 pb-3 mb-4">
                  <Cpu className="w-5 h-5 text-purple-500 animate-pulse" />
                  <h2 className="text-sm font-bold font-cyber tracking-wider text-slate-200 uppercase">Zenith AI Copilot Lab</h2>
                </div>
                <p className="text-[11px] text-slate-400 font-mono mb-4 leading-relaxed">
                  The Zenith AI Copilot leverages large language model intelligence to inspect your security logs catalog, explain attack methodologies, and design remediation actions.
                </p>
                <div className="flex-1 flex flex-col gap-3 font-mono text-[10px] overflow-y-auto">
                  <div className="text-slate-500 font-bold uppercase tracking-wider">Suggested Threat Queries</div>
                  {[
                    { label: "Summarize High-Risk Incidents", prompt: "Summarize all high and critical risk alerts currently stored in our system and tell me the primary threat source." },
                    { label: "Identify Malware Activity", prompt: "Have there been any malware detections? Explain their impact and map them to MITRE ATT&CK techniques." },
                    { label: "Investigate SSH Brute Force", prompt: "Review SSH brute force incidents in the logs and write a custom iptables firewall script to block the source IPs." },
                    { label: "Explain System Risk Scoring", prompt: "How does the risk scorer weigh CVSS base metrics versus real-time anomaly scores? Explain in detail." },
                    { label: "Draft Incident Report Summary", prompt: "Write a high-level executive cybersecurity incident summary report for the SOC team covering today's threat landscape." },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendChatMessage(item.prompt)}
                      className="text-left w-full p-2.5 rounded border border-cyber-card-border hover:border-purple-500/50 bg-cyber-card/10 hover:bg-purple-500/5 text-slate-300 hover:text-white transition-all duration-200"
                    >
                      <div className="font-bold text-[11px] text-purple-500 uppercase mb-1">{item.label}</div>
                      <div className="text-[10px] text-slate-400 italic line-clamp-2">"{item.prompt}"</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </main>
        )}

        {activeTab === 'audit' && (
          <ErrorBoundary>
            <Suspense fallback={<div className="flex-grow flex items-center justify-center py-20"><div className="text-zinc-500 text-xs font-mono">LOADING...</div></div>}>
              <SOARAuditLogs />
            </Suspense>
          </ErrorBoundary>
        )}
      </div>
    </ErrorBoundary>
  );
}

export default App;
