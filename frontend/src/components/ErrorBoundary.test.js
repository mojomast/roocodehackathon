import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorBoundary from './ErrorBoundary';

// Component that throws an error for testing
function ThrowError() {
  throw new Error('Test error');
  return <div>This should not render</div>;
}

// Component that renders normally
function NoError() {
  return <div>No error component</div>;
}

describe('ErrorBoundary', () => {
  // Suppress console.error for cleaner test output
  let originalError;

  beforeAll(() => {
    originalError = console.error;
    console.error = jest.fn();
  });

  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <NoError />
      </ErrorBoundary>
    );

    expect(screen.getByText('No error component')).toBeInTheDocument();
  });

  it('catches child component errors and renders fallback UI', () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong.')).toBeInTheDocument();
    expect(screen.getByText('Please refresh the page or try again later.')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;

    // Set to development to show error details
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText(/Test error/)).toBeInTheDocument();

    // Cleanup
    process.env.NODE_ENV = originalEnv;
  });

  it('hides error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV;

    // Set to production to hide error details
    process.env.NODE_ENV = 'production';

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Test error')).not.toBeInTheDocument();

    // Cleanup
    process.env.NODE_ENV = originalEnv;
  });

  it('renders error details with whitespace preserved', () => {
    const originalEnv = process.env.NODE_ENV;

    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    // Check that details element exists with pre-wrap style
    const details = screen.getByText(/Test error/).closest('details');
    expect(details).toBeInTheDocument();
    expect(details).toHaveStyle({ whiteSpace: 'pre-wrap' });

    process.env.NODE_ENV = originalEnv;
  });
});