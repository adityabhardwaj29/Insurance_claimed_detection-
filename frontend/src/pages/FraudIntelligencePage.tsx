import React from 'react';
import {
  Network,
  Copy,
  Activity,
  Cpu,
  ShieldCheck,
  AlertTriangle,
  Layers,
  ArrowUpRight
} from 'lucide-react';

export const FraudIntelligencePage: React.FC = () => {
  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          Fraud Syndicate & Graph Intelligence Console
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Deep-dive forensic models: Graph network collusion rings, multi-claim duplicate recycling, and unsupervised anomaly detection.
        </p>
      </div>

      {/* Model Performance Ribbon */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Supervised ROC-AUC</span>
          <p className="text-2xl font-mono font-bold text-sky-400 mt-1">0.842</p>
          <span className="text-[10px] text-slate-500">XGBoost cross-validated test set</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Collusion Precision</span>
          <p className="text-2xl font-mono font-bold text-emerald-400 mt-1">91.4%</p>
          <span className="text-[10px] text-slate-500">Shared entity ring discovery</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Duplicate Search Index</span>
          <p className="text-2xl font-mono font-bold text-amber-400 mt-1">1,000 Claims</p>
          <span className="text-[10px] text-slate-500">O(1) Locality-sensitive hashed</span>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase">Threshold Calibration</span>
          <p className="text-2xl font-mono font-bold text-purple-400 mt-1">T=0.50</p>
          <span className="text-[10px] text-slate-500">Auto-escalates risk &gt;= 50%</span>
        </div>
      </div>

      {/* Syndicate Graph Explorer */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Network className="h-5 w-5 text-sky-400" />
              <span>Collusion Syndicate Network Explorer</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Identifies organized fraud rings sharing crooked medical providers, shared collision addresses, and recycled vehicles.
            </p>
          </div>
          <span className="px-3 py-1 rounded-full bg-red-950/80 border border-red-500/50 text-red-300 text-xs font-mono font-semibold animate-pulse">
            3 Active Syndicates Flagged
          </span>
        </div>

        <div className="h-72 bg-slate-950 rounded-xl border border-slate-800 relative flex items-center justify-center overflow-hidden">
          {/* Simulated Graph Rings */}
          <svg className="w-full h-full" viewBox="0 0 700 280">
            {/* Cluster 1 - Albany Collision Ring */}
            <g transform="translate(180, 140)">
              <circle r="60" fill="rgba(239, 68, 68, 0.05)" stroke="#ef4444" strokeWidth="1" strokeDasharray="4" />
              <line x1="0" y1="0" x2="-40" y2="-30" stroke="#ef4444" strokeWidth="2" />
              <line x1="0" y1="0" x2="40" y2="-30" stroke="#ef4444" strokeWidth="2" />
              <line x1="0" y1="0" x2="0" y2="45" stroke="#ef4444" strokeWidth="2" />

              <circle r="18" fill="#7f1d1d" stroke="#ef4444" strokeWidth="2" />
              <text y="3" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold">CLINIC #1</text>

              <circle cx="-40" cy="-30" r="10" fill="#0284c7" />
              <circle cx="40" cy="-30" r="10" fill="#0284c7" />
              <circle cx="0" cy="45" r="10" fill="#0284c7" />
            </g>

            {/* Cluster 2 - VIN Recycling Ring */}
            <g transform="translate(480, 140)">
              <circle r="60" fill="rgba(245, 158, 11, 0.05)" stroke="#f59e0b" strokeWidth="1" strokeDasharray="4" />
              <line x1="0" y1="0" x2="-35" y2="-25" stroke="#f59e0b" strokeWidth="2" />
              <line x1="0" y1="0" x2="35" y2="-25" stroke="#f59e0b" strokeWidth="2" />
              <line x1="0" y1="0" x2="0" y2="40" stroke="#f59e0b" strokeWidth="2" />

              <circle r="18" fill="#78350f" stroke="#f59e0b" strokeWidth="2" />
              <text y="3" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold">VIN-882</text>

              <circle cx="-35" cy="-25" r="10" fill="#0284c7" />
              <circle cx="35" cy="-25" r="10" fill="#0284c7" />
              <circle cx="0" cy="40" r="10" fill="#0284c7" />
            </g>
          </svg>

          <div className="absolute top-4 left-4 bg-slate-900/90 border border-slate-800 rounded-lg p-3 text-xs space-y-1">
            <span className="text-white font-bold block">Syndicate Ring #A4: Metro Health & Collision</span>
            <span className="text-slate-400 block">3 Policyholders • 4 Claims • $184,000 Combined Exposure</span>
          </div>
        </div>
      </div>

      {/* Duplicate Claim Radar & Anomaly Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Copy className="h-4 w-4 text-amber-400" />
            <span>Recycled & Duplicate Claim Patterns</span>
          </h3>
          <p className="text-xs text-slate-400">
            Automated similarity scoring flagging policyholders submitting identical damages across multiple carriers or previous loss events.
          </p>
          <div className="space-y-2 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="text-white font-medium block">Exact VIN Match across multiple policies</span>
                <span className="text-[11px] text-slate-400">Recycled vehicle collision scam</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-red-950 text-red-300 font-mono">3 incidents</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="text-white font-medium block">Identical claim dollar amounts within 30 days</span>
                <span className="text-[11px] text-slate-400">Inverted quote recycling</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-amber-950 text-amber-300 font-mono">5 incidents</span>
            </div>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-3">
          <h3 className="text-base font-bold text-white flex items-center space-x-2">
            <Activity className="h-4 w-4 text-purple-400" />
            <span>Unsupervised Anomaly Outliers</span>
          </h3>
          <p className="text-xs text-slate-400">
            Isolation Forest models detecting non-linear multi-variable outliers in high-dimensional feature space.
          </p>
          <div className="space-y-2 pt-2 text-xs">
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="text-white font-medium block">Severe injury claim with trivial vehicle damage</span>
                <span className="text-[11px] text-slate-400">Disproportionate physical biomechanics</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-mono">Anomaly 0.88</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex justify-between items-center">
              <div>
                <span className="text-white font-medium block">Claim filed within 48 hours of policy inception</span>
                <span className="text-[11px] text-slate-400">Pre-existing damage concealment</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-mono">Anomaly 0.79</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
