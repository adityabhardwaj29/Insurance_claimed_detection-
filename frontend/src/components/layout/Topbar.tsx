import React, { useState } from 'react';
import { Search, Bell, ShieldCheck, ChevronDown, UserCheck } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

export const Topbar: React.FC = () => {
  const { user, role, switchRole } = useAuth();
  const [roleDropdownOpen, setRoleDropdownOpen] = useState(false);

  const roles: { role: UserRole; label: string; desc: string }[] = [
    { role: 'CLAIMS_OFFICER', label: 'Claims Officer', desc: 'Intake, document collection, policy validation' },
    { role: 'INVESTIGATOR', label: 'SIU Investigator', desc: 'Case management, evidence review, interviews' },
    { role: 'SUPERVISOR', label: 'Operations Supervisor', desc: 'Claim sign-off, threshold overrides, case assignment' },
    { role: 'ANALYST', label: 'Fraud Analytics Lead', desc: 'Model calibration, graph topology, drift monitor' },
    { role: 'ADMIN', label: 'System Administrator', desc: 'Security, RLS policies, audit inspection' },
  ];

  return (
    <header className="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between z-20">
      {/* Search Bar */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search claims (e.g. CLM-2024-001), policies, or claimants..."
            className="w-full bg-slate-950/70 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 transition-all"
          />
        </div>
      </div>

      {/* Action Controls & Persona Switcher */}
      <div className="flex items-center space-x-4">
        {/* Quick Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center space-x-2 bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 transition-all"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-sky-400" />
            <span className="font-medium text-slate-300">Persona:</span>
            <span className="font-semibold text-white">{role.replace('_', ' ')}</span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
          </button>

          {roleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl py-2 z-50">
              <div className="px-3 py-2 border-b border-slate-800 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Switch Active Role
              </div>
              <div className="py-1">
                {roles.map((r) => (
                  <button
                    key={r.role}
                    onClick={() => {
                      switchRole(r.role);
                      setRoleDropdownOpen(false);
                    }}
                    className={`w-full text-left px-3 py-2 text-xs flex flex-col transition-colors ${
                      role === r.role
                        ? 'bg-sky-500/10 text-sky-400 font-semibold'
                        : 'text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{r.label}</span>
                      {role === r.role && <UserCheck className="h-3 w-3 text-sky-400" />}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5">{r.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Notifications Icon */}
        <button className="relative p-2 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-slate-400 hover:text-white transition-all">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-slate-900 animate-pulse" />
        </button>

        {/* User Card */}
        <div className="flex items-center space-x-3 pl-3 border-l border-slate-800">
          <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white uppercase">
            {user?.full_name ? user.full_name.charAt(0) : 'U'}
          </div>
          <div className="hidden md:block">
            <p className="text-xs font-medium text-white leading-tight">
              {user?.full_name || 'Sarah Connor'}
            </p>
            <p className="text-[11px] text-slate-400 leading-tight">
              {user?.department || 'Claims Operations'}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
