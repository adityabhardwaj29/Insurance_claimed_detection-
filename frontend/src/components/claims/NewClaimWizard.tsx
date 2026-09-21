import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  CheckCircle2,
  FileText,
  User,
  Shield,
  DollarSign,
  Upload,
  ArrowRight,
  ArrowLeft,
  Search,
  Sparkles,
  Loader2,
  FileUp
} from 'lucide-react';
import { api } from '../../services/api';

interface WizardState {
  // Step 1: Customer
  claimant_name: string;
  claimant_email: string;
  claimant_phone: string;
  national_id: string;
  customer_type: 'existing' | 'new';
  
  // Step 2: Policy
  policy_number: string;
  policy_verified: boolean;
  policy_type: string;
  deductible: number;
  coverage_limit: number;
  
  // Step 3: Incident
  incident_date: string;
  incident_hour_of_the_day: number;
  incident_type: string;
  collision_type: string;
  incident_severity: string;
  incident_state: string;
  incident_city: string;
  authorities_contacted: string;
  number_of_vehicles_involved: number;
  witnesses: number;
  bodily_injuries: number;
  police_report_available: string;
  
  // Step 4: Amounts & Vehicle
  injury_claim: number;
  property_claim: number;
  vehicle_claim: number;
  total_claim_amount: number;
  vehicle_make: string;
  vehicle_model: string;
  auto_year: number;
  auto_vin: string;
  provider_name: string;
  
  // Step 5: Documents
  documents: Array<{ name: string; type: string; size: string }>;
}

const INITIAL_STATE: WizardState = {
  claimant_name: 'Aditya Bhardwaj',
  claimant_email: 'aditya.bhardwaj@email.com',
  claimant_phone: '+1 (555) 382-9104',
  national_id: 'ID-88492019',
  customer_type: 'existing',
  
  policy_number: 'POL-521948',
  policy_verified: true,
  policy_type: 'Comprehensive Auto Coverage',
  deductible: 1000,
  coverage_limit: 500000,
  
  incident_date: new Date().toISOString().split('T')[0],
  incident_hour_of_the_day: 14,
  incident_type: 'Multi-vehicle Collision',
  collision_type: 'Front Collision',
  incident_severity: 'Major Damage',
  incident_state: 'NY',
  incident_city: 'Albany',
  authorities_contacted: 'Police',
  number_of_vehicles_involved: 2,
  witnesses: 1,
  bodily_injuries: 1,
  police_report_available: 'YES',
  
  injury_claim: 12500,
  property_claim: 8200,
  vehicle_claim: 43500,
  total_claim_amount: 64200,
  vehicle_make: 'Audi',
  vehicle_model: 'A4',
  auto_year: 2021,
  auto_vin: 'WAUZZZ8K8FA982014',
  provider_name: 'Metro Collision Center & Trauma Clinic',
  
  documents: [
    { name: 'Police_Incident_Report_NY_091824.pdf', type: 'Police Report', size: '1.8 MB' },
    { name: 'Vehicle_Damage_Estimate_MetroAuto.pdf', type: 'Repair Estimate', size: '2.4 MB' },
  ],
};

export const NewClaimWizard: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState<number>(1);
  const [form, setForm] = useState<WizardState>(INITIAL_STATE);
  const [isVerifyingPolicy, setIsVerifyingPolicy] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pipelineProgress, setPipelineProgress] = useState<string>('');

  const steps = [
    { num: 1, label: 'Customer Lookup', icon: User },
    { num: 2, label: 'Policy Verification', icon: Shield },
    { num: 3, label: 'Incident Details', icon: FileText },
    { num: 4, label: 'Amounts & Vehicle', icon: DollarSign },
    { num: 5, label: 'Document Intake', icon: Upload },
    { num: 6, label: 'Multi-Signal Analysis', icon: Sparkles },
  ];

  const updateForm = (fields: Partial<WizardState>) => {
    setForm((prev) => {
      const updated = { ...prev, ...fields };
      // Recalculate total claim amount if component claims change
      if (
        fields.injury_claim !== undefined ||
        fields.property_claim !== undefined ||
        fields.vehicle_claim !== undefined
      ) {
        updated.total_claim_amount =
          Number(updated.injury_claim || 0) +
          Number(updated.property_claim || 0) +
          Number(updated.vehicle_claim || 0);
      }
      return updated;
    });
  };

  const handleVerifyPolicy = async () => {
    setIsVerifyingPolicy(true);
    try {
      const res = await api.verifyPolicy(form.policy_number, form.incident_date);
      updateForm({
        policy_verified: res.valid,
        policy_type: 'Comprehensive Full Collision & Medical',
      });
    } finally {
      setIsVerifyingPolicy(false);
    }
  };

  const handleFinalSubmit = async () => {
    setIsSubmitting(true);
    setPipelineProgress('Registering new claim in database...');

    try {
      // Step 1: Create Claim
      const claimPayload = {
        claim_number: `CLM-2024-${Math.floor(1000 + Math.random() * 9000)}`,
        claimant_name: form.claimant_name,
        policy_number: form.policy_number,
        incident_date: form.incident_date,
        report_date: new Date().toISOString().split('T')[0],
        incident_type: form.incident_type,
        collision_type: form.collision_type,
        incident_severity: form.incident_severity,
        incident_state: form.incident_state,
        incident_city: form.incident_city,
        incident_hour_of_the_day: form.incident_hour_of_the_day,
        number_of_vehicles_involved: form.number_of_vehicles_involved,
        witnesses: form.witnesses,
        bodily_injuries: form.bodily_injuries,
        police_report_available: form.police_report_available,
        total_claim_amount: form.total_claim_amount,
        injury_claim: form.injury_claim,
        property_claim: form.property_claim,
        vehicle_claim: form.vehicle_claim,
        vehicle_make: form.vehicle_make,
        vehicle_model: form.vehicle_model,
        auto_year: form.auto_year,
        auto_vin: form.auto_vin,
        provider_name: form.provider_name,
        status: 'SUBMITTED' as const,
      };

      const createdClaim = await api.createClaim(claimPayload);

      // Step 2: Automated Pipeline Steps
      setPipelineProgress('Extracting and engineering 38 behavioral features...');
      await new Promise((r) => setTimeout(r, 600));

      setPipelineProgress('Scoring Supervised XGBoost ensemble model...');
      await new Promise((r) => setTimeout(r, 500));

      setPipelineProgress('Running Isolation Forest unsupervised anomaly detector...');
      await new Promise((r) => setTimeout(r, 500));

      setPipelineProgress('Scanning historical claims for duplicate & recycled attributes...');
      await new Promise((r) => setTimeout(r, 500));

      setPipelineProgress('Executing bipartite graph syndicate collusion detection...');
      await new Promise((r) => setTimeout(r, 500));

      setPipelineProgress('Synthesizing hybrid risk score & SHAP explainability waterfall...');
      await api.analyzeClaim(createdClaim.id);

      setPipelineProgress('Analysis complete! Redirecting to 360° Claim Dossier...');
      await new Promise((r) => setTimeout(r, 400));

      navigate(`/claims/${createdClaim.id}`);
    } catch (err: any) {
      console.error('Claim submission error:', err);
      navigate('/claims');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
      {/* Wizard Progress Stepper */}
      <div className="bg-white p-3 sm:p-5 rounded-xl border border-[#E2E8F0] shadow-xs overflow-x-auto">
        <div className="flex items-center justify-between min-w-[300px]">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            const isDone = step > s.num;
            const isCurrent = step === s.num;
            return (
              <React.Fragment key={s.num}>
                <div className="flex flex-col items-center">
                  <div
                    className={`h-8 w-8 sm:h-10 sm:w-10 rounded-lg sm:rounded-xl flex items-center justify-center font-bold text-xs transition-all ${
                      isDone
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : isCurrent
                        ? 'bg-[#2563EB] text-white shadow-xs ring-2 ring-blue-200'
                        : 'bg-slate-100 text-slate-400 border border-slate-200'
                    }`}
                  >
                    {isDone ? <CheckCircle2 className="h-4 w-4 sm:h-5 sm:w-5" /> : <Icon className="h-4 w-4 sm:h-5 sm:w-5" />}
                  </div>
                  <span
                    className={`text-[10px] sm:text-[11px] font-medium mt-1 sm:mt-2 hidden sm:block ${
                      isCurrent ? 'text-[#2563EB] font-bold' : isDone ? 'text-slate-700' : 'text-slate-400'
                    }`}
                  >
                    {s.label}
                  </span>
                </div>
                {idx < steps.length - 1 && (
                  <div
                    className={`flex-1 h-0.5 mx-1 sm:mx-2 transition-all ${
                      step > s.num ? 'bg-emerald-400' : 'bg-slate-200'
                    }`}
                  />
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Main Form Body */}
      <div className="bg-white p-4 sm:p-7 rounded-xl border border-[#E2E8F0] shadow-xs">
        {/* STEP 1: CUSTOMER */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 1: Policyholder Identification</h2>
              <p className="text-xs text-slate-500 mt-1">
                Search existing claimant directory or register a verified claimant intake profile.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Claimant Full Name *
                </label>
                <input
                  type="text"
                  value={form.claimant_name}
                  onChange={(e) => updateForm({ claimant_name: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  National ID / Driver License *
                </label>
                <input
                  type="text"
                  value={form.national_id}
                  onChange={(e) => updateForm({ national_id: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 font-mono transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Contact Email Address *
                </label>
                <input
                  type="email"
                  value={form.claimant_email}
                  onChange={(e) => updateForm({ claimant_email: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Phone Number *
                </label>
                <input
                  type="text"
                  value={form.claimant_phone}
                  onChange={(e) => updateForm({ claimant_phone: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <CheckCircle2 className="h-5 w-5 text-[#2563EB]" />
                <div>
                  <p className="text-xs font-bold text-blue-950">Customer Identity Verified</p>
                  <p className="text-[11px] text-blue-800">Matched to master policyholder database record</p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold bg-white text-blue-700 border border-blue-200 px-2.5 py-1 rounded shadow-xs">
                Tier 1 - Standard
              </span>
            </div>
          </div>
        )}

        {/* STEP 2: POLICY */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 2: Policy Coverage Verification</h2>
              <p className="text-xs text-slate-500 mt-1">
                Validate active coverage window, deductible terms, and limit compliance.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Policy Reference Number *
                </label>
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={form.policy_number}
                    onChange={(e) => updateForm({ policy_number: e.target.value })}
                    className="flex-1 bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                  />
                  <button
                    type="button"
                    onClick={handleVerifyPolicy}
                    disabled={isVerifyingPolicy}
                    className="bg-slate-50 hover:bg-slate-100 text-[#2563EB] px-3.5 py-2 rounded-lg text-xs font-semibold border border-slate-300 flex items-center space-x-1.5 cursor-pointer"
                  >
                    {isVerifyingPolicy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
                    <span>Verify</span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Coverage Plan Type
                </label>
                <input
                  type="text"
                  readOnly
                  value={form.policy_type}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3.5 py-2 text-xs text-slate-600 font-medium cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Policy Deductible ($)
                </label>
                <input
                  type="number"
                  value={form.deductible}
                  onChange={(e) => updateForm({ deductible: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Total Policy Limit ($)
                </label>
                <input
                  type="number"
                  value={form.coverage_limit}
                  onChange={(e) => updateForm({ coverage_limit: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>
            </div>

            {form.policy_verified && (
              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center space-x-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                <div>
                  <p className="text-xs font-bold text-emerald-950">Active Underwriting Policy</p>
                  <p className="text-[11px] text-emerald-800">
                    Policy is current with no lapsed premium or outstanding non-pay cancellation notices.
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 3: INCIDENT DETAILS */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 3: Loss Incident Details</h2>
              <p className="text-xs text-slate-500 mt-1">
                Record exact collision dynamics, loss circumstances, and reporting timeline.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Incident Date *
                </label>
                <input
                  type="date"
                  value={form.incident_date}
                  onChange={(e) => updateForm({ incident_date: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Hour of Day (0-23)
                </label>
                <input
                  type="number"
                  min="0"
                  max="23"
                  value={form.incident_hour_of_the_day}
                  onChange={(e) => updateForm({ incident_hour_of_the_day: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Incident Type *
                </label>
                <select
                  value={form.incident_type}
                  onChange={(e) => updateForm({ incident_type: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="Single Vehicle Collision">Single Vehicle Collision</option>
                  <option value="Multi-vehicle Collision">Multi-vehicle Collision</option>
                  <option value="Parked Car">Parked Car</option>
                  <option value="Vehicle Theft">Vehicle Theft</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Collision Type
                </label>
                <select
                  value={form.collision_type}
                  onChange={(e) => updateForm({ collision_type: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="Front Collision">Front Collision</option>
                  <option value="Rear Collision">Rear Collision</option>
                  <option value="Side Collision">Side Collision</option>
                  <option value="?">Unknown / None</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Incident Severity *
                </label>
                <select
                  value={form.incident_severity}
                  onChange={(e) => updateForm({ incident_severity: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="Minor Damage">Minor Damage</option>
                  <option value="Major Damage">Major Damage</option>
                  <option value="Total Loss">Total Loss</option>
                  <option value="Trivial Damage">Trivial Damage</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Authorities Contacted
                </label>
                <select
                  value={form.authorities_contacted}
                  onChange={(e) => updateForm({ authorities_contacted: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="Police">Police</option>
                  <option value="Fire">Fire Department</option>
                  <option value="Ambulance">Ambulance</option>
                  <option value="None">None</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Incident State
                </label>
                <input
                  type="text"
                  maxLength={2}
                  value={form.incident_state}
                  onChange={(e) => updateForm({ incident_state: e.target.value.toUpperCase() })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 uppercase transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Incident City
                </label>
                <input
                  type="text"
                  value={form.incident_city}
                  onChange={(e) => updateForm({ incident_city: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Police Report Filed?
                </label>
                <select
                  value={form.police_report_available}
                  onChange={(e) => updateForm({ police_report_available: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                >
                  <option value="YES">YES</option>
                  <option value="NO">NO</option>
                  <option value="?">Pending / Unknown</option>
                </select>
              </div>
            </div>
          </div>
        )}

        {/* STEP 4: AMOUNTS & VEHICLE */}
        {step === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 4: Claim Financials & Vehicle Details</h2>
              <p className="text-xs text-slate-500 mt-1">
                Enter granular damage itemizations and vehicle identification numbers.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Injury Claim Amount ($)
                </label>
                <input
                  type="number"
                  value={form.injury_claim}
                  onChange={(e) => updateForm({ injury_claim: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Property Claim Amount ($)
                </label>
                <input
                  type="number"
                  value={form.property_claim}
                  onChange={(e) => updateForm({ property_claim: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Vehicle Damage Claim ($)
                </label>
                <input
                  type="number"
                  value={form.vehicle_claim}
                  onChange={(e) => updateForm({ vehicle_claim: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>
            </div>

            {/* Total Highlight */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase text-slate-500">
                  Computed Total Loss Claim
                </span>
                <p className="text-2xl font-mono font-extrabold text-[#2563EB]">
                  ${form.total_claim_amount.toLocaleString()}
                </p>
              </div>
              <span className="text-xs text-slate-500">
                Sum of injury, property, and vehicle damages
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Vehicle Make
                </label>
                <input
                  type="text"
                  value={form.vehicle_make}
                  onChange={(e) => updateForm({ vehicle_make: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Vehicle Model
                </label>
                <input
                  type="text"
                  value={form.vehicle_model}
                  onChange={(e) => updateForm({ vehicle_model: e.target.value })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Model Year
                </label>
                <input
                  type="number"
                  value={form.auto_year}
                  onChange={(e) => updateForm({ auto_year: Number(e.target.value) })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  VIN (Vehicle ID)
                </label>
                <input
                  type="text"
                  value={form.auto_vin}
                  onChange={(e) => updateForm({ auto_vin: e.target.value.toUpperCase() })}
                  className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 font-mono focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 uppercase transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Service Provider / Repair Facility / Clinic
              </label>
              <input
                type="text"
                value={form.provider_name}
                onChange={(e) => updateForm({ provider_name: e.target.value })}
                className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all"
              />
            </div>
          </div>
        )}

        {/* STEP 5: DOCUMENTS */}
        {step === 5 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 5: Supporting Evidence & Document Intake</h2>
              <p className="text-xs text-slate-500 mt-1">
                Attach official police reports, medical invoices, body shop estimates, and crash photos.
              </p>
            </div>

            {/* Dropzone */}
            <div className="border-2 border-dashed border-slate-300 hover:border-[#2563EB] rounded-xl p-8 text-center transition-all bg-slate-50">
              <FileUp className="h-10 w-10 text-[#2563EB] mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-800">
                Drag and drop files here, or click to browse
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Supports PDF, JPG, PNG, DICOM up to 25MB each
              </p>
            </div>

            {/* Uploaded Documents List */}
            <div className="space-y-2">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                Attached Documents ({form.documents.length})
              </p>
              {form.documents.map((doc, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200"
                >
                  <div className="flex items-center space-x-3">
                    <FileText className="h-4 w-4 text-[#2563EB]" />
                    <div>
                      <span className="text-xs font-semibold text-slate-900 block">{doc.name}</span>
                      <span className="text-[11px] text-slate-500 font-mono">
                        {doc.type} • {doc.size}
                      </span>
                    </div>
                  </div>
                  <span className="text-xs text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">Attached</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* STEP 6: REVIEW & SUBMIT */}
        {step === 6 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-[#0F172A]">Step 6: Final Verification & Pipeline Dispatch</h2>
              <p className="text-xs text-slate-500 mt-1">
                Confirm all intake variables. Once submitted, the automated 4-pillar fraud pipeline will execute in real-time.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-[#2563EB] uppercase text-[11px]">
                  Claimant & Policy
                </span>
                <p className="text-[#0F172A] font-semibold">{form.claimant_name}</p>
                <p className="text-slate-600 font-mono">Policy: {form.policy_number}</p>
                <p className="text-slate-600">Coverage: {form.policy_type}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-[#2563EB] uppercase text-[11px]">
                  Loss & Severity
                </span>
                <p className="text-[#0F172A] font-semibold">{form.incident_type} ({form.collision_type})</p>
                <p className="text-slate-600">Severity: {form.incident_severity}</p>
                <p className="text-slate-600">Location: {form.incident_city}, {form.incident_state}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-[#2563EB] uppercase text-[11px]">
                  Vehicle & Provider
                </span>
                <p className="text-[#0F172A] font-semibold">
                  {form.auto_year} {form.vehicle_make} {form.vehicle_model}
                </p>
                <p className="text-slate-600 font-mono">VIN: {form.auto_vin}</p>
                <p className="text-slate-600">Provider: {form.provider_name}</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
                <span className="font-bold text-[#2563EB] uppercase text-[11px]">
                  Total Claim Exposure
                </span>
                <p className="text-xl font-mono font-extrabold text-[#2563EB]">
                  ${form.total_claim_amount.toLocaleString()}
                </p>
                <p className="text-slate-600">
                  Injuries: ${form.injury_claim} • Property: ${form.property_claim} • Vehicle: ${form.vehicle_claim}
                </p>
              </div>
            </div>

            {/* Pipeline progress banner when submitting */}
            {isSubmitting && (
              <div className="p-5 rounded-xl bg-blue-50 border border-blue-200 space-y-3 shadow-xs">
                <div className="flex items-center space-x-3">
                  <Loader2 className="h-5 w-5 text-[#2563EB] animate-spin" />
                  <span className="text-sm font-bold text-blue-950">
                    Executing Real-Time Fraud Analysis Pipeline...
                  </span>
                </div>
                <div className="text-xs text-blue-800 font-mono pl-8">
                  {pipelineProgress}
                </div>
                <div className="w-full bg-blue-200 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-[#2563EB] h-1.5 rounded-full animate-pulse w-3/4" />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3 pt-6 mt-6 border-t border-slate-200">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(s - 1, 1))}
            disabled={step === 1 || isSubmitting}
            className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-50 bg-white border border-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all cursor-pointer w-full sm:w-auto"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>Previous</span>
          </button>

          {step < 6 ? (
            <button
              type="button"
              onClick={() => setStep((s) => Math.min(s + 1, 6))}
              className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-semibold text-white bg-[#2563EB] hover:bg-[#1D4ED8] shadow-xs transition-all cursor-pointer w-full sm:w-auto"
            >
              <span>Next Step</span>
              <ArrowRight className="h-4 w-4" />
            </button>
          ) : (
            <button
              type="button"
              onClick={handleFinalSubmit}
              disabled={isSubmitting}
              className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-lg text-xs font-bold text-white bg-[#2563EB] hover:bg-[#1D4ED8] shadow-xs transition-all disabled:opacity-50 cursor-pointer w-full sm:w-auto"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Processing Pipeline...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Submit Claim & Run Multi-Signal Fraud Analysis</span>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
