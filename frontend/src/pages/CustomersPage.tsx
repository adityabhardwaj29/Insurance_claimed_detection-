import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  UserCheck,
  Shield,
  FileText,
  Phone,
  Mail,
  MapPin,
  X,
  ExternalLink,
  PlusCircle,
  AlertTriangle,
  Car,
  Calendar,
  DollarSign,
  Activity,
  CheckCircle2,
  Clock,
  Briefcase
} from 'lucide-react';
import { api } from '../services/api';
import { Customer, Customer360 } from '../types';

export const CustomersPage: React.FC = () => {
  const navigate = useNavigate();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [customer360, setCustomer360] = useState<Customer360 | null>(null);
  const [isLoading360, setIsLoading360] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'policies' | 'claims' | 'vehicles' | 'risk'>('overview');

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const data = await api.getCustomers();
        setCustomers(data);
      } catch (err) {
        console.error('Error fetching customers', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  const handleOpen360 = async (customerId: string) => {
    setSelectedCustomerId(customerId);
    setIsLoading360(true);
    setActiveTab('overview');
    try {
      const data = await api.getCustomer360(customerId);
      setCustomer360(data);
    } catch (err) {
      console.error('Failed to load Customer 360 dossier', err);
    } finally {
      setIsLoading360(false);
    }
  };

  const handleClose360 = () => {
    setSelectedCustomerId(null);
    setCustomer360(null);
  };

  const filtered = customers.filter(
    (c) =>
      (c?.first_name || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (c?.last_name || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (c?.customer_number || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (c?.city || '').toLowerCase().includes((search || '').toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center space-x-2.5">
            <UserCheck className="h-6 w-6 text-blue-600" />
            <span>Customer 360 & Policyholder Directory</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Master policyholder profiles with unified claim history, active underwriting policies, and cumulative risk tiering. Click any card to inspect full 360° dossier.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800">
            Total Insureds: <strong className="font-mono text-blue-900 font-bold">{customers.length}</strong>
          </span>
          <button
            onClick={() => navigate('/claims/new')}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg shadow-sm transition-colors"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            <span>New Claim</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search policyholders by name, ID, or city..."
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-all"
          />
        </div>
      </div>

      {/* Grid of Policyholder Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {filtered.length > 0 ? (
          filtered.map((c, idx) => (
            <div
              key={c.customer_number || c.id || `cust-${idx}`}
              onClick={() => handleOpen360(c.customer_number || c.id)}
              className="group bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all cursor-pointer space-y-4 relative overflow-hidden"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleOpen360(c.customer_number || c.id);
                }
              }}
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2.5 py-1 rounded border border-blue-100 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                  {c.customer_number}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-semibold">
                  {c.risk_tier || 'Verified Client'}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors flex items-center justify-between">
                  <span>{c.first_name} {c.last_name}</span>
                  <ExternalLink className="h-4 w-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
                </h3>
                <p className="text-xs text-slate-500 font-mono mt-0.5">
                  ID: {c.national_id || c.customer_number}
                </p>
              </div>

              <div className="space-y-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100 group-hover:bg-slate-50/80">
                <div className="flex items-center space-x-2">
                  <Mail className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{c.email || `${(c.first_name || 'user').toLowerCase()}@insurance.com`}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Phone className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span>{c.phone || '+1 (555) 019-2834'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span>{c.city || 'New York'}, NY</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
                <span className="text-blue-600 font-medium group-hover:underline">View 360° Profile &rarr;</span>
                <span className="text-[11px] text-slate-400">Click to expand</span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 text-center py-12 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center space-y-2">
                <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                <span>Loading policyholder records...</span>
              </div>
            ) : (
              'No policyholders found matching your search.'
            )}
          </div>
        )}
      </div>

      {/* Customer 360 Modal / Drawer */}
      {selectedCustomerId && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-3 sm:p-6 animate-fadeIn">
          <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[90vh]">
            {/* Modal Header */}
            <div className="bg-slate-900 text-white p-5 sm:p-6 flex items-start justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-600/30 border border-blue-500/40 rounded-xl">
                  <UserCheck className="h-7 w-7 text-blue-400" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h2 className="text-xl font-bold tracking-tight text-white">
                      {customer360?.customer?.name || 'Customer 360 Profile'}
                    </h2>
                    <span className="font-mono text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      {selectedCustomerId}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Unified Insurance Identity &bull; {customer360?.customer?.city || 'New York'} &bull; {customer360?.customer?.occupation || 'Employed'}
                  </p>
                </div>
              </div>
              <button
                onClick={handleClose360}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Quick KPI Bar */}
            {customer360 && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-100 p-3 border-b border-slate-200 text-xs">
                <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                  <div className="text-slate-400">Total Claims</div>
                  <div className="text-base font-bold text-slate-900 font-mono mt-0.5">
                    {customer360.total_claims_count}
                  </div>
                </div>
                <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                  <div className="text-slate-400">Total Claim Amount</div>
                  <div className="text-base font-bold text-slate-900 font-mono mt-0.5">
                    ${Number(customer360.total_claim_amount || 0).toLocaleString()}
                  </div>
                </div>
                <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                  <div className="text-slate-400">Active Policies</div>
                  <div className="text-base font-bold text-blue-600 font-mono mt-0.5">
                    {customer360.policies?.length || 0}
                  </div>
                </div>
                <div className="bg-white p-2.5 rounded-lg border border-slate-200">
                  <div className="text-slate-400">Fraud / Risk Alerts</div>
                  <div className={`text-base font-bold font-mono mt-0.5 ${customer360.fraud_alert_count > 0 ? 'text-red-600' : 'text-emerald-600'}`}>
                    {customer360.fraud_alert_count} Alert{customer360.fraud_alert_count === 1 ? '' : 's'}
                  </div>
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="flex border-b border-slate-200 px-6 bg-slate-50 gap-2 overflow-x-auto text-xs font-semibold">
              {[
                { id: 'overview', label: 'Overview', icon: UserCheck },
                { id: 'policies', label: `Policies (${customer360?.policies?.length || 0})`, icon: Shield },
                { id: 'claims', label: `Claims History (${customer360?.claims?.length || 0})`, icon: FileText },
                { id: 'vehicles', label: `Vehicles (${customer360?.vehicles?.length || 0})`, icon: Car },
                { id: 'risk', label: 'Risk & Syndicate Assessment', icon: Activity },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-1.5 py-3 px-3 border-b-2 transition-all whitespace-nowrap ${
                      isActive
                        ? 'border-blue-600 text-blue-600 bg-white shadow-sm -mb-[1px]'
                        : 'border-transparent text-slate-500 hover:text-slate-800'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Contents */}
            <div className="p-6 overflow-y-auto flex-1">
              {isLoading360 ? (
                <div className="flex flex-col items-center justify-center py-12 space-y-3">
                  <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <p className="text-xs text-slate-500">Querying Customer 360 graph and policy records...</p>
                </div>
              ) : customer360 ? (
                <>
                  {/* OVERVIEW TAB */}
                  {activeTab === 'overview' && (
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                            <UserCheck className="h-4 w-4 text-blue-600" />
                            <span>Personal Information</span>
                          </h4>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div><span className="text-slate-400">Full Name:</span> <strong className="block text-slate-800">{customer360.customer?.name}</strong></div>
                            <div><span className="text-slate-400">Claimant ID:</span> <strong className="block font-mono text-slate-800">{customer360.customer?.claimant_id}</strong></div>
                            <div><span className="text-slate-400">Age:</span> <strong className="block text-slate-800">{customer360.customer?.age || '42'} yrs</strong></div>
                            <div><span className="text-slate-400">Gender:</span> <strong className="block text-slate-800">{customer360.customer?.gender || 'N/A'}</strong></div>
                            <div><span className="text-slate-400">Marital Status:</span> <strong className="block text-slate-800">{customer360.customer?.marital_status || 'Single'}</strong></div>
                            <div><span className="text-slate-400">Occupation:</span> <strong className="block text-slate-800">{customer360.customer?.occupation || 'Professional'}</strong></div>
                          </div>
                        </div>

                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-3">
                          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                            <MapPin className="h-4 w-4 text-blue-600" />
                            <span>Contact & Address</span>
                          </h4>
                          <div className="space-y-2 text-xs">
                            <div><span className="text-slate-400">Email:</span> <strong className="block text-slate-800">{customer360.customer?.email || 'verified.policyholder@insurance.com'}</strong></div>
                            <div><span className="text-slate-400">Phone:</span> <strong className="block text-slate-800">{customer360.customer?.phone || '+1 (555) 234-5678'}</strong></div>
                            <div><span className="text-slate-400">Location:</span> <strong className="block text-slate-800">{customer360.customer?.city || 'New York'}, NY</strong></div>
                            <div><span className="text-slate-400">Address:</span> <strong className="block text-slate-800">{customer360.customer?.address || '742 Evergreen Terrace'}</strong></div>
                          </div>
                        </div>
                      </div>

                      {/* Quick Action Footer */}
                      <div className="flex items-center justify-between p-4 bg-blue-50 border border-blue-200 rounded-xl">
                        <div>
                          <div className="text-xs font-bold text-blue-900">Need to record an incident for this customer?</div>
                          <div className="text-[11px] text-blue-700">Pre-fill customer policy info directly in the New Claim wizard.</div>
                        </div>
                        <button
                          onClick={() => {
                            handleClose360();
                            navigate(`/claims/new?customer_id=${customer360.customer?.claimant_id}`);
                          }}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs rounded-lg transition-colors shadow-sm flex items-center space-x-1.5"
                        >
                          <PlusCircle className="h-3.5 w-3.5" />
                          <span>File Claim for {customer360.customer?.name}</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* POLICIES TAB */}
                  {activeTab === 'policies' && (
                    <div className="space-y-4">
                      {customer360.policies && customer360.policies.length > 0 ? (
                        customer360.policies.map((p, idx) => (
                          <div key={p.id || `pol-${idx}`} className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-blue-300 transition-colors">
                            <div className="flex items-center justify-between mb-3">
                              <div className="flex items-center space-x-2">
                                <Shield className="h-5 w-5 text-blue-600" />
                                <span className="font-mono text-xs font-bold text-slate-900">{p.policy_number}</span>
                                <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                                  {p.status || 'ACTIVE'}
                                </span>
                              </div>
                              <span className="text-xs font-bold text-blue-600 font-mono">
                                ${p.annual_premium || 1200}/yr
                              </span>
                            </div>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                              <div><span className="text-slate-400">Coverage Type:</span> <strong className="block text-slate-800">{p.policy_type}</strong></div>
                              <div><span className="text-slate-400">Coverage Limit:</span> <strong className="block font-mono text-slate-800">${Number(p.coverage_limit || 0).toLocaleString()}</strong></div>
                              <div><span className="text-slate-400">Deductible:</span> <strong className="block font-mono text-slate-800">${p.deductible || 500}</strong></div>
                              <div><span className="text-slate-400">Valid Through:</span> <strong className="block text-slate-800">{p.end_date || '2025-12-31'}</strong></div>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-slate-500 text-xs bg-slate-50 rounded-xl border border-slate-200">
                          No active underwriting policies found for this policyholder.
                        </div>
                      )}
                    </div>
                  )}

                  {/* CLAIMS HISTORY TAB */}
                  {activeTab === 'claims' && (
                    <div className="space-y-4">
                      {customer360.claims && customer360.claims.length > 0 ? (
                        <div className="overflow-x-auto rounded-xl border border-slate-200">
                          <table className="w-full text-left text-xs text-slate-600">
                            <thead className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                              <tr>
                                <th className="p-3">Claim ID</th>
                                <th className="p-3">Incident Date</th>
                                <th className="p-3">Claim Type</th>
                                <th className="p-3 text-right">Amount</th>
                                <th className="p-3">Risk Band</th>
                                <th className="p-3">Status</th>
                                <th className="p-3 text-right">Action</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {customer360.claims.map((c) => (
                                <tr key={c.claim_id} className="hover:bg-slate-50/80 transition-colors">
                                  <td className="p-3 font-mono font-bold text-blue-600">{c.claim_id}</td>
                                  <td className="p-3">{c.claim_date || '2024-01-01'}</td>
                                  <td className="p-3 font-medium text-slate-800">{c.claim_type}</td>
                                  <td className="p-3 text-right font-mono font-semibold text-slate-900">
                                    ${Number(c.claim_amount || 0).toLocaleString()}
                                  </td>
                                  <td className="p-3">
                                    <span
                                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                        c.risk_band === 'HIGH' || c.risk_band === 'CRITICAL'
                                          ? 'bg-red-50 text-red-700 border border-red-200'
                                          : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                      }`}
                                    >
                                      {c.risk_band || 'LOW'}
                                    </span>
                                  </td>
                                  <td className="p-3">
                                    <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-medium">
                                      {c.status}
                                    </span>
                                  </td>
                                  <td className="p-3 text-right">
                                    <button
                                      onClick={() => {
                                        handleClose360();
                                        navigate(`/claims/${c.claim_id}`);
                                      }}
                                      className="text-blue-600 hover:text-blue-800 font-semibold hover:underline inline-flex items-center space-x-1"
                                    >
                                      <span>View</span>
                                      <ExternalLink className="h-3 w-3" />
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="text-center py-8 text-slate-500 text-xs bg-slate-50 rounded-xl border border-slate-200">
                          Zero prior claims on file for this customer. Clean underwriting profile.
                        </div>
                      )}
                    </div>
                  )}

                  {/* VEHICLES TAB */}
                  {activeTab === 'vehicles' && (
                    <div className="space-y-4">
                      {customer360.vehicles && customer360.vehicles.length > 0 ? (
                        customer360.vehicles.map((v, idx) => (
                          <div key={v.vehicle_id || `veh-${idx}`} className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg">
                                <Car className="h-5 w-5" />
                              </div>
                              <div>
                                <h4 className="text-xs font-bold text-slate-900">
                                  {v.model_year} {v.make} ({v.vehicle_type})
                                </h4>
                                <p className="text-[11px] font-mono text-slate-500 mt-0.5">
                                  VIN / Reg: {v.registration_no || 'WAUZZZ8K8FA982014'}
                                </p>
                              </div>
                            </div>
                            <span className="px-2.5 py-1 rounded bg-slate-100 text-slate-700 text-xs font-medium">
                              Insured Asset
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-slate-500 text-xs bg-slate-50 rounded-xl border border-slate-200">
                          No vehicles linked to this customer account.
                        </div>
                      )}
                    </div>
                  )}

                  {/* RISK & NETWORK TAB */}
                  {activeTab === 'risk' && (
                    <div className="space-y-5">
                      <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 space-y-3">
                        <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
                          <Activity className="h-4 w-4 text-blue-600" />
                          <span>Graph & Syndicate Intelligence</span>
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                          <div className="p-3 bg-white rounded-lg border border-slate-200">
                            <div className="text-slate-400">Syndicate Risk Level</div>
                            <div className={`text-base font-bold font-mono mt-1 ${customer360.fraud_alert_count > 0 ? 'text-amber-600' : 'text-emerald-600'}`}>
                              {customer360.fraud_alert_count > 0 ? 'Elevated Cluster Risk' : 'Normal Underwriting'}
                            </div>
                            <p className="text-[11px] text-slate-500 mt-1">
                              Network sub-graph verified against duplicate vehicle registrations and shared repair providers.
                            </p>
                          </div>
                          <div className="p-3 bg-white rounded-lg border border-slate-200">
                            <div className="text-slate-400">Total Historical Incurred</div>
                            <div className="text-base font-bold text-slate-900 font-mono mt-1">
                              ${Number(customer360.total_claim_amount || 0).toLocaleString()}
                            </div>
                            <p className="text-[11px] text-slate-500 mt-1">
                              Across {customer360.total_claims_count} documented insurance submissions.
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex justify-end space-x-3 pt-3 border-t border-slate-200">
                        <button
                          onClick={() => {
                            handleClose360();
                            navigate('/cases');
                          }}
                          className="px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-semibold transition-colors"
                        >
                          View SIU Investigations
                        </button>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-8 text-red-500 text-xs">
                  Failed to load customer profile details.
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex justify-end">
              <button
                onClick={handleClose360}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 font-medium text-xs rounded-lg transition-colors"
              >
                Close Dossier
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

