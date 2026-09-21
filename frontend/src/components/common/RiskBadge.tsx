import React from 'react';

interface RiskBadgeProps {
  score?: number;
  level?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  score,
  level,
  size = 'md',
  showScore = true,
}) => {
  // Infer level if score is provided and level is not
  let derivedLevel = level?.toUpperCase();
  if (!derivedLevel && score !== undefined) {
    if (score >= 0.7) derivedLevel = 'CRITICAL';
    else if (score >= 0.5) derivedLevel = 'HIGH';
    else if (score >= 0.25) derivedLevel = 'MEDIUM';
    else derivedLevel = 'LOW';
  }

  const getColors = () => {
    switch (derivedLevel) {
      case 'CRITICAL':
        return {
          bg: 'bg-rose-50 border-rose-300 text-rose-800',
          dot: 'bg-rose-600',
        };
      case 'HIGH':
        return {
          bg: 'bg-red-50 border-red-200 text-red-700',
          dot: 'bg-red-600',
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-50 border-amber-200 text-amber-800',
          dot: 'bg-amber-500',
        };
      case 'LOW':
      default:
        return {
          bg: 'bg-emerald-50 border-emerald-200 text-emerald-800',
          dot: 'bg-emerald-600',
        };
    }
  };

  const colors = getColors();

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 space-x-1.5 font-bold',
    md: 'text-xs px-2.5 py-1 space-x-2 font-semibold',
    lg: 'text-sm px-3.5 py-1.5 space-x-2.5 font-bold',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border ${colors.bg} ${sizeClasses}`}
    >
      <span className={`inline-block h-2 w-2 rounded-full ${colors.dot}`} />
      <span>{derivedLevel || 'UNKNOWN'}</span>
      {showScore && score !== undefined && (
        <span className="font-mono text-slate-500 border-l border-slate-300 pl-1.5">
          {(score * 100).toFixed(0)}%
        </span>
      )}
    </span>
  );
};
