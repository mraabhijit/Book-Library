import { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  // Check if user is logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    if (initialized) return;

    const token = localStorage.getItem('authToken');
    if (!token) {
      setInitialized(true);
      return;
    }

    setLoading(true);
    try {
      const response = await authAPI.getCurrentUser();
      setUser(response.data);
    } catch (error) {
      if (error.response?.status === 401) {
        console.log('No valid session found');
      } else {
        console.error('Error fetching user: ', error);
      }

      localStorage.removeItem('authToken');
      localStorage.removeItem('tokenType');
      setUser(null);
    } finally {
      setLoading(false);
      setInitialized(true);
    }
  };

  const login = (token, userData) => {
    localStorage.setItem('authToken', token);
    setUser(userData);
    setInitialized(true);
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('tokenType');
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    checkAuth,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAAuth must be used within AuthProvider');
  }

  return context;
}
