import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  highlightColor?: 'blue' | 'red' | 'amber' | 'emerald';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  highlightColor = 'blue',
}) => {
  const getGlow = () => {
    switch (highlightColor) {
      case 'red':
        return 'border-red-500/20 hover:border-red-500/40 hover:glow-red';
      case 'amber':
        return 'border-amber-500/20 hover:border-amber-500/40 hover:glow-amber';
      case 'emerald':
        return 'border-emerald-500/20 hover:border-emerald-500/40 hover:glow-emerald';
      case 'blue':
      default:
        return 'border-sky-500/20 hover:border-sky-500/40 hover:glow-cyan';
    }
  };

  const getIconBg = () => {
    switch (highlightColor) {
      case 'red':
        return 'bg-red-500/10 text-red-400 border border-red-500/20';
      case 'amber':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'emerald':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'blue':
      default:
        return 'bg-sky-500/10 text-sky-400 border border-sky-500/20';
    }
  };

  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-slate-900/70 backdrop-blur-md p-5 border transition-all duration-200 ${getGlow()}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            {title}
          </p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-white">
            {value}
          </p>
        </div>
        <div className={`p-3 rounded-lg ${getIconBg()}`}>
          {icon}
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="mt-3 flex items-center space-x-2 text-xs">
          {trend && (
            <span
              className={`font-semibold ${
                trend.isPositive ? 'text-emerald-400' : 'text-red-400'
              }`}
            >
              {trend.value}
            </span>
          )}
          {subtitle && <span className="text-slate-500">{subtitle}</span>}
        </div>
      )}
    </div>
  );
};
