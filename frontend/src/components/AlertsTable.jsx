import React from 'react';
import { Search, Shield, ChevronLeft, ChevronRight, Filter } from 'lucide-react';

function AlertsTable({
  alerts,
  total,
  page,
  perPage,
  filters,
  onFilterChange,
  onAlertSelect,
  selectedAlertId,
}) {
  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const eventTypes = [
    { label: 'ALL EVENTS', value: 'ALL' },
    { label: 'MALWARE', value: 'MALWARE_DETECTION' },
    { label: 'BRUTE FORCE', value: 'SSH_BRUTE_FORCE' },
    { label: 'EXFILTRATION', value: 'DATA_EXFILTRATION' },
    { label: 'PORT SCAN', value: 'PORT_SCAN' },
    { label: 'FAILED LOGIN', value: 'FAILED_LOGIN' },
  ];

  // Helper to color code severity badges with professional muted colors
  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-rose-500/10 border border-rose-500/20 text-rose-400';
      case 'HIGH':
        return 'bg-amber-500/10 border border-amber-500/20 text-amber-400';
      case 'MEDIUM':
        return 'bg-blue-500/10 border border-blue-500/20 text-blue-400';
      case 'LOW':
        return 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400';
      default:
        return 'bg-zinc-800 border border-zinc-700 text-zinc-400';
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / perPage));

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full min-h-[480px]">
      {/* 1. Header Filters Section */}
      <div className="flex flex-col md:flex-row gap-3 justify-between items-start md:items-center border-b border-zinc-800/80 pb-4 mb-4">
        {/* Title & Count */}
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-emerald-500/80" />
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100">
              Security Alert Feed
            </h2>
            <p className="text-[11px] text-zinc-500 font-mono">
              Total system events: <span className="text-zinc-300 font-semibold">{total}</span>
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Search bar */}
          <div className="relative flex-1 md:flex-none">
            <span className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
              <Search className="w-3.5 h-3.5" />
            </span>
            <input
              type="text"
              placeholder="Search IP, host, user..."
              value={filters.search}
              onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-mono text-xs rounded-lg pl-8 pr-3 py-1.5 w-full md:w-56 focus:outline-none focus:border-zinc-700 transition-colors"
            />
          </div>

          {/* Severity selector */}
          <div className="flex items-center gap-1.5 font-sans text-xs">
            <Filter className="w-3.5 h-3.5 text-zinc-500" />
            <select
              value={filters.severity}
              onChange={(e) => onFilterChange({ ...filters, severity: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {severities.map((sev) => (
                <option key={sev} value={sev === 'ALL' ? '' : sev} className="bg-zinc-950 text-zinc-300">
                  {sev}
                </option>
              ))}
            </select>
          </div>

          {/* Event type selector */}
          <div className="flex items-center gap-1.5 font-sans text-xs">
            <select
              value={filters.eventType}
              onChange={(e) => onFilterChange({ ...filters, eventType: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {eventTypes.map((et) => (
                <option key={et.value} value={et.value === 'ALL' ? '' : et.value} className="bg-zinc-950 text-zinc-300">
                  {et.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* 2. Grid Table Body */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left font-mono text-[11px] border-collapse">
          <thead>
            <tr className="text-zinc-500 border-b border-zinc-800/60 pb-2 uppercase text-[10px] tracking-wider font-semibold">
              <th className="py-2.5 px-3">Timestamp</th>
              <th className="py-2.5 px-3">Severity</th>
              <th className="py-2.5 px-3">Threat Type</th>
              <th className="py-2.5 px-3">Source IP</th>
              <th className="py-2.5 px-3">Destination IP</th>
              <th className="py-2.5 px-3 text-right">Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {alerts && alerts.length > 0 ? (
              alerts.map((alert) => {
                const isSelected = selectedAlertId === alert.id;
                const isRecent = alert.isNew;
                return (
                  <tr
                    key={alert.id}
                    onClick={() => onAlertSelect(alert)}
                    className={`cursor-pointer border-b border-zinc-800/40 transition-all hover:bg-zinc-800/20 ${isSelected ? 'bg-zinc-800/40 border-l-2 border-l-emerald-500 text-white font-medium' : 'text-zinc-300'}`}
                  >
                    <td className="py-3 px-3 text-zinc-400 flex items-center gap-1.5">
                      {isRecent && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block animate-pulse" title="New Alert" />}
                      {alert.timestamp}
                    </td>
                    <td className="py-3 px-3">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-semibold uppercase tracking-wider ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-semibold text-zinc-200">{alert.event_type}</td>
                    <td className="py-3 px-3 text-blue-400 font-semibold">{alert.src_ip}</td>
                    <td className="py-3 px-3 text-zinc-400">{alert.dest_ip}</td>
                    <td className="py-3 px-3 text-right font-bold">
                      <span className={alert.risk_score > 75 ? 'text-rose-400' : alert.risk_score > 50 ? 'text-amber-400' : 'text-emerald-400'}>
                        {alert.risk_score}
                      </span>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="6" className="py-12 text-center text-zinc-500 text-xs">
                  No security alerts matching search query.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* 3. Footer Pagination */}
      <div className="border-t border-zinc-800/80 pt-3 mt-3 flex justify-between items-center font-mono text-[10px] text-zinc-500">
        <div>
          Showing {alerts?.length ?? 0} of {total} events
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onFilterChange({ ...filters, page: Math.max(1, page - 1) })}
            disabled={page === 1}
            className="p-1 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white disabled:opacity-30 disabled:hover:text-zinc-400 transition-colors cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>
            Page <span className="text-zinc-200 font-semibold">{page}</span> of {totalPages}
          </span>
          <button
            onClick={() => onFilterChange({ ...filters, page: Math.min(totalPages, page + 1) })}
            disabled={page === totalPages}
            className="p-1 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white disabled:opacity-30 disabled:hover:text-zinc-400 transition-colors cursor-pointer"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

export default AlertsTable;
