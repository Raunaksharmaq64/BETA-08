"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { apiClient } from "../services/apiClient";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "CANDIDATE" | "RECRUITER" | "ADMIN";
  status: "PENDING_VERIFICATION" | "ACTIVE" | "SUSPENDED" | "DELETION_PENDING" | "DELETED";
  is_email_verified: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    try {
      const resp = await apiClient<User>("/auth/me");
      setUser(resp.data);
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      await apiClient("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await refreshUser();
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (fullName: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      await apiClient("/auth/register", {
        method: "POST",
        body: JSON.stringify({ full_name: fullName, email, password }),
      });
      await login(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient("/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
