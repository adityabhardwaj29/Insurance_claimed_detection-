import React from 'react';
import { NewClaimWizard } from '../components/claims/NewClaimWizard';

export const NewClaimPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-extrabold text-white tracking-tight">
          New Claim Intake & Underwriting Registration
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Complete the guided intake to verify policy eligibility, attach corroborating documents, and trigger automated fraud risk assessment.
        </p>
      </div>
      <NewClaimWizard />
    </div>
  );
};
