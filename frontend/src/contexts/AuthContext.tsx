import { createContext, useContext, useReducer, useEffect } from "react";
import type { ReactNode } from "react";
import type { User, AuthState } from "../types";
import { authService } from "../services";

interface AuthContextType {
  state: AuthState;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: "AUTH_START" }
  | { type: "AUTH_SUCCESS"; payload: { user: User; token: string } }
  | { type: "AUTH_ERROR"; payload: string }
  | { type: "LOGOUT" }
  | { type: "UPDATE_USER"; payload: User };

const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
};

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case "AUTH_START":
      return {
        ...state,
        isLoading: true,
      };
    case "AUTH_SUCCESS":
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case "AUTH_ERROR":
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case "LOGOUT":
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case "UPDATE_USER":
      return {
        ...state,
        user: action.payload,
      };
    default:
      return state;
  }
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  useEffect(() => {
    // Check if user is already logged in
    // Skip auto-login only for demo pages and landing page
    const currentPath = window.location.pathname;
    if (currentPath === '/' || currentPath.startsWith('/demo/')) {
      return; // Don't auto-login for landing page and demo pages
    }

    const token = authService.getAuthToken();
    const user = authService.getCurrentUser();

    if (token && user) {
      dispatch({
        type: "AUTH_SUCCESS",
        payload: { user, token },
      });
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      dispatch({ type: "AUTH_START" });
      const result = await authService.login({ email, password });
      dispatch({
        type: "AUTH_SUCCESS",
        payload: result,
      });
    } catch (error) {
      dispatch({ type: "AUTH_ERROR", payload: (error as Error).message });
      throw error;
    }
  };

  const register = async (userData: any) => {
    try {
      dispatch({ type: "AUTH_START" });
      const result = await authService.register(userData);
      dispatch({
        type: "AUTH_SUCCESS",
        payload: result,
      });
    } catch (error) {
      dispatch({ type: "AUTH_ERROR", payload: (error as Error).message });
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
      dispatch({ type: "LOGOUT" });
    } catch (error) {
      console.error("Logout error:", error);
      dispatch({ type: "LOGOUT" });
    }
  };

  const updateProfile = async (userData: Partial<User>) => {
    try {
      const updatedUser = await authService.updateProfile(userData);
      dispatch({ type: "UPDATE_USER", payload: updatedUser });
    } catch (error) {
      throw error;
    }
  };

  const value: AuthContextType = {
    state,
    login,
    register,
    logout,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
