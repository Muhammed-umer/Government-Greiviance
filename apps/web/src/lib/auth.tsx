'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchApi } from './api';

interface User {
  id: str;
  phone_number: str;
  full_name?: str;
  district?: str;
  roles: Array<{ id: string; name: string }>;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  currentRole: string;
  language: 'en' | 'ta';
  setLanguage: (lang: 'en' | 'ta') => void;
  setCurrentRole: (role: string) => void;
  loginWithOtp: (phone: string, otp: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [currentRole, setCurrentRole] = useState<string>('citizen');
  const [language, setLanguage] = useState<'en' | 'ta'>('en');

  useEffect(() => {
    const savedToken = localStorage.getItem('tn_token');
    const savedRole = localStorage.getItem('tn_role');
    const savedLang = localStorage.getItem('tn_lang') as 'en' | 'ta';

    if (savedRole) setCurrentRole(savedRole);
    if (savedLang) setLanguage(savedLang);

    if (savedToken) {
      setToken(savedToken);
      fetchApi('/auth/me')
        .then((u) => setUser(u))
        .catch(() => {
          localStorage.removeItem('tn_token');
          setToken(null);
        });
    }
  }, []);

  const loginWithOtp = async (phone: string, otp: string) => {
    const data = await fetchApi('/auth/verify-otp', {
      method: 'POST',
      body: JSON.stringify({ phone_number: phone, otp_code: otp }),
    });

    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('tn_token', data.access_token);
    
    if (data.user.roles && data.user.roles.length > 0) {
      const roleName = data.user.roles[0].name;
      setCurrentRole(roleName);
      localStorage.setItem('tn_role', roleName);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('tn_token');
  };

  const setLanguageHandler = (lang: 'en' | 'ta') => {
    setLanguage(lang);
    localStorage.setItem('tn_lang', lang);
  };

  const setRoleHandler = (role: string) => {
    setCurrentRole(role);
    localStorage.setItem('tn_role', role);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        currentRole,
        language,
        setLanguage: setLanguageHandler,
        setCurrentRole: setRoleHandler,
        loginWithOtp,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
