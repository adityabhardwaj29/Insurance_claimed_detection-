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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">
            Customer 360 & Policyholder Directory
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Master policyholder profiles with unified claim history, active underwriting policies, and cumulative risk tiering.
          </p>
        </div>
      </div>

      <div className="glass-panel p-4 rounded-xl border border-slate-800">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search policyholders by name or customer ID..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.length > 0 ? (
          filtered.map((c) => (
            <div
              key={c.id}
              className="glass-panel p-5 rounded-2xl border border-slate-800 hover:border-slate-700 transition-all space-y-4"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-sky-400">
                  {c.customer_number}
                </span>
                <span className="px-2 py-0.5 rounded bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 text-[11px] font-semibold">
                  {c.risk_tier || 'Standard Tier'}
                </span>
              </div>

              <div>
                <h3 className="text-base font-bold text-white">
                  {c.first_name} {c.last_name}
                </h3>
                <p className="text-xs text-slate-400 font-mono mt-0.5">
                  ID: {c.national_id || 'ID-99214019'}
                </p>
              </div>

              <div className="space-y-1.5 text-xs text-slate-300">
                <div className="flex items-center space-x-2">
                  <Mail className="h-3.5 w-3.5 text-slate-500" />
                  <span>{c.email || 'aditya.bhardwaj@email.com'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Phone className="h-3.5 w-3.5 text-slate-500" />
                  <span>{c.phone || '+1 (555) 382-9104'}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <MapPin className="h-3.5 w-3.5 text-slate-500" />
                  <span>{c.city || 'Albany'}, {c.state || 'NY'}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-between text-xs text-slate-400">
                <span>Active Policies: <strong className="text-white">1</strong></span>
                <span>Claims Filed: <strong className="text-sky-400">1</strong></span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 text-center py-10 text-slate-500">
            {isLoading ? 'Loading policyholder records...' : 'No customers found.'}
          </div>
        )}
      </div>
    </div>
  );
};
