import React, { useState, memo } from 'react';
import {
  ShieldAlert, Terminal, Activity, GitPullRequest, Clock, Play, RotateCw, X,
  AlertOctagon, Radar, Fingerprint, Bell, ArrowUpRight, Zap, FileSearch, Target, Brain
} from 'lucide-react';

import type { AlertEvent } from '../types';

interface AlertDetailSidebarProps {
  alert: AlertEvent | null;
  onRespond: (action: string) => void;
  responseLogs: Record<string, unknown>;
  isResponding: string | null;
  onClose: () => void;
  onVerifyAlert: (alertId: string, status: string) => Promise<void>;
}

function AlertDetailSidebar({ alert, onRespond, responseLogs, isResponding, onClose, onVerifyAlert }: AlertDetailSidebarProps) {
  const [activeTab, setActiveTab] = useState<'triage' | 'mitre' | 'playbook' | 'intel'>('triage');
  const [isVerifying, setIsVerifying] = useState<string | null>(null);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL': return 'text-rose-400 border-rose-500/20 bg-rose-500/5';
      case 'HIGH': return 'text-amber-400 border-amber-500/20 bg-amber-500/5';
      case 'MEDIUM': return 'text-blue-400 border-blue-500/20 bg-blue-500/5';
      case 'LOW': return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
      default: return 'text-zinc-400 border-zinc-700 bg-zinc-800/10';
    }
  };

  const getRiskColor = (score: number) => {
    if (score > 75) return 'text-rose-400';
    if (score > 50) return 'text-amber-400';
    return 'text-emerald-400';
  };

  const getRiskBarColor = (score: number) => {
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
                  Target Asset: <span className="text-zinc-200 font-semibold">{alert.dest_ip} ({alert.asset_type})</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[9px] text-zinc-500 font-mono">RISK SCORE</div>
                <div className={`text-2xl font-bold leading-none tracking-tight ${getRiskColor(alert.risk_score)}`}>{alert.risk_score}</div>
              </div>
            </div>
            <div className="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-700 ${getRiskBarColor(alert.risk_score)}`} style={{ width: `${Math.min(alert.risk_score, 100)}%` }} />
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
                      >{isVerifying === 'TRUE_POSITIVE' ? 'Saving...' : 'True Positive'}</button>
                      <button
                        onClick={async () => { if (onVerifyAlert) { setIsVerifying('FALSE_POSITIVE'); await onVerifyAlert(alert.id, 'FALSE_POSITIVE'); setIsVerifying(null); } }}
                        disabled={isVerifying !== null}
                        className="flex-1 bg-rose-950/20 hover:bg-rose-900/30 border border-rose-900/30 hover:border-rose-700/80 text-rose-300 font-semibold py-1.5 rounded-lg text-[10px] transition-colors disabled:opacity-40 cursor-pointer text-center"
                      >{isVerifying === 'FALSE_POSITIVE' ? 'Saving...' : 'False Positive'}</button>
                    </div>
                  )}
                </div>

                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 uppercase tracking-wide">Risk Assessment Matrix</div>
                  <div className="flex flex-col gap-1.5 text-[10px]">
                    {[
                      { label: 'CVSS Base Severity:', value: `${alert.cvss_base ?? 'N/A'} / 10` },
                      { label: 'Anomaly Engine Score:', value: `${(alert.anomaly_score * 100)?.toFixed(1) ?? 'N/A'}%` },
                      { label: 'Asset Criticality Factor:', value: `${(alert.asset_criticality * 100)?.toFixed(0) ?? 'N/A'}%` },
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
                  <div className="flex justify-between items-center border-b border-blue-900/20 pb-2 mb-3">
                    <span className="text-blue-400 font-semibold text-xs flex items-center gap-1.5">
                      <GitPullRequest className="w-3.5 h-3.5" />MITRE ATT&CK Classification
                    </span>
                    <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold text-[10px] px-2 py-0.5 rounded">{alert.mitre?.technique_id || 'N/A'}</span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Technique Name</div>
                      <div className="text-zinc-200 text-xs font-semibold mt-0.5">{alert.mitre?.technique_name || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Attack Tactic</div>
                      <div className="text-amber-400 font-semibold text-xs mt-0.5">{alert.mitre?.tactic || 'N/A'}</div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Tactic Description</div>
                      <p className="text-zinc-300 text-xs font-sans mt-1 leading-relaxed">{alert.mitre?.description || 'No mapping description available.'}</p>
                    </div>
                  </div>
                </div>

                {alert.mitre?.sub_techniques && alert.mitre.sub_techniques.length > 0 && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-zinc-400 font-semibold mb-2 uppercase tracking-wide">Targeted Sub-Techniques</div>
                    <div className="flex flex-col gap-1.5">
                      {alert.mitre.sub_techniques.map((sub, idx) => (
                        <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2 text-[10px] text-zinc-300">{sub}</div>
                      ))}
                    </div>
                  </div>
                )}

                {alert.mitre?.llm_analysis && (
                  <div className="bg-purple-950/15 border border-purple-900/30 rounded-xl p-3">
                    <div className="text-[10px] text-purple-400 font-semibold mb-1 uppercase flex items-center gap-1.5">
                      <Brain className="w-3 h-3" />Tactical Analyst Enrichment
                    </div>
                    <p className="text-zinc-300 text-xs italic leading-relaxed font-sans">{alert.mitre.llm_analysis}</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'playbook' && (
              <div className="flex flex-col gap-3">
                {alert.playbook && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-2 mb-2">
                      <span className="font-semibold text-zinc-200 text-xs uppercase">{alert.playbook.name}</span>
                      <span className="text-[9px] text-zinc-500 font-semibold">EST. TIME: {alert.playbook.estimated_time}</span>
                    </div>
                    <div className="flex flex-col gap-2 text-[11px] text-zinc-300 max-h-[140px] overflow-y-auto">
                      {alert.playbook.steps?.map((step, idx) => (
                        <div key={idx} className="leading-relaxed border-b border-zinc-800/40 pb-1.5">{step}</div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Auto Playbook Actions */}
                {alert.auto_playbook_actions && alert.auto_playbook_actions.length > 0 && (
                  <div className="bg-emerald-950/15 border border-emerald-900/30 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-2 uppercase tracking-wide flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" />Auto-Triggered Playbook Actions
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {alert.auto_playbook_actions.map((action, idx) => (
                        <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2 text-[10px] flex justify-between items-center">
                          <span className="text-emerald-300 font-semibold">{action.action}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${
                            action.status === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                            action.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                            'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          }`}>{action.status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-3 uppercase tracking-wide">Orchestrated Response Actions</div>
                  <div className="flex flex-col gap-2">
                    {[
                      { action: 'block_ip', icon: Play, label: 'Firewall: Block Attacker IP', color: 'rose' },
                      { action: 'quarantine_host', icon: Play, label: 'EDR: Quarantine Host Segment', color: 'amber' },
                      { action: 'create_ticket', icon: Play, label: 'Jira: Dispatch Ticket (Tier-2)', color: 'blue' },
                      { action: 'escalate_to_siem', icon: ArrowUpRight, label: 'SIEM: Escalate to Splunk/Sentinel', color: 'violet' },
                      { action: 'notify_slack', icon: Bell, label: 'Slack: Notify #soc-critical-alerts', color: 'emerald' },
                    ].map(({ action, icon: BtnIcon, label, color }) => (
                      <button
                        key={action}
                        onClick={() => onRespond(action)}
                        disabled={isResponding !== null}
                        className={`bg-${color}-950/20 hover:bg-${color}-900/30 border border-${color}-900/30 hover:border-${color}-700/80 text-${color}-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer`}
                      >
                        <span className="flex items-center gap-2"><BtnIcon className="w-3.5 h-3.5" />{label}</span>
                        {isResponding === action && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                      </button>
                    ))}
                  </div>
                </div>

                {responseLogs[alert.id] && (
                  <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-2 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-emerald-400" />Playbook Execution Log
                    </div>
                    <div className="font-mono text-[9px] leading-relaxed text-zinc-300 max-h-[120px] overflow-y-auto bg-zinc-950/40 p-2 rounded-lg border border-zinc-800/50">
                      <div className="text-emerald-400 font-semibold">&gt; Status: {(responseLogs[alert.id] as { success?: boolean })?.success ? 'SUCCESSFUL' : 'FAILED'}</div>
                      <div className="text-zinc-400 mt-1">&gt; Action: {(responseLogs[alert.id] as { action?: string })?.action}</div>
                      <div className="text-zinc-200 mt-1">&gt; Message: {(responseLogs[alert.id] as { message?: string })?.message}</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'intel' && (
              <div className="flex flex-col gap-3">
                {/* Threat Intel */}
                <div className="bg-rose-950/15 border border-rose-900/30 rounded-xl p-3">
                  <div className="text-[10px] text-rose-400 font-semibold mb-2 flex items-center gap-1.5 uppercase tracking-wide">
                    <Radar className="w-3.5 h-3.5" />Threat Intelligence
                  </div>
                  {alert.threat_intel ? (
                    <div className="flex flex-col gap-1.5 text-[10px]">
                      {[
                        { label: 'Known Malicious:', value: alert.threat_intel.is_known_malicious ? '⚠ YES' : '✓ CLEAN', color: alert.threat_intel.is_known_malicious ? 'text-rose-400' : 'text-emerald-400' },
                        alert.threat_intel.blocklist_source && { label: 'Blocklist Source:', value: alert.threat_intel.blocklist_source, color: 'text-rose-300' },
                        alert.threat_intel.threat_category && { label: 'Category:', value: alert.threat_intel.threat_category.toUpperCase(), color: 'text-zinc-200' },
                        { label: 'Analyst Blocked:', value: alert.threat_intel.analyst_blocked ? 'YES' : 'NO', color: alert.threat_intel.analyst_blocked ? 'text-amber-400' : 'text-zinc-400' },
                      ].filter(Boolean).map(({ label, value, color }, idx) => (
                        <div key={idx} className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5 last:border-0">
                          <span className="text-zinc-500">{label}</span>
                          <span className={`${color} font-semibold`}>{value}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-zinc-500 text-[10px] italic">No threat intel data available.</div>
                  )}
                </div>

                {/* SIGMA */}
                <div className="bg-amber-950/10 border border-amber-900/30 rounded-xl p-3">
                  <div className="text-[10px] text-amber-400 font-semibold mb-2 flex items-center gap-1.5 uppercase tracking-wide">
                    <Fingerprint className="w-3.5 h-3.5" />SIGMA Rule Matches
                  </div>
                  {alert.sigma_matches && alert.sigma_matches.length > 0 ? (
                    <div className="flex flex-col gap-1.5">
                      {alert.sigma_matches.map((match, idx) => (
                        <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2 text-[10px]">
                          <div className="flex justify-between items-center">
                            <span className="text-amber-300 font-semibold">{match.rule_name}</span>
                            <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold uppercase ${
                              match.severity === 'CRITICAL' ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400' :
                              match.severity === 'HIGH' ? 'bg-amber-500/10 border border-amber-500/20 text-amber-400' :
                              'bg-blue-500/10 border border-blue-500/20 text-blue-400'
                            }`}>{match.severity}</span>
                          </div>
                          <div className="text-zinc-400 mt-1 text-[9px] leading-relaxed">{match.description}</div>
                          {match.tags && match.tags.length > 0 && (
                            <div className="flex gap-1 mt-1.5 flex-wrap">
                              {match.tags.map((tag, tidx) => (
                                <span key={tidx} className="bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded text-[8px]">{tag}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-zinc-500 text-[10px] italic">No SIGMA rules triggered.</div>
                  )}
                </div>

                {/* Correlation */}
                {alert.correlation && alert.correlation.is_correlated && (
                  <div className="bg-violet-950/15 border border-violet-900/30 rounded-xl p-3">
                    <div className="text-[10px] text-violet-400 font-semibold mb-2 flex items-center gap-1.5 uppercase tracking-wide">
                      <FileSearch className="w-3.5 h-3.5" />Attack Campaign Correlation
                    </div>
                    <div className="flex flex-col gap-1.5 text-[10px]">
                      {[
                        { label: 'Campaign ID:', value: alert.correlation.campaign_id, color: 'text-violet-300' },
                        { label: 'Primary Pattern:', value: alert.correlation.primary_pattern, color: 'text-zinc-200' },
                        { label: 'Risk Boost:', value: `+${alert.correlation.total_risk_boost}`, color: 'text-rose-400' },
                        { label: 'Related Alerts:', value: alert.correlation.related_alert_count, color: 'text-zinc-200' },
                      ].map(({ label, value, color }, idx) => (
                        <div key={idx} className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5 last:border-0">
                          <span className="text-zinc-500">{label}</span>
                          <span className={`${color} font-semibold`}>{value}</span>
                        </div>
                      ))}
                    </div>
                    {alert.correlation.patterns && alert.correlation.patterns.length > 1 && (
                      <div className="mt-2 pt-2 border-t border-zinc-800/50">
                        <div className="text-[9px] text-zinc-500 font-semibold uppercase mb-1">All Patterns</div>
                        {alert.correlation.patterns.map((p, pidx) => (
                          <div key={pidx} className="text-[9px] text-zinc-400 py-0.5">• {p.pattern_name}</div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Feedback Confidence */}
                {alert.feedback && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 uppercase tracking-wide">ML Feedback Confidence</div>
                    <div className="flex items-center gap-3">
                      <div className="flex-1">
                        <div className="w-full bg-zinc-800 h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              alert.feedback.feedback_confidence > 0.7 ? 'bg-emerald-500' :
                              alert.feedback.feedback_confidence > 0.4 ? 'bg-amber-500' : 'bg-rose-500'
                            }`}
                            style={{ width: `${(alert.feedback.feedback_confidence * 100).toFixed(0)}%` }}
                          />
                        </div>
                      </div>
                      <span className={`text-xs font-bold ${
                        alert.feedback.feedback_confidence > 0.7 ? 'text-emerald-400' :
                        alert.feedback.feedback_confidence > 0.4 ? 'text-amber-400' : 'text-rose-400'
                      }`}>{(alert.feedback.feedback_confidence * 100).toFixed(0)}%</span>
                    </div>
                    <div className="flex justify-between items-center mt-2 text-[9px]">
                      <span className="text-zinc-500">True Positive Probability</span>
                      {alert.feedback.suppress_recommendation && <span className="text-amber-400 font-semibold">⚠ Suppress Recommended</span>}
                      {!alert.feedback.classifier_trained && <span className="text-zinc-600 italic">Classifier untrained</span>}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex-grow flex flex-col justify-center items-center gap-3 text-zinc-500 font-sans text-xs text-center p-6 border border-dashed border-zinc-800 rounded-xl">
          <AlertOctagon className="w-7 h-7 text-zinc-600 animate-pulse" />
          <div>
            No alert selected for triage
            <p className="text-[10px] text-zinc-500 mt-1.5 uppercase tracking-wide">Click an alert row in the feed to investigate details</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default memo(AlertDetailSidebar);
