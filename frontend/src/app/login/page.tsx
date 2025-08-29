// frontend/src/app/login/page.tsx
import React from 'react';
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
const LoginPage: React.FC = () => {
  const searchParams = useSearchParams();
  const redirectParam = searchParams.get('redirect');
  const safeRedirect = validateRedirectURL(redirectParam);

  // FE-003: Handle login with validated redirect parameter
  const handleLogin = () => {
    const baseUrl = '/api/auth/github';
    const url = safeRedirect
      ? `${baseUrl}?redirect=${encodeURIComponent(safeRedirect)}`
      : baseUrl;
    window.location.href = url;
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Welcome to FixMyDocs</h1>
        <p className="text-gray-600 mb-8">Please log in to continue.</p>
        <button
          onClick={handleLogin}
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 ease-in-out"
        >
          Login with GitHub
        </button>
      </div>
    </div>
  );
};

export default LoginPage;