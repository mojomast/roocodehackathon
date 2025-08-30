"use client";
// frontend/src/app/login/Login.tsx
import React, { useMemo, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';

// FE-003: XSS prevention for login redirect handling
// Function to validate redirect URL against allowlist and encode it
const getSafeRedirectUrl = (redirectParam: string | null): string => {
  const allowlist = ['/dashboard', '/repos', '/jobs'];
  if (redirectParam && allowlist.includes(redirectParam)) {
    return encodeURIComponent(redirectParam);
  }
  return '';
};

const Login = () => {
  const searchParams = useSearchParams();
  const redirectUrl = searchParams.get('redirect');

  // FE-003: Memoize the safe redirect URL to prevent re-computation on every render
  const safeRedirectUrl = useMemo(() => getSafeRedirectUrl(redirectUrl), [redirectUrl]);

  // FE-003: Use useCallback to memoize the login handler
  const handleLogin = useCallback(() => {
    const finalRedirectUrl = safeRedirectUrl ? `?redirect=${safeRedirectUrl}` : '';
    window.location.href = `http://localhost:8000/auth/github/login${finalRedirectUrl}`;
  }, [safeRedirectUrl]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100" role="main">
      <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md w-full mx-4" role="region" aria-labelledby="login-title">
        <h1 id="login-title" className="text-2xl font-bold mb-6 text-gray-800">Welcome to FixMyDocs</h1>
        <p className="text-gray-600 mb-8">Please log in to continue.</p>
        <button
          onClick={handleLogin}
          className="bg-gray-800 text-white px-6 py-3 rounded-lg hover:bg-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-800"
          aria-describedby="login-description"
        >
          Login with GitHub
        </button>
        <div id="login-description" className="sr-only">
          Click this button to log in with your GitHub account.
        </div>
      </div>
    </main>
  );
};

export default Login;