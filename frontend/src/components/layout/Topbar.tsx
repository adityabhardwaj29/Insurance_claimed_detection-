import React, { useState } from 'react';
import { Search, Bell, ShieldCheck, ChevronDown, UserCheck, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';

interface TopbarProps {
  onMenuClick?: () => void;
}

export const Topbar: React.FC<TopbarProps> = ({ onMenuClick }) => {
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
    <header className="h-16 bg-white border-b border-slate-200 px-3 sm:px-4 md:px-6 flex items-center justify-between z-20 shadow-xs gap-2 sm:gap-4">
      {/* Left: Mobile Hamburger & App Title */}
      <div className="flex items-center space-x-2.5">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200 transition-colors cursor-pointer"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5 text-slate-700" />
        </button>

        <div className="flex items-center space-x-2 md:hidden">
          <div className="h-7 w-7 rounded-lg bg-[#0F3B82] flex items-center justify-center text-white shadow-xs">
            <ShieldCheck className="h-4 w-4 text-blue-200" />
          </div>
          <span className="font-bold text-slate-900 text-xs sm:text-sm tracking-tight truncate max-w-[140px] sm:max-w-none">
            Graph Enhanced
          </span>
        </div>

        {/* Search Bar - Hidden on Mobile, Compact on Tablet, Full on Desktop */}
        <div className="hidden md:block flex-1 md:max-w-xs lg:max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search claims, policies, or claimants..."
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
            />
          </div>
        </div>
      </div>

      {/* Right: Action Controls & Persona Switcher */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Quick Role Switcher Dropdown */}
        <div className="relative">
          <button
            onClick={() => setRoleDropdownOpen(!roleDropdownOpen)}
            className="flex items-center space-x-1.5 sm:space-x-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg px-2 sm:px-3 py-1.5 text-xs text-slate-700 transition-all cursor-pointer"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-blue-600 shrink-0" />
            <span className="hidden sm:inline font-medium text-slate-500">Persona:</span>
            <span className="font-semibold text-slate-900 text-[11px] sm:text-xs truncate max-w-[90px] sm:max-w-none">
              {role.replace('_', ' ')}
            </span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-400 shrink-0" />
          </button>

          {roleDropdownOpen && (
            <div className="absolute right-0 mt-2 w-72 bg-white border border-slate-200 rounded-xl shadow-xl py-2 z-50 animate-fadeIn">
              <div className="px-3 py-2 border-b border-slate-100 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
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
                    className={`w-full text-left px-3 py-2 text-xs flex flex-col transition-colors cursor-pointer ${
                      role === r.role
                        ? 'bg-blue-50 text-blue-700 font-semibold'
                        : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span>{r.label}</span>
                      {role === r.role && <UserCheck className="h-3.5 w-3.5 text-blue-600" />}
                    </div>
                    <span className="text-[10px] text-slate-500 mt-0.5">{r.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Notifications Icon */}
        <button
          className="relative p-2 rounded-lg bg-slate-50 hover:bg-slate-100 text-slate-600 hover:text-slate-900 border border-slate-200 transition-all cursor-pointer shrink-0"
          aria-label="Notifications"
        >
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-600 ring-2 ring-white" />
        </button>

        {/* User Card */}
        <div className="flex items-center space-x-2 sm:space-x-3 pl-2 sm:pl-3 border-l border-slate-200 shrink-0">
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white uppercase shadow-xs shrink-0">
            {user?.full_name ? user.full_name.charAt(0) : 'A'}
          </div>
          <div className="hidden lg:block">
            <p className="text-xs font-semibold text-slate-900 leading-tight">
              {user?.full_name || 'Aditya Bhardwaj'}
            </p>
            <p className="text-[11px] text-slate-500 leading-tight">
              {user?.department || 'Claims Operations'}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
};
