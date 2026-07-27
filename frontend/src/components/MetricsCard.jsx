import React from 'react';

export default function MetricsCard({ title, value, icon: Icon, description, trend, trendType = 'neutral' }) {
  const trendColor = {
    positive: 'text-emerald-400',
    negative: 'text-rose-400',
    neutral: 'text-slate-400'
  }[trendType];

  return (
    <div className="glass-card p-6 flex flex-col justify-between hover:border-slate-600/70 transition-all duration-200">
      <div className="flex justify-between items-start">
        <div>
          <span className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
            {title}
          </span>
          <span className="text-3xl font-bold text-white tracking-tight">
            {value}
          </span>
        </div>
        <div className="p-3 bg-slate-700/30 rounded-lg text-indigo-400 border border-slate-700/50">
          <Icon className="w-5 h-5" />
        </div>
      </div>
      {(description || trend) && (
        <div className="mt-4 flex items-center gap-2 text-xs">
          {trend && (
            <span className={`font-semibold ${trendColor}`}>
              {trend}
            </span>
          )}
          {description && (
            <span className="text-slate-400">
              {description}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
