import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderGit2,
  DollarSign,
  Activity,
  ArrowRight,
  FilePlus,
  FileCheck,
  ShieldCheck,
  Zap,
  Network
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
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-white border border-[#E2E8F0] p-4 sm:p-6 rounded-xl shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-[#2563EB] uppercase tracking-wider mb-1">
            <ShieldCheck className="h-4 w-4" />
            <span>Insurance Fraud Intelligence Overview</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-extrabold text-[#0F172A] tracking-tight">
            Fraud Operations & SIU Command Center
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-2xl">
            Real-time multi-signal fraud scoring engine combining Supervised XGBoost, Unsupervised Isolation Forest, Bipartite Graph Syndicates, and SHAP Attribution.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-2.5 flex-shrink-0 w-full sm:w-auto">
          <button
            onClick={() => navigate('/claims/new')}
            className="flex items-center justify-center space-x-2 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-2.5 rounded-lg font-semibold text-xs shadow-xs transition-all cursor-pointer w-full sm:w-auto"
          >
            <FilePlus className="h-4 w-4" />
            <span>New Claim Intake</span>
          </button>
          <button
            onClick={() => navigate('/cases')}
            className="flex items-center justify-center space-x-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 px-4 py-2.5 rounded-lg font-semibold text-xs shadow-xs transition-all cursor-pointer w-full sm:w-auto"
          >
            <FolderGit2 className="h-4 w-4 text-amber-600" />
            <span>SIU Worklist</span>
          </button>
        </div>
      </div>

      {/* KPI Ribbon: 1 col on XS, 2 col on SM & MD, 4 col on LG+ */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-5">
        <StatCard
          title="Total Claims Volume"
          value={kpis ? kpis.total_claims.toLocaleString() : '320'}
          subtitle={kpis ? `${formatCurrency(kpis.total_claims_amount)} exposure` : '$18,450,000 exposure'}
          icon={<FileCheck className="h-5 w-5" />}
          highlightColor="blue"
        />
        <StatCard
          title="Active SIU Cases"
          value={kpis ? kpis.active_investigations : '27'}
          subtitle="High & critical priority triage"
          icon={<FolderGit2 className="h-5 w-5" />}
          highlightColor="red"
          trend={{ value: '+4 this week', isPositive: false }}
        />
        <StatCard
          title="Fraud Loss Prevented"
          value={kpis ? formatCurrency(kpis.fraud_amount_prevented) : '$4,820,000'}
          subtitle="Confirmed fraudulent exposure"
          icon={<DollarSign className="h-5 w-5" />}
          highlightColor="emerald"
          trend={{ value: '16.3% fraud rate', isPositive: true }}
        />
        <StatCard
          title="Auto-Triage Rate"
          value={kpis ? `${kpis.automation_rate}%` : '68.5%'}
          subtitle="Low-risk straight-through processing"
          icon={<Activity className="h-5 w-5" />}
          highlightColor="amber"
          trend={{ value: 'Avg Risk 0.28', isPositive: true }}
        />
      </div>

      {/* Signal Detection Grid & Risk Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Breakdown */}
        <div className="bg-white border border-[#E2E8F0] p-6 rounded-xl shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider">
              Portfolio Risk Tiering
            </h2>
            <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              320 Claims
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-emerald-700 font-semibold">Low Risk (Auto-Approve / Fast Track)</span>
                <span className="font-mono text-slate-700 font-bold">55% (176)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-emerald-600 h-2.5 rounded-full" style={{ width: '55%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-amber-700 font-semibold">Medium Risk (Standard Adjuster Review)</span>
                <span className="font-mono text-slate-700 font-bold">20% (64)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-amber-500 h-2.5 rounded-full" style={{ width: '20%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-red-700 font-semibold">High Risk (Desk Audit Required)</span>
                <span className="font-mono text-slate-700 font-bold">15% (48)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-red-600 h-2.5 rounded-full" style={{ width: '15%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-medium mb-1">
                <span className="text-rose-800 font-bold">Critical Risk (SIU Fraud Escalation)</span>
                <span className="font-mono text-slate-700 font-bold">10% (32)</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div className="bg-rose-700 h-2.5 rounded-full" style={{ width: '10%' }} />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-[#E2E8F0] text-xs text-slate-600 space-y-2">
            <div className="flex items-center justify-between">
              <span>Threshold Calibration (T_high)</span>
              <span className="font-mono text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-100">0.50</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Auto-Approval Bound (T_low)</span>
              <span className="font-mono text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">0.25</span>
            </div>
          </div>
        </div>

        {/* 4 Multi-Signal Pillars */}
        <div className="bg-white border border-[#E2E8F0] p-6 rounded-xl shadow-xs lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider">
                  Multi-Signal Detection Architecture
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Every claim is evaluated concurrently across four distinct forensic analytical models:
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-xs font-bold font-mono">
                Hybrid Formula
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mt-4">
              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-200 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-700 uppercase tracking-wider">
                    1. Supervised Machine Learning
                  </span>
                  <span className="font-mono text-xs text-slate-500 font-bold">40%</span>
                </div>
                <p className="text-xs text-slate-800 mt-1.5 font-semibold">
                  XGBoost Classifier
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                  Evaluates 38 engineered relational, financial, and temporal indicators to predict fraud probability.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-200 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider">
                    2. Unsupervised Anomaly
                  </span>
                  <span className="font-mono text-xs text-slate-500 font-bold">20%</span>
                </div>
                <p className="text-xs text-slate-800 mt-1.5 font-semibold">
                  Isolation Forest Outlier Model
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                  Flags high-dimensional multivariate deviations and novel claim staging without requiring historical labels.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-200 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-amber-700 uppercase tracking-wider">
                    3. Duplicate Matching Engine
                  </span>
                  <span className="font-mono text-xs text-slate-500 font-bold">20%</span>
                </div>
                <p className="text-xs text-slate-800 mt-1.5 font-semibold">
                  TF-IDF & Pairwise Cosine Similarity
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                  Identifies recycled claims across identical VINs, matching damage totals, collision dates, and claimant aliases.
                </p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 hover:border-blue-200 transition-all">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider">
                    4. Graph Syndicate Collusion
                  </span>
                  <span className="font-mono text-xs text-slate-500 font-bold">20%</span>
                </div>
                <p className="text-xs text-slate-800 mt-1.5 font-semibold">
                  NetworkX Bipartite Topology
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5 leading-relaxed">
                  Uncovers organized rings sharing crooked repair providers, shared addresses, and recycled vehicles.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Priority Investigation Worklist (Recent Claims) */}
      <div className="bg-white border border-[#E2E8F0] rounded-xl shadow-xs overflow-hidden">
        <div className="p-5 border-b border-[#E2E8F0] flex items-center justify-between bg-slate-50/50">
          <div>
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider">
              Recent Claims & Risk Triage Stream
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Live claims feed prioritized by hybrid risk score and automated recommendation.
            </p>
          </div>
          <button
            onClick={() => navigate('/claims')}
            className="flex items-center space-x-1.5 text-xs font-bold text-[#2563EB] hover:text-[#1D4ED8] transition-colors cursor-pointer"
          >
            <span>View All Claims</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[700px] text-left text-xs">
            <thead className="bg-slate-50 border-b border-[#E2E8F0] text-slate-600 uppercase font-bold tracking-wider text-[11px]">
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
            <tbody className="divide-y divide-slate-100 font-medium">
              {recentClaims.length > 0 ? (
                recentClaims.map((claim) => (
                  <tr
                    key={claim.id}
                    className="hover:bg-[#EFF6FF]/60 transition-colors group cursor-pointer"
                    onClick={() => navigate(`/claims/${claim.id}`)}
                  >
                    <td className="px-5 py-3.5 font-mono text-[#2563EB] font-bold">
                      {claim.claim_number}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="text-[#0F172A] font-semibold">{claim.claimant_name || 'Policyholder'}</div>
                      <div className="text-slate-500 font-mono text-[11px]">
                        {claim.policy_number || 'POL-782910'}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-slate-600">
                      {claim.incident_date}
                    </td>
                    <td className="px-5 py-3.5 font-mono font-bold text-[#0F172A]">
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
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-medium">
                        {claim.status}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/claims/${claim.id}`);
                        }}
                        className="text-xs bg-white hover:bg-blue-50 text-[#2563EB] hover:text-[#1D4ED8] px-3 py-1.5 rounded-lg border border-blue-200 transition-all font-semibold cursor-pointer"
                      >
                        Inspect 360°
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-8 text-slate-500">
                    {isLoading ? 'Loading claims records from database...' : 'No claims found.'}
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
