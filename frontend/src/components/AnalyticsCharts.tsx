import React, { memo } from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar,
} from 'recharts';
import { Shield, Flame, Activity, Clock, BarChart3, Gauge } from 'lucide-react';
import type { TopSource, EventTypeDistribution, RiskDistribution } from '../types';

interface AnalyticsChartsProps {
  timeline: { time: string; count: number }[];
  severity: { severity: string; count: number }[];
  sources: TopSource[];
  eventTypes: EventTypeDistribution[];
  riskDistribution: RiskDistribution[];
  selectedRange: string;
  onRangeChange: (range: string) => void;
}

const SEV_COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#10b981',
};

const RISK_COLORS: Record<string, string> = {
  Critical: '#ef4444',
  High: '#f59e0b',
  Medium: '#3b82f6',
  Low: '#10b981',
};

const EVENT_COLORS = ['#8b5cf6', '#06b6d4', '#f43f5e', '#f59e0b', '#10b981', '#ec4899', '#6366f1'];

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-zinc-950 border border-zinc-800 p-2.5 rounded-lg font-mono text-[11px] shadow-lg">
        <p className="text-zinc-400 font-semibold">{label}</p>
        <p className="text-emerald-400 mt-0.5">
          Events: <span className="font-bold text-zinc-100">{payload[0].value}</span>
        </p>
      </div>
    );
  }
  return null;
}

function AnalyticsCharts({ timeline, severity, sources, eventTypes, riskDistribution, selectedRange, onRangeChange }: AnalyticsChartsProps) {
  const chartTimeline = timeline?.map((p) => ({
    time: p.time.split(' ')[1] || p.time,
    count: p.count,
  })) || [];

  const chartSeverity = severity?.map((s) => ({ name: s.severity, value: s.count })) || [];

  const chartEventTypes = eventTypes?.map((e) => ({
    name: e.event_type.replace('_', ' ').replace(/\b\w/g, (c) => c),
    value: e.count,
  })) || [];

  const chartRisk = riskDistribution?.map((r) => ({
    name: r.label,
    value: r.count,
  })) || [];

  return (
    <div className="flex flex-col gap-4 px-6 pb-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* 1. Timeline */}
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-500" />
              <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Threat Volume Timeline</h3>
            </div>
            {onRangeChange && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-zinc-500 mr-1" />
                {['1h', '6h', '24h', '7d'].map((r) => (
                  <button
                    key={r}
                    onClick={() => onRangeChange(r)}
                    className={`px-2 py-0.5 rounded text-[9px] font-semibold uppercase tracking-wider transition-all cursor-pointer ${
                      selectedRange === r
                        ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                        : 'bg-zinc-900 border border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="flex-1 w-full text-slate-300">
            {chartTimeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartTimeline} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(63, 63, 70, 0.1)" vertical={false} />
                  <XAxis dataKey="time" stroke="#52525b" fontSize={9} tickLine={false} axisLine={false} />
                  <YAxis stroke="#52525b" fontSize={9} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip content={<ChartTooltip />} />
                  <Area type="monotone" dataKey="count" stroke="#10b981" strokeWidth={1.5} fillOpacity={1} fill="url(#colorCount)" dot={false} activeDot={{ r: 3, fill: '#10b981', stroke: '#09090b', strokeWidth: 1.5 }} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
                <div className="text-center"><Activity className="w-6 h-6 mx-auto mb-2 opacity-30" />Awaiting telemetry signals...</div>
              </div>
            )}
          </div>
        </div>

        {/* 2. Severity Pie */}
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
          <div className="flex items-center gap-2 mb-3">
            <Flame className="w-4 h-4 text-amber-500" />
            <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Incidents by Severity</h3>
          </div>
          <div className="flex-1 flex flex-col sm:flex-row items-center justify-center gap-4 text-slate-300">
            {chartSeverity.length > 0 ? (
              <>
                <div className="w-[130px] h-[130px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={chartSeverity} cx="50%" cy="50%" innerRadius={42} outerRadius={56} paddingAngle={3} dataKey="value" strokeWidth={0}>
                        {chartSeverity.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={SEV_COLORS[entry.name] || '#71717a'} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#09090b', border: '1px solid rgba(63, 63, 70, 0.4)', borderRadius: '8px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-col gap-1.5 font-mono text-xs flex-1 w-full justify-center">
                  {chartSeverity.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center border-b border-zinc-800/60 pb-1">
                      <span className="flex items-center gap-1.5 text-zinc-400 text-[11px] font-sans">
                        <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: SEV_COLORS[item.name] || '#71717a' }} />
                        {item.name}
                      </span>
                      <span className="font-semibold text-zinc-200 text-[11px]">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
                <div className="text-center"><Flame className="w-6 h-6 mx-auto mb-2 opacity-30" />No incident data received.</div>
              </div>
            )}
          </div>
        </div>

        {/* 3. Top Sources */}
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-blue-500" />
            <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Top Aggressors (Sources)</h3>
          </div>
          <div className="flex-1 overflow-y-auto pr-1">
            {sources && sources.length > 0 ? (
              <div className="flex flex-col gap-2 font-mono">
                {sources.slice(0, 5).map((src, index) => (
                  <div key={index} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2.5 flex flex-col gap-1 text-[11px] hover:border-blue-900/20 transition-colors">
                    <div className="flex justify-between items-center">
                      <span className="text-blue-400 font-semibold tracking-wider">{src.ip}</span>
                      <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[9px] px-1.5 py-0.5 rounded font-bold">{src.count} Alerts</span>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-zinc-500 font-sans">
                      <span>Type: {src.primary_attack}</span>
                      <span className="text-[9px] font-mono">Last seen: {src.last_seen?.split(' ')[1] || src.last_seen}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
                <div className="text-center"><Shield className="w-6 h-6 mx-auto mb-2 opacity-30" />No host reconnaissance detected.</div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* 4. Event Type Distribution Bar Chart */}
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
          <div className="flex items-center gap-2 mb-3">
            <BarChart3 className="w-4 h-4 text-cyan-500" />
            <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Event Type Distribution</h3>
          </div>
          <div className="flex-1 w-full">
            {chartEventTypes.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartEventTypes} margin={{ top: 5, right: 5, left: -20, bottom: 0 }} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(63, 63, 70, 0.1)" horizontal={false} />
                  <XAxis type="number" stroke="#52525b" fontSize={9} tickLine={false} axisLine={false} allowDecimals={false} />
                  <YAxis type="category" dataKey="name" stroke="#52525b" fontSize={8} tickLine={false} axisLine={false} width={100} />
                  <Tooltip contentStyle={{ backgroundColor: '#09090b', border: '1px solid rgba(63, 63, 70, 0.4)', borderRadius: '8px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {chartEventTypes.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={EVENT_COLORS[index % EVENT_COLORS.length]} fillOpacity={0.8} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
                <div className="text-center"><BarChart3 className="w-6 h-6 mx-auto mb-2 opacity-30" />No event type data.</div>
              </div>
            )}
          </div>
        </div>

        {/* 5. Risk Distribution */}
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex flex-col h-[260px]">
          <div className="flex items-center gap-2 mb-3">
            <Gauge className="w-4 h-4 text-violet-500" />
            <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Risk Distribution</h3>
          </div>
          <div className="flex-1 flex flex-col sm:flex-row items-center justify-center gap-4 text-slate-300">
            {chartRisk.length > 0 ? (
              <>
                <div className="w-[130px] h-[130px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={chartRisk} cx="50%" cy="50%" innerRadius={42} outerRadius={56} paddingAngle={3} dataKey="value" strokeWidth={0}>
                        {chartRisk.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || '#71717a'} />
                        ))}
                      </Pie>
                      <Tooltip contentStyle={{ backgroundColor: '#09090b', border: '1px solid rgba(63, 63, 70, 0.4)', borderRadius: '8px', fontSize: '11px', fontFamily: 'JetBrains Mono, monospace' }} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-col gap-1.5 font-mono text-xs flex-1 w-full justify-center">
                  {chartRisk.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center border-b border-zinc-800/60 pb-1">
                      <span className="flex items-center gap-1.5 text-zinc-400 text-[11px] font-sans">
                        <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: RISK_COLORS[item.name] || '#71717a' }} />
                        {item.name}
                      </span>
                      <span className="font-semibold text-zinc-200 text-[11px]">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
                <div className="text-center"><Gauge className="w-6 h-6 mx-auto mb-2 opacity-30" />No risk data available.</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(AnalyticsCharts);
