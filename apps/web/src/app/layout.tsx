import React from 'react';
import './globals.css';
import { AuthProvider } from '../lib/auth';
import { Navbar } from '../components/Navbar';

export const metadata = {
  title: 'Makkal Kural | Citizen Grievance Intelligence System',
  description: 'AI-powered unified citizen grievance intelligence system for Tamil Nadu.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased">
        <AuthProvider>
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="bg-tn-navy text-slate-300 py-6 border-t border-yellow-500/20 text-center text-xs">
            <div className="max-w-7xl mx-auto px-4 space-y-2">
              <p className="font-semibold text-amber-300">
                Government of Tamil Nadu - e-Governance Division & Civic Redressal Authority
              </p>
              <p className="text-slate-400">
                © 2026 Makkal Kural. Privacy-by-design | Dual Language (Tamil & English) Support.
              </p>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
