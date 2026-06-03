import React, { useState } from 'react';
import {
  ShieldAlert,
  Terminal,
  Activity,
  GitPullRequest,
  Clock,
  Play,
  RotateCw,
  X,
  AlertOctagon
} from 'lucide-react';

function AlertDetailSidebar({ alert, onRespond, responseLogs, isResponding, onClose }) {
  const [activeTab, setActiveTab] = useState('triage');

  // Helper to color code severity
  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'text-rose-400 border-rose-500/20 bg-rose-500/5';
      case 'HIGH':
        return 'text-amber-400 border-amber-500/20 bg-amber-500/5';
      case 'MEDIUM':
        return 'text-blue-400 border-blue-500/20 bg-blue-500/5';
      case 'LOW':
        return 'text-emerald-400 border-emerald-500/20 bg-emerald-500/5';
      default:
        return 'text-zinc-400 border-zinc-700 bg-zinc-800/10';
    }
  };

  const getRiskColor = (score) => {
    if (score > 75) return 'text-rose-400';
    if (score > 50) return 'text-amber-400';
    return 'text-emerald-400';
  };

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-full">
      {/* 1. Header Details Title */}
      <div className="flex items-center justify-between border-b border-zinc-800/80 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-500/80" />
          <h2 className="text-xs font-semibold tracking-wider text-zinc-100 uppercase">
            Incident Investigator
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <div className="font-mono text-[9px] text-zinc-500">
            ID: {alert ? alert.id?.substring(0, 15) + '...' : 'N/A'}
          </div>
          {alert && onClose && (
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-rose-400 transition-colors p-1 rounded-lg hover:bg-zinc-800 cursor-pointer"
              title="Close Panel"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {alert ? (
        <div className="flex-1 flex flex-col min-h-0">
          {/* 2. Top Summary Widget */}
          <div className="bg-zinc-900 border border-zinc-800/80 rounded-xl p-4 flex justify-between items-center gap-4 mb-3">
            <div>
              <div className="font-semibold text-zinc-100 text-xs tracking-wide uppercase">
                {alert.event_type}
              </div>
              <div className="text-[10px] text-zinc-400 font-mono mt-1">
                Target Asset: <span className="text-zinc-200 font-semibold">{alert.dest_ip} ({alert.asset_type})</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-[9px] text-zinc-500 font-mono">RISK SCORE</div>
              <div className={`text-2xl font-bold leading-none tracking-tight ${getRiskColor(alert.risk_score)}`}>
                {alert.risk_score}
              </div>
            </div>
          </div>

          {/* 3. Triage Tabs Navigation */}
          <div className="flex border-b border-zinc-800 mb-3 text-[11px]">
            <button
              onClick={() => setActiveTab('triage')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'triage' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Triage
            </button>
            <button
              onClick={() => setActiveTab('mitre')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'mitre' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              MITRE ATT&CK
            </button>
            <button
              onClick={() => setActiveTab('playbook')}
              className={`flex-1 py-2 text-center border-b-2 font-medium transition-colors cursor-pointer ${activeTab === 'playbook' ? 'border-emerald-500 text-zinc-200 font-semibold' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Playbook & Actions
            </button>
          </div>

          {/* 4. Tab Contents */}
          <div className="flex-1 overflow-y-auto min-h-0 font-mono text-[11px] pr-1">
            {activeTab === 'triage' && (
              <div className="flex flex-col gap-3">
                {/* AI Summary Card */}
                {alert.ai_summary && (
                  <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-1.5 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5" />
                      AI Analysis Summary
                    </div>
                    <p className="text-zinc-300 text-[11px] leading-relaxed font-sans font-normal">
                      {alert.ai_summary}
                    </p>
                  </div>
                )}

                {/* Score Breakdown telemetry */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 uppercase tracking-wide">
                    Risk Assessment Matrix
                  </div>
                  <div className="flex flex-col gap-1.5 text-[10px]">
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">CVSS Base Severity:</span>
                      <span className="text-zinc-200 font-semibold">{alert.cvss_base ?? 'N/A'} / 10</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">Anomaly Engine Score:</span>
                      <span className="text-zinc-200 font-semibold">{(alert.anomaly_score * 100)?.toFixed(1) ?? 'N/A'}%</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-1.5">
                      <span className="text-zinc-500">Asset Criticality Factor:</span>
                      <span className="text-zinc-200 font-semibold">{(alert.asset_criticality * 100)?.toFixed(0) ?? 'N/A'}%</span>
                    </div>
                    <div className="flex justify-between items-center pt-0.5">
                      <span className="text-zinc-500">Target IP Host:</span>
                      <span className="text-blue-400 font-semibold">{alert.dest_ip}</span>
                    </div>
                  </div>
                </div>

                {/* Raw security log logs */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-2.5 flex items-center gap-1">
                    <Terminal className="w-3 h-3 text-zinc-500" />
                    RAW SYSLOG TELEMETRY
                  </div>
                  <pre className="text-[10px] text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed bg-zinc-950/60 p-2 rounded-lg border border-zinc-800/80 max-h-[100px] overflow-y-auto">
                    {alert.raw_log}
                  </pre>
                </div>

                {/* Alert Metadata */}
                <div className="flex justify-between items-center text-[10px] text-zinc-500 px-1">
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Time: {alert.timestamp}</span>
                  </div>
                  <span>User: {alert.user || 'SYSTEM'}</span>
                </div>
              </div>
            )}

            {activeTab === 'mitre' && (
              <div className="flex flex-col gap-3">
                {/* MITRE technique main display */}
                <div className="bg-blue-950/15 border border-blue-900/30 rounded-xl p-4">
                  <div className="flex justify-between items-center border-b border-blue-900/20 pb-2 mb-3">
                    <span className="text-blue-400 font-semibold text-xs flex items-center gap-1.5">
                      <GitPullRequest className="w-3.5 h-3.5" />
                      MITRE ATT&CK Classification
                    </span>
                    <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 font-semibold text-[10px] px-2 py-0.5 rounded">
                      {alert.mitre?.technique_id || 'N/A'}
                    </span>
                  </div>
                  <div className="flex flex-col gap-3">
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Technique Name</div>
                      <div className="text-zinc-200 text-xs font-semibold mt-0.5">
                        {alert.mitre?.technique_name || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Attack Tactic</div>
                      <div className="text-amber-400 font-semibold text-xs mt-0.5">
                        {alert.mitre?.tactic || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-zinc-500 text-[10px] uppercase font-semibold">Tactic Description</div>
                      <p className="text-zinc-300 text-xs font-sans mt-1 leading-relaxed">
                        {alert.mitre?.description || 'No mapping description available.'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* MITRE Sub-techniques */}
                {alert.mitre?.sub_techniques && alert.mitre.sub_techniques.length > 0 && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-zinc-400 font-semibold mb-2 uppercase tracking-wide">
                      Targeted Sub-Techniques
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {alert.mitre.sub_techniques.map((sub, idx) => (
                        <div key={idx} className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2 text-[10px] text-zinc-300">
                          {sub}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* LLM ATT&CK Enrichment Description */}
                {alert.mitre?.llm_analysis && (
                  <div className="bg-purple-950/15 border border-purple-900/30 rounded-xl p-3">
                    <div className="text-[10px] text-purple-400 font-semibold mb-1 uppercase">
                      Tactical Analyst Enrichment
                    </div>
                    <p className="text-zinc-300 text-xs italic leading-relaxed font-sans">
                      {alert.mitre.llm_analysis}
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'playbook' && (
              <div className="flex flex-col gap-3">
                {/* Playbook recommendations */}
                {alert.playbook && (
                  <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                    <div className="flex justify-between items-center border-b border-zinc-800/50 pb-2 mb-2">
                      <span className="font-semibold text-zinc-200 text-xs uppercase">
                        {alert.playbook.name}
                      </span>
                      <span className="text-[9px] text-zinc-500 font-semibold">
                        EST. TIME: {alert.playbook.estimated_time}
                      </span>
                    </div>
                    <div className="flex flex-col gap-2 text-[11px] text-zinc-300 max-h-[140px] overflow-y-auto">
                      {alert.playbook.steps?.map((step, idx) => (
                        <div key={idx} className="leading-relaxed border-b border-zinc-800/40 pb-1.5">
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Automated response trigger buttons */}
                <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-xl p-3">
                  <div className="text-[10px] text-zinc-400 font-semibold mb-3 uppercase tracking-wide">
                    Orchestrated Response Actions
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => onRespond('block_ip')}
                      disabled={isResponding}
                      className="bg-rose-950/20 hover:bg-rose-900/30 border border-rose-900/30 hover:border-rose-700/80 text-rose-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        Firewall: Block Attacker IP
                      </span>
                      {isResponding === 'block_ip' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>

                    <button
                      onClick={() => onRespond('quarantine_host')}
                      disabled={isResponding}
                      className="bg-amber-950/20 hover:bg-amber-900/30 border border-amber-900/30 hover:border-amber-700/80 text-amber-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        EDR: Quarantine Host Segment
                      </span>
                      {isResponding === 'quarantine_host' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>

                    <button
                      onClick={() => onRespond('create_ticket')}
                      disabled={isResponding}
                      className="bg-blue-950/20 hover:bg-blue-900/30 border border-blue-900/30 hover:border-blue-700/80 text-blue-300 font-semibold py-2 px-3 rounded-lg flex items-center justify-between text-[11px] transition-colors disabled:opacity-40 cursor-pointer"
                    >
                      <span className="flex items-center gap-2">
                        <Play className="w-3.5 h-3.5" />
                        Jira: Dispatch Ticket (Tier-2)
                      </span>
                      {isResponding === 'create_ticket' && <RotateCw className="w-3.5 h-3.5 animate-spin" />}
                    </button>
                  </div>
                </div>

                {/* Monospace Action Console Output Logs */}
                {responseLogs[alert.id] && (
                  <div className="bg-zinc-950 border border-zinc-800/80 rounded-xl p-3">
                    <div className="text-[10px] text-emerald-400 font-semibold mb-2 flex items-center gap-1.5">
                      <Terminal className="w-3.5 h-3.5 text-emerald-400" />
                      Playbook Execution Log
                    </div>
                    <div className="font-mono text-[9px] leading-relaxed text-zinc-300 max-h-[120px] overflow-y-auto bg-zinc-950/40 p-2 rounded-lg border border-zinc-800/50">
                      <div className="text-emerald-400 font-semibold">
                        &gt; Status: {responseLogs[alert.id].success ? 'SUCCESSFUL' : 'FAILED'}
                      </div>
                      <div className="text-zinc-400 mt-1">&gt; Action: {responseLogs[alert.id].action}</div>
                      <div className="text-zinc-200 mt-1">&gt; Message: {responseLogs[alert.id].message}</div>
                      {responseLogs[alert.id].details && (
                        <div className="text-zinc-500 mt-1 whitespace-pre-wrap">
                          &gt; Details: {JSON.stringify(responseLogs[alert.id].details, null, 2)}
                        </div>
                      )}
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
            <p className="text-[10px] text-zinc-500 mt-1.5 uppercase tracking-wide">
              Click an alert row in the feed to investigate details
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default AlertDetailSidebar;
