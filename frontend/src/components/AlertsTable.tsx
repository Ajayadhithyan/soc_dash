import React, { useState, memo, useCallback, useMemo } from 'react';
import { Search, Shield, ChevronLeft, ChevronRight, Filter, Download, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { useDebounce } from '../hooks/useDebounce';
import { exportAlertsToCsv } from '../utils/api';
import { AlertTableSkeleton } from './LoadingSkeleton';

import type { AlertEvent, SortField, SortOrder } from '../types';

interface AlertsTableProps {
  alerts: AlertEvent[];
  total: number;
  page: number;
  perPage: number;
  filters: { search: string; severity: string; eventType: string; page?: number };
  onFilterChange: (filters: { search: string; severity: string; eventType: string; page?: number }) => void;
  onAlertSelect: (alert: AlertEvent) => void;
  selectedAlertId: string | undefined;
  loading?: boolean;
}

function AlertsTable({
  alerts,
  total,
  page,
  perPage,
  filters,
  onFilterChange,
  onAlertSelect,
  selectedAlertId,
  loading = false,
}: AlertsTableProps) {
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  const debouncedSearch = useDebounce(filters.search, 300);

  const severities = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  const eventTypes = [
    { label: 'ALL EVENTS', value: 'ALL' },
    { label: 'MALWARE', value: 'MALWARE_DETECTION' },
    { label: 'BRUTE FORCE', value: 'SSH_BRUTE_FORCE' },
    { label: 'EXFILTRATION', value: 'DATA_EXFILTRATION' },
    { label: 'PORT SCAN', value: 'PORT_SCAN' },
    { label: 'FAILED LOGIN', value: 'FAILED_LOGIN' },
  ];

  const getSeverityBadge = useCallback((severity: string) => {
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
  }, []);

  const handleSort = useCallback((field: SortField) => {
    setSortField((prev) => {
      if (prev === field) {
        setSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
        return field;
      }
      setSortOrder('desc');
      return field;
    });
  }, []);

  const SortIcon = useCallback(({ field }: { field: SortField }) => {
    if (sortField !== field) return <ArrowUpDown className="w-2.5 h-2.5 text-zinc-600" />;
    return sortOrder === 'asc' ? <ArrowUp className="w-2.5 h-2.5 text-emerald-400" /> : <ArrowDown className="w-2.5 h-2.5 text-emerald-400" />;
  }, [sortField, sortOrder]);

  const sortedAlerts = useMemo(() => {
    if (!alerts) return [];
    const sorted = [...alerts];
    sorted.sort((a, b) => {
      let aVal: number | string = '';
      let bVal: number | string = '';
      switch (sortField) {
        case 'timestamp': aVal = a.timestamp || ''; bVal = b.timestamp || ''; break;
        case 'severity': {
          const order = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
          aVal = order[a.severity as keyof typeof order] || 0;
          bVal = order[b.severity as keyof typeof order] || 0;
          break;
        }
        case 'event_type': aVal = a.event_type || ''; bVal = b.event_type || ''; break;
        case 'src_ip': aVal = a.src_ip || ''; bVal = b.src_ip || ''; break;
        case 'dest_ip': aVal = a.dest_ip || ''; bVal = b.dest_ip || ''; break;
        case 'risk_score': aVal = a.risk_score || 0; bVal = b.risk_score || 0; break;
        default: break;
      }
      if (typeof aVal === 'string') return sortOrder === 'asc' ? aVal.localeCompare(bVal as string) : (bVal as string).localeCompare(aVal);
      return sortOrder === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
    return sorted;
  }, [alerts, sortField, sortOrder]);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, search: e.target.value });
  }, [filters, onFilterChange]);

  const totalPages = Math.max(1, Math.ceil(total / perPage));

  if (loading) return <AlertTableSkeleton />;

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full min-h-[480px]">
      <div className="flex flex-col md:flex-row gap-3 justify-between items-start md:items-center border-b border-zinc-800/80 pb-4 mb-4">
        <div className="flex items-center gap-2.5">
          <Shield className="w-5 h-5 text-emerald-500/80" />
          <div>
            <h2 className="text-sm font-semibold tracking-wide text-zinc-100">Security Alert Feed</h2>
            <p className="text-[11px] text-zinc-500 font-mono">
              Total system events: <span className="text-zinc-300 font-semibold">{total}</span>
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:flex-none">
            <span className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none text-zinc-500">
              <Search className="w-3.5 h-3.5" />
            </span>
            <input
              type="text"
              placeholder="Search IP, host, user..."
              value={filters.search}
              onChange={handleSearchChange}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 font-mono text-xs rounded-lg pl-8 pr-3 py-1.5 w-full md:w-56 focus:outline-none focus:border-zinc-700 transition-colors"
            />
          </div>

          <div className="flex items-center gap-1.5 font-sans text-xs">
            <Filter className="w-3.5 h-3.5 text-zinc-500" />
            <select
              value={filters.severity}
              onChange={(e) => onFilterChange({ ...filters, severity: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {severities.map((sev) => (
                <option key={sev} value={sev === 'ALL' ? '' : sev} className="bg-zinc-950 text-zinc-300">{sev}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-1.5 font-sans text-xs">
            <select
              value={filters.eventType}
              onChange={(e) => onFilterChange({ ...filters, eventType: e.target.value })}
              className="bg-zinc-950/60 border border-zinc-800 text-zinc-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-zinc-700 transition-colors text-xs"
            >
              {eventTypes.map((et) => (
                <option key={et.value} value={et.value === 'ALL' ? '' : et.value} className="bg-zinc-950 text-zinc-300">{et.label}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => exportAlertsToCsv(alerts)}
            disabled={!alerts || alerts.length === 0}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-zinc-800 bg-zinc-950/60 hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors cursor-pointer text-xs disabled:opacity-30"
            title="Export to CSV"
          >
            <Download className="w-3.5 h-3.5" />
            Export
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-left font-mono text-[11px] border-collapse">
          <thead>
            <tr className="text-zinc-500 border-b border-zinc-800/60 pb-2 uppercase text-[10px] tracking-wider font-semibold">
              {[
                { field: 'timestamp' as SortField, label: 'Timestamp' },
                { field: 'severity' as SortField, label: 'Severity' },
                { field: 'event_type' as SortField, label: 'Threat Type' },
                { field: 'src_ip' as SortField, label: 'Source IP' },
                { field: 'dest_ip' as SortField, label: 'Destination IP' },
                { field: 'risk_score' as SortField, label: 'Risk Score' },
              ].map(({ field, label }) => (
                <th
                  key={field}
                  className={`py-2.5 px-3 cursor-pointer select-none transition-colors hover:text-zinc-300 ${field === 'risk_score' ? 'text-right' : ''}`}
                  onClick={() => handleSort(field)}
                >
                  <span className="flex items-center gap-1">
                    {label}
                    <SortIcon field={field} />
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedAlerts.length > 0 ? (
              sortedAlerts.map((alert) => {
                const isSelected = selectedAlertId === alert.id;
                const isRecent = alert.isNew;
                const isHovered = hoveredRow === alert.id;
                return (
                  <tr
                    key={alert.id}
                    onClick={() => onAlertSelect(alert)}
                    onMouseEnter={() => setHoveredRow(alert.id)}
                    onMouseLeave={() => setHoveredRow(null)}
                    className={`cursor-pointer border-b border-zinc-800/40 transition-all ${
                      isSelected ? 'bg-zinc-800/40 border-l-2 border-l-emerald-500 text-white font-medium' : isHovered ? 'bg-zinc-800/20' : 'text-zinc-300'
                    }`}
                  >
                    <td className="py-3 px-3 text-zinc-400">
                      <span className="flex items-center gap-1.5">
                        {isRecent && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block animate-pulse" title="New Alert" />}
                        {alert.severity === 'CRITICAL' && (
                          <span className="w-1 h-1 rounded-full bg-rose-500 inline-block animate-pulse" />
                        )}
                        {alert.timestamp}
                      </span>
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
                <td colSpan="6" className="py-12 text-center text-zinc-500 text-xs">No security alerts matching search query.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="border-t border-zinc-800/80 pt-3 mt-3 flex justify-between items-center font-mono text-[10px] text-zinc-500">
        <div>Showing {alerts?.length ?? 0} of {total} events</div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onFilterChange({ ...filters, page: Math.max(1, page - 1) })}
            disabled={page === 1}
            className="p-1 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-white disabled:opacity-30 disabled:hover:text-zinc-400 transition-colors cursor-pointer"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span>Page <span className="text-zinc-200 font-semibold">{page}</span> of {totalPages}</span>
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

export default memo(AlertsTable);
