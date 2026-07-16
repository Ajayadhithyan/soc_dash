import React, { useState, memo } from 'react';
import { Target, MapPin, Shield } from 'lucide-react';
import type { GeoData } from '../types';

interface ThreatHotspotsProps {
  geoData: GeoData[];
}

function ThreatHotspots({ geoData }: ThreatHotspotsProps) {
  const [hoveredSpot, setHoveredSpot] = useState<number | null>(null);
  const [mapScale, setMapScale] = useState(1);

  const hotspots = [...(geoData || [])].sort((a, b) => b.count - a.count).slice(0, 8);
  const maxCount = hotspots.length > 0 ? Math.max(...hotspots.map((h) => h.count)) : 1;

  const getX = (lng: number) => ((lng + 180) / 360) * 200;
  const getY = (lat: number) => ((90 - lat) / 180) * 100;

  const socLng = -97.0;
  const socLat = 38.0;
  const socX = getX(socLng);
  const socY = getY(socLat);

  const continentPaths = [
    'M 30,12 L 55,10 L 68,12 L 72,25 L 60,35 L 54,46 L 46,43 L 34,38 L 28,24 Z',
    'M 54,46 L 63,48 L 70,58 L 65,72 L 58,85 L 56,80 L 53,58 Z',
    'M 80,24 L 92,10 L 115,6 L 150,6 L 180,10 L 180,28 L 165,42 L 140,46 L 120,42 L 102,46 L 90,32 Z',
    'M 88,46 L 102,43 L 115,48 L 120,58 L 112,72 L 102,78 L 95,70 L 90,58 Z',
    'M 158,68 L 172,66 L 178,72 L 172,80 L 162,78 Z',
  ];

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-5 flex flex-col h-[320px] relative overflow-hidden">
      <div className="flex items-center gap-2 mb-4 z-10">
        <Target className="w-4 h-4 text-rose-500/95 animate-pulse" />
        <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">Tactical Threat Map & Hotspots</h3>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0 z-10">
        <div
          className="lg:col-span-7 bg-zinc-950/80 rounded-lg border border-zinc-800/60 p-2 relative flex items-center justify-center min-h-[150px] overflow-hidden transition-transform duration-300"
          style={{ transform: `scale(${mapScale})` }}
          onMouseEnter={() => setMapScale(1.02)}
          onMouseLeave={() => setMapScale(1)}
        >
          <div className="absolute inset-0 pointer-events-none opacity-[0.02] bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-zinc-200 via-zinc-900 to-black" />

          <svg viewBox="0 0 200 100" className="w-full h-full max-h-[170px] select-none">
            <defs>
              <pattern id="dotPattern" width="4" height="4" patternUnits="userSpaceOnUse">
                <circle cx="1" cy="1" r="0.4" fill="rgba(63, 63, 70, 0.2)" />
              </pattern>
              <linearGradient id="arcGlow" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f43f5e" stopOpacity="0" />
                <stop offset="50%" stopColor="#f43f5e" stopOpacity="1" />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
              </linearGradient>
            </defs>
            <rect width="200" height="100" fill="url(#dotPattern)" />

            {continentPaths.map((path, idx) => (
              <path key={idx} d={path} fill="rgba(24, 24, 27, 0.6)" stroke="rgba(82, 82, 91, 0.25)" strokeWidth="0.8" className="transition-all duration-300" />
            ))}

            {hotspots.map((spot, index) => {
              const x = getX(spot.lng);
              const y = getY(spot.lat);
              const midX = (x + socX) / 2;
              const midY = (y + socY) / 2 - 12;
              const pathD = `M ${x} ${y} Q ${midX} ${midY} ${socX} ${socY}`;
              const isHovered = hoveredSpot === index;
              return (
                <g key={`arc-${index}`}>
                  <path d={pathD} fill="none" stroke={isHovered ? 'rgba(244, 63, 94, 0.4)' : 'rgba(244, 63, 94, 0.15)'} strokeWidth={isHovered ? '1.5' : '0.8'} strokeDasharray="4, 4" className="transition-all" />
                  <path d={pathD} fill="none" stroke="url(#arcGlow)" strokeWidth="1.2" strokeDasharray="15, 80" style={{ animation: `dash 3s linear infinite`, animationDelay: `${index * 0.4}s` }} />
                </g>
              );
            })}

            {hotspots.map((spot, index) => {
              const x = getX(spot.lng);
              const y = getY(spot.lat);
              const isHovered = hoveredSpot === index;
              return (
                <g key={`marker-${index}`} onMouseEnter={() => setHoveredSpot(index)} onMouseLeave={() => setHoveredSpot(null)} className="cursor-pointer group">
                  <circle cx={x} cy={y} r="4" fill="none" stroke="#ef4444" strokeWidth="0.5" className="animate-ping" style={{ animationDuration: '2.5s' }} />
                  <circle cx={x} cy={y} r={isHovered ? '2.5' : '1.8'} fill="#ef4444" className="transition-all group-hover:fill-rose-400" />
                  {isHovered && (
                    <text x={x + 3} y={y - 3} fill="#e5e7eb" fontSize="3" fontFamily="Inter, sans-serif" className="pointer-events-none">
                      {spot.country} ({spot.count})
                    </text>
                  )}
                </g>
              );
            })}

            <g>
              <circle cx={socX} cy={socY} r="7" fill="none" stroke="#10b981" strokeWidth="0.4" className="animate-ping" style={{ animationDuration: '3s' }} />
              <circle cx={socX} cy={socY} r="2.2" fill="#10b981" />
              <circle cx={socX} cy={socY} r="3.8" fill="none" stroke="#10b981" strokeWidth="0.7" />
            </g>
          </svg>

          <style>{`@keyframes dash { to { stroke-dashoffset: -95; } }`}</style>
        </div>

        <div className="lg:col-span-5 overflow-y-auto pr-1 flex flex-col gap-1.5 font-mono text-[10px]">
          {hotspots.length > 0 ? (
            hotspots.map((spot, index) => {
              const ratio = Math.round((spot.count / maxCount) * 100);
              const isHovered = hoveredSpot === index;
              return (
                <div
                  key={index}
                  onMouseEnter={() => setHoveredSpot(index)}
                  onMouseLeave={() => setHoveredSpot(null)}
                  className={`border rounded-lg p-1.5 flex items-center justify-between gap-3 transition-all cursor-default ${
                    isHovered ? 'bg-rose-950/15 border-rose-800/40 scale-[1.02]' : 'bg-zinc-950/30 border-zinc-800/40 hover:border-zinc-800'
                  }`}
                >
                  <div className="flex items-center gap-1.5 min-w-0">
                    <MapPin className={`w-3 h-3 flex-shrink-0 ${isHovered ? 'text-rose-400' : 'text-zinc-500'}`} />
                    <span className="font-semibold text-zinc-300 uppercase truncate text-[9px] font-sans">{spot.country}</span>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <div className="w-12 bg-zinc-800 h-1 rounded-full overflow-hidden border border-zinc-700/20 hidden sm:block">
                      <div className="bg-rose-500/60 h-full rounded-full transition-all duration-500" style={{ width: `${ratio}%` }} />
                    </div>
                    <span className="bg-rose-500/10 border border-rose-500/15 text-rose-400 font-semibold px-1.5 py-0.5 rounded text-[8px]">{spot.count} IP</span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="flex-1 flex items-center justify-center text-zinc-500 font-sans text-xs">No geographical signals.</div>
          )}
        </div>
      </div>

      <div className="mt-2 border-t border-zinc-800/80 pt-2 flex justify-between items-center text-[9px] text-zinc-500 font-mono">
        <span className="flex items-center gap-1"><Shield className="w-3 h-3 text-emerald-500" />SOC CENTRAL NODE: USA HUB</span>
        <span className="text-rose-500 font-semibold uppercase animate-pulse-glow">TRACKING RADAR ACTIVE</span>
      </div>
    </div>
  );
}

export default memo(ThreatHotspots);
