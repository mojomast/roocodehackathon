import type { Metadata } from "next";
import "./globals.css";
import { MswComponent } from "./MswComponent";
import ErrorBoundary from "../components/ErrorBoundary";
import { TopNav } from "../components/TopNav";
import ParticleBackground from "../components/ParticleBackground";

export const metadata: Metadata = {
  title: "RooCode",
  description: "Code generation and GitHub integration platform",
  other: {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' data: https:; font-src 'self' data: https://fonts.gstatic.com; connect-src 'self' https:;",
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
      <body className="antialiased flex bg-background">
        <ParticleBackground />
        <MswComponent />
        <div className="relative z-10 flex flex-col w-full">
          <TopNav />
          <main className="flex-1 p-8">
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
          </main>
        </div>
      </body>
    </html>
  );
}
