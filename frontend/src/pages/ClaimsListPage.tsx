import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Filter,
  FilePlus,
  ArrowUpDown,
  Download,
  ShieldAlert,
  Calendar,
  DollarSign
} from 'lucide-react';
import { api } from '../services/api';
import { Claim } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

export const ClaimsListPage: React.FC = () => {
  const navigate = useNavigate();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [filteredClaims, setFilteredClaims] = useState<Claim[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchClaims = async () => {
      try {
        const data = await api.getClaims({ limit: 100 });
        setClaims(data);
        setFilteredClaims(data);
      } catch (err) {
        console.error('Error fetching claims list', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchClaims();
  }, []);

  // Filter effect
  useEffect(() => {
    let result = [...claims];

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (c) =>
          c.claim_number.toLowerCase().includes(q) ||
          c.claimant_name?.toLowerCase().includes(q) ||
          c.policy_number?.toLowerCase().includes(q)
      );
    }

    if (statusFilter !== 'ALL') {
      result = result.filter((c) => c.status === statusFilter);
    }

    if (riskFilter !== 'ALL') {
      result = result.filter((c) => c.risk_level === riskFilter);
    }

    setFilteredClaims(result);
  }, [searchQuery, statusFilter, riskFilter, claims]);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Title & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Claims Queue & Risk Triage
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Browse, search, and audit all insurance claims scored through the 4-pillar fraud detection architecture.
          </p>
        </div>
        <button
          onClick={() => navigate('/claims/new')}
          className="flex items-center space-x-2 bg-sky-600 hover:bg-sky-500 text-white px-4 py-2.5 rounded-xl font-semibold text-xs shadow-lg shadow-sky-600/20 transition-all cursor-pointer"
        >
          <FilePlus className="h-4 w-4" />
          <span>New Claim Intake</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by Claim ID, policyholder name, or policy number..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Status Select */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Status:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="ANALYZED">Analyzed</option>
              <option value="ESCALATED_SIU">Escalated SIU</option>
              <option value="APPROVED">Approved</option>
              <option value="REJECTED">Rejected</option>
            </select>
          </div>

          {/* Risk Select */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Risk Tier:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-sky-500"
            >
              <option value="ALL">All Tiers</option>
              <option value="LOW">Low Risk (&lt;25%)</option>
              <option value="MEDIUM">Medium Risk (25-50%)</option>
              <option value="HIGH">High Risk (50-70%)</option>
              <option value="CRITICAL">Critical (&gt;70%)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Claims Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-5 py-3.5">Claim ID</th>
                <th className="px-5 py-3.5">Claimant & Policy</th>
                <th className="px-5 py-3.5">Incident Date</th>
                <th className="px-5 py-3.5">Claim Type & Severity</th>
                <th className="px-5 py-3.5">Claim Amount</th>
                <th className="px-5 py-3.5">Risk Score</th>
                <th className="px-5 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {filteredClaims.length > 0 ? (
                filteredClaims.map((c) => (
                  <tr
                    key={c.id}
                    onClick={() => navigate(`/claims/${c.id}`)}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                  >
                    <td className="px-5 py-4 font-mono text-sky-400 font-bold">
                      {c.claim_number}
                    </td>
                    <td className="px-5 py-4">
                      <div className="text-white font-semibold">{c.claimant_name || 'Policyholder'}</div>
                      <div className="text-slate-400 font-mono text-[11px]">
                        {c.policy_number || 'POL-521948'}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-slate-300">
                      {c.incident_date}
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-slate-200 block">{c.incident_type}</span>
                      <span className="text-slate-400 text-[11px]">{c.incident_severity}</span>
                    </td>
                    <td className="px-5 py-4 font-mono font-bold text-white">
                      {formatCurrency(c.total_claim_amount)}
                    </td>
                    <td className="px-5 py-4">
                      <RiskBadge
                        score={c.risk_score}
                        level={c.risk_level || 'MEDIUM'}
                        size="sm"
                      />
                    </td>
                    <td className="px-5 py-4">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[11px]">
                        {c.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/claims/${c.id}`);
                        }}
                        className="text-xs bg-slate-800 hover:bg-sky-600 text-slate-200 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 transition-all font-semibold"
                      >
                        Inspect 360°
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-10 text-slate-500">
                    {isLoading ? 'Loading claims from database...' : 'No claims found matching your filter criteria.'}
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
