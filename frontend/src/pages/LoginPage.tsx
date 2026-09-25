import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  ShieldCheck, 
  Lock, 
  Mail, 
  ArrowRight, 
  AlertCircle, 
  Eye, 
  EyeOff, 
  UserCheck, 
  Sparkles,
  Fingerprint,
  Building2,
  Scale,
  BrainCircuit,
  KeyRound
} from 'lucide-react';
import { UserRole } from '../types';

export const LoginPage: React.FC = () => {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email.trim(), password);
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err?.message || 'Invalid officer credentials. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (demoEmail: string, demoPass: string, demoRole: UserRole) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  const demoOfficers = [
    {
      name: 'Rahul Varma, CFE',
      role: 'INVESTIGATOR' as UserRole,
      title: 'Senior SIU Investigator',
      email: 'investigator@insurance.com',
      pass: 'investigator123',
      icon: Scale,
      color: 'from-amber-500/20 to-orange-500/20 border-amber-400/40 text-amber-200',
    },
    {
      name: 'Priya Sharma',
      role: 'CLAIMS_OFFICER' as UserRole,
      title: 'Claims Intake Officer',
      email: 'claims.officer@insurance.com',
      pass: 'claims123',
      icon: Building2,
      color: 'from-blue-500/20 to-cyan-500/20 border-blue-400/40 text-blue-200',
    },
    {
      name: 'Vikram Malhotra',
      role: 'ANALYST' as UserRole,
      title: 'Fraud Analytics Lead',
      email: 'analyst@insurance.com',
      pass: 'analyst123',
      icon: BrainCircuit,
      color: 'from-purple-500/20 to-pink-500/20 border-purple-400/40 text-purple-200',
    },
    {
      name: 'System Admin',
      role: 'ADMIN' as UserRole,
      title: 'IT & Security Admin',
      email: 'admin@insurance.com',
      pass: 'admin123',
      icon: KeyRound,
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-400/40 text-emerald-200',
    },
  ];

  return (
    <div className="min-h-screen bg-[#071739] bg-gradient-to-br from-[#061430] via-[#0B2556] to-[#0A3278] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden font-sans">
      {/* Background Ambient Glows */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header / Branding */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center z-10">
        <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 shadow-xl mb-4">
          <ShieldCheck className="h-10 w-10 text-blue-400" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          FraudShield Enterprise
        </h1>
        <p className="mt-2 text-xs sm:text-sm text-blue-200/80">
          Insurance Claims Fraud Detection & SIU Intelligence Console
        </p>
      </div>

      {/* Main Container */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0 z-10">
        <div className="bg-white/95 backdrop-blur-md py-8 px-6 sm:px-10 shadow-2xl rounded-2xl border border-white/40">
          
          <div className="mb-6 border-b border-slate-200 pb-4">
            <h2 className="text-lg font-bold text-slate-900 flex items-center">
              <Fingerprint className="h-5 w-5 text-blue-600 mr-2" />
              Officer Sign In
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Authorized insurance personnel & investigator access only.
            </p>
          </div>

          {error && (
            <div className="mb-5 bg-red-50 border border-red-200 rounded-xl p-3 flex items-start space-x-2 text-red-800 text-xs">
              <AlertCircle className="h-4 w-4 text-red-600 shrink-0 mt-0.5" />
              <div className="flex-1 font-medium">{error}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official Email Address
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
                  placeholder="officer@insurance.com"
                  className="block w-full pl-9 pr-3 py-2.5 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Security Password
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
                  placeholder="••••••••"
                  className="block w-full pl-9 pr-10 py-2.5 text-xs text-slate-900 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 bg-white"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center text-slate-600 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked
                  className="h-3.5 w-3.5 text-blue-600 focus:ring-blue-500 border-slate-300 rounded"
                />
                <span className="ml-2 text-[11px]">Remember credentials</span>
              </label>
              <span className="text-[11px] text-blue-600 hover:underline cursor-pointer">
                Forgot password?
              </span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all cursor-pointer"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Authenticating...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <span>Sign In to Platform</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </div>
              )}
            </button>
          </form>

          {/* Quick Demo Personas Fill */}
          <div className="mt-6 border-t border-slate-200 pt-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 flex items-center">
                <Sparkles className="h-3 w-3 text-amber-500 mr-1" />
                One-Click Quick Test Login
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {demoOfficers.map((officer) => {
                const Icon = officer.icon;
                return (
                  <button
                    key={officer.email}
                    type="button"
                    onClick={() => handleQuickLogin(officer.email, officer.pass, officer.role)}
                    className="p-2 border border-slate-200 hover:border-blue-400 bg-slate-50 hover:bg-blue-50/50 rounded-lg text-left transition-all group cursor-pointer"
                  >
                    <div className="flex items-center space-x-1.5">
                      <Icon className="h-3.5 w-3.5 text-blue-600" />
                      <span className="text-xs font-semibold text-slate-800 group-hover:text-blue-700 truncate">
                        {officer.name}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-500 truncate mt-0.5">
                      {officer.title}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Registration Link */}
          <div className="mt-6 text-center text-xs text-slate-600 border-t border-slate-100 pt-4">
            New Claims Officer or Investigator?{' '}
            <Link
              to="/register"
              className="font-bold text-blue-600 hover:text-blue-700 hover:underline inline-flex items-center"
            >
              <span>Register Officer Account</span>
              <ArrowRight className="h-3 w-3 ml-0.5" />
            </Link>
          </div>

        </div>

        {/* Security Footer */}
        <div className="mt-6 text-center text-[11px] text-blue-200/70">
          <p>Protected by SHA-256 JWT & PBKDF2 Encryption.</p>
          <p className="mt-0.5">Insurance Regulatory Compliance & ISO-27001 Certified System.</p>
        </div>
      </div>
    </div>
  );
};
