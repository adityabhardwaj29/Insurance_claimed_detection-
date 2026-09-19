import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  ShieldAlert,
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
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col flex-shrink-0 min-h-screen">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="h-9 w-9 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
          <ShieldAlert className="h-5 w-5 text-sky-400" />
        </div>
        <div>
          <span className="font-bold text-white tracking-tight text-base block leading-tight">
            FraudShield <span className="text-sky-400 font-mono text-xs">AI</span>
          </span>
          <span className="text-[10px] text-slate-400 tracking-wider font-semibold uppercase">
            SIU Enterprise Platform
          </span>
        </div>
      </div>

      {/* Role Pill */}
      <div className="px-5 py-3 border-b border-slate-800/60 bg-slate-950/40">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400">Active Persona:</span>
          <span className="font-mono px-2 py-0.5 rounded bg-sky-950/80 text-sky-300 border border-sky-800/60 text-[11px] font-medium">
            {(role || 'CLAIMS_OFFICER').replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1.5 overflow-y-auto">
        <p className="px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Claims Operations
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 font-semibold'
                    : item.highlight
                    ? 'bg-slate-800/60 text-slate-200 hover:bg-slate-800 hover:text-white border border-slate-700/50'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded">
                  {item.badge}
                </span>
              )}
              {item.count !== undefined && (
                <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/30 px-1.5 py-0.5 rounded-full font-mono">
                  {item.count}
                </span>
              )}
            </NavLink>
          );
        })}

        <div className="pt-4 mt-4 border-t border-slate-800/80">
          <p className="px-3 text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Research & Analytics
          </p>
          <a
            href="http://localhost:8501"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 hover:bg-slate-800/50 hover:text-white group"
          >
            <div className="flex items-center space-x-3">
              <Activity className="h-4 w-4 text-emerald-400" />
              <span>Streamlit Console</span>
            </div>
            <ExternalLink className="h-3.5 w-3.5 text-slate-500 group-hover:text-slate-300" />
          </a>
        </div>
      </nav>

      {/* Platform Health Status */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/60 text-xs">
        <div className="flex items-center space-x-2 text-emerald-400 font-medium mb-1">
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Hybrid Engine Online</span>
        </div>
        <div className="text-[11px] text-slate-400 flex justify-between pt-1">
          <span>PostgreSQL / ML Stack</span>
          <span className="font-mono text-slate-400">v2.4.0</span>
        </div>
      </div>
    </aside>
  );
};
