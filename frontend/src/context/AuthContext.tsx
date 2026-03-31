import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { getMe, login as loginApi, register as registerApi } from "../api/auth";
import { getToken, removeToken, saveToken } from "../utils/storage";
import type { User } from "../types";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const me = await getMe();
      setUser(me);
    } catch {
      removeToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadUser();
  }, []);

  async function login(email: string, password: string) {
    const data = await loginApi(email, password);
    saveToken(data.access_token);
    const me = await getMe();
    setUser(me);
  }

  async function register(email: string, password: string) {
    await registerApi(email, password);
    await login(email, password);
  }

  function logout() {
    removeToken();
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      isAuthenticated: !!user
    }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}