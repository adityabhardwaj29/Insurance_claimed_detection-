import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  ShieldCheck, 
  Lock, 
  Mail, 
  User, 
  BadgeCheck, 
  Building2, 
  ArrowRight, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  Scale, 
  BrainCircuit, 
  CheckCircle2,
  FileCheck2
} from 'lucide-react';
import { UserRole } from '../types';

export const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [roleId, setRoleId] = useState<UserRole>('INVESTIGATOR');
  const [department, setDepartment] = useState('Special Investigation Unit (SIU)');
  const [badgeNumber, setBadgeNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const roleOptions: { role: UserRole; title: string; defaultDept: string; icon: any }[] = [
    { 
      role: 'INVESTIGATOR', 
      title: 'SIU Field Investigator', 
      defaultDept: 'Special Investigation Unit (SIU)',
      icon: Scale 
    },
    { 
      role: 'CLAIMS_OFFICER', 
      title: 'Claims Intake & Triage Officer', 
      defaultDept: 'Claims Operations & Verification',
      icon: Building2 
    },
    { 
      role: 'SUPERVISOR', 
      title: 'Operations & Sign-Off Supervisor', 
      defaultDept: 'SIU Governance & Operations',
      icon: BadgeCheck 
    },
    { 
      role: 'ANALYST', 
      title: 'Fraud Analytics & Risk Modeler', 
      defaultDept: 'Risk Analytics & Data Science',
      icon: BrainCircuit 
    },
    { 
      role: 'ADMIN', 
      title: 'System & Security Administrator', 
      defaultDept: 'IT & Enterprise Security',
      icon: ShieldCheck 
    },
  ];

  const handleRoleChange = (role: UserRole) => {
    setRoleId(role);
    const found = roleOptions.find((r) => r.role === role);
    if (found) {
      setDepartment(found.defaultDept);
      if (!badgeNumber || badgeNumber.startsWith('OFF-') || badgeNumber.startsWith('SIU-')) {
        const prefix = role === 'INVESTIGATOR' ? 'SIU' : 'OFF';
        setBadgeNumber(`${prefix}-${Math.floor(1000 + Math.random() * 9000)}`);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please re-enter.');
      return;
    }

    setLoading(true);

    try {
      await register({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        password: password,
        role_id: roleId,
        department: department.trim(),
        badge_number: badgeNumber.trim() || `OFF-${Math.floor(1000 + Math.random() * 9000)}`,
      });
      navigate('/', { replace: true });
    } catch (err: any) {
      console.error('Registration failed:', err);
      setError(err?.message || 'Registration failed. Email may already be in use.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#071739] bg-gradient-to-br from-[#061430] via-[#0B2556] to-[#0A3278] flex flex-col justify-center py-10 sm:px-6 lg:px-8 relative overflow-hidden font-sans">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header / Branding */}
      <div className="sm:mx-auto sm:w-full sm:max-w-xl text-center z-10">
        <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 shadow-xl mb-3">
          <ShieldCheck className="h-9 w-9 text-blue-400" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          Register New Insurance Officer
        </h1>
        <p className="mt-1.5 text-xs sm:text-sm text-blue-200/80">
          Create an official personnel credential with role-based access control.
        </p>
      </div>

      {/* Main Form Container */}
      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-xl px-4 sm:px-0 z-10">
        <div className="bg-white/95 backdrop-blur-md py-8 px-6 sm:px-10 shadow-2xl rounded-2xl border border-white/40">
          
          <div className="mb-5 border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 flex items-center">
                <FileCheck2 className="h-4.5 w-4.5 text-blue-600 mr-2" />
                Officer Onboarding Form
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                All accounts are audited under IRDAI / Enterprise SIU Guidelines.
              </p>
            </div>
            <span className="hidden sm:inline-block px-2.5 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-[11px] font-semibold">
              Live DB Sync
            </span>
          </div>

          {error && (
            <div className="mb-5 bg-red-50 border border-red-200 rounded-xl p-3 flex items-start space-x-2 text-red-800 text-xs">
              <AlertCircle className="h-4 w-4 text-red-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            
            {/* Full Name & Email */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Name & Title *
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <User className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Officer Vikram Sharma"
                    className="block w-full pl-9 pr-3 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Official Email Address *
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Mail className="h-4 w-4" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="v.sharma@insurance.com"
                    className="block w-full pl-9 pr-3 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Role / Designation Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                Designation / Access Role *
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {roleOptions.slice(0, 3).map((r) => {
                  const Icon = r.icon;
                  const isSelected = roleId === r.role;
                  return (
                    <button
                      key={r.role}
                      type="button"
                      onClick={() => handleRoleChange(r.role)}
                      className={`p-2.5 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? 'border-blue-600 bg-blue-50/80 ring-2 ring-blue-500/20 text-blue-900'
                          : 'border-slate-200 hover:border-slate-300 bg-slate-50/50 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <Icon className={`h-4 w-4 ${isSelected ? 'text-blue-600' : 'text-slate-500'}`} />
                        {isSelected && <CheckCircle2 className="h-3.5 w-3.5 text-blue-600" />}
                      </div>
                      <span className="text-xs font-bold leading-tight">{r.title}</span>
                    </button>
                  );
                })}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                {roleOptions.slice(3).map((r) => {
                  const Icon = r.icon;
                  const isSelected = roleId === r.role;
                  return (
                    <button
                      key={r.role}
                      type="button"
                      onClick={() => handleRoleChange(r.role)}
                      className={`p-2.5 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? 'border-blue-600 bg-blue-50/80 ring-2 ring-blue-500/20 text-blue-900'
                          : 'border-slate-200 hover:border-slate-300 bg-slate-50/50 text-slate-700'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <Icon className={`h-4 w-4 ${isSelected ? 'text-blue-600' : 'text-slate-500'}`} />
                        {isSelected && <CheckCircle2 className="h-3.5 w-3.5 text-blue-600" />}
                      </div>
                      <span className="text-xs font-bold leading-tight">{r.title}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Department & Badge Number */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Department / Unit
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Building2 className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    placeholder="Department name"
                    className="block w-full pl-9 pr-3 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Badge / Officer ID
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <BadgeCheck className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    value={badgeNumber}
                    onChange={(e) => setBadgeNumber(e.target.value)}
                    placeholder="e.g. SIU-8821"
                    className="block w-full pl-9 pr-3 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                </div>
              </div>
            </div>

            {/* Passwords */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Security Password *
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min. 6 chars"
                    className="block w-full pl-9 pr-9 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 cursor-pointer"
                  >
                    {showPassword ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Confirm Password *
                </label>
                <div className="relative rounded-lg shadow-xs">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Lock className="h-4 w-4" />
                  </div>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Re-enter password"
                    className="block w-full pl-9 pr-3 py-2 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Enrolling Officer in Database...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span>Register & Launch Officer Console</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              )}
            </button>
          </form>

          {/* Already have account */}
          <div className="mt-5 text-center text-xs text-slate-600 border-t border-slate-100 pt-3">
            Already have an officer account?{' '}
            <Link
              to="/login"
              className="font-bold text-blue-600 hover:text-blue-700 hover:underline inline-flex items-center"
            >
              <span>Sign In to Existing Account</span>
              <ArrowRight className="h-3 w-3 ml-0.5" />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};
