import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ShieldCheck, Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0A295C] via-[#0F3B82] to-[#1E3A8A] flex flex-col items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-md border border-white/20 p-8 rounded-2xl shadow-2xl flex flex-col items-center max-w-sm text-center">
          <div className="h-16 w-16 rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center mb-4 shadow-inner">
            <ShieldCheck className="h-9 w-9 text-blue-300 animate-pulse" />
          </div>
          <h2 className="text-lg font-bold text-white tracking-wide">
            Enterprise Security Core
          </h2>
          <p className="text-xs text-blue-200/80 mt-1 mb-6">
            Verifying Officer Credentials & Access Control List...
          </p>
          <div className="flex items-center space-x-2 text-blue-300 text-xs font-mono">
            <Loader2 className="h-4 w-4 animate-spin text-blue-400" />
            <span>Establishing Secure Session...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children ? <>{children}</> : null;
};
