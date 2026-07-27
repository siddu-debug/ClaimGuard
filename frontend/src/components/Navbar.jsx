import React, { useEffect, useState } from 'react';
import { Shield, Activity } from 'lucide-react';
import { healthCheck } from '../api/client';

export default function Navbar({ onNavigate, currentPage }) {
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const data = await healthCheck();
        if (data && data.status === 'ok') {
          setIsOnline(true);
        } else {
          setIsOnline(false);
        }
      } catch (err) {
        setIsOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="glass-card-dark rounded-none border-t-0 border-x-0 border-b border-slate-800/80 sticky top-0 z-40 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('dashboard')}>
        <div className="p-2 bg-indigo-600/20 border border-indigo-500/30 rounded-lg text-indigo-400">
          <Shield className="w-6 h-6 animate-pulse-slow" />
        </div>
        <div>
          <h1 className="font-extrabold text-lg text-white leading-none flex items-center gap-1.5">
            ClaimGuard <span className="text-xs bg-indigo-600/30 text-indigo-400 border border-indigo-500/40 px-1.5 py-0.5 rounded font-mono font-medium">AI</span>
          </h1>
          <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Claims Automation & Risk Analysis
          </span>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <nav className="flex items-center gap-2">
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
              currentPage === 'dashboard'
                ? 'text-white bg-slate-800/80 border border-slate-700/60 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/30'
            }`}
          >
            Claims Queue
          </button>
        </nav>

        <div className="flex items-center gap-2 border-l border-slate-800 pl-6">
          <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-emerald-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'}`} />
          <span className="text-xs font-medium text-slate-400 flex items-center gap-1">
            API {isOnline ? 'Connected' : 'Offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
