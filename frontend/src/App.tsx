import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AppLayout } from './components/layout/AppLayout';

// Eager load auth and initial dashboard
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';

// Code split heavier pages for fast initial bundle and navigation
const ClaimsListPage = lazy(() => import('./pages/ClaimsListPage').then(m => ({ default: m.ClaimsListPage })));
const NewClaimPage = lazy(() => import('./pages/NewClaimPage').then(m => ({ default: m.NewClaimPage })));
const ClaimDetailPage = lazy(() => import('./pages/ClaimDetailPage').then(m => ({ default: m.ClaimDetailPage })));
const CasesPage = lazy(() => import('./pages/CasesPage').then(m => ({ default: m.CasesPage })));
const FraudIntelligencePage = lazy(() => import('./pages/FraudIntelligencePage').then(m => ({ default: m.FraudIntelligencePage })));
const CustomersPage = lazy(() => import('./pages/CustomersPage').then(m => ({ default: m.CustomersPage })));
const AuditLogsPage = lazy(() => import('./pages/AuditLogsPage').then(m => ({ default: m.AuditLogsPage })));

const RouteLoadingFallback = () => (
  <div className="flex flex-col items-center justify-center min-h-[300px] space-y-3">
    <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
    <span className="text-xs text-slate-500 font-medium">Loading module...</span>
  </div>
);

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Enterprise Routes */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<DashboardPage />} />
            <Route
              path="/claims"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <ClaimsListPage />
                </Suspense>
              }
            />
            <Route
              path="/claims/new"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <NewClaimPage />
                </Suspense>
              }
            />
            <Route
              path="/claims/:id"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <ClaimDetailPage />
                </Suspense>
              }
            />
            <Route
              path="/cases"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <CasesPage />
                </Suspense>
              }
            />
            <Route
              path="/intelligence"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <FraudIntelligencePage />
                </Suspense>
              }
            />
            <Route
              path="/customers"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <CustomersPage />
                </Suspense>
              }
            />
            <Route
              path="/audit-logs"
              element={
                <Suspense fallback={<RouteLoadingFallback />}>
                  <AuditLogsPage />
                </Suspense>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
