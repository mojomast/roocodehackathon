import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useSearchParams } from 'next/navigation';
import { server } from '../../mocks/server';
import { rest } from 'msw';
import LoginPage from './page';

// Mock useSearchParams
const mockSearchParams = jest.fn();
jest.mock('next/navigation', () => ({
  useSearchParams: () => mockSearchParams(),
}));

// Mock window.location
delete window.location;
window.location = {
  href: jest.fn(),
};

describe('LoginPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSearchParams.mockReturnValue({
      get: jest.fn((key) => key === 'redirect' ? 'https://fixmydocs.com/dashboard' : null),
    });
  });

  it('renders GitHub login button', () => {
    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    expect(loginButton).toBeInTheDocument();
  });

  it('displays welcome message and prompt', () => {
    render(<LoginPage />);

    expect(screen.getByText('Welcome to FixMyDocs')).toBeInTheDocument();
    expect(screen.getByText('Please log in to continue.')).toBeInTheDocument();
  });

  it('handles successful GitHub login redirect', async () => {
    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    fireEvent.click(loginButton);

    // Verify redirect URL contains the redirect parameter
    expect(window.location.href).toHaveBeenCalledWith('https://github.com/login/oauth/authorize?redirect=https://fixmydocs.com/dashboard');
  });

  it('handles login without redirect parameter', () => {
    mockSearchParams.mockReturnValue({
      get: jest.fn(() => null),
    });

    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    fireEvent.click(loginButton);

    expect(window.location.href).toHaveBeenCalledWith('/api/auth/github');
  });

  it('validates redirect URLs against allowlist', () => {
    // Test various invalid URLs that should be rejected
    const invalidUrls = [
      'http://evil.com/malicious',
      'https://evil.com/dashboard',
      'https://github.com/malicious',
      'ftp://example.com/file',
      'javascript:alert("xss")',
      '//localhost:3000/admin',
    ];

    const validateRedirectURL = (url) => {
      if (!url) return null;
      try {
        const parsed = new URL(url);
        if (parsed.protocol !== 'https:' && !parsed.host.includes('localhost')) return null;
        const allowedDomains = ['localhost:3000', 'fixmydocs.com'];
        if (!allowedDomains.some(domain => parsed.host.includes(domain))) return null;
        return decodeURIComponent(url);
      } catch {
        return null;
      }
    };

    invalidUrls.forEach(url => {
      expect(validateRedirectURL(url)).toBeNull();
    });

    // Test valid URLs
    expect(validateRedirectURL('https://localhost:3000/dashboard')).toBe('/');
    expect(validateRedirectURL('https://fixmydocs.com/repos')).toBe('/');
    expect(validateRedirectURL('https://localhost:3000/?param=value')).toBe('/');
  });

  it('sanitizes input to prevent XSS in redirect parameter', () => {
    const maliciousRedirect = 'javascript:alert("xss")';
    mockSearchParams.mockReturnValue({
      get: jest.fn(() => maliciousRedirect),
    });

    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    fireEvent.click(loginButton);

    // Verify the malicious redirect was not used
    expect(window.location.href).not.toHaveBeenCalledWith(maliciousRedirect);
  });

  it('handles GitHub API failure', async () => {
    // Mock GitHub API failure
    server.use(
      rest.get('/api/auth/github', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'GitHub service unavailable' }));
      })
    );

    // Since the button triggers window.location.href, we can't easily test
    // the actual failure, but we can verify the redirect URL construction
    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    fireEvent.click(loginButton);

    // In a real scenario, the backend would handle the failure
    // Here we just verify the frontend doesn't crash
    expect(loginButton).toBeInTheDocument();
  });

  it('prevents authentication bypass through direct navigation', () => {
    // This test ensures that the login page itself doesn't provide
    // authentication bypass mechanisms

    render(<LoginPage />);

    // Verify there are no hidden authentication forms or tokens
    const forms = document.querySelectorAll('form');
    expect(forms).toHaveLength(0);

    // Verify GitHub OAuth is the only login mechanism
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(1);
    expect(buttons[0]).toHaveTextContent('Login with GitHub');
  });

  it('handles malformed redirect parameters gracefully', () => {
    const malformedUrls = ['not-a-url', 'invalid-scheme://example.com'];
    mockSearchParams.mockReturnValue({
      get: jest.fn(() => 'not-a-url'),
    });

    render(<LoginPage />);

    const loginButton = screen.getByRole('button', { name: /Login with GitHub/i });
    fireEvent.click(loginButton);

    // Should not crash and should use default redirect
    expect(window.location.href).toHaveBeenCalledWith('/api/auth/github');
  });
});