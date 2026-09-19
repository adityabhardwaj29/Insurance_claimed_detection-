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
          bg: 'bg-red-950/70 border-red-500/50 text-red-300',
          dot: 'bg-red-500 animate-ping',
          dotCore: 'bg-red-400',
        };
      case 'HIGH':
        return {
          bg: 'bg-orange-950/70 border-orange-500/50 text-orange-300',
          dot: 'bg-orange-500 animate-pulse',
          dotCore: 'bg-orange-400',
        };
      case 'MEDIUM':
        return {
          bg: 'bg-amber-950/60 border-amber-500/40 text-amber-300',
          dot: 'bg-amber-500',
          dotCore: 'bg-amber-400',
        };
      case 'LOW':
      default:
        return {
          bg: 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300',
          dot: 'bg-emerald-500',
          dotCore: 'bg-emerald-400',
        };
    }
  };

  const colors = getColors();

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 space-x-1.5',
    md: 'text-xs px-2.5 py-1 space-x-2 font-medium',
    lg: 'text-sm px-3.5 py-1.5 space-x-2.5 font-semibold',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full border backdrop-blur-sm ${colors.bg} ${sizeClasses}`}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`absolute inline-flex h-full w-full rounded-full opacity-75 ${colors.dot}`}
        />
        <span
          className={`relative inline-flex rounded-full h-2 w-2 ${colors.dotCore}`}
        />
      </span>
      <span>{derivedLevel || 'UNKNOWN'}</span>
      {showScore && score !== undefined && (
        <span className="font-mono text-slate-400 border-l border-slate-700 pl-1.5">
          {(score * 100).toFixed(0)}%
        </span>
      )}
    </span>
  );
};
