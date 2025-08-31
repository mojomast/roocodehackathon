"use client";
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { clearAuthToken, setAuthToken } from '../utils/apiClient';

const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    if (token) {
      setAuthToken(token);
      setIsAuthenticated(true);
    } else {
      router.push('/login');
    }
  }, [router]);

  const logout = () => {
    localStorage.removeItem('authToken');
    clearAuthToken();
    setIsAuthenticated(false);
    router.push('/login');
  };

  return { isAuthenticated, logout };
};

export default useAuth;