import React, { memo } from 'react';
import { AlertTriangle, ShieldAlert, Zap, Award } from 'lucide-react';
import { useCountUp } from '../hooks/useCountUp';
import type { StatsOverview } from '../types';

interface OverviewCardsProps {
  stats: StatsOverview | null;
}

function AnimatedNumber({ value, prefix = '' }: { value: number; prefix?: string }) {
  const animated = useCountUp(Math.round(value));
  return <>{prefix}{animated.toLocaleString()}</>;
}

function OverviewCards({ stats }: OverviewCardsProps) {
  const avgRisk = stats?.avg_risk_score ?? 0;
  const kpis = [
    {
      title: 'Total Alerts',
      value: stats?.total_alerts ?? 0,
      subtext: `Last hour: ${stats?.alerts_last_hour ?? 0}`,
      Icon: AlertTriangle,
      color: 'text-blue-500',
      indicatorColor: 'bg-blue-500',
    },
    {
      title: 'Active Threats',
      value: stats?.active_threats ?? 0,
      subtext: 'High/critical in last hour',
      Icon: ShieldAlert,
      color: 'text-rose-500',
      indicatorColor: 'bg-rose-500',
    },
    {
      title: 'Average Risk Score',
      value: avgRisk,
      subtext: avgRisk > 75 ? 'Status: Critical' : avgRisk > 50 ? 'Status: High' : avgRisk > 25 ? 'Status: Elevated' : 'Status: Normal',
      Icon: Zap,
      color: avgRisk > 75 ? 'text-rose-500' : avgRisk > 50 ? 'text-amber-500' : 'text-emerald-500',
      indicatorColor: avgRisk > 75 ? 'bg-rose-500' : avgRisk > 50 ? 'bg-amber-500' : 'bg-emerald-500',
      isDecimal: true,
    },
    {
      title: 'Severity Ratio',
      value: stats?.critical_count ?? 0,
      displayValue: `${stats?.critical_count ?? 0} / ${stats?.high_count ?? 0}`,
      subtext: 'Critical vs High severity',
      Icon: Award,
      color: 'text-violet-500',
      indicatorColor: 'bg-violet-500',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 px-6 py-4">
      {kpis.map((kpi, idx) => (
        <div
          key={idx}
          className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 hover:border-zinc-700 transition-all duration-200 flex items-center justify-between gap-4 overflow-hidden relative group"
        >
          <div className="flex flex-col">
            <span className="text-[11px] text-zinc-400 font-medium tracking-wide uppercase">
              {kpi.title}
            </span>
            <span className="text-3xl font-bold text-white mt-1 leading-none tracking-tight">
              {kpi.displayValue ? kpi.displayValue : <AnimatedNumber value={kpi.value} />}
            </span>
            <span className="text-xs text-zinc-400 mt-2 flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full ${kpi.indicatorColor} inline-block`} />
              {kpi.subtext}
            </span>
          </div>
          <div className={`p-2.5 rounded-lg border border-zinc-800 bg-zinc-950 text-zinc-400 ${kpi.color} group-hover:scale-110 transition-transform duration-200`}>
            <kpi.Icon className="w-5 h-5" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default memo(OverviewCards);
