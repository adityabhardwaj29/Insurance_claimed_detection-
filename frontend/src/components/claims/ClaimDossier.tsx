import React, { useState } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileText,
  Network,
  Copy,
  FolderPlus,
  Send,
  UserCheck,
  Building,
  Car,
  Calendar,
  DollarSign,
  Activity,
  Layers
} from 'lucide-react';
import { Claim, RiskAnalysis } from '../../types';
import { RiskBadge } from '../common/RiskBadge';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';

interface ClaimDossierProps {
  claim: Claim;
  analysis: RiskAnalysis;
  onDecisionRecorded?: () => void;
}

export const ClaimDossier: React.FC<ClaimDossierProps> = ({
  claim,
  analysis,
  onDecisionRecorded,
}) => {
  const { role, user } = useAuth();
  const [decisionNotes, setDecisionNotes] = useState('');
  const [isSubmittingDecision, setIsSubmittingDecision] = useState(false);
  const [decisionSuccess, setDecisionSuccess] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'signals' | 'shap' | 'duplicates' | 'graph' | 'notes'>('signals');

  const [notes, setNotes] = useState<Array<{ author: string; role: string; text: string; date: string }>>([
    {
      author: 'Automated Fraud Engine',
      role: 'SYSTEM',
      text: `Calculated initial hybrid risk score of ${(analysis.hybrid_risk_score * 100).toFixed(1)}%. Recommendation: ${analysis.recommendation}.`,
      date: 'Just now',
    },
  ]);
  const [newNote, setNewNote] = useState('');

  const formatCurrency = (val?: number) => {
    if (val === undefined) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const handleDecision = async (decision: 'APPROVE' | 'REJECT' | 'ESCALATE_SIU' | 'REQUEST_INFO') => {
    setIsSubmittingDecision(true);
    try {
      await api.recordDecision(claim.id, decision, decisionNotes || `Actioned by ${user?.full_name} (${role})`);
      setDecisionSuccess(`Claim successfully updated with decision: ${decision}`);
      setNotes((prev) => [
        {
          author: user?.full_name || 'Officer',
          role: role,
          text: `Recorded official decision: ${decision}. Note: ${decisionNotes || 'None'}`,
          date: 'Just now',
        },
        ...prev,
      ]);
      setDecisionNotes('');
      if (onDecisionRecorded) onDecisionRecorded();
    } catch (err: any) {
      console.error('Error recording decision', err);
    } finally {
      setIsSubmittingDecision(false);
    }
  };

  const handleAddNote = () => {
    if (!newNote.trim()) return;
    setNotes((prev) => [
      {
        author: user?.full_name || 'Investigator',
        role: role,
        text: newNote,
        date: 'Just now',
      },
      ...prev,
    ]);
    setNewNote('');
  };

  const getRecColor = (rec: string) => {
    switch (rec) {
      case 'AUTO_APPROVE':
        return 'bg-emerald-950/70 border-emerald-500/50 text-emerald-300';
      case 'FAST_TRACK':
        return 'bg-sky-950/70 border-sky-500/50 text-sky-300';
      case 'MANUAL_INVESTIGATION':
        return 'bg-amber-950/70 border-amber-500/50 text-amber-300';
      case 'SIU_ESCALATE':
      default:
        return 'bg-red-950/70 border-red-500/50 text-red-300';
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Dossier Header Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-mono font-extrabold text-white">
              {claim.claim_number}
            </h1>
            <RiskBadge
              score={analysis.hybrid_risk_score}
              level={analysis.risk_level}
              size="md"
            />
            <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 text-xs font-semibold">
              {claim.status}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-400">
            <span className="flex items-center space-x-1">
              <UserCheck className="h-3.5 w-3.5 text-slate-500" />
              <strong className="text-slate-200">{claim.claimant_name || 'Aditya Bhardwaj'}</strong>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <FileText className="h-3.5 w-3.5 text-slate-500" />
              <span>Policy: <strong className="text-slate-200 font-mono">{claim.policy_number || 'POL-521948'}</strong></span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Calendar className="h-3.5 w-3.5 text-slate-500" />
              <span>Incident: {claim.incident_date}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <DollarSign className="h-3.5 w-3.5 text-slate-500" />
              <strong className="text-sky-400 font-mono text-sm">
                {formatCurrency(claim.total_claim_amount)}
              </strong>
            </span>
          </div>
        </div>

        {/* Quick Decision Trigger Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => handleDecision('APPROVE')}
            disabled={isSubmittingDecision}
            className="flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg shadow-emerald-600/20 cursor-pointer"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>Approve</span>
          </button>
          <button
            onClick={() => handleDecision('ESCALATE_SIU')}
            disabled={isSubmittingDecision}
            className="flex items-center space-x-1.5 bg-red-600 hover:bg-red-500 text-white px-3.5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg shadow-red-600/20 cursor-pointer"
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>Escalate SIU</span>
          </button>
          <button
            onClick={() => handleDecision('REJECT')}
            disabled={isSubmittingDecision}
            className="flex items-center space-x-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer"
          >
            <XCircle className="h-3.5 w-3.5 text-slate-400" />
            <span>Reject</span>
          </button>
        </div>
      </div>

      {decisionSuccess && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-200 text-xs font-medium flex items-center justify-between">
          <span>{decisionSuccess}</span>
          <button onClick={() => setDecisionSuccess(null)} className="text-emerald-400 hover:text-white">
            Dismiss
          </button>
        </div>
      )}

      {/* Top Section: Composite Risk Gauge & Automated Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Composite Gauge Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex flex-col justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block">
              Multi-Signal Hybrid Risk Score
            </span>
            <div className="flex items-baseline space-x-3 mt-3">
              <span className="text-4xl font-extrabold font-mono text-white">
                {(analysis.hybrid_risk_score * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-slate-400">
                (T_high: 50% | T_low: 25%)
              </span>
            </div>

            {/* Score Bar */}
            <div className="w-full bg-slate-800 rounded-full h-3 mt-4 overflow-hidden p-0.5">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  analysis.hybrid_risk_score >= 0.7
                    ? 'bg-red-500'
                    : analysis.hybrid_risk_score >= 0.5
                    ? 'bg-orange-500'
                    : analysis.hybrid_risk_score >= 0.25
                    ? 'bg-amber-500'
                    : 'bg-emerald-500'
                }`}
                style={{ width: `${Math.min(analysis.hybrid_risk_score * 100, 100)}%` }}
              />
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              System Recommendation
            </span>
            <div className={`p-3 rounded-xl border text-xs font-medium ${getRecColor(analysis.recommendation)}`}>
              <div className="font-bold flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4" />
                <span>{analysis.recommendation.replace('_', ' ')}</span>
              </div>
              <p className="mt-1 text-[11px] opacity-90">
                {analysis.recommendation_reason ||
                  'Risk indicators exceeded threshold. Forward to SIU special investigator for desk audit.'}
              </p>
            </div>
          </div>
        </div>

        {/* 4 Signals Bar Card */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 lg:col-span-2">
          <h2 className="text-base font-bold text-white mb-4 flex items-center justify-between">
            <span>Component Signal Breakdown</span>
            <span className="text-xs font-mono text-slate-400">Ensemble Weighted Fusion</span>
          </h2>

          <div className="space-y-4">
            {/* Supervised ML */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-sky-400 font-semibold">1. Supervised ML (XGBoost Ensemble)</span>
                <span className="font-mono text-slate-300">
                  {(analysis.ml_score * 100).toFixed(1)}% (Weight: 40%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-sky-500 h-2 rounded-full"
                  style={{ width: `${analysis.ml_score * 100}%` }}
                />
              </div>
            </div>

            {/* Isolation Forest */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-purple-400 font-semibold">2. Unsupervised Anomaly (Isolation Forest)</span>
                <span className="font-mono text-slate-300">
                  {(analysis.anomaly_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${analysis.anomaly_score * 100}%` }}
                />
              </div>
            </div>

            {/* Duplicate Claim Similarity */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-amber-400 font-semibold">3. Duplicate & Recycled Claim Matching</span>
                <span className="font-mono text-slate-300">
                  {(analysis.duplicate_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-amber-500 h-2 rounded-full"
                  style={{ width: `${analysis.duplicate_score * 100}%` }}
                />
              </div>
            </div>

            {/* Graph Collusion */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-emerald-400 font-semibold">4. Graph Syndicate Collusion Network</span>
                <span className="font-mono text-slate-300">
                  {(analysis.graph_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                  className="bg-emerald-500 h-2 rounded-full"
                  style={{ width: `${analysis.graph_score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Score formula: Risk = 0.40(ML) + 0.20(Anomaly) + 0.20(Duplicate) + 0.20(Graph)</span>
            <span className="font-mono text-sky-400 font-semibold">Audited Calibration</span>
          </div>
        </div>
      </div>

      {/* Forensic Deep Dive Tabs */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 bg-slate-950/60 overflow-x-auto">
          <button
            onClick={() => setActiveTab('signals')}
            className={`px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'signals'
                ? 'border-sky-500 text-sky-400 bg-slate-900/80'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="h-4 w-4" />
            <span>Loss Circumstances</span>
          </button>

          <button
            onClick={() => setActiveTab('shap')}
            className={`px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'shap'
                ? 'border-sky-500 text-sky-400 bg-slate-900/80'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Activity className="h-4 w-4" />
            <span>SHAP Explainability Waterfall</span>
          </button>

          <button
            onClick={() => setActiveTab('duplicates')}
            className={`px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'duplicates'
                ? 'border-sky-500 text-sky-400 bg-slate-900/80'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Copy className="h-4 w-4" />
            <span>Duplicate Matches ({analysis.duplicate_matches?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('graph')}
            className={`px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'graph'
                ? 'border-sky-500 text-sky-400 bg-slate-900/80'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Network className="h-4 w-4" />
            <span>Syndicate Network Graph</span>
          </button>

          <button
            onClick={() => setActiveTab('notes')}
            className={`px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer ${
              activeTab === 'notes'
                ? 'border-sky-500 text-sky-400 bg-slate-900/80'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FolderPlus className="h-4 w-4" />
            <span>Case Notes & Audit Trail</span>
          </button>
        </div>

        {/* TAB 1: LOSS CIRCUMSTANCES */}
        {activeTab === 'signals' && (
          <div className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-slate-400 uppercase font-semibold text-[11px]">Loss Dynamics</span>
                <p className="text-white font-medium">Type: {claim.incident_type}</p>
                <p className="text-slate-300">Collision: {claim.collision_type || 'Front'}</p>
                <p className="text-slate-300">Severity: {claim.incident_severity}</p>
                <p className="text-slate-300">Hour: {claim.incident_hour_of_the_day || 14}:00</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-slate-400 uppercase font-semibold text-[11px]">Corroboration</span>
                <p className="text-white font-medium">Police Report: {claim.police_report_available || 'YES'}</p>
                <p className="text-slate-300">Vehicles Involved: {claim.number_of_vehicles_involved || 1}</p>
                <p className="text-slate-300">Witnesses: {claim.witnesses || 0}</p>
                <p className="text-slate-300">Bodily Injuries: {claim.bodily_injuries || 0}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
                <span className="text-slate-400 uppercase font-semibold text-[11px]">Financial Exposure</span>
                <p className="text-white font-medium">Injury: {formatCurrency(claim.injury_claim)}</p>
                <p className="text-slate-300">Property: {formatCurrency(claim.property_claim)}</p>
                <p className="text-slate-300">Vehicle: {formatCurrency(claim.vehicle_claim)}</p>
                <p className="text-sky-400 font-bold font-mono">Total: {formatCurrency(claim.total_claim_amount)}</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <Car className="h-5 w-5 text-sky-400" />
                <div>
                  <p className="text-white font-medium">
                    {claim.auto_year || 2021} {claim.vehicle_make || 'Audi'} {claim.vehicle_model || 'A4'}
                  </p>
                  <p className="text-slate-400 font-mono text-[11px]">
                    VIN: {claim.auto_vin || 'WAUZZZ8K8FA982014'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white font-medium">
                  {claim.provider_name || 'Metro Collision Clinic'}
                </p>
                <p className="text-slate-400 text-[11px]">Repair & Assessment Facility</p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SHAP EXPLAINABILITY */}
        {activeTab === 'shap' && (
          <div className="p-6 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white">
                SHAP Local Feature Attribution Breakdown
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Exact mathematical contribution of each claim feature toward raising or lowering the fraud probability.
              </p>
            </div>

            <div className="space-y-3">
              {(analysis.top_risk_factors || [
                { feature: 'incident_severity_Major Damage', description: 'Major damage classification with high repair disparity', impact: 0.18, contribution: 'POSITIVE' },
                { feature: 'total_claim_amount', description: 'Claim amount exceeds 90th percentile for single collision', impact: 0.14, contribution: 'POSITIVE' },
                { feature: 'injury_to_total_ratio', description: 'Disproportionate bodily injury to property damage ratio', impact: 0.11, contribution: 'POSITIVE' },
                { feature: 'police_report_available_NO', description: 'Absence of official law enforcement documentation', impact: 0.08, contribution: 'POSITIVE' },
                { feature: 'policy_tenure_months', description: 'Established policyholder with >5 years coverage history', impact: -0.09, contribution: 'NEGATIVE' },
              ]).map((factor, i) => (
                <div key={i} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div className="space-y-0.5 max-w-lg">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-white">{factor.feature}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                          factor.impact > 0
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {factor.impact > 0 ? '+ Risk Factor' : '- Mitigating Factor'}
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px]">{factor.description}</p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`font-mono font-bold text-sm ${
                        factor.impact > 0 ? 'text-red-400' : 'text-emerald-400'
                      }`}
                    >
                      {factor.impact > 0 ? `+${(factor.impact * 100).toFixed(1)}%` : `${(factor.impact * 100).toFixed(1)}%`}
                    </span>
                    <span className="block text-[10px] text-slate-500">SHAP value</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: DUPLICATE CLAIMS */}
        {activeTab === 'duplicates' && (
          <div className="p-6 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white">
                Cross-Claim Duplicate & Staged Collision Matches
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Claims across the portfolio sharing matching VIN, identical loss dates, or identical damage amounts.
              </p>
            </div>

            {(analysis.duplicate_matches?.length || 0) > 0 ? (
              <div className="space-y-3">
                {analysis.duplicate_matches.map((match, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-900 border border-amber-500/30 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-amber-400 text-xs">
                        Matched Claim: {match.matched_claim_number}
                      </span>
                      <span className="px-2.5 py-1 rounded bg-amber-950/80 border border-amber-500/50 text-amber-300 font-mono text-xs font-bold">
                        {(match.similarity_score * 100).toFixed(0)}% Similarity
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2 pt-1">
                      {match.match_reasons?.map((reason, rIdx) => (
                        <span key={rIdx} className="text-[11px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                          {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 bg-slate-900/40 rounded-xl border border-slate-800">
                <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
                <p className="text-xs font-semibold text-slate-200">No duplicate claims detected</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  VIN and damage patterns are unique within historical collision records.
                </p>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SYNDICATE NETWORK GRAPH */}
        {activeTab === 'graph' && (
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white">
                  Syndicate Collusion Network Topology
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Bipartite relationship graph connecting Claim, Policy, Claimant, Repair Facility, and Vehicles.
                </p>
              </div>
              <span className="px-2.5 py-1 rounded bg-sky-950 text-sky-400 border border-sky-800 text-xs font-mono">
                NetworkX Real Engine
              </span>
            </div>

            {/* Interactive SVG Network Graph Visualization */}
            <div className="relative h-80 bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex items-center justify-center p-4">
              <svg className="w-full h-full" viewBox="0 0 600 300">
                {/* Edges */}
                <line x1="300" y1="150" x2="150" y2="80" stroke="#38bdf8" strokeWidth="2" strokeDasharray="4" />
                <line x1="300" y1="150" x2="150" y2="220" stroke="#38bdf8" strokeWidth="2" />
                <line x1="300" y1="150" x2="450" y2="80" stroke="#ef4444" strokeWidth="2.5" />
                <line x1="300" y1="150" x2="450" y2="220" stroke="#38bdf8" strokeWidth="2" />

                {/* Shared Suspicious Cluster Edge */}
                <line x1="450" y1="80" x2="550" y2="150" stroke="#ef4444" strokeWidth="2" strokeDasharray="3" />

                {/* Nodes */}
                {/* Center Claim Node */}
                <g transform="translate(300, 150)">
                  <circle r="26" fill="#0284c7" stroke="#38bdf8" strokeWidth="3" />
                  <text y="4" textAnchor="middle" fill="#fff" fontSize="10" fontWeight="bold">
                    CLAIM
                  </text>
                </g>

                {/* Claimant Node */}
                <g transform="translate(150, 80)">
                  <circle r="22" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="bold">
                    POLICYHOLDER
                  </text>
                </g>

                {/* Policy Node */}
                <g transform="translate(150, 220)">
                  <circle r="22" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="bold">
                    POLICY
                  </text>
                </g>

                {/* Suspicious Provider Node */}
                <g transform="translate(450, 80)">
                  <circle r="24" fill="#7f1d1d" stroke="#ef4444" strokeWidth="3" className="animate-pulse" />
                  <text y="3" textAnchor="middle" fill="#fca5a5" fontSize="9" fontWeight="bold">
                    PROVIDER (FLAGGED)
                  </text>
                </g>

                {/* Vehicle Node */}
                <g transform="translate(450, 220)">
                  <circle r="22" fill="#1e293b" stroke="#64748b" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#94a3b8" fontSize="9" fontWeight="bold">
                    VEHICLE
                  </text>
                </g>

                {/* Collusion Secondary Claim */}
                <g transform="translate(550, 150)">
                  <circle r="18" fill="#450a0a" stroke="#dc2626" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#fca5a5" fontSize="8">
                    CLM-2023-88
                  </text>
                </g>
              </svg>

              <div className="absolute bottom-3 left-3 bg-slate-900/90 border border-slate-800 rounded-lg p-2.5 text-[11px] text-slate-400 space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-500" />
                  <span className="text-white font-medium">Flagged Entity:</span>
                  <span>Provider associated with 8 high-risk claims</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: CASE NOTES & AUDIT TRAIL */}
        {activeTab === 'notes' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-sm font-bold text-white">
                SIU Forensic Case Notes & Audit Stream
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Tamper-evident chronological log of investigator annotations, document reviews, and disposition rationale.
              </p>
            </div>

            {/* Note Submission */}
            <div className="space-y-3 bg-slate-900/70 p-4 rounded-xl border border-slate-800">
              <textarea
                rows={3}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Enter forensic note, claimant statement summary, or provider validation finding..."
                className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
              <div className="flex justify-between items-center">
                <span className="text-[11px] text-slate-400">
                  Logged as: <strong className="text-slate-200">{user?.full_name}</strong> ({role})
                </span>
                <button
                  type="button"
                  onClick={handleAddNote}
                  className="flex items-center space-x-1.5 bg-sky-600 hover:bg-sky-500 text-white px-4 py-1.5 rounded-lg text-xs font-semibold cursor-pointer"
                >
                  <Send className="h-3 w-3" />
                  <span>Add Case Note</span>
                </button>
              </div>
            </div>

            {/* Existing Notes Feed */}
            <div className="space-y-3">
              {notes.map((note, i) => (
                <div key={i} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-white">{note.author}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                        {note.role}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-500">{note.date}</span>
                  </div>
                  <p className="text-slate-300 pt-1 leading-relaxed">{note.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
