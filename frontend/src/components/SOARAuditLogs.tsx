import React, { useState, useEffect, useCallback, memo } from 'react';
import { getAuditLogs } from '../utils/api';
import { ShieldAlert, Terminal, CheckCircle2, Search, RefreshCw, ChevronDown, ChevronUp, Clock, User, Clipboard, Download, Shield, Activity, FileText } from 'lucide-react';

import type { AuditLog } from '../types';

function SOARAuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const [filterAction, setFilterAction] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAuditLogs(100);
      setLogs(data.audit_logs || []);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setError('Failed to retrieve SOAR audit trails from the server.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const toggleRow = (index: number) => {
    setExpandedRow(expandedRow === index ? null : index);
  };

  const getActionLabel = (action: string) => {
    switch (action) {
      case 'block_ip':
        return { label: 'BLOCK IP', color: 'bg-rose-500/10 border-rose-500/20 text-rose-400' };
      case 'quarantine_host':
        return { label: 'ISOLATE HOST', color: 'bg-amber-500/10 border-amber-500/20 text-amber-400' };
      case 'create_ticket':
        return { label: 'CREATE TICKET', color: 'bg-blue-500/10 border-blue-500/20 text-blue-400' };
      default:
        return { label: action.toUpperCase(), color: 'bg-zinc-800 border-zinc-700 text-zinc-300' };
    }
  };

  const filteredLogs = logs.filter((log) => {
    const matchesAction = filterAction === 'all' || log.action === filterAction;
    const matchesSearch =
      searchTerm === '' ||
      log.alert_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.analyst_user?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      JSON.stringify(log.details || {}).toLowerCase().includes(searchTerm.toLowerCase());
    return matchesAction && matchesSearch;
  });

  const totalActions = logs.length;
  const ipsBlocked = logs.filter(log => log.action === 'block_ip').length;
  const hostsIsolated = logs.filter(log => log.action === 'quarantine_host').length;
  const ticketsCreated = logs.filter(log => log.action === 'create_ticket').length;

  const handleExportCSV = () => {
    if (logs.length === 0) return;

    let csvContent = "Timestamp,Action,Alert ID Target,Triggered By,Status,Details\n";
    logs.forEach((log) => {
      const timestamp = log.timestamp || "";
      const action = log.action || "";
      const alertId = log.alert_id || "";
      const user = log.analyst_user || "";
      const status = "SUCCESS";
      const details = JSON.stringify(log.details || {}).replace(/"/g, '""');
      csvContent += `"${timestamp}","${action}","${alertId}","${user}","${status}","${details}"\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `soar_compliance_audit_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex-grow px-6 py-6 flex flex-col min-h-0">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <Terminal className="w-5 h-5 text-purple-500" />
            SOAR Automation Compliance Audit
          </h2>
          <p className="text-xs text-zinc-400">
            Chronological ledger of executed active containment playbooks and security integrations.
          </p>
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <button onClick={handleExportCSV} disabled={loading || logs.length === 0} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors cursor-pointer text-xs disabled:opacity-40">
            <Download className="w-3.5 h-3.5 text-purple-400" />Export CSV
          </button>
          <button onClick={fetchLogs} disabled={loading} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-zinc-300 hover:text-white transition-colors cursor-pointer text-xs disabled:opacity-40">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />Sync Logs
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Mitigations', value: totalActions, color: 'purple', icon: Terminal, status: 'Ledger coverage active', pulse: true },
          { label: 'IPs Blocked', value: ipsBlocked, color: 'rose', icon: Shield, status: 'Firewall sync active', pulse: false },
          { label: 'Hosts Isolated', value: hostsIsolated, color: 'amber', icon: Activity, status: 'EDR quarantine active', pulse: false },
          { label: 'Jira Tickets', value: ticketsCreated, color: 'blue', icon: FileText, status: 'ITSM escalation active', pulse: false },
        ].map(({ label, value, color, icon: KpiIcon, status, pulse }) => (
          <div key={label} className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4">
            <div className="flex flex-col">
              <span className="text-[10px] text-zinc-500 font-semibold tracking-wide uppercase">{label}</span>
              <span className="text-2xl font-bold text-white mt-1 leading-none tracking-tight">{value}</span>
              <span className="text-[9px] text-zinc-400 mt-2 flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full bg-${color}-500 inline-block ${pulse ? 'animate-pulse' : ''}`}></span>
                {status}
              </span>
            </div>
            <div className={`p-2 rounded-lg border border-zinc-800 bg-zinc-950 text-${color}-400`}>
              <KpiIcon className="w-4 h-4" />
            </div>
          </div>
        ))}
      </div>

      <div className="bg-zinc-950/80 border border-zinc-800 rounded-xl p-4 mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-80">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-zinc-500 pointer-events-none"><Search className="w-3.5 h-3.5" /></span>
          <input
            type="text"
            placeholder="Search by ID, IP, or parameter..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-900/40 border border-zinc-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-zinc-300 placeholder-zinc-500 focus:outline-none focus:border-zinc-700 focus:bg-zinc-900 transition-colors"
          />
        </div>
        <div className="flex bg-zinc-900/60 p-1 rounded-lg border border-zinc-800/80 text-xs w-full md:w-auto justify-center">
          {[
            { id: 'all', name: 'All Actions' },
            { id: 'block_ip', name: 'IP Block' },
            { id: 'quarantine_host', name: 'Isolations' },
            { id: 'create_ticket', name: 'Jira Tickets' },
          ].map((item) => (
            <button key={item.id} onClick={() => setFilterAction(item.id)} className={`px-3 py-1 rounded-md transition-all font-medium cursor-pointer ${filterAction === item.id ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'}`}>
              {item.name}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 bg-zinc-900/25 border border-zinc-800/80 rounded-xl overflow-hidden flex flex-col min-h-0">
        <div className="flex-grow overflow-auto">
          {loading && logs.length === 0 ? (
            <div className="h-60 flex flex-col justify-center items-center gap-3">
              <RefreshCw className="w-6 h-6 text-purple-500 animate-spin" />
              <span className="text-zinc-500 text-xs font-mono">RETRIEVING COMPLIANCE LEDGER...</span>
            </div>
          ) : error ? (
            <div className="h-60 flex flex-col justify-center items-center gap-3 text-center px-4">
              <ShieldAlert className="w-8 h-8 text-rose-500" />
              <span className="text-zinc-300 text-xs font-semibold">{error}</span>
              <button onClick={fetchLogs} className="mt-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs rounded border border-zinc-700 cursor-pointer">Retry Request</button>
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="h-60 flex flex-col justify-center items-center text-zinc-500 text-xs font-sans">
              <Clipboard className="w-8 h-8 text-zinc-700 mb-2" />No audit logs found matching the search criteria.
            </div>
          ) : (
            <table className="w-full text-left border-collapse font-sans text-xs">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-950/60 text-zinc-400 uppercase font-mono text-[10px] tracking-wider">
                  <th className="py-3 px-4 font-semibold">Timestamp</th>
                  <th className="py-3 px-4 font-semibold">Action Triggered</th>
                  <th className="py-3 px-4 font-semibold">Security Alert Target</th>
                  <th className="py-3 px-4 font-semibold">Triggered By</th>
                  <th className="py-3 px-4 font-semibold text-center">Status</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/40">
                {filteredLogs.map((log, index) => {
                  const actionStyle = getActionLabel(log.action);
                  const isExpanded = expandedRow === index;

                  let targetStr = 'N/A';
                  if (log.action === 'block_ip') {
                    targetStr = `IP: ${log.details?.ip_blocked || 'Unknown'}`;
                  } else if (log.action === 'quarantine_host') {
                    targetStr = `Subnet Isolation`;
                  } else if (log.action === 'create_ticket') {
                    targetStr = `Ticket: ${log.details?.ticket_id || 'INC-ID'}`;
                  }

                  return (
                    <React.Fragment key={index}>
                      <tr className="hover:bg-zinc-800/20 transition-colors">
                        <td className="py-3 px-4 text-zinc-400 font-mono flex items-center gap-1.5">
                          <Clock className="w-3 h-3 text-zinc-600" />{log.timestamp}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded border text-[9px] font-mono font-semibold ${actionStyle.color}`}>{actionStyle.label}</span>
                        </td>
                        <td className="py-3 px-4 text-zinc-300 font-mono font-medium">{targetStr}</td>
                        <td className="py-3 px-4 text-zinc-400 font-mono flex items-center gap-1.5">
                          <User className="w-3 h-3 text-zinc-600" />{log.analyst_user}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-500/5 px-2 py-0.5 rounded-full border border-emerald-500/10 text-[9px] font-semibold">
                            <CheckCircle2 className="w-3 h-3" />SUCCESS
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button onClick={() => toggleRow(index)} className="text-zinc-500 hover:text-zinc-300 p-1 rounded hover:bg-zinc-800/50 cursor-pointer">
                            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                          </button>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-zinc-950/40">
                          <td colSpan={6} className="py-4 px-6 border-b border-zinc-800/80">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div className="space-y-2">
                                <div className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">Audit Metadata</div>
                                <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-lg p-3 space-y-1.5 font-mono text-[10px] text-zinc-400">
                                  <div><span className="text-zinc-600">Event ID Ref:</span> {log.alert_id}</div>
                                  <div><span className="text-zinc-600">Action:</span> {log.action}</div>
                                  <div><span className="text-zinc-600">User Scope:</span> {log.analyst_user} (Tier-1 SOC Admin)</div>
                                  <div><span className="text-zinc-600">Timestamp:</span> {log.timestamp}</div>
                                </div>
                              </div>
                              <div className="space-y-2">
                                <div className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">SOAR Response Payload</div>
                                <div className="bg-zinc-900/60 border border-zinc-800/60 rounded-lg p-3">
                                  <pre className="text-emerald-500 font-mono text-[10px] whitespace-pre-wrap leading-relaxed">{JSON.stringify(log.details || {}, null, 2)}</pre>
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
        <div className="bg-zinc-950/60 border-t border-zinc-800 px-4 py-2.5 flex justify-between items-center text-[10px] text-zinc-500 font-mono">
          <div>TOTAL AUDITED ACTIONS: {filteredLogs.length}</div>
          <div>COMPLIANCE STATUS: SECURE</div>
        </div>
      </div>
    </div>
  );
}

export default memo(SOARAuditLogs);
