import { useState, useEffect, useCallback, memo } from 'react';
import { getEndpoints } from '../utils/api';
import { Server, Wifi, WifiOff, RefreshCw, MonitorCog, Cpu, MemoryStick, HardDrive } from 'lucide-react';
import type { EndpointInfo } from '../types';

function relativeTime(iso: string | undefined): string {
  if (!iso) return 'never';
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return 'unknown';
  const seconds = Math.max(0, Math.floor((Date.now() - then) / 1000));
  if (seconds < 5) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function UsageBar({ value, color }: { value: number; color: string }) {
  const pct = Math.min(100, Math.max(0, value));
  return (
    <div className="flex items-center gap-2 min-w-[120px]">
      <div className="flex-1 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-mono text-zinc-400 w-9 text-right">{Math.round(pct)}%</span>
    </div>
  );
}

function EndpointsTable() {
  const [endpoints, setEndpoints] = useState<EndpointInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEndpoints = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEndpoints();
      setEndpoints(data.endpoints || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Error fetching endpoints:', err);
      setError('Failed to load endpoint inventory from the server.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEndpoints();
    const interval = setInterval(fetchEndpoints, 15000);
    return () => clearInterval(interval);
  }, [fetchEndpoints]);

  const onlineCount = endpoints.filter((e) => e.is_online).length;

  return (
    <main className="flex-grow px-6 py-6 min-h-0">
      <div className="max-w-6xl mx-auto flex flex-col gap-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-sm font-bold font-cyber tracking-wider text-zinc-200 uppercase flex items-center gap-2">
              <MonitorCog className="w-4 h-4 text-cyan-400" /> Endpoint Agents
            </h1>
            <p className="text-[11px] text-zinc-500 font-mono mt-1">
              Telemetry inventory of deployed endpoint detection agents.
            </p>
          </div>
          <button
            onClick={fetchEndpoints}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md border border-zinc-700 hover:border-cyan-500/50 text-zinc-300 hover:text-white text-xs font-medium transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* KPI strip */}
        <div className="grid grid-cols-3 gap-3">
          <div className="glassmorphism rounded-xl border border-cyber-card-border p-4">
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono">Endpoints</div>
            <div className="text-2xl font-bold font-mono text-zinc-100 mt-1">{total}</div>
          </div>
          <div className="glassmorphism rounded-xl border border-cyber-card-border p-4">
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono flex items-center gap-1">
              <Wifi className="w-3 h-3 text-emerald-500" /> Online
            </div>
            <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{onlineCount}</div>
          </div>
          <div className="glassmorphism rounded-xl border border-cyber-card-border p-4">
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-mono flex items-center gap-1">
              <WifiOff className="w-3 h-3 text-rose-500" /> Offline
            </div>
            <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{total - onlineCount}</div>
          </div>
        </div>

        {/* Table */}
        <div className="glassmorphism rounded-xl border border-cyber-card-border overflow-hidden">
          <div className="border-b border-cyber-card-border/40 px-4 py-2.5 flex items-center gap-2">
            <Server className="w-4 h-4 text-cyan-500" />
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-300">Endpoint Inventory</span>
            <span className="ml-auto text-[10px] font-mono text-zinc-500">AUTO-REFRESH 15s</span>
          </div>

          {error && (
            <div className="px-4 py-3 text-xs text-rose-400 border-b border-rose-500/20 bg-rose-500/5">{error}</div>
          )}

          {loading && !error && endpoints.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-2">
              <RefreshCw className="w-5 h-5 text-zinc-600 animate-spin" />
              <div className="text-zinc-500 text-xs font-mono">SYNCING ENDPOINT TELEMETRY...</div>
            </div>
          ) : endpoints.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 gap-2 text-center px-6">
              <Server className="w-6 h-6 text-zinc-700" />
              <div className="text-zinc-400 text-xs font-mono">No endpoints have checked in yet.</div>
              <div className="text-zinc-600 text-[11px] font-mono max-w-md leading-relaxed">
                Deploy the endpoint agent (agent/ package) with a valid token and it will appear here
                automatically on its first heartbeat.
              </div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-[10px] uppercase tracking-wider text-zinc-500 border-b border-cyber-card-border/40">
                    <th className="px-4 py-2.5 font-mono">Status</th>
                    <th className="px-4 py-2.5 font-mono">Hostname</th>
                    <th className="px-4 py-2.5 font-mono">OS</th>
                    <th className="px-4 py-2.5 font-mono">Agent</th>
                    <th className="px-4 py-2.5 font-mono">IP</th>
                    <th className="px-4 py-2.5 font-mono">CPU / MEM / DISK</th>
                    <th className="px-4 py-2.5 font-mono">Events</th>
                    <th className="px-4 py-2.5 font-mono text-right">Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {endpoints.map((ep) => (
                    <tr key={ep.agent_id} className="border-b border-cyber-card-border/30 hover:bg-cyan-500/5 transition-colors">
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1.5 text-[10px] font-bold px-2 py-0.5 rounded border ${
                            ep.is_online
                              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                              : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                          }`}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${ep.is_online ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
                          {ep.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-xs font-semibold text-zinc-200 font-mono">{ep.hostname || ep.agent_id}</div>
                        <div className="text-[10px] text-zinc-500 font-mono">{ep.agent_id}</div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="text-xs text-zinc-300 font-mono">{ep.os || '—'}</div>
                        <div className="text-[10px] text-zinc-500 font-mono">{ep.os_version || ''}</div>
                      </td>
                      <td className="px-4 py-3 text-xs text-zinc-400 font-mono">v{ep.agent_version || '?'}</td>
                      <td className="px-4 py-3 text-xs text-zinc-400 font-mono">{ep.ip || '—'}</td>
                      <td className="px-4 py-3">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-1.5">
                            <Cpu className="w-3 h-3 text-cyan-500 shrink-0" />
                            <UsageBar value={ep.cpu_percent} color="bg-cyan-500" />
                          </div>
                          <div className="flex items-center gap-1.5">
                            <MemoryStick className="w-3 h-3 text-purple-500 shrink-0" />
                            <UsageBar value={ep.memory_percent} color="bg-purple-500" />
                          </div>
                          <div className="flex items-center gap-1.5">
                            <HardDrive className="w-3 h-3 text-amber-500 shrink-0" />
                            <UsageBar value={ep.disk_percent} color="bg-amber-500" />
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-xs font-mono text-zinc-400">{ep.event_count}</td>
                      <td className="px-4 py-3 text-right">
                        <div className={`text-xs font-mono ${ep.is_online ? 'text-emerald-400' : 'text-zinc-500'}`}>
                          {relativeTime(ep.last_seen)}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default memo(EndpointsTable);