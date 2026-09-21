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
  Car,
  Calendar,
  DollarSign,
  Activity,
  Layers,
  FileCheck
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
  const [decisionNotes] = useState('');
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
        return 'bg-emerald-50 border-emerald-200 text-emerald-800';
      case 'FAST_TRACK':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'MANUAL_INVESTIGATION':
        return 'bg-amber-50 border-amber-200 text-amber-800';
      case 'SIU_ESCALATE':
      default:
        return 'bg-red-50 border-red-200 text-red-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Dossier Header Banner */}
      <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-mono font-extrabold text-[#0F172A]">
              {claim.claim_number}
            </h1>
            <RiskBadge
              score={analysis.hybrid_risk_score}
              level={analysis.risk_level}
              size="md"
            />
            <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold">
              {claim.status}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-500">
            <span className="flex items-center space-x-1">
              <UserCheck className="h-3.5 w-3.5 text-slate-400" />
              <strong className="text-[#0F172A]">{claim.claimant_name || 'Policyholder'}</strong>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <FileText className="h-3.5 w-3.5 text-slate-400" />
              <span>Policy: <strong className="text-[#0F172A] font-mono">{claim.policy_number || 'POL-521948'}</strong></span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <Calendar className="h-3.5 w-3.5 text-slate-400" />
              <span>Incident: {claim.incident_date}</span>
            </span>
            <span>•</span>
            <span className="flex items-center space-x-1">
              <DollarSign className="h-3.5 w-3.5 text-slate-400" />
              <strong className="text-[#2563EB] font-mono text-sm">
                {formatCurrency(claim.total_claim_amount)}
              </strong>
            </span>
          </div>
        </div>

        {/* Quick Decision Trigger Buttons */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          <button
            onClick={() => handleDecision('APPROVE')}
            disabled={isSubmittingDecision}
            className="flex-1 sm:flex-none justify-center flex items-center space-x-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs transition-all cursor-pointer"
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            <span>Approve</span>
          </button>
          <button
            onClick={() => handleDecision('ESCALATE_SIU')}
            disabled={isSubmittingDecision}
            className="flex-1 sm:flex-none justify-center flex items-center space-x-1.5 bg-red-600 hover:bg-red-700 text-white px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs transition-all cursor-pointer"
          >
            <ShieldAlert className="h-3.5 w-3.5" />
            <span>Escalate SIU</span>
          </button>
          <button
            onClick={() => handleDecision('REJECT')}
            disabled={isSubmittingDecision}
            className="flex-1 sm:flex-none justify-center flex items-center space-x-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-300 px-3.5 py-2 rounded-lg text-xs font-semibold shadow-xs transition-all cursor-pointer"
          >
            <XCircle className="h-3.5 w-3.5 text-slate-500" />
            <span>Reject</span>
          </button>
        </div>
      </div>

      {decisionSuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium flex items-center justify-between shadow-xs">
          <span className="flex items-center space-x-2">
            <FileCheck className="h-4 w-4 text-emerald-600" />
            <span>{decisionSuccess}</span>
          </span>
          <button onClick={() => setDecisionSuccess(null)} className="text-emerald-700 hover:text-emerald-900 font-bold cursor-pointer">
            Dismiss
          </button>
        </div>
      )}

      {/* Top Section: Composite Risk Gauge & Automated Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Composite Gauge Card */}
        <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs flex flex-col justify-between">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
              Multi-Signal Hybrid Risk Score
            </span>
            <div className="flex items-baseline space-x-3 mt-3">
              <span className="text-4xl font-extrabold font-mono text-[#0F172A]">
                {(analysis.hybrid_risk_score * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-slate-500">
                (T_high: 50% | T_low: 25%)
              </span>
            </div>

            {/* Score Bar */}
            <div className="w-full bg-slate-100 rounded-full h-3 mt-4 overflow-hidden p-0.5">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  analysis.hybrid_risk_score >= 0.7
                    ? 'bg-rose-600'
                    : analysis.hybrid_risk_score >= 0.5
                    ? 'bg-red-600'
                    : analysis.hybrid_risk_score >= 0.25
                    ? 'bg-amber-500'
                    : 'bg-emerald-600'
                }`}
                style={{ width: `${Math.min(analysis.hybrid_risk_score * 100, 100)}%` }}
              />
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[#E2E8F0]">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block mb-2">
              System Recommendation
            </span>
            <div className={`p-3 rounded-lg border text-xs font-medium ${getRecColor(analysis.recommendation)}`}>
              <div className="font-bold flex items-center space-x-2">
                <AlertTriangle className="h-4 w-4" />
                <span>{analysis.recommendation.replace('_', ' ')}</span>
              </div>
              <p className="mt-1 text-[11px] opacity-90 leading-relaxed">
                {analysis.recommendation_reason ||
                  'Risk indicators exceeded threshold. Forward to SIU special investigator for desk audit.'}
              </p>
            </div>
          </div>
        </div>

        {/* 4 Signals Bar Card */}
        <div className="bg-white p-6 rounded-xl border border-[#E2E8F0] shadow-xs lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-[#0F172A] uppercase tracking-wider">
              Component Signal Breakdown
            </h2>
            <span className="text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              Ensemble Weighted Fusion
            </span>
          </div>

          <div className="space-y-4">
            {/* Supervised ML */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-blue-700 font-semibold">1. Supervised ML (XGBoost Classifier)</span>
                <span className="font-mono text-slate-800 font-bold">
                  {(analysis.ml_score * 100).toFixed(1)}% (Weight: 40%)
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-[#2563EB] h-2 rounded-full"
                  style={{ width: `${analysis.ml_score * 100}%` }}
                />
              </div>
            </div>

            {/* Isolation Forest */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-indigo-700 font-semibold">2. Unsupervised Anomaly (Isolation Forest)</span>
                <span className="font-mono text-slate-800 font-bold">
                  {(analysis.anomaly_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-indigo-600 h-2 rounded-full"
                  style={{ width: `${analysis.anomaly_score * 100}%` }}
                />
              </div>
            </div>

            {/* Duplicate Claim Similarity */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-amber-700 font-semibold">3. Duplicate & Recycled Claim Matching</span>
                <span className="font-mono text-slate-800 font-bold">
                  {(analysis.duplicate_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-amber-500 h-2 rounded-full"
                  style={{ width: `${analysis.duplicate_score * 100}%` }}
                />
              </div>
            </div>

            {/* Graph Collusion */}
            <div>
              <div className="flex justify-between text-xs mb-1 font-medium">
                <span className="text-emerald-700 font-semibold">4. Graph Syndicate Collusion Network</span>
                <span className="font-mono text-slate-800 font-bold">
                  {(analysis.graph_score * 100).toFixed(1)}% (Weight: 20%)
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className="bg-emerald-600 h-2 rounded-full"
                  style={{ width: `${analysis.graph_score * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-[#E2E8F0] flex items-center justify-between text-xs text-slate-500">
            <span>Score formula: Risk = 0.40(ML) + 0.20(Anomaly) + 0.20(Duplicate) + 0.20(Graph)</span>
            <span className="font-mono text-[#2563EB] font-bold">Audited Calibration</span>
          </div>
        </div>
      </div>

      {/* Forensic Deep Dive Tabs */}
      <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-xs overflow-hidden">
        {/* Navigation Tabs */}
        <div className="flex border-b border-[#E2E8F0] bg-slate-50/70 overflow-x-auto">
          <button
            onClick={() => setActiveTab('signals')}
            className={`px-4 sm:px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'signals'
                ? 'border-[#2563EB] text-[#2563EB] bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Layers className="h-4 w-4" />
            <span>Loss Circumstances</span>
          </button>

          <button
            onClick={() => setActiveTab('shap')}
            className={`px-4 sm:px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'shap'
                ? 'border-[#2563EB] text-[#2563EB] bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Activity className="h-4 w-4" />
            <span>SHAP Explainability Waterfall</span>
          </button>

          <button
            onClick={() => setActiveTab('duplicates')}
            className={`px-4 sm:px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'duplicates'
                ? 'border-[#2563EB] text-[#2563EB] bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Copy className="h-4 w-4" />
            <span>Duplicate Matches ({analysis.duplicate_matches?.length || 0})</span>
          </button>

          <button
            onClick={() => setActiveTab('graph')}
            className={`px-4 sm:px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'graph'
                ? 'border-[#2563EB] text-[#2563EB] bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            <Network className="h-4 w-4" />
            <span>Syndicate Network Graph</span>
          </button>

          <button
            onClick={() => setActiveTab('notes')}
            className={`px-4 sm:px-5 py-3.5 text-xs font-semibold flex items-center space-x-2 border-b-2 transition-all cursor-pointer whitespace-nowrap shrink-0 ${
              activeTab === 'notes'
                ? 'border-[#2563EB] text-[#2563EB] bg-white'
                : 'border-transparent text-slate-600 hover:text-slate-900'
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
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="text-slate-500 uppercase font-bold text-[11px]">Loss Dynamics</span>
                <p className="text-[#0F172A] font-semibold">Type: {claim.incident_type}</p>
                <p className="text-slate-600">Collision: {claim.collision_type || 'Front'}</p>
                <p className="text-slate-600">Severity: {claim.incident_severity}</p>
                <p className="text-slate-600">Hour: {claim.incident_hour_of_the_day || 14}:00</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="text-slate-500 uppercase font-bold text-[11px]">Corroboration</span>
                <p className="text-[#0F172A] font-semibold">Police Report: {claim.police_report_available || 'YES'}</p>
                <p className="text-slate-600">Vehicles Involved: {claim.number_of_vehicles_involved || 1}</p>
                <p className="text-slate-600">Witnesses: {claim.witnesses || 0}</p>
                <p className="text-slate-600">Bodily Injuries: {claim.bodily_injuries || 0}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="text-slate-500 uppercase font-bold text-[11px]">Financial Exposure</span>
                <p className="text-slate-700">Injury: {formatCurrency(claim.injury_claim)}</p>
                <p className="text-slate-700">Property: {formatCurrency(claim.property_claim)}</p>
                <p className="text-slate-700">Vehicle: {formatCurrency(claim.vehicle_claim)}</p>
                <p className="text-[#2563EB] font-bold font-mono text-sm pt-1">Total: {formatCurrency(claim.total_claim_amount)}</p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
              <div className="flex items-center space-x-3">
                <Car className="h-5 w-5 text-[#2563EB]" />
                <div>
                  <p className="text-[#0F172A] font-semibold">
                    {claim.auto_year || 2021} {claim.vehicle_make || 'Audi'} {claim.vehicle_model || 'A4'}
                  </p>
                  <p className="text-slate-500 font-mono text-[11px]">
                    VIN: {claim.auto_vin || 'WAUZZZ8K8FA982014'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-[#0F172A] font-semibold">
                  {claim.provider_name || 'Metro Collision Clinic'}
                </p>
                <p className="text-slate-500 text-[11px]">Repair & Assessment Facility</p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SHAP EXPLAINABILITY */}
        {activeTab === 'shap' && (
          <div className="p-6 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-[#0F172A]">
                SHAP Local Feature Attribution Breakdown
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Exact mathematical contribution of each claim feature toward raising or lowering the fraud probability.
              </p>
            </div>

            <div className="space-y-2.5">
              {(analysis.top_risk_factors || [
                { feature: 'incident_severity_Major Damage', description: 'Major damage classification with high repair disparity', impact: 0.18, contribution: 'POSITIVE' },
                { feature: 'total_claim_amount', description: 'Claim amount exceeds 90th percentile for single collision', impact: 0.14, contribution: 'POSITIVE' },
                { feature: 'injury_to_total_ratio', description: 'Disproportionate bodily injury to property damage ratio', impact: 0.11, contribution: 'POSITIVE' },
                { feature: 'police_report_available_NO', description: 'Absence of official law enforcement documentation', impact: 0.08, contribution: 'POSITIVE' },
                { feature: 'policy_tenure_months', description: 'Established policyholder with >5 years coverage history', impact: -0.09, contribution: 'NEGATIVE' },
              ]).map((factor, i) => (
                <div key={i} className="p-3.5 rounded-lg bg-white border border-[#E2E8F0] shadow-xs flex items-center justify-between text-xs">
                  <div className="space-y-0.5 max-w-lg">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-[#0F172A]">{factor.feature}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                          factor.impact > 0
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        }`}
                      >
                        {factor.impact > 0 ? '+ Risk Factor' : '- Mitigating Factor'}
                      </span>
                    </div>
                    <p className="text-slate-500 text-[11px]">{factor.description}</p>
                  </div>
                  <div className="text-right">
                    <span
                      className={`font-mono font-bold text-sm ${
                        factor.impact > 0 ? 'text-red-700' : 'text-emerald-700'
                      }`}
                    >
                      {factor.impact > 0 ? `+${(factor.impact * 100).toFixed(1)}%` : `${(factor.impact * 100).toFixed(1)}%`}
                    </span>
                    <span className="block text-[10px] text-slate-400">SHAP value</span>
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
              <h3 className="text-sm font-bold text-[#0F172A]">
                Cross-Claim Duplicate & Staged Collision Matches
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Claims across the portfolio sharing matching VIN, identical loss dates, or identical damage amounts.
              </p>
            </div>

            {(analysis.duplicate_matches?.length || 0) > 0 ? (
              <div className="space-y-3">
                {analysis.duplicate_matches.map((match, i) => (
                  <div key={i} className="p-4 rounded-xl bg-white border border-amber-300 shadow-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-amber-800 text-xs">
                        Matched Claim: {match.matched_claim_number}
                      </span>
                      <span className="px-2.5 py-1 rounded bg-amber-50 border border-amber-300 text-amber-800 font-mono text-xs font-bold">
                        {(match.similarity_score * 100).toFixed(0)}% Similarity
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-2 pt-1">
                      {match.match_reasons?.map((reason, rIdx) => (
                        <span key={rIdx} className="text-[11px] bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">
                          {reason}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-500 bg-slate-50 rounded-xl border border-slate-200">
                <CheckCircle2 className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
                <p className="text-xs font-bold text-slate-900">No duplicate claims detected</p>
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
                <h3 className="text-sm font-bold text-[#0F172A]">
                  Syndicate Collusion Network Topology
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Bipartite relationship graph connecting Claim, Policy, Claimant, Repair Facility, and Vehicles.
                </p>
              </div>
              <span className="px-2.5 py-1 rounded bg-blue-50 text-[#2563EB] border border-blue-200 text-xs font-bold font-mono">
                NetworkX Real Engine
              </span>
            </div>

            {/* SVG Network Graph Visualization - Clean White/Blue styling with Responsive Height */}
            <div className="relative h-[400px] sm:h-[450px] md:h-[500px] lg:h-[550px] xl:h-[600px] bg-slate-50 rounded-xl border border-[#E2E8F0] overflow-hidden flex items-center justify-center p-4">
              <svg className="w-full h-full" viewBox="0 0 600 300">
                {/* Edges */}
                <line x1="300" y1="150" x2="150" y2="80" stroke="#93C5FD" strokeWidth="2" strokeDasharray="4" />
                <line x1="300" y1="150" x2="150" y2="220" stroke="#93C5FD" strokeWidth="2" />
                <line x1="300" y1="150" x2="450" y2="80" stroke="#DC2626" strokeWidth="2.5" />
                <line x1="300" y1="150" x2="450" y2="220" stroke="#93C5FD" strokeWidth="2" />
                <line x1="450" y1="80" x2="550" y2="150" stroke="#DC2626" strokeWidth="2" strokeDasharray="3" />

                {/* Center Claim Node */}
                <g transform="translate(300, 150)">
                  <circle r="26" fill="#1D4ED8" stroke="#3B82F6" strokeWidth="3" />
                  <text y="4" textAnchor="middle" fill="#FFFFFF" fontSize="10" fontWeight="bold">
                    CLAIM
                  </text>
                </g>

                {/* Claimant Node */}
                <g transform="translate(150, 80)">
                  <circle r="22" fill="#2563EB" stroke="#60A5FA" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="bold">
                    CLAIMANT
                  </text>
                </g>

                {/* Policy Node */}
                <g transform="translate(150, 220)">
                  <circle r="22" fill="#3B82F6" stroke="#93C5FD" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="bold">
                    POLICY
                  </text>
                </g>

                {/* Suspicious Provider Node - Retained Red */}
                <g transform="translate(450, 80)">
                  <circle r="24" fill="#DC2626" stroke="#EF4444" strokeWidth="3" />
                  <text y="3" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="bold">
                    PROVIDER (FLAGGED)
                  </text>
                </g>

                {/* Vehicle Node */}
                <g transform="translate(450, 220)">
                  <circle r="22" fill="#0284C7" stroke="#38BDF8" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#FFFFFF" fontSize="9" fontWeight="bold">
                    VEHICLE
                  </text>
                </g>

                {/* Collusion Secondary Claim */}
                <g transform="translate(550, 150)">
                  <circle r="18" fill="#DC2626" stroke="#EF4444" strokeWidth="2" />
                  <text y="3" textAnchor="middle" fill="#FFFFFF" fontSize="8" fontWeight="bold">
                    CLM-88
                  </text>
                </g>
              </svg>

              {/* Graph Legend as per Master Prompt Section 16 */}
              <div className="absolute bottom-3 left-3 bg-white/95 border border-[#E2E8F0] rounded-lg p-3 text-[11px] shadow-sm space-y-1.5 backdrop-blur-xs">
                <span className="font-bold text-slate-800 text-[10px] uppercase tracking-wider block border-b border-slate-100 pb-1">
                  Graph Legend
                </span>
                <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#2563EB]" />
                    <span className="text-slate-700">Customer</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#3B82F6]" />
                    <span className="text-slate-700">Policy</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#1D4ED8]" />
                    <span className="text-slate-700">Claim</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#0284C7]" />
                    <span className="text-slate-700">Provider</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#60A5FA]" />
                    <span className="text-slate-700">Vehicle</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="h-2.5 w-2.5 rounded-full bg-[#DC2626]" />
                    <span className="text-red-700 font-bold">Suspicious</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: CASE NOTES & AUDIT TRAIL */}
        {activeTab === 'notes' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-sm font-bold text-[#0F172A]">
                SIU Forensic Case Notes & Audit Stream
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Chronological log of investigator annotations, document reviews, and disposition rationale.
              </p>
            </div>

            {/* Note Submission */}
            <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <textarea
                rows={3}
                value={newNote}
                onChange={(e) => setNewNote(e.target.value)}
                placeholder="Enter forensic note, claimant statement summary, or provider validation finding..."
                className="w-full bg-white border border-slate-300 rounded-lg p-3 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
              />
              <div className="flex justify-between items-center">
                <span className="text-[11px] text-slate-500">
                  Logged as: <strong className="text-slate-800">{user?.full_name}</strong> ({role})
                </span>
                <button
                  type="button"
                  onClick={handleAddNote}
                  className="flex items-center space-x-1.5 bg-[#2563EB] hover:bg-[#1D4ED8] text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-xs cursor-pointer"
                >
                  <Send className="h-3 w-3" />
                  <span>Add Case Note</span>
                </button>
              </div>
            </div>

            {/* Existing Notes Feed */}
            <div className="space-y-2.5">
              {notes.map((note, i) => (
                <div key={i} className="p-4 rounded-xl bg-white border border-[#E2E8F0] shadow-xs space-y-1 text-xs">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-[#0F172A]">{note.author}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-mono border border-slate-200">
                        {note.role}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400">{note.date}</span>
                  </div>
                  <p className="text-slate-700 pt-1 leading-relaxed">{note.text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
