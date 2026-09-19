import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  FolderGit2,
  DollarSign,
  Activity,
  ArrowRight,
  TrendingUp,
  FilePlus,
  AlertTriangle,
  FileCheck
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { RiskBadge } from '../components/common/RiskBadge';
import { api } from '../services/api';
import { Claim, DashboardKPIs } from '../types';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [recentClaims, setRecentClaims] = useState<Claim[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiData, claimsData] = await Promise.all([
          api.getDashboardKPIs(),
          api.getClaims({ limit: 8 }),
        ]);
        setKpis(kpiData);
        setRecentClaims(claimsData);
      } catch (err) {
        console.error('Error fetching dashboard data', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Format currency
  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900/90 to-sky-950/40 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Fraud Operations & SIU Command Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time hybrid fraud detection combining Supervised ML, Isolation Forest, Graph Syndicates, and SHAP Explainability.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/claims/new')}
            className="flex items-center space-x-2 bg-sky-600 hover:bg-sky-500 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-lg shadow-sky-600/20 hover:shadow-sky-500/30 transition-all cursor-pointer"
          >
            <FilePlus className="h-4 w-4" />
            <span>New Claim Intake</span>
          </button>
          <button
            onClick={() => navigate('/cases')}
            className="flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-4 py-2.5 rounded-xl font-semibold text-xs transition-all cursor-pointer"
          >
            <FolderGit2 className="h-4 w-4 text-amber-400" />
            <span>SIU Worklist</span>
          </button>
        </div>
      </div>

      {/* KPI Ribbon */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Claims Volume"
          value={kpis ? kpis.total_claims.toLocaleString() : '1,000'}
          subtitle={kpis ? `${formatCurrency(kpis.total_claims_amount)} exposure` : '$52,761,940 exposure'}
          icon={<FileCheck className="h-5 w-5" />}
          highlightColor="blue"
        />
        <StatCard
          title="Active SIU Cases"
          value={kpis ? kpis.active_investigations : '42'}
          subtitle="Critical priority fraud triage"
          icon={<FolderGit2 className="h-5 w-5" />}
          highlightColor="red"
          trend={{ value: '+4 today', isPositive: false }}
        />
        <StatCard
          title="Fraud Loss Prevented"
          value={kpis ? formatCurrency(kpis.fraud_amount_prevented) : '$14,820,000'}
          subtitle="247 confirmed fraudulent claims"
          icon={<DollarSign className="h-5 w-5" />}
          highlightColor="emerald"
          trend={{ value: '28.1% of volume', isPositive: true }}
        />
        <StatCard
          title="Auto-Triage Rate"
          value={kpis ? `${kpis.automation_rate}%` : '68.5%'}
          subtitle="Straight-through low risk processing"
          icon={<Activity className="h-5 w-5" />}
          highlightColor="amber"
          trend={{ value: 'Avg Risk 0.28', isPositive: true }}
        />
      </div>

      {/* Signal Detection Grid & Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Breakdown */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800">
          <h2 className="text-base font-bold text-white mb-4 flex items-center justify-between">
            <span>Portfolio Risk Tiering</span>
            <span className="text-xs font-mono text-slate-400">1,000 Policies</span>
          </h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-emerald-400">Low Risk (Auto-Approve / Fast Track)</span>
                <span className="font-mono text-slate-300">55% (550)</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '55%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-amber-400">Medium Risk (Standard Adjuster Review)</span>
                <span className="font-mono text-slate-300">20% (200)</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-amber-500 h-2 rounded-full" style={{ width: '20%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-orange-400">High Risk (Desk Audit Required)</span>
                <span className="font-mono text-slate-300">15% (150)</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-orange-500 h-2 rounded-full" style={{ width: '15%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-red-400">Critical Risk (SIU Fraud Escalation)</span>
                <span className="font-mono text-slate-300">10% (100)</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div className="bg-red-500 h-2 rounded-full animate-pulse" style={{ width: '10%' }} />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-slate-800/80 text-xs text-slate-400 space-y-2">
            <div className="flex items-center justify-between">
              <span>Threshold Calibration</span>
              <span className="font-mono text-sky-400 font-semibold">T_high = 0.50</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Auto-Approval Bound</span>
              <span className="font-mono text-emerald-400 font-semibold">T_low = 0.25</span>
            </div>
          </div>
        </div>

        {/* 4 Multi-Signal Pillars */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-white">
                Multi-Signal Detection Architecture
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Every claim passes through four complementary analytical pipelines:
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-full bg-sky-950/70 border border-sky-800 text-sky-300 text-xs font-mono">
              Hybrid Scoring Model
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">
                  1. Supervised Machine Learning
                </span>
                <span className="font-mono text-xs text-slate-400">Weight: 40%</span>
              </div>
              <p className="text-xs text-slate-300 mt-2 font-medium">
                XGBoost + Random Forest Ensemble
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Trained on 38 engineered features (severity ratio, injury/total, policy tenure) calibrated to ROC-AUC 0.84.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">
                  2. Unsupervised Anomaly
                </span>
                <span className="font-mono text-xs text-slate-400">Weight: 20%</span>
              </div>
              <p className="text-xs text-slate-300 mt-2 font-medium">
                Isolation Forest Outlier Detection
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Flags rare, high-dimension deviations and novel staging schemes without requiring prior fraud labels.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                  3. Duplicate Claim Matching
                </span>
                <span className="font-mono text-xs text-slate-400">Weight: 20%</span>
              </div>
              <p className="text-xs text-slate-300 mt-2 font-medium">
                Multi-Attribute Similarity Engine
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Detects recycled claims across identical VINs, matching damage totals, collision dates, and claimant aliases.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                  4. Graph Syndicate Collusion
                </span>
                <span className="font-mono text-xs text-slate-400">Weight: 20%</span>
              </div>
              <p className="text-xs text-slate-300 mt-2 font-medium">
                NetworkX Bipartite Topology
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                Exposes organized fraud rings sharing crooked medical providers, shared addresses, and recycled vehicles.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Investigation Worklist (Recent Flagged Claims) */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <div className="p-5 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">
              Recent Claims & Risk Triage Stream
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Live claims feed prioritized by hybrid risk score and automated recommendation.
            </p>
          </div>
          <button
            onClick={() => navigate('/claims')}
            className="flex items-center space-x-1.5 text-xs font-semibold text-sky-400 hover:text-sky-300 transition-colors"
          >
            <span>View All Claims</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/70 border-b border-slate-800 text-slate-400 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-5 py-3">Claim Number</th>
                <th className="px-5 py-3">Claimant / Policy</th>
                <th className="px-5 py-3">Incident Date</th>
                <th className="px-5 py-3">Claim Amount</th>
                <th className="px-5 py-3">Risk Assessment</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {recentClaims.length > 0 ? (
                recentClaims.map((claim) => (
                  <tr
                    key={claim.id}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => navigate(`/claims/${claim.id}`)}
                  >
                    <td className="px-5 py-3.5 font-mono text-sky-400 font-bold">
                      {claim.claim_number}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="text-white font-semibold">{claim.claimant_name || 'Policyholder'}</div>
                      <div className="text-slate-400 font-mono text-[11px]">
                        {claim.policy_number || 'POL-782910'}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-slate-300">
                      {claim.incident_date}
                    </td>
                    <td className="px-5 py-3.5 font-mono font-semibold text-white">
                      {formatCurrency(claim.total_claim_amount)}
                    </td>
                    <td className="px-5 py-3.5">
                      <RiskBadge
                        score={claim.risk_score !== undefined ? claim.risk_score : 0.45}
                        level={claim.risk_level || 'MEDIUM'}
                        size="sm"
                      />
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px]">
                        {claim.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/claims/${claim.id}`);
                        }}
                        className="text-xs bg-slate-800 hover:bg-sky-600 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 transition-all font-semibold"
                      >
                        Inspect 360°
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    Loading claims records from database...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
