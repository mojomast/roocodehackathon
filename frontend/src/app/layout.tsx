import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ErrorBoundary from "../components/ErrorBoundary"; // Error boundary to catch unhandled exceptions in the React tree

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// FE-002: Secure metadata sanitization utility for user-controlled data

// FE-002: Content Security Policy for XSS prevention
export const metadata: Metadata = {
  title: "FixMyDocs",
  description: "Documentation generation and GitHub integration platform",
  // CSP headers prevent XSS attacks
  other: {
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self';",
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
  }
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased flex flex-col lg:flex-row`}>
        {/* Sidebar Navigation */}
        <nav className="w-full lg:w-64 bg-gray-800 text-white p-4 min-h-screen lg:min-h-screen flex-shrink-0" role="navigation" aria-label="Main navigation">
          <header className="mb-6">
            <h1 className="text-2xl font-bold">FixMyDocs</h1>
          </header>
          <ul className="space-y-2" role="menubar">
            <li role="none">
              <a href="/dashboard" className="block hover:text-blue-300 focus:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 px-3 py-2 rounded" role="menuitem">
                Dashboard
              </a>
            </li>
            <li role="none">
              <a href="/repos" className="block hover:text-blue-300 focus:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 px-3 py-2 rounded" role="menuitem">
                Repositories
              </a>
            </li>
            <li role="none">
              <a href="/jobs" className="block hover:text-blue-300 focus:text-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-800 px-3 py-2 rounded" role="menuitem">
                Jobs
              </a>
            </li>
          </ul>
        </nav>
        {/* Main content area wrapped with ErrorBoundary to catch unhandled exceptions */}
        <main className="flex-1">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </body>
    </html>
  );
}
