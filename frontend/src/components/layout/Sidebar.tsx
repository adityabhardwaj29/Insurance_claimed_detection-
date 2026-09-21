import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldCheck,
  LayoutDashboard,
  FileSpreadsheet,
  FilePlus2,
  FolderGit2,
  Network,
  Users,
  History,
  ExternalLink,
  Activity,
  CheckCircle2
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  const navItems = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/claims', label: 'Claims Queue', icon: FileSpreadsheet, badge: 'Active' },
    { to: '/claims/new', label: 'New Claim Intake', icon: FilePlus2, highlight: true },
    { to: '/cases', label: 'SIU Investigations', icon: FolderGit2, count: 42 },
    { to: '/intelligence', label: 'Fraud Intelligence', icon: Network },
    { to: '/customers', label: 'Customer 360', icon: Users },
    { to: '/audit-logs', label: 'Audit Logs', icon: History },
  ];

  return (
    <aside className="w-64 bg-[#0F3B82] border-r border-[#0D326E] flex flex-col flex-shrink-0 min-h-screen text-white select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-[#1A4C9C] gap-3 bg-[#0C316D]">
        <div className="h-9 w-9 rounded-lg bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-white shadow-sm">
          <ShieldCheck className="h-5 w-5 text-blue-200" />
        </div>
        <div className="overflow-hidden">
          <span className="font-bold text-white tracking-tight text-sm block leading-snug">
            Graph Enhanced
          </span>
          <span className="text-[10px] text-blue-200 tracking-wide font-medium block truncate">
            Insurance Fraud Intelligence
          </span>
        </div>
      </div>

      {/* Active Persona Pill */}
      <div className="px-5 py-2.5 border-b border-[#1A4C9C]/60 bg-[#0A295C]">
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-200 text-[11px]">Active Persona:</span>
          <span className="font-mono px-2 py-0.5 rounded bg-blue-900/80 text-blue-100 border border-blue-400/30 text-[10px] font-semibold">
            {(role || 'CLAIMS_OFFICER').replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-3 text-[10px] font-bold text-blue-200/70 uppercase tracking-wider mb-2">
          Claims & Intelligence
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-[#2563EB] text-white shadow-sm font-semibold'
                    : item.highlight
                    ? 'bg-white/10 text-white hover:bg-white/15 border border-white/10'
                    : 'text-blue-100/80 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] bg-blue-950/60 text-blue-200 border border-blue-400/20 px-1.5 py-0.5 rounded font-mono">
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && (
                <span className="text-[10px] bg-amber-400 text-slate-900 font-bold px-1.5 py-0.5 rounded-full font-mono shadow-xs">
                  {item.count}
                </span>
              )}
            </NavLink>
          );
        })}

        <div className="pt-4 mt-4 border-t border-[#1A4C9C]/60">
          <p className="px-3 text-[10px] font-bold text-blue-200/70 uppercase tracking-wider mb-2">
            Research & Analytics
          </p>
          <a
            href="http://localhost:8501"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium text-blue-100/80 hover:bg-white/10 hover:text-white group"
          >
            <div className="flex items-center space-x-3">
              <Activity className="h-4 w-4 text-emerald-300" />
              <span>Streamlit Console</span>
            </div>
            <ExternalLink className="h-3.5 w-3.5 text-blue-300/70 group-hover:text-white" />
          </a>
        </div>
      </nav>

      {/* Platform Health Status Footer */}
      <div className="p-4 border-t border-[#1A4C9C] bg-[#0A295C] text-xs">
        <div className="flex items-center space-x-2 text-emerald-300 font-medium mb-1">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Hybrid Engine Online</span>
        </div>
        <div className="text-[11px] text-blue-200/80 flex justify-between pt-0.5">
          <span>Enterprise Core</span>
          <span className="font-mono text-blue-100">v2.4.0</span>
        </div>
      </div>
    </aside>
  );
};
