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
      <div className="border-b border-slate-200 pb-5">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center space-x-2.5">
          <Network className="h-6 w-6 text-blue-600" />
          <span>Fraud Syndicate & Graph Intelligence Console</span>
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Deep-dive forensic models: Graph network collusion rings, multi-claim duplicate recycling, and unsupervised anomaly detection.
        </p>
      </div>

      {/* Model Performance Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Supervised ROC-AUC</span>
          <p className="text-2xl font-mono font-bold text-blue-600 mt-1">0.842</p>
          <span className="text-[10px] text-slate-400">XGBoost cross-validated test set</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Collusion Precision</span>
          <p className="text-2xl font-mono font-bold text-emerald-600 mt-1">91.4%</p>
          <span className="text-[10px] text-slate-400">Shared entity ring discovery</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Duplicate Search Index</span>
          <p className="text-2xl font-mono font-bold text-slate-900 mt-1">1,000 Claims</p>
          <span className="text-[10px] text-slate-400">O(1) Locality-sensitive hashed</span>
        </div>
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-sm">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Threshold Calibration</span>
          <p className="text-2xl font-mono font-bold text-purple-600 mt-1">T=0.50</p>
          <span className="text-[10px] text-slate-400">Auto-escalates risk &ge; 50%</span>
        </div>
      </div>

      {/* Syndicate Graph Explorer */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <Network className="h-5 w-5 text-blue-600" />
              <span>Collusion Syndicate Network Explorer</span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Identifies organized fraud rings sharing medical providers, collision addresses, and recycled vehicles.
            </p>
          </div>
          <span className="self-start sm:self-auto px-3 py-1 rounded-full bg-red-50 border border-red-200 text-red-700 text-xs font-mono font-semibold">
            3 Active Syndicates Flagged
          </span>
        </div>

        {/* SVG Graph on Light Canvas */}
        <div className="h-80 bg-slate-50 rounded-xl border border-slate-200 relative flex items-center justify-center overflow-hidden">
          {/* Subtle Grid Dot Pattern */}
          <div
            className="absolute inset-0 opacity-40"
            style={{
              backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)',
              backgroundSize: '24px 24px'
            }}
          />

          <svg className="w-full h-full relative z-10" viewBox="0 0 700 280">
            {/* Cluster 1 - Albany Collision Ring */}
            <g transform="translate(200, 140)">
              <circle r="65" fill="rgba(239, 68, 68, 0.06)" stroke="#fca5a5" strokeWidth="1.5" strokeDasharray="4" />
              <line x1="0" y1="0" x2="-45" y2="-35" stroke="#ef4444" strokeWidth="2" />
              <line x1="0" y1="0" x2="45" y2="-35" stroke="#ef4444" strokeWidth="2" />
              <line x1="0" y1="0" x2="0" y2="48" stroke="#ef4444" strokeWidth="2" />

              {/* Central Flagged Clinic Node */}
              <circle r="20" fill="#dc2626" stroke="#991b1b" strokeWidth="2" />
              <text y="4" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold">CLINIC #1</text>

              {/* Connected Claim/Policy Nodes */}
              <circle cx="-45" cy="-35" r="12" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1.5" />
              <text x="-45" y="-32" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">CLM-1</text>

              <circle cx="45" cy="-35" r="12" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1.5" />
              <text x="45" y="-32" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">CLM-2</text>

              <circle cx="0" cy="48" r="12" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1.5" />
              <text x="0" y="51" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">CLM-3</text>
            </g>

            {/* Inter-cluster Bridge */}
            <line x1="245" y1="105" x2="445" y2="105" stroke="#cbd5e1" strokeWidth="1.5" strokeDasharray="3" />

            {/* Cluster 2 - VIN Recycling Ring */}
            <g transform="translate(490, 140)">
              <circle r="65" fill="rgba(245, 158, 11, 0.06)" stroke="#fcd34d" strokeWidth="1.5" strokeDasharray="4" />
              <line x1="0" y1="0" x2="-45" y2="-35" stroke="#f59e0b" strokeWidth="2" />
              <line x1="0" y1="0" x2="45" y2="-35" stroke="#f59e0b" strokeWidth="2" />
              <line x1="0" y1="0" x2="0" y2="48" stroke="#f59e0b" strokeWidth="2" />

              {/* Central Flagged Asset Node */}
              <circle r="20" fill="#d97706" stroke="#b45309" strokeWidth="2" />
              <text y="4" textAnchor="middle" fill="#fff" fontSize="8" fontWeight="bold">VIN-882</text>

              {/* Connected Claim Nodes */}
              <circle cx="-45" cy="-35" r="12" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1.5" />
              <text x="-45" y="-32" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">CLM-4</text>

              <circle cx="45" cy="-35" r="12" fill="#2563eb" stroke="#1d4ed8" strokeWidth="1.5" />
              <text x="45" y="-32" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">CLM-5</text>

              <circle cx="0" cy="48" r="12" fill="#1d4ed8" stroke="#0f172a" strokeWidth="1.5" />
              <text x="0" y="51" textAnchor="middle" fill="#fff" fontSize="7" fontWeight="bold">HUB</text>
            </g>
          </svg>

          {/* Floating Dossier Tag */}
          <div className="absolute top-4 left-4 bg-white/95 border border-slate-200 shadow-sm rounded-lg p-3 text-xs space-y-0.5 z-20">
            <span className="text-slate-900 font-bold block">Syndicate Ring #A4: Metro Health & Collision</span>
            <span className="text-slate-500 block">3 Policyholders • 5 Claims • $184,000 Combined Exposure</span>
          </div>
        </div>

        {/* Graph Legend */}
        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs">
          <span className="font-semibold text-slate-700">Graph Legend:</span>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-blue-600 inline-block"></span>
            <span className="text-slate-600">Claim / Policy Node</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-[#1d4ed8] inline-block"></span>
            <span className="text-slate-600">Central Hub</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-red-600 inline-block"></span>
            <span className="text-slate-600">Flagged Syndicate (Clinic)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block"></span>
            <span className="text-slate-600">Recycled Asset (VIN)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-6 h-0.5 bg-red-400 inline-block"></span>
            <span className="text-slate-600">Collusion Link</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-6 h-0.5 border-t border-dashed border-slate-400 inline-block"></span>
            <span className="text-slate-600">Cross-entity Bridge</span>
          </div>
        </div>
      </div>

      {/* Duplicate Claim Radar & Anomaly Distribution */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Copy className="h-4 w-4 text-amber-600" />
            <span>Recycled & Duplicate Claim Patterns</span>
          </h3>
          <p className="text-xs text-slate-500">
            Automated similarity scoring flagging policyholders submitting identical damages across multiple carriers or previous loss events.
          </p>
          <div className="space-y-2.5 pt-2 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex justify-between items-center">
              <div>
                <span className="text-slate-900 font-medium block">Exact VIN Match across multiple policies</span>
                <span className="text-[11px] text-slate-500">Recycled vehicle collision scam</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-red-50 text-red-700 border border-red-200 font-mono font-semibold text-[11px]">
                3 incidents
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex justify-between items-center">
              <div>
                <span className="text-slate-900 font-medium block">Identical claim dollar amounts within 30 days</span>
                <span className="text-[11px] text-slate-500">Inverted quote recycling</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200 font-mono font-semibold text-[11px]">
                5 incidents
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
          <h3 className="text-base font-bold text-slate-900 flex items-center space-x-2">
            <Activity className="h-4 w-4 text-purple-600" />
            <span>Unsupervised Anomaly Outliers</span>
          </h3>
          <p className="text-xs text-slate-500">
            Isolation Forest models detecting non-linear multi-variable outliers in high-dimensional feature space.
          </p>
          <div className="space-y-2.5 pt-2 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex justify-between items-center">
              <div>
                <span className="text-slate-900 font-medium block">Severe injury claim with trivial vehicle damage</span>
                <span className="text-[11px] text-slate-500">Disproportionate physical biomechanics</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 font-mono font-semibold text-[11px]">
                Anomaly 0.88
              </span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 flex justify-between items-center">
              <div>
                <span className="text-slate-900 font-medium block">Claim filed within 48 hours of policy inception</span>
                <span className="text-[11px] text-slate-500">Pre-existing damage concealment</span>
              </div>
              <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-200 font-mono font-semibold text-[11px]">
                Anomaly 0.79
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
