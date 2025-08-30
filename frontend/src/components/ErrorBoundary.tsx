'use client';

import { Component, ErrorInfo, ReactNode } from 'react';

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

// Error boundary component to handle unhandled exceptions in the React tree
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to console for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  override render() {
    if (this.state.hasError) {
      // Render fallback UI when an error occurs
      return (
        <div className="text-center p-8">
            <h2 className="text-2xl font-bold text-red-600">Oops! Something went wrong.</h2>
            <p className="text-gray-700 mt-2">We've encountered an unexpected error. Please try refreshing the page.</p>
            {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="mt-4 p-4 bg-red-100 border border-red-400 rounded text-left">
                    <summary className="font-bold cursor-pointer">Error Details</summary>
                    <pre className="mt-2 text-sm text-red-800 whitespace-pre-wrap">
                        {this.state.error.stack || this.state.error.toString()}
                    </pre>
                </details>
            )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;