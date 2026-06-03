import React from 'react';
import { AlertTriangle, ShieldAlert, Zap, Award } from 'lucide-react';

function OverviewCards({ stats }) {
  const kpis = [
    {
      title: 'Total Alerts',
      value: stats?.total_alerts ?? 0,
      subtext: `Last hour: ${stats?.alerts_last_hour ?? 0}`,
      icon: AlertTriangle,
      color: 'text-blue-500',
      borderColor: 'border-blue-500/10',
      bgColor: 'bg-blue-500/5',
      indicatorColor: 'bg-blue-500',
    },
    {
      title: 'Active Threats',
      value: stats?.active_threats ?? 0,
      subtext: 'High/critical in last hour',
      icon: ShieldAlert,
      color: 'text-rose-500',
      borderColor: 'border-rose-500/10',
      bgColor: 'bg-rose-500/5',
      indicatorColor: 'bg-rose-500',
    },
    {
      title: 'Average Risk Score',
      value: stats?.avg_risk_score ?? 0,
      subtext: stats?.avg_risk_score > 75 ? 'Status: Critical' : stats?.avg_risk_score > 50 ? 'Status: High' : stats?.avg_risk_score > 25 ? 'Status: Elevated' : 'Status: Normal',
      icon: Zap,
      color: stats?.avg_risk_score > 75 ? 'text-rose-500' : stats?.avg_risk_score > 50 ? 'text-amber-500' : 'text-emerald-500',
      borderColor: stats?.avg_risk_score > 50 ? 'border-amber-500/10' : 'border-emerald-500/10',
      bgColor: stats?.avg_risk_score > 50 ? 'bg-amber-500/5' : 'bg-emerald-500/5',
      indicatorColor: stats?.avg_risk_score > 75 ? 'bg-rose-500' : stats?.avg_risk_score > 50 ? 'bg-amber-500' : 'bg-emerald-500',
    },
    {
      title: 'Severity Ratio',
      value: `${stats?.critical_count ?? 0} / ${stats?.high_count ?? 0}`,
      subtext: 'Critical vs High severity',
      icon: Award,
      color: 'text-violet-500',
      borderColor: 'border-violet-500/10',
      bgColor: 'bg-violet-500/5',
      indicatorColor: 'bg-violet-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-6 py-4">
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 hover:border-zinc-700 transition-colors flex items-center justify-between gap-4 overflow-hidden relative"
        >
          {/* Left Contents */}
          <div className="flex flex-col">
            <span className="text-[11px] text-zinc-400 font-medium tracking-wide uppercase">
              {kpi.title}
            </span>
            <span className="text-3xl font-bold text-white mt-1 leading-none tracking-tight">
              {kpi.value}
            </span>
            <span className="text-xs text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${kpi.indicatorColor} inline-block`}></span>
              {kpi.subtext}
            </span>
          </div>

          {/* Right Icon Shield */}
          <div className={`p-2.5 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-400 ${kpi.color}`}>
            <kpi.icon className="w-5 h-5" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default OverviewCards;
