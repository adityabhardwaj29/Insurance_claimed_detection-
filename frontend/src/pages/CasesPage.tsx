import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FolderGit2,
  AlertTriangle,
  UserCheck,
  Search,
  Clock,
  CheckCircle2,
  FileText,
  DollarSign
} from 'lucide-react';
import { api } from '../services/api';
import { InvestigationCase } from '../types';
import { RiskBadge } from '../components/common/RiskBadge';

export const CasesPage: React.FC = () => {
  const navigate = useNavigate();
  const [cases, setCases] = useState<InvestigationCase[]>([]);
  const [activeTab, setActiveTab] = useState<'ALL' | 'OPEN' | 'IN_PROGRESS' | 'CLOSED'>('ALL');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const data = await api.getCases();
        setCases(data);
      } catch (err) {
        console.error('Error fetching cases', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCases();
  }, []);

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const filteredCases = cases.filter((c) => {
    if (activeTab === 'ALL') return true;
    if (activeTab === 'OPEN') return c.status === 'OPEN';
    if (activeTab === 'IN_PROGRESS') return c.status === 'IN_PROGRESS' || c.status === 'EVIDENCE_COLLECTION';
    if (activeTab === 'CLOSED') return c.status === 'RESOLVED_FRAUD' || c.status === 'RESOLVED_LEGITIMATE' || c.status === 'CLOSED';
    return true;
  });

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Special Investigation Unit (SIU) Case Management
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Active forensic investigation dockets, evidence collection repositories, and investigator assignment queues.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-mono">
            Active Cases: <strong className="text-amber-400">42</strong>
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800 text-xs font-semibold space-x-2">
        {(['ALL', 'OPEN', 'IN_PROGRESS', 'CLOSED'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 rounded-t-lg transition-all cursor-pointer ${
              activeTab === tab
                ? 'bg-slate-900 border-t border-x border-slate-800 text-sky-400 font-bold'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {tab.replace('_', ' ')}
          </button>
        ))}
      </div>

      {/* Cases Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredCases.map((cs) => (
          <div
            key={cs.id}
            onClick={() => navigate(`/claims/${cs.claim_id}`)}
            className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all cursor-pointer group flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-sky-400">
                  {cs.case_number}
                </span>
                <RiskBadge score={cs.risk_score} level={cs.priority} size="sm" />
              </div>

              <div>
                <h3 className="text-sm font-bold text-white group-hover:text-sky-400 transition-colors">
                  Claim: {cs.claim_number}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Claimant: <strong className="text-slate-200">{cs.claimant_name || 'Policyholder'}</strong>
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-slate-400">Exposure:</span>
                  <span className="font-mono font-bold text-white">
                    {formatCurrency(cs.total_claim_amount)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Investigator:</span>
                  <span className="text-slate-200 font-medium">
                    {cs.investigator_name || 'Unassigned (Triage)'}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
              <div className="flex items-center space-x-1">
                <Clock className="h-3.5 w-3.5 text-slate-500" />
                <span>Opened {cs.created_at?.split('T')[0] || 'Recently'}</span>
              </div>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                {cs.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
