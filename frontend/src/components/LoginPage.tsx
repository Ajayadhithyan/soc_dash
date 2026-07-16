import React, { useState } from 'react';
import { Shield, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { login, setAuthToken } from '../utils/api';

interface LoginPageProps {
  onLogin: (token: string) => void;
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const data = await login(username, password);
      setAuthToken(data.access_token);
      localStorage.setItem('soc_token', data.access_token);
      onLogin(data.access_token);
    } catch {
      setError('Invalid username or password. Try admin/admin123');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid-bg flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-zinc-900 border border-zinc-800 text-emerald-500 mb-4">
            <Shield className="w-8 h-8" />
          </div>
          <h1 className="text-xl font-bold text-white tracking-tight">Zenith AI SOC</h1>
          <p className="text-xs text-zinc-500 mt-1">Security Operations Center Login</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-zinc-900/60 rounded-xl border border-zinc-800 p-6 flex flex-col gap-4">
          {error && (
            <div className="flex items-center gap-2 bg-rose-950/30 border border-rose-500/30 rounded-lg p-3 text-xs text-rose-300">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          <div>
            <label className="text-[11px] text-zinc-400 font-semibold uppercase tracking-wider mb-1.5 block">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-zinc-950/60 border border-zinc-800 text-zinc-200 font-mono text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-zinc-700 transition-colors"
              placeholder="admin"
              required
            />
          </div>

          <div>
            <label className="text-[11px] text-zinc-400 font-semibold uppercase tracking-wider mb-1.5 block">Password</label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-zinc-950/60 border border-zinc-800 text-zinc-200 font-mono text-sm rounded-lg px-3 py-2 pr-10 focus:outline-none focus:border-zinc-700 transition-colors"
                placeholder="admin123"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors cursor-pointer"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm mt-1 cursor-pointer"
          >
            {isLoading ? 'Authenticating...' : 'Sign In'}
          </button>

          <p className="text-[10px] text-zinc-600 text-center mt-1">
            Demo: admin / admin123
          </p>
        </form>
      </div>
    </div>
  );
}
