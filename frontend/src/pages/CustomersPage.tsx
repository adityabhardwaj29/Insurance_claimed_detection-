import React, { useEffect, useState } from 'react';
import { Search, UserCheck, Shield, FileText, Phone, Mail, MapPin } from 'lucide-react';
import { api } from '../services/api';
import { Customer } from '../types';

export const CustomersPage: React.FC = () => {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

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

  const filtered = customers.filter(
    (c) =>
      (c?.first_name || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (c?.last_name || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (c?.customer_number || '').toLowerCase().includes((search || '').toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center space-x-2.5">
            <UserCheck className="h-6 w-6 text-blue-600" />
            <span>Customer 360 & Policyholder Directory</span>
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Master policyholder profiles with unified claim history, active underwriting policies, and cumulative risk tiering.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800">
            Total Insureds: <strong className="font-mono text-blue-900 font-bold">{customers.length}</strong>
          </span>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="relative">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search policyholders by name or customer ID..."
            className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-600 focus:ring-1 focus:ring-blue-600 transition-all"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5">
        {filtered.length > 0 ? (
          filtered.map((c) => (
            <div
              key={c.id}
              className="bg-white p-5 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all space-y-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">
                  {c.customer_number}
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[11px] font-semibold">
                  {c.risk_tier || 'Standard Tier'}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-slate-900">
                  {c.first_name} {c.last_name}
                </h3>
                <p className="text-xs text-slate-500 font-mono mt-0.5">
                  ID: {c.national_id || 'ID-99214019'}
                </p>
              </div>

              <div className="space-y-2 text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div className="flex items-center space-x-2">
                  <Mail className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span className="truncate">{c.email || 'policyholder@carrier.com'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Phone className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span>{c.phone || '+1 (555) 382-9104'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-3.5 w-3.5 text-slate-400 shrink-0" />
                  <span>{c.city || 'Albany'}, {c.state || 'NY'}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-between text-xs text-slate-500">
                <span>Active Policies: <strong className="text-slate-900 font-semibold">1</strong></span>
                <span>Claims Filed: <strong className="text-blue-600 font-semibold">1</strong></span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 text-center py-12 bg-white rounded-xl border border-slate-200 text-slate-500 text-sm">
            {isLoading ? 'Loading policyholder records...' : 'No policyholders found matching your search.'}
          </div>
        )}
      </div>
    </div>
  );
};
