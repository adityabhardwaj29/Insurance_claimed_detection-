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

  const matchesTab = (c: InvestigationCase, tab: string) => {
    const s = (c.status || '').toUpperCase();
    if (tab === 'ALL') return true;
    if (tab === 'OPEN') return s === 'OPEN' || s === 'NEW';
    if (tab === 'IN_PROGRESS') return s === 'IN_PROGRESS' || s === 'UNDER_REVIEW' || s === 'ESCALATED' || s === 'EVIDENCE_COLLECTION';
    if (tab === 'CLOSED') return s === 'CLOSED' || s === 'RESOLVED' || s === 'FALSE_POSITIVE' || s.includes('RESOLVED');
    return true;
  };

  const filteredCases = cases.filter((c) => matchesTab(c, activeTab));

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center space-x-2.5">
            <FolderGit2 className="h-6 w-6 text-blue-600" />
            <span>Special Investigation Unit (SIU) Case Management</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Active forensic investigation dockets, evidence collection repositories, and investigator assignment queues.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800">
            Active Dockets: <strong className="font-mono text-blue-900 font-bold">{cases.length}</strong>
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 text-xs font-medium space-x-1 overflow-x-auto">
        {(['ALL', 'OPEN', 'IN_PROGRESS', 'CLOSED'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2.5 -mb-px rounded-t-lg transition-all cursor-pointer font-semibold whitespace-nowrap shrink-0 ${
              activeTab === tab
                ? 'bg-white border-t-2 border-x border-b-0 border-blue-600 text-blue-600 shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
            }`}
          >
            {tab === 'OPEN' ? 'NEW / TRIAGE' : tab === 'IN_PROGRESS' ? 'UNDER INQUIRY' : tab.replace('_', ' ')}
            <span className="ml-1.5 px-1.5 py-0.5 rounded-full text-[10px] bg-slate-100 text-slate-600 font-mono font-bold">
              {tab === 'ALL'
                ? cases.length
                : cases.filter((c) => matchesTab(c, tab)).length}
            </span>
          </button>
        ))}
      </div>

      {/* Cases Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {isLoading ? (
          <div className="col-span-full py-16 text-center text-slate-500 text-sm">
            Loading investigation dockets...
          </div>
        ) : filteredCases.length === 0 ? (
          <div className="col-span-full py-16 text-center bg-white rounded-xl border border-dashed border-slate-300">
            <FolderGit2 className="h-10 w-10 text-slate-400 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-slate-800">No cases found in this view</h3>
            <p className="text-xs text-slate-500 mt-1">Switch to ALL or NEW / TRIAGE to inspect assigned dockets.</p>
          </div>
        ) : (
          filteredCases.map((cs) => (
            <div
              key={cs.id}
              onClick={() => navigate(`/claims/${cs.claim_id}`)}
              className="bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                    {cs.case_number}
                  </span>
                  <RiskBadge score={cs.risk_score} level={cs.priority} size="sm" />
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    Claim: {cs.claim_number}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Claimant: <strong className="text-slate-800">{cs.claimant_name || 'Policyholder'}</strong>
                  </p>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 text-xs space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Exposure:</span>
                    <span className="font-mono font-bold text-slate-900">
                      {formatCurrency(cs.total_claim_amount)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-500">Investigator:</span>
                    <span className="text-slate-700 font-medium">
                      {cs.investigator_name || 'Unassigned (Triage)'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <div className="flex items-center space-x-1.5">
                  <Clock className="h-3.5 w-3.5 text-slate-400" />
                  <span>Opened {cs.created_at?.split('T')[0] || 'Recently'}</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium border border-slate-200">
                  {cs.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

