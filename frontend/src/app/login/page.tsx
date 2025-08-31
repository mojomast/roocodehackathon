"use client";
// frontend/src/app/login/page.tsx
import React, { useMemo, useCallback } from 'react';
import { useSearchParams } from 'next/navigation';

// FE-003: XSS prevention for login redirect handling
// Function to validate redirect URL against allowlist and encode it
const validateRedirectURL = (url: string | null): string | null => {
  if (!url) return null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' && !parsed.host.includes('localhost')) return null; // Allow http for localhost in dev
    const allowedDomains = ['localhost:3000', 'fixmydocs.com']; // Allowlist of safe domains
    if (!allowedDomains.some(domain => parsed.host.includes(domain))) return null;
    return decodeURIComponent(url); // Already encoded, but we trust it's safe now
  } catch {
    return null;
  }
};

/**
 * Renders the Login page with a GitHub OAuth button.
 * Implements XSS prevention by validating redirect URLs before auth flow.
 */
import { Suspense } from 'react';

const LoginPageContent: React.FC = () => {
  const searchParams = useSearchParams();

  // Memoize redirect parameter validation to prevent unnecessary re-computations
  const safeRedirect = useMemo(() => {
    const redirectParam = searchParams.get('redirect');
    return validateRedirectURL(redirectParam);
  }, [searchParams]);

  // Memoize the login handler to stable reference
  const handleLogin = useCallback(() => {
    const baseUrl = '/api/auth/github';
    const url = safeRedirect
      ? `${baseUrl}?redirect=${encodeURIComponent(safeRedirect)}`
      : baseUrl;
    window.location.href = url;
  }, [safeRedirect]);

  return (
    <main className="min-h-screen flex items-center justify-center" role="main">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg text-center max-w-md w-full mx-4 border border-primary-red" role="region" aria-labelledby="login-title">
        <h1 id="login-title" className="text-2xl font-bold mb-6 text-white font-heading">Welcome to FixMyDocs</h1>
        <p className="text-gray-300 mb-8">Please log in to continue.</p>
        <button
          onClick={handleLogin}
          className="inline-block bg-primary-red hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 ease-in-out focus:outline-none focus:ring-2 focus:ring-accent-cyan focus:ring-offset-2 focus:ring-offset-gray-800"
          aria-describedby="login-description"
        >
          Login with GitHub
        </button>
        <div id="login-description" className="sr-only">
          Click to authenticate with your GitHub account and access FixMyDocs
        </div>
      </div>
    </main>
  );
};

const LoginPage: React.FC = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginPageContent />
    </Suspense>
  );
};

export default LoginPage;