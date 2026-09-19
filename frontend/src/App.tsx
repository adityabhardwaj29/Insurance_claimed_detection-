import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { DashboardPage } from './pages/DashboardPage';
import { ClaimsListPage } from './pages/ClaimsListPage';
import { NewClaimPage } from './pages/NewClaimPage';
import { ClaimDetailPage } from './pages/ClaimDetailPage';
import { CasesPage } from './pages/CasesPage';
import { FraudIntelligencePage } from './pages/FraudIntelligencePage';
import { CustomersPage } from './pages/CustomersPage';
import { AuditLogsPage } from './pages/AuditLogsPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/claims" element={<ClaimsListPage />} />
            <Route path="/claims/new" element={<NewClaimPage />} />
            <Route path="/claims/:id" element={<ClaimDetailPage />} />
            <Route path="/cases" element={<CasesPage />} />
            <Route path="/intelligence" element={<FraudIntelligencePage />} />
            <Route path="/customers" element={<CustomersPage />} />
            <Route path="/audit-logs" element={<AuditLogsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
