import React, { useState, useEffect, useCallback, memo } from 'react';
import { Target, AlertTriangle, Shield, BarChart3, ExternalLink, X } from 'lucide-react';
import { getMitreHeatmap } from '../utils/api';
import type { MitreHeatmapData, MitreTechniqueData } from '../types';

const SEV_COLORS: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f59e0b',
  MEDIUM: '#3b82f6',
  LOW: '#10b981',
};

const TACTIC_SHORT: Record<string, string> = {
  'Reconnaissance': 'RECON',
  'Resource Development': 'RES DEV',
  'Initial Access': 'INIT ACC',
  'Execution': 'EXEC',
  'Persistence': 'PERSIST',
  'Privilege Escalation': 'PRIV ESC',
  'Defense Evasion': 'DEF EVA',
  'Credential Access': 'CRED ACC',
  'Discovery': 'DISC',
  'Lateral Movement': 'LAT MOV',
  'Collection': 'COLLECT',
  'Command and Control': 'C2',
  'Exfiltration': 'EXFIL',
  'Impact': 'IMPACT',
};

function getHeatColor(count: number, maxCount: number): string {
  if (count === 0) return 'rgba(24, 24, 27, 0.3)';
  const ratio = count / maxCount;
  if (ratio > 0.75) return 'rgba(239, 68, 68, 0.85)';
  if (ratio > 0.5) return 'rgba(245, 158, 11, 0.7)';
  if (ratio > 0.25) return 'rgba(59, 130, 246, 0.55)';
  return 'rgba(16, 185, 129, 0.4)';
}

function getHeatBorder(count: number, maxCount: number): string {
  if (count === 0) return 'rgba(63, 63, 70, 0.15)';
  const ratio = count / maxCount;
  if (ratio > 0.75) return 'rgba(239, 68, 68, 0.5)';
  if (ratio > 0.5) return 'rgba(245, 158, 11, 0.4)';
  if (ratio > 0.25) return 'rgba(59, 130, 246, 0.3)';
  return 'rgba(16, 185, 129, 0.25)';
}

function MitreHeatmap() {
  const [data, setData] = useState<MitreHeatmapData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hoveredCell, setHoveredCell] = useState<{ tactic: string; technique: MitreTechniqueData } | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [selectedTactic, setSelectedTactic] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getMitreHeatmap();
      setData(result);
    } catch (err) {
      console.error('Error fetching MITRE heatmap:', err);
      setError('Failed to load MITRE ATT&CK heatmap data.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const buildMatrix = useCallback(() => {
    if (!data) return { matrix: {}, uniqueTechniques: [] };

    const matrix: Record<string, Record<string, MitreTechniqueData>> = {};
    const techniqueMap = new Map<string, MitreTechniqueData>();

    for (const t of data.techniques) {
      const primaryTactic = t.tactic.split(',')[0].trim();
      if (!matrix[primaryTactic]) matrix[primaryTactic] = {};
      matrix[primaryTactic][t.technique_id] = t;

      if (!techniqueMap.has(t.technique_id)) {
        techniqueMap.set(t.technique_id, t);
      } else {
        const existing = techniqueMap.get(t.technique_id)!;
        existing.count += t.count;
      }
    }

    const uniqueTechniques = Array.from(techniqueMap.values()).sort((a, b) => b.count - a.count);

    return { matrix, uniqueTechniques };
  }, [data]);

  if (loading) {
    return (
      <div className="flex-grow px-6 py-6 flex flex-col items-center justify-center gap-3">
        <Target className="w-8 h-8 text-emerald-500 animate-pulse" />
        <span className="text-zinc-500 text-xs font-mono">LOADING MITRE ATT&CK MATRIX...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-grow px-6 py-6 flex flex-col items-center justify-center gap-3 text-center">
        <AlertTriangle className="w-8 h-8 text-rose-500" />
        <span className="text-zinc-300 text-xs font-semibold">{error}</span>
        <button onClick={fetchData} className="mt-2 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs rounded border border-zinc-700 cursor-pointer">Retry</button>
      </div>
    );
  }

  if (!data) return null;

  const { matrix, uniqueTechniques } = buildMatrix();
  const activeTactics = data.tactics.filter(t => data.tactic_totals[t]);

  const handleMouseEnter = (e: React.MouseEvent, tactic: string, technique: MitreTechniqueData) => {
    setHoveredCell({ tactic, technique });
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseLeave = () => {
    setHoveredCell(null);
  };

  const filteredTactics = selectedTactic ? activeTactics.filter(t => t === selectedTactic) : activeTactics;
  const filteredTechniques = selectedTactic
    ? uniqueTechniques.filter(t => {
        const primaryTactic = t.tactic.split(',')[0].trim();
        return primaryTactic === selectedTactic;
      })
    : uniqueTechniques;

  return (
    <div className="flex-grow px-6 py-6 flex flex-col min-h-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <Target className="w-5 h-5 text-emerald-500" />
            MITRE ATT&CK Coverage Heatmap
          </h2>
          <p className="text-xs text-zinc-400">
            Matrix of detected adversary techniques mapped across the ATT&CK kill chain.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {selectedTactic && (
            <button onClick={() => setSelectedTactic(null)} className="flex items-center gap-1 px-2 py-1 text-[10px] text-zinc-400 hover:text-white border border-zinc-700 rounded bg-zinc-900/60 cursor-pointer transition-colors">
              <X className="w-3 h-3" />Clear Filter
            </button>
          )}
          <a href="https://attack.mitre.org/matrices/enterprise/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 px-2 py-1 text-[10px] text-emerald-400 hover:text-emerald-300 border border-emerald-900/30 rounded bg-emerald-950/20 transition-colors">
            <ExternalLink className="w-3 h-3" />MITRE Reference
          </a>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-3">
          <div className="text-[9px] text-zinc-500 font-semibold uppercase tracking-wide">Total Mapped Alerts</div>
          <div className="text-xl font-bold text-white mt-1">{data.total_mapped_alerts.toLocaleString()}</div>
        </div>
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-3">
          <div className="text-[9px] text-zinc-500 font-semibold uppercase tracking-wide">Unique Techniques</div>
          <div className="text-xl font-bold text-emerald-400 mt-1">{uniqueTechniques.length}</div>
        </div>
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-3">
          <div className="text-[9px] text-zinc-500 font-semibold uppercase tracking-wide">Active Tactics</div>
          <div className="text-xl font-bold text-amber-400 mt-1">{activeTactics.length}/{data.tactics.length}</div>
        </div>
        <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-3">
          <div className="text-[9px] text-zinc-500 font-semibold uppercase tracking-wide">Hottest Technique</div>
          <div className="text-sm font-bold text-rose-400 mt-1 truncate">{uniqueTechniques[0]?.technique_id || 'N/A'}</div>
          <div className="text-[9px] text-zinc-500 truncate">{uniqueTechniques[0]?.technique_name || ''}</div>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="bg-zinc-900/25 border border-zinc-800/80 rounded-xl overflow-hidden flex-1 flex flex-col min-h-0">
        <div className="flex-grow overflow-auto p-4">
          {filteredTechniques.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-zinc-500 gap-2">
              <Target className="w-8 h-8 opacity-30" />
              <span className="text-xs font-sans">No MITRE ATT&CK techniques detected in current alerts.</span>
            </div>
          ) : (
            <div className="min-w-[800px]">
              {/* Column Headers - Tactics */}
              <div className="flex mb-1">
                <div className="w-[200px] flex-shrink-0" />
                {filteredTactics.map(tactic => (
                  <div
                    key={tactic}
                    className={`flex-1 text-center px-1 py-2 cursor-pointer transition-all rounded-t-lg ${
                      selectedTactic === tactic ? 'bg-emerald-500/15 border-b-2 border-emerald-500' : 'hover:bg-zinc-800/30'
                    }`}
                    onClick={() => setSelectedTactic(selectedTactic === tactic ? null : tactic)}
                  >
                    <div className="text-[8px] font-bold text-zinc-400 uppercase tracking-wider leading-tight">
                      {TACTIC_SHORT[tactic] || tactic}
                    </div>
                    <div className="text-[7px] text-zinc-600 mt-0.5 hidden xl:block truncate">{tactic}</div>
                    <div className="text-[9px] font-bold text-zinc-300 mt-0.5">
                      {(data.tactic_totals[tactic] || 0).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>

              {/* Matrix Rows */}
              <div className="flex flex-col gap-[2px]">
                {filteredTechniques.map(tech => {
                  const primaryTactic = tech.tactic.split(',')[0].trim();
                  return (
                    <div key={tech.technique_id} className="flex items-center group">
                      {/* Technique Label */}
                      <div className="w-[200px] flex-shrink-0 pr-3 py-1.5">
                        <div className="flex items-center gap-1.5">
                          <span className="text-[10px] font-bold font-mono text-emerald-400">{tech.technique_id}</span>
                          <span className="text-[10px] text-zinc-300 truncate font-sans">{tech.technique_name}</span>
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[8px] text-zinc-500">{tech.count.toLocaleString()} alerts</span>
                          <div className="flex gap-0.5">
                            {Object.entries(tech.severity_breakdown).map(([sev, count]) => (
                              <span
                                key={sev}
                                className="inline-block w-1.5 h-1.5 rounded-full"
                                style={{ backgroundColor: SEV_COLORS[sev] || '#71717a' }}
                                title={`${sev}: ${count}`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Cells per tactic */}
                      {filteredTactics.map(tactic => {
                        const cellTech = matrix[tactic]?.[tech.technique_id];
                        const count = cellTech?.count || 0;
                        const isActive = count > 0;
                        return (
                          <div
                            key={`${tech.technique_id}-${tactic}`}
                            className="flex-1 px-[2px]"
                          >
                            <div
                              className={`h-10 rounded-md border transition-all duration-150 flex items-center justify-center ${
                                isActive ? 'cursor-pointer hover:scale-110 hover:z-10 hover:shadow-lg' : ''
                              }`}
                              style={{
                                backgroundColor: getHeatColor(count, data.max_count),
                                borderColor: getHeatBorder(count, data.max_count),
                              }}
                              onMouseEnter={(e) => isActive && cellTech && handleMouseEnter(e, tactic, cellTech)}
                              onMouseMove={handleMouseMove}
                              onMouseLeave={handleMouseLeave}
                            >
                              {isActive && (
                                <span className={`text-[9px] font-bold font-mono ${count / data.max_count > 0.5 ? 'text-white' : 'text-zinc-300'}`}>
                                  {count}
                                </span>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer: Legend + Totals */}
        <div className="border-t border-zinc-800/80 px-4 py-3 flex flex-wrap items-center justify-between gap-3 text-[9px]">
          <div className="flex items-center gap-4">
            <span className="text-zinc-500 font-semibold uppercase">Heat Scale:</span>
            <div className="flex items-center gap-1.5">
              <span className="text-zinc-500">None</span>
              <div className="w-5 h-3 rounded" style={{ backgroundColor: 'rgba(24, 24, 27, 0.3)', border: '1px solid rgba(63, 63, 70, 0.15)' }} />
              <div className="w-5 h-3 rounded" style={{ backgroundColor: 'rgba(16, 185, 129, 0.4)', border: '1px solid rgba(16, 185, 129, 0.25)' }} />
              <div className="w-5 h-3 rounded" style={{ backgroundColor: 'rgba(59, 130, 246, 0.55)', border: '1px solid rgba(59, 130, 246, 0.3)' }} />
              <div className="w-5 h-3 rounded" style={{ backgroundColor: 'rgba(245, 158, 11, 0.7)', border: '1px solid rgba(245, 158, 11, 0.4)' }} />
              <div className="w-5 h-3 rounded" style={{ backgroundColor: 'rgba(239, 68, 68, 0.85)', border: '1px solid rgba(239, 68, 68, 0.5)' }} />
              <span className="text-zinc-500">Critical</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="text-zinc-500">Severity:</span>
              {Object.entries(SEV_COLORS).map(([sev, color]) => (
                <span key={sev} className="flex items-center gap-1">
                  <span className="inline-block w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                  <span className="text-zinc-400">{sev}</span>
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top Techniques Table */}
      <div className="mt-6 bg-zinc-900/25 border border-zinc-800/80 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-zinc-800/80 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-emerald-500" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Top Techniques by Volume</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left font-sans text-xs">
            <thead>
              <tr className="border-b border-zinc-800/60 text-zinc-500 uppercase font-mono text-[9px] tracking-wider">
                <th className="py-2.5 px-4 font-semibold">Rank</th>
                <th className="py-2.5 px-4 font-semibold">Technique</th>
                <th className="py-2.5 px-4 font-semibold">Name</th>
                <th className="py-2.5 px-4 font-semibold">Tactic</th>
                <th className="py-2.5 px-4 font-semibold text-right">Alerts</th>
                <th className="py-2.5 px-4 font-semibold">Severity Breakdown</th>
                <th className="py-2.5 px-4 font-semibold">Coverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/40">
              {uniqueTechniques.slice(0, 10).map((tech, idx) => {
                const coverage = data.total_mapped_alerts > 0 ? ((tech.count / data.total_mapped_alerts) * 100).toFixed(1) : '0';
                return (
                  <tr key={tech.technique_id} className="hover:bg-zinc-800/20 transition-colors">
                    <td className="py-2 px-4 text-zinc-500 font-mono">#{idx + 1}</td>
                    <td className="py-2 px-4">
                      <span className="font-mono font-bold text-emerald-400">{tech.technique_id}</span>
                    </td>
                    <td className="py-2 px-4 text-zinc-200 font-semibold">{tech.technique_name}</td>
                    <td className="py-2 px-4 text-zinc-400">{tech.tactic.split(',')[0].trim()}</td>
                    <td className="py-2 px-4 text-right font-mono font-bold text-white">{tech.count.toLocaleString()}</td>
                    <td className="py-2 px-4">
                      <div className="flex gap-1">
                        {Object.entries(tech.severity_breakdown).map(([sev, count]) => (
                          <span key={sev} className="flex items-center gap-0.5">
                            <span className="inline-block w-1.5 h-1.5 rounded-full" style={{ backgroundColor: SEV_COLORS[sev] || '#71717a' }} />
                            <span className="text-[9px] text-zinc-400">{count}</span>
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-2 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full bg-emerald-500 transition-all duration-500"
                            style={{ width: `${coverage}%` }}
                          />
                        </div>
                        <span className="text-[9px] text-zinc-500 font-mono">{coverage}%</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Floating Tooltip */}
      {hoveredCell && (
        <div
          className="fixed z-50 pointer-events-none bg-zinc-950 border border-zinc-700 rounded-xl p-3 shadow-2xl max-w-[280px]"
          style={{
            left: tooltipPos.x + 16,
            top: tooltipPos.y - 10,
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-emerald-500" />
              <span className="text-[10px] font-bold font-mono text-emerald-400">{hoveredCell.technique.technique_id}</span>
            </div>
            <span className="text-[9px] font-bold text-white bg-zinc-800 px-1.5 py-0.5 rounded">{hoveredCell.technique.count}</span>
          </div>
          <div className="text-[11px] font-semibold text-zinc-100 mb-1">{hoveredCell.technique.technique_name}</div>
          <div className="text-[9px] text-zinc-400 mb-2">Tactic: <span className="text-zinc-200">{hoveredCell.tactic}</span></div>
          <div className="flex gap-1.5">
            {Object.entries(hoveredCell.technique.severity_breakdown).map(([sev, count]) => (
              <span key={sev} className="flex items-center gap-1 bg-zinc-900/60 border border-zinc-800 rounded px-1.5 py-0.5">
                <span className="inline-block w-1.5 h-1.5 rounded-full" style={{ backgroundColor: SEV_COLORS[sev] || '#71717a' }} />
                <span className="text-[8px] text-zinc-300 font-mono">{sev}: {count}</span>
              </span>
            ))}
          </div>
          <div className="mt-2 pt-2 border-t border-zinc-800/60 text-[8px] text-zinc-500">
            Click tactic column header to filter
          </div>
        </div>
      )}
    </div>
  );
}

export default memo(MitreHeatmap);
