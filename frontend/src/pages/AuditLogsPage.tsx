import React, { useEffect, useState } from 'react';
import { History, Shield, Search, Clock, Lock } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await api.getAuditLogs(100);
        setLogs(data);
      } catch (err) {
        console.error('Error fetching audit logs', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(
    (l) =>
      (l?.action || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (l?.entity_id || '').toLowerCase().includes((search || '').toLowerCase()) ||
      (l?.user_email || '').toLowerCase().includes((search || '').toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight flex items-center space-x-2">
            <Lock className="h-6 w-6 text-sky-400" />
            <span>Immutable Regulatory Audit Stream</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Cryptographically sealed and tamper-evident activity ledger logging all intake, analysis, investigator actions, and executive sign-offs.
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
            placeholder="Search audit trail by action, entity ID, or operator email..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase font-semibold tracking-wider text-[11px]">
              <tr>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5">Operator</th>
                <th className="px-5 py-3.5">Role</th>
                <th className="px-5 py-3.5">Action</th>
                <th className="px-5 py-3.5">Entity</th>
                <th className="px-5 py-3.5">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-medium">
              {filteredLogs.length > 0 ? (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-5 py-3.5 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                      {log.timestamp?.replace('T', ' ').substring(0, 19) || 'Just now'}
                    </td>
                    <td className="px-5 py-3.5 text-white font-semibold">
                      {log.user_email}
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 text-[10px] font-mono">
                        {log.user_role}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-sky-400 font-bold">
                      {log.action}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-slate-300">
                      {log.entity_type}:{log.entity_id}
                    </td>
                    <td className="px-5 py-3.5 text-slate-300 max-w-xs truncate">
                      {log.details}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-slate-500">
                    {isLoading ? 'Loading audit records...' : 'No audit events found.'}
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
