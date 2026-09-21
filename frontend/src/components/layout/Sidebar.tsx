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
  CheckCircle2,
  X
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  mobileOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen = false, onClose }) => {
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

  const renderNavContent = (isMobile = false) => (
    <>
      {/* Brand Header */}
      <div className={`h-16 flex items-center border-b border-[#1A4C9C] bg-[#0C316D] ${
        isMobile ? 'px-5 justify-between' : 'px-3 lg:px-5 justify-center lg:justify-start gap-3'
      }`}>
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-white shadow-sm shrink-0">
            <ShieldCheck className="h-5 w-5 text-blue-200" />
          </div>
          <div className={`overflow-hidden ${isMobile ? 'block' : 'hidden lg:block'}`}>
            <span className="font-bold text-white tracking-tight text-sm block leading-snug">
              Graph Enhanced
            </span>
            <span className="text-[10px] text-blue-200 tracking-wide font-medium block truncate">
              Insurance Fraud Intelligence
            </span>
          </div>
        </div>
        {isMobile && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-blue-200 hover:text-white hover:bg-white/10 transition-colors"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Active Persona Pill */}
      <div className={`px-5 py-2.5 border-b border-[#1A4C9C]/60 bg-[#0A295C] ${
        isMobile ? 'block' : 'hidden lg:block'
      }`}>
        <div className="flex items-center justify-between text-xs">
          <span className="text-blue-200 text-[11px]">Active Persona:</span>
          <span className="font-mono px-2 py-0.5 rounded bg-blue-900/80 text-blue-100 border border-blue-400/30 text-[10px] font-semibold truncate max-w-[120px]">
            {(role || 'CLAIMS_OFFICER').replace('_', ' ')}
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 lg:px-3 py-4 space-y-1 overflow-y-auto">
        <p className={`px-3 text-[10px] font-bold text-blue-200/70 uppercase tracking-wider mb-2 ${
          isMobile ? 'block' : 'hidden lg:block'
        }`}>
          Claims & Intelligence
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              title={item.label}
              onClick={isMobile ? onClose : undefined}
              className={({ isActive }) =>
                `flex items-center rounded-lg text-xs font-medium transition-all ${
                  isMobile || !isMobile ? '' : ''
                } ${
                  isMobile
                    ? 'justify-between px-3 py-2.5'
                    : 'justify-center lg:justify-between px-2.5 lg:px-3 py-2.5'
                } ${
                  isActive
                    ? 'bg-[#2563EB] text-white shadow-sm font-semibold'
                    : item.highlight
                    ? 'bg-white/10 text-white hover:bg-white/15 border border-white/10'
                    : 'text-blue-100/80 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-5 w-5 lg:h-4 lg:w-4 flex-shrink-0" />
                <span className={isMobile ? 'inline' : 'hidden lg:inline'}>{item.label}</span>
              </div>
              <div className={isMobile ? 'flex items-center space-x-1.5' : 'hidden lg:flex items-center space-x-1.5'}>
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
              </div>
            </NavLink>
          );
        })}

        <div className="pt-4 mt-4 border-t border-[#1A4C9C]/60">
          <p className={`px-3 text-[10px] font-bold text-blue-200/70 uppercase tracking-wider mb-2 ${
            isMobile ? 'block' : 'hidden lg:block'
          }`}>
            Research & Analytics
          </p>
          <a
            href="http://localhost:8501"
            target="_blank"
            rel="noopener noreferrer"
            title="Streamlit Console"
            className={`flex items-center rounded-lg text-xs font-medium text-blue-100/80 hover:bg-white/10 hover:text-white group ${
              isMobile
                ? 'justify-between px-3 py-2.5'
                : 'justify-center lg:justify-between px-2.5 lg:px-3 py-2.5'
            }`}
          >
            <div className="flex items-center space-x-3">
              <Activity className="h-5 w-5 lg:h-4 lg:w-4 text-emerald-300 flex-shrink-0" />
              <span className={isMobile ? 'inline' : 'hidden lg:inline'}>Streamlit Console</span>
            </div>
            <ExternalLink className={`h-3.5 w-3.5 text-blue-300/70 group-hover:text-white ${
              isMobile ? 'inline' : 'hidden lg:inline'
            }`} />
          </a>
        </div>
      </nav>

      {/* Platform Health Status Footer */}
      <div className={`border-t border-[#1A4C9C] bg-[#0A295C] text-xs ${
        isMobile ? 'p-4' : 'p-2 lg:p-4'
      }`}>
        <div className={`items-center space-x-2 text-emerald-300 font-medium ${
          isMobile ? 'flex mb-1' : 'hidden lg:flex mb-1'
        }`}>
          <CheckCircle2 className="h-3.5 w-3.5" />
          <span>Hybrid Engine Online</span>
        </div>
        <div className={`text-[11px] text-blue-200/80 justify-between pt-0.5 ${
          isMobile ? 'flex' : 'hidden lg:flex'
        }`}>
          <span>Enterprise Core</span>
          <span className="font-mono text-blue-100">v2.4.0</span>
        </div>
        {/* Tablet collapsed icon */}
        {!isMobile && (
          <div className="flex lg:hidden justify-center py-1" title="Hybrid Engine Online (v2.4.0)">
            <CheckCircle2 className="h-4 w-4 text-emerald-300" />
          </div>
        )}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Drawer (XS/SM: 0-767px) */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/60 z-40 md:hidden backdrop-blur-xs transition-opacity animate-fadeIn"
          onClick={onClose}
        />
      )}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#0F3B82] border-r border-[#0D326E] flex flex-col min-h-screen text-white select-none transition-transform duration-300 ease-in-out md:hidden shadow-2xl ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {renderNavContent(true)}
      </aside>

      {/* Static Sidebar for Tablet (MD: collapsed w-16) and Desktop (LG+: expanded w-64) */}
      <aside className="hidden md:flex flex-col flex-shrink-0 min-h-screen bg-[#0F3B82] border-r border-[#0D326E] text-white select-none transition-all duration-300 w-16 lg:w-64">
        {renderNavContent(false)}
      </aside>
    </>
  );
};

