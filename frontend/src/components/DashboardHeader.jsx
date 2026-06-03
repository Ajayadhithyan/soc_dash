import React, { useState, useEffect } from 'react';
import { Shield, Radio, Activity, RefreshCw, Cpu } from 'lucide-react';

function DashboardHeader({ wsStatus, systemHealth, onRefresh, onTrainModel }) {
  const [time, setTime] = useState(new Date());
  const [isTraining, setIsTraining] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleTrainClick = async () => {
    if (isTraining || !onTrainModel) return;
    setIsTraining(true);
    setFeedback(null);
    try {
      const res = await onTrainModel();
      if (res && res.success) {
        setFeedback('success');
        setTimeout(() => setFeedback(null), 3000);
      } else {
        setFeedback('error');
        setTimeout(() => setFeedback(null), 3000);
      }
    } catch (err) {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <header className="bg-zinc-950 border-b border-zinc-800 px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4 relative z-10">
      {/* Brand Logo & Title */}
      <div className="flex items-center gap-3">
        <div className="bg-zinc-900 border border-zinc-800 p-2 rounded-lg text-emerald-500">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-1.5">
            Aegis AI <span className="text-zinc-500 font-normal">|</span> <span className="text-zinc-400 font-normal">SOC Platform</span>
          </h1>
          <p className="text-[11px] text-zinc-500 font-medium">
            Real-time Threat Intelligence & Automated Response
          </p>
        </div>
      </div>

      {/* Health signals */}
      <div className="flex flex-wrap items-center gap-3 text-xs">
        {/* WebSocket Link Status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : wsStatus === 'connecting' ? 'bg-amber-500' : 'bg-rose-500'}`} />
          <span>Feed: <span className="text-zinc-200 capitalize font-medium">{wsStatus}</span></span>
        </div>

        {/* Database Status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          <span>API: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.status || 'offline'}</span></span>
        </div>

        {/* Anomaly model status */}
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.anomaly_detector === 'trained' ? 'bg-violet-500' : 'bg-zinc-600'}`} />
          <span>ML Model: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.anomaly_detector || 'untrained'}</span></span>
        </div>

        {/* Train Model button */}
        <button
          onClick={handleTrainClick}
          disabled={isTraining || systemHealth?.status !== 'online'}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs transition-all cursor-pointer font-medium ${
            isTraining
              ? 'bg-zinc-900 border-zinc-800 text-zinc-500 cursor-not-allowed'
              : feedback === 'success'
              ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
              : feedback === 'error'
              ? 'bg-rose-950/40 border-rose-500/50 text-rose-300'
              : 'bg-violet-950/30 hover:bg-violet-900/40 border-violet-800/50 hover:border-violet-700/60 text-violet-300 hover:text-violet-100 disabled:opacity-50 disabled:cursor-not-allowed'
          }`}
          title="Train Isolation Forest model on latest 500 security events"
        >
          <Cpu className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
          <span>
            {isTraining
              ? 'Training...'
              : feedback === 'success'
              ? 'Trained!'
              : feedback === 'error'
              ? 'Error!'
              : 'Train Model'}
          </span>
        </button>

        {/* Manual Refresh Trigger */}
        <button
          onClick={onRefresh}
          className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
          title="Force Sync Stats"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Digital clock HUD */}
      <div className="flex items-center gap-3 text-right">
        <div className="text-xs text-zinc-500">
          {formatDate(time)}
        </div>
        <div className="text-sm font-semibold text-zinc-300 font-mono">
          {formatTime(time)}
        </div>
      </div>
    </header>
  );
}

export default DashboardHeader;
