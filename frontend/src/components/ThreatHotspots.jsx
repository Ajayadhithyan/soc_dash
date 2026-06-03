import React from 'react';
import { Globe, MapPin, Target } from 'lucide-react';

function ThreatHotspots({ geoData }) {
  // Sort hotspots by count descending
  const hotspots = [...(geoData || [])].sort((a, b) => b.count - a.count).slice(0, 8);
  const maxCount = hotspots.length > 0 ? Math.max(...hotspots.map(h => h.count)) : 1;

  return (
    <div className="bg-zinc-900/40 rounded-xl border border-zinc-800 p-4 flex-1 min-h-[300px] flex flex-col relative overflow-hidden">
      <div className="flex items-center gap-2 mb-3 z-10">
        <Target className="w-4 h-4 text-rose-500/80" />
        <h3 className="text-xs font-semibold tracking-wider text-zinc-200 uppercase">
          Threat Hotspots (Origins)
        </h3>
      </div>

      {/* Main List */}
      <div className="flex-1 overflow-y-auto pr-1 z-10 font-mono text-[11px]">
        {hotspots.length > 0 ? (
          <div className="flex flex-col gap-2">
            {hotspots.map((spot, index) => {
              const ratio = Math.round((spot.count / maxCount) * 100);
              return (
                <div
                  key={index}
                  className="bg-zinc-950/40 border border-zinc-800/60 rounded-lg p-2.5 flex items-center justify-between gap-4 hover:border-rose-900/40 transition-colors"
                >
                  {/* Country Name + Coordinates */}
                  <div className="flex items-start gap-2.5">
                    <div className="bg-rose-500/10 text-rose-400 p-1.5 rounded-md border border-rose-500/20">
                      <MapPin className="w-3.5 h-3.5" />
                    </div>
                    <div className="flex flex-col gap-0.5 font-sans">
                      <span className="font-semibold text-zinc-200 text-xs uppercase">
                        {spot.country}
                      </span>
                      <span className="text-[9px] text-zinc-500 font-mono">
                        Lat: {spot.lat?.toFixed(2)} / Lng: {spot.lng?.toFixed(2)}
                      </span>
                    </div>
                  </div>

                  {/* Visual ratio bar + Count */}
                  <div className="flex items-center gap-3 w-40 justify-end">
                    <div className="hidden sm:flex flex-col items-end w-20">
                      <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden border border-zinc-700/30">
                        <div
                          className="bg-rose-500/60 h-full rounded-full"
                          style={{ width: `${ratio}%` }}
                        ></div>
                      </div>
                    </div>
                    <span className="bg-rose-500/10 border border-rose-500/20 text-rose-400 font-semibold px-2 py-0.5 rounded text-[10px] font-mono">
                      {spot.count} IP
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-zinc-500 font-sans text-xs">
            No geographic signal detected.
          </div>
        )}
      </div>

      {/* Footer GPS system metadata */}
      <div className="mt-2 border-t border-zinc-800/80 pt-2 flex justify-between items-center text-[9px] text-zinc-500 font-mono z-10">
        <span>LOCATOR SIGNAL: ACTIVE</span>
        <span className="text-emerald-500 font-semibold">● ONLINE</span>
      </div>
    </div>
  );
}

export default ThreatHotspots;
