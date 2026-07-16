import React, { useState, useEffect, useCallback } from 'react';
import { Shield, RefreshCw, Cpu, Sun, Moon, Menu, X, LogOut } from 'lucide-react';
import type { SystemHealth } from '../types';

interface DashboardHeaderProps {
  wsStatus: string;
  systemHealth: SystemHealth | null;
  onRefresh: () => void;
  onTrainModel: () => Promise<{ success: boolean; message?: string }>;
  onLogout?: () => void;
}

function DashboardHeader({ wsStatus, systemHealth, onRefresh, onTrainModel, onLogout }: DashboardHeaderProps) {
  const [time, setTime] = useState(new Date());
  const [isTraining, setIsTraining] = useState(false);
  const [feedback, setFeedback] = useState<'success' | 'error' | null>(null);
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('soc-theme');
    return saved ? saved === 'dark' : true;
  });
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('light-theme', !isDark);
  }, [isDark]);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', { hour12: false });
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };

  const toggleTheme = useCallback(() => {
    setIsDark((prev) => {
      const next = !prev;
      localStorage.setItem('soc-theme', next ? 'dark' : 'light');
      return next;
    });
  }, []);

  const handleTrainClick = async () => {
    if (isTraining) return;
    setIsTraining(true);
    setFeedback(null);
    try {
      const res = await onTrainModel();
      setFeedback(res && res.success ? 'success' : 'error');
      setTimeout(() => setFeedback(null), 3000);
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-zinc-950/80 backdrop-blur-xl border-b border-zinc-800 px-4 md:px-6 py-3 flex justify-between items-center gap-3 relative">
      <div className="flex items-center gap-3">
        <div className="bg-zinc-900 border border-zinc-800 p-2 rounded-lg text-emerald-500">
          <Shield className="w-5 h-5" />
        </div>
        <div className="hidden sm:block">
          <h1 className="text-base font-semibold tracking-tight text-white flex items-center gap-1.5">
            Zenith AI <span className="text-zinc-500 font-normal">|</span> <span className="text-zinc-400 font-normal">SOC Platform</span>
          </h1>
          <p className="text-[11px] text-zinc-500 font-medium">
            Real-time Threat Intelligence & Automated Response
          </p>
        </div>
      </div>

      <div className="hidden lg:flex flex-wrap items-center gap-2 text-xs">
        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : wsStatus === 'connecting' ? 'bg-amber-500' : 'bg-rose-500'}`} />
          <span>Feed: <span className="text-zinc-200 capitalize font-medium">{wsStatus}</span></span>
        </div>

        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'}`} />
          <span>API: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.status || 'offline'}</span></span>
        </div>

        <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
          <span className={`w-2 h-2 rounded-full ${systemHealth?.anomaly_detector === 'trained' ? 'bg-violet-500' : 'bg-zinc-600'}`} />
          <span>ML: <span className="text-zinc-200 capitalize font-medium">{systemHealth?.anomaly_detector || 'untrained'}</span></span>
        </div>

        <button
          onClick={handleTrainClick}
          disabled={isTraining || systemHealth?.status !== 'online'}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs transition-all cursor-pointer font-medium ${
            isTraining ? 'bg-zinc-900 border-zinc-800 text-zinc-500 cursor-not-allowed'
            : feedback === 'success' ? 'bg-emerald-950/40 border-emerald-500/50 text-emerald-300'
            : feedback === 'error' ? 'bg-rose-950/40 border-rose-500/50 text-rose-300'
            : 'bg-violet-950/30 hover:bg-violet-900/40 border-violet-800/50 hover:border-violet-700/60 text-violet-300 hover:text-violet-100 disabled:opacity-50 disabled:cursor-not-allowed'
          }`}
          title="Train Isolation Forest model on latest 500 security events"
        >
          <Cpu className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
          <span>{isTraining ? 'Training...' : feedback === 'success' ? 'Trained!' : feedback === 'error' ? 'Error!' : 'Train Model'}</span>
        </button>

        <button
          onClick={onRefresh}
          className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
          title="Force Sync Stats"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>

        <button
          onClick={toggleTheme}
          className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
          title="Toggle Theme"
        >
          {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
        </button>

        {onLogout && (
          <button
            onClick={onLogout}
            className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 transition-colors rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
            title="Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="hidden md:flex items-center gap-3 text-right">
        <div className="text-xs text-zinc-500">{formatDate(time)}</div>
        <div className="text-sm font-semibold text-zinc-300 font-mono">{formatTime(time)}</div>
      </div>

      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden bg-zinc-900 border border-zinc-800 rounded-lg p-1.5 text-zinc-400 hover:text-zinc-200 cursor-pointer"
      >
        {mobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
      </button>

      {mobileMenuOpen && (
        <div className="absolute top-full left-0 right-0 bg-zinc-950/95 backdrop-blur-xl border-b border-zinc-800 p-4 lg:hidden z-50 flex flex-col gap-3">
          <div className="flex flex-wrap gap-2 text-xs">
            <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
              <span className={`w-2 h-2 rounded-full ${wsStatus === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              Feed: {wsStatus}
            </div>
            <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
              <span className={`w-2 h-2 rounded-full ${systemHealth?.status === 'online' ? 'bg-emerald-500' : 'bg-rose-500'}`} />
              API: {systemHealth?.status || 'offline'}
            </div>
            <div className="bg-zinc-900/40 border border-zinc-800/80 rounded-full px-3 py-1 flex items-center gap-2 text-zinc-400">
              <span className={`w-2 h-2 rounded-full ${systemHealth?.anomaly_detector === 'trained' ? 'bg-violet-500' : 'bg-zinc-600'}`} />
              ML: {systemHealth?.anomaly_detector || 'untrained'}
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleTrainClick} disabled={isTraining} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-violet-950/30 border border-violet-800/50 text-violet-300 text-xs cursor-pointer">
              <Cpu className={`w-3.5 h-3.5 ${isTraining ? 'animate-spin' : ''}`} />
              {isTraining ? 'Training...' : 'Train Model'}
            </button>
            <button onClick={onRefresh} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs cursor-pointer">
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
            <button onClick={toggleTheme} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs cursor-pointer">
              {isDark ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />} Theme
            </button>
            {onLogout && (
              <button onClick={onLogout} className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-400 text-xs cursor-pointer">
                <LogOut className="w-3.5 h-3.5" /> Logout
              </button>
            )}
          </div>
          <div className="text-xs text-zinc-500 font-mono text-center">
            {formatDate(time)} — {formatTime(time)}
          </div>
        </div>
      )}
    </header>
  );
}

export default React.memo(DashboardHeader);
