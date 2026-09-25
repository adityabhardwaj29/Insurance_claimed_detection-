import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../services/api';
import { User, UserRole } from '../types';

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  role_id: string;
  department?: string;
  badge_number?: string;
}

interface AuthContextType {
  user: User | null;
  role: UserRole;
  isAuthenticated: boolean;
  isLoading: boolean;
  switchRole: (role: UserRole) => void;
  login: (email: string, password?: string, role?: UserRole) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<UserRole>('CLAIMS_OFFICER');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      try {
        const currentUser = await api.getMe();
        setUser(currentUser);
        setRole(currentUser.role);
        localStorage.setItem('user_role', currentUser.role);
      } catch (err) {
        console.warn('Session verification failed, logging out:', err);
        api.setToken(null);
        setUser(null);
        localStorage.removeItem('user_role');
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const switchRole = (newRole: UserRole) => {
    setRole(newRole);
    localStorage.setItem('user_role', newRole);
    if (user) {
      setUser({
        ...user,
        role: newRole,
      });
    }
  };

  const login = async (email: string, password?: string, selectedRole?: UserRole) => {
    setIsLoading(true);
    try {
      const res = await api.login(email, password, selectedRole);
      setUser(res.user);
      setRole(res.user.role);
      localStorage.setItem('user_role', res.user.role);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: RegisterPayload) => {
    setIsLoading(true);
    try {
      const res = await api.register(payload);
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
    localStorage.removeItem('auth_token');
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
        register,
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
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
