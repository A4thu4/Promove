"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id?: number;
  email?: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedName = sessionStorage.getItem('display_name');
    if (savedName) {
      setUser({ id: 0, full_name: savedName });
    }
    setIsLoading(false);
  }, []);

  const login = (newUser: User) => {
    setUser(newUser);
    if (newUser.full_name) {
      sessionStorage.setItem('display_name', newUser.full_name);
    }
  };

  const logout = () => {
    setUser(null);
    sessionStorage.removeItem('display_name');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
