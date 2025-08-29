// frontend/src/app/login/page.tsx
import React from 'react';

/**
 * Renders the Login page with a GitHub OAuth button.
 * This page serves as a placeholder for initiating the OAuth flow.
 */
const LoginPage: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">Welcome to FixMyDocs</h1>
        <p className="text-gray-600 mb-8">Please log in to continue.</p>
        <button
          onClick={() => { window.location.href = '/api/auth/github'; }}
          className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition duration-300 ease-in-out"
        >
          Login with GitHub
        </button>
      </div>
    </div>
  );
};

export default LoginPage;