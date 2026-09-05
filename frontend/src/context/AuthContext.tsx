'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, Tenant } from '@/lib/types';
import { getAuthToken, setAuthToken, fetchUserProfile, loginUser, registerUser } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  tenant: Tenant | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (companyName: string, fullName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const loadUser = useCallback(async () => {
    try {
      const storedToken = getAuthToken();
      if (storedToken) {
        setToken(storedToken);
        const profile = await fetchUserProfile();
        setUser(profile);
      } else {
        // Fetch default dev/demo profile
        try {
          const profile = await fetchUserProfile();
          setUser(profile);
        } catch {
          setUser(null);
        }
      }
    } catch (err) {
      console.warn('Could not load user profile:', err);
      setAuthToken(null);
      setToken(null);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await loginUser(email, password);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (companyName: string, fullName: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await registerUser(companyName, fullName, email, password);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    await loadUser();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        tenant: user?.tenant || null,
        token,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
