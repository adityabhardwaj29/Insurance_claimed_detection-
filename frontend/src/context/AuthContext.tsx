import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../services/api';
import { User, UserRole } from '../types';

interface AuthContextType {
  user: User | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  switchRole: (role: UserRole) => void;
  login: (email: string, role?: UserRole) => Promise<void>;
  logout: () => void;
}

const DEMO_PERSONAS: Record<UserRole, { email: string; name: string; department: string }> = {
  CLAIMS_OFFICER: {
    email: 'claims.officer@insurance.com',
    name: 'Sarah Connor',
    department: 'Claims Intake & Triage',
  },
  INVESTIGATOR: {
    email: 'investigator@insurance.com',
    name: 'John Doe, CFE',
    department: 'Special Investigation Unit (SIU)',
  },
  SUPERVISOR: {
    email: 'supervisor@insurance.com',
    name: 'Marcus Vance',
    department: 'Claims Operations Management',
  },
  ANALYST: {
    email: 'analyst@insurance.com',
    name: 'Elena Rostova',
    department: 'Fraud Analytics & Risk Modeling',
  },
  ADMIN: {
    email: 'admin@insurance.com',
    name: 'David Chen',
    department: 'System & Security Administration',
  },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>('CLAIMS_OFFICER');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const rawRole = localStorage.getItem('user_role') as UserRole;
        const validRole = (rawRole && DEMO_PERSONAS[rawRole]) ? rawRole : 'CLAIMS_OFFICER';
        setRole(validRole);
        const persona = DEMO_PERSONAS[validRole];
        setUser({
          id: 'usr_' + validRole.toLowerCase(),
          email: persona.email,
          full_name: persona.name,
          role: validRole,
          department: persona.department,
        });
      } catch (err) {
        console.error('Error initializing auth', err);
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
    localStorage.setItem('user_role', newRole);
    const persona = DEMO_PERSONAS[newRole];
    setUser({
      id: 'usr_' + newRole.toLowerCase(),
      email: persona.email,
      full_name: persona.name,
      role: newRole,
      department: persona.department,
    });
  };

  const login = async (email: string, selectedRole?: UserRole) => {
    setIsLoading(true);
    try {
      const res = await api.login(email, selectedRole);
      setUser(res.user);
      setRole(res.user.role);
      localStorage.setItem('user_role', res.user.role);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    api.setToken(null);
    setUser(null);
    localStorage.removeItem('user_role');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        isLoading,
        switchRole,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: {
        id: 'usr_claims_officer',
        email: 'claims.officer@insurance.com',
        full_name: 'Sarah Connor',
        role: 'CLAIMS_OFFICER' as UserRole,
        department: 'Claims Operations',
      },
      role: 'CLAIMS_OFFICER' as UserRole,
      isAuthenticated: true,
      isLoading: false,
      login: async () => {},
      logout: () => {},
      switchRole: () => {},
    };
  }
  return context;
};
