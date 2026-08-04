import { useState, memo } from 'react';
import {
  ShieldAlert, Terminal, Activity, GitPullRequest, Clock, X,
  Radar, Zap, Target
} from 'lucide-react';

import type { AlertEvent } from '../types';

interface AlertDetailSidebarProps {
  alert: AlertEvent | null;
  onClose: () => void;
  onVerifyAlert: (alertId: string, status: string) => Promise<void>;
}

function AlertDetailSidebar({ alert, onClose, onVerifyAlert }: AlertDetailSidebarProps) {
  const [activeTab, setActiveTab] = useState<'triage' | 'mitre' | 'playbook' | 'intel'>('triage');
  const [isVerifying, setIsVerifying] = useState<string | null>(null);

  const getRiskColor = (score: number | null | undefined) => {
    if (score === null || score === undefined) return 'text-zinc-400';
    if (score > 75) return 'text-rose-400';
    if (score > 50) return 'text-amber-400';
    return 'text-emerald-400';
  };

  const getRiskBarColor = (score: number | null | undefined) => {
    if (score === null || score === undefined) return 'bg-zinc-500';
    if (score > 75) return 'bg-rose-500';
    if (score > 50) return 'bg-amber-500';
    return 'bg-emerald-500';
  };

  const tabs = [
    { id: 'triage' as const, label: 'Triage', icon: Target },
    { id: 'mitre' as const, label: 'MITRE', icon: GitPullRequest },
    { id: 'playbook' as const, label: 'Playbook', icon: Zap },
    { id: 'intel' as const, label: 'Intel', icon: Radar },
  ];

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full slide-in">
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-500/80" />
          <h2 className="text-xs font-semibold tracking-wider text-zinc-100 uppercase">Incident Investigator</h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="font-mono text-[9px] text-zinc-500">ID: {alert ? alert.id?.substring(0, 15) + '...' : 'N/A'}</div>
          {alert && onClose && (
            <button onClick={onClose} className="text-zinc-400 hover:text-rose-400 transition-colors p-1 rounded-lg hover:bg-zinc-800 cursor-pointer" title="Close Panel">
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {alert ? (
        <div className="flex-1 flex flex-col min-h-0">
          {/* Top Summary */}
          <div className="bg-zinc-900 border border-zinc-800/80 rounded-xl p-4 mb-3">
            <div className="flex justify-between items-center gap-4">
              <div>
                <div className="font-semibold text-zinc-100 text-xs tracking-wide uppercase">{alert.event_type}</div>
                <div className="text-[10px] text-zinc-400 font-mono mt-1">
                  Target Asset: <span className="text-zinc-600">{alert.dest_ip} ({alert.asset_type || 'unknown'})</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-zinc-500 font-mono">RISK SCORE</div>
                <div className={`text-2xl font-bold leading-none tracking-tight ${getRiskColor(alert.risk_score)}`}>{alert.risk_score ?? 0}</div>
              </div>
            </div>
            <div className="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-700 ${getRiskBarColor(alert.risk_score)}`} style={{ width: `${Math.min((alert.risk_score ?? 0), 100)}%` }} />
            </div>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-zinc-800 mb-3 text-[11px]">
            {tabs.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer flex items-center justify-center gap-1 ${
                  activeTab === id ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'
                }`}
                >
                  <Icon className="w-3 h-3" />
                  {label}
                </button>
              ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto min-h-0 font-mono text-[11px] pr-1">
            {activeTab === 'triage' && (
              <div className="flex flex-col gap-3">
                {alert.ai_summary && (
                  <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-1.5 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5" />
                      AI Analysis Summary
                    </div>
                    <p className="text-zinc-300 text-[11px] leading-relaxed font-sans font-normal">{alert.ai_summary}</p>
                  </div>
                )}

                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3 flex flex-col gap-2">
                  <div className="text-[10px] text-zinc-400 font-semibold uppercase tracking-wide">Incident Classification</div>
                  {alert.analyst_verification ? (
                    <div className={`text-center py-1.5 px-3 rounded-lg border text-[10px] font-semibold tracking-wide ${
                      alert.analyst_verification === 'TRUE_POSITIVE' ? 'bg-emerald-950/30 border-emerald-500/50 text-emerald-400' : 'bg-rose-950/30 border-rose-500/50 text-rose-400'
                    }`}>VERIFIED: {alert.analyst_verification.replace('_', ' ')}</div>
                  ) : (
                    <div className="flex gap-2">
                      <button
                        onClick={async () => { if (onVerifyAlert) { setIsVerifying('TRUE_POSITIVE'); await onVerifyAlert(alert.id, 'TRUE_POSITIVE'); setIsVerifying(null); } }}
                        disabled={isVerifying !== null}
                        className="flex-1 bg-emerald-950/20 hover:bg-emerald-900/30 border border-emerald-900/30 hover:border-emerald-700/80 text-emerald-300 font-semibold py-1.5 rounded-lg text-[10px] transition-colors disabled:opacity-40 cursor-pointer text-center"
                      >
                        {isVerifying === 'TRUE_POSITIVE' ? 'Saving...' : 'True Positive'}
                      </button>
                      <button
                        onClick={async () => { if (onVerifyAlert) { setIsVerifying('FALSE_POSITIVE'); await onVerifyAlert(alert.id, 'FALSE_POSITIVE'); setIsVerifying(null); } }}
                        disabled={isVerifying !== null}
                        className="flex-1 bg-rose-950/20 hover:bg-rose-900/30 border border-rose-900/30 hover:border-rose-700/80 text-rose-300 font-semibold py-1.5 rounded-lg text-[10px] transition-colors disabled:opacity-40 cursor-pointer text-center"
                      >
                        {isVerifying === 'FALSE_POSITIVE' ? 'Saving...' : 'False Positive'}
                      </button>
                    </div>
                  )}
                </div>

                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 uppercase tracking-wide">Risk Assessment Matrix</div>
                  <div className="flex flex-col gap-1.5 text-[10px]">
                    {[
                      { label: 'CVSS Base Severity:', value: `${alert.cvss_base ?? 'N/A'} / 10` },
                      { label: 'Anomaly Engine Score:', value: `${(alert.anomaly_score ?? 0) * 100}%.toFixed(1)` },
                      { label: 'Asset Criticality Factor:', value: `${(alert.asset_criticality ?? 0) * 100}%.toFixed(0)` },
                      { label: 'Target IP Host:', value: alert.dest_ip, color: 'text-blue-400' },
                    ].map(({ label, value, color }, idx) => (
                      <div key={idx} className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5 last:border-0">
                        <span className="text-zinc-500">{label}</span>
                        <span className={`${color || 'text-zinc-200'} font-semibold`}>{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 flex items-center gap-1">
                    <Terminal className="w-3 h-3 text-zinc-500" />
                    RAW SYSLOG TELEMETRY
                  </div>
                  <pre className="text-[10px] text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed bg-zinc-950/60 p-2 rounded-lg border border-zinc-800/80 max-h-[100px] overflow-y-auto">{alert.raw_log}</pre>
                </div>

                <div className="flex justify-between items-center text-[10px] text-zinc-500 px-1">
                  <div className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /><span>Time: {alert.timestamp}</span></div>
                  <span>User: {alert.user || 'SYSTEM'}</span>
                </div>
              </div>
            )}

            {activeTab === 'mitre' && (
              <div className="flex flex-col gap-3">
                <div className="bg-blue-950/15 border border-blue-900/30 rounded-xl p-4">
                  <div className="justify-between items-center border-b border-blue-900/20 pb-2 mb-3">
                    <span className="text-blue-400 font-semibold text-xs flex items-center gap-1.5">
                      <GitPullRequest className="w-3.5 h-3.5" />MITRE ATT&CK Classification
                    </span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'playbook' && (
              <div className="flex flex-col gap-3">
                <div className="bg-red-950/15 border border-red-900/30 rounded-xl p-4">
                  <div className="justify-between items-center border-b border-red-900/20 pb-2 mb-3">
                    <span className="text-red-400 font-semibold text-xs flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" />Playbook Actions
                    </span>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'intel' && (
              <div className="flex flex-col gap-3">
                <div className="bg-purple-950/15 border border-purple-900/30 rounded-xl p-4">
                  <div className="justify-between items-center border-b border-purple-900/20 pb-2 mb-3">
                    <span className="text-purple-400 font-semibold text-xs flex items-center gap-1.5">
                      <Radar className="w-3.5 h-3.5" />Threat Intelligence
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col h-full items-center justify-center">
          <div className="text-center py-8">
            <ShieldAlert className="w-8 h-8 text-amber-500" />
            <h2 className="text-xl font-bold text-zinc-100 mt-4">Select an alert to view details</h2>
            <p className="text-zinc-400 mt-2">Click on any alert in the table to see its detailed information.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default memo(AlertDetailSidebar);