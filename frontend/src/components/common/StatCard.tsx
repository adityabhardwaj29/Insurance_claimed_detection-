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
  const getIconBg = () => {
    switch (highlightColor) {
      case 'red':
        return 'bg-red-50 text-red-600 border border-red-100';
      case 'amber':
        return 'bg-amber-50 text-amber-600 border border-amber-100';
      case 'emerald':
        return 'bg-emerald-50 text-emerald-600 border border-emerald-100';
      case 'blue':
      default:
        return 'bg-blue-50 text-blue-600 border border-blue-100';
    }
  };

  return (
    <div className="bg-white border border-[#E2E8F0] rounded-xl p-5 shadow-xs hover:shadow-md transition-all duration-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
            {title}
          </p>
          <p className="mt-2 text-2xl font-extrabold tracking-tight text-[#0F172A]">
            {value}
          </p>
        </div>
        <div className={`p-2.5 rounded-lg ${getIconBg()}`}>
          {icon}
        </div>
      </div>
      {(subtitle || trend) && (
        <div className="mt-3 flex items-center space-x-2 text-xs">
          {trend && (
            <span
              className={`font-semibold ${
                trend.isPositive ? 'text-emerald-600' : 'text-red-600'
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
