import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginPage from '@/app/login/page';
import { AppRouterContextProviderMock } from '@/mocks/AppRouterContextProviderMock';

// Mock the useRouter
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => ({
    get: () => null,
  }),
}));

describe('Security Tests', () => {
  it('should not allow XSS in redirect URL', () => {
    const maliciousRedirect = 'javascript:alert("XSS")';
    const { container } = render(
      <AppRouterContextProviderMock router={{ push: mockPush }}>
        <LoginPage />
      </AppRouterContextProviderMock>
    );

    const loginButton = screen.getByRole('button', { name: /login with github/i });
    
    // Simulate a click with a malicious redirect in the URL
    Object.defineProperty(window, 'location', {
        value: {
            href: '',
            search: `?redirect=${encodeURIComponent(maliciousRedirect)}`,
        },
        writable: true,
    });

    userEvent.click(loginButton);

    // The router should not be called with the malicious URL
    expect(mockPush).not.toHaveBeenCalledWith(maliciousRedirect);
  });
});