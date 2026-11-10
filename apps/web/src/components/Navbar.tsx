'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '../lib/auth';
import { translations } from '../lib/i18n';
import { Shield, Languages, UserCheck, FileText, ClipboardList, BarChart3, AlertCircle } from 'lucide-react';

export function Navbar() {
  const { user, language, setLanguage, currentRole, setCurrentRole, logout } = useAuth();
  const t = translations[language];

  return (
    <header className="sticky top-0 z-50 bg-tn-navy text-white shadow-lg border-b border-yellow-500/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Emblem */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-tn-gold text-tn-navy flex items-center justify-center font-bold text-xl shadow-md border border-white">
              TN
            </div>
            <div>
              <h1 className="font-bold text-base sm:text-lg leading-tight tracking-wide text-amber-300">
                {t.portalTitle}
              </h1>
              <p className="text-xs text-slate-300 hidden sm:block">{t.portalSubtitle}</p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <Link href="/petition/new" className="flex items-center space-x-1 hover:text-amber-300 transition-colors">
              <FileText className="w-4 h-4" />
              <span>{t.submitComplaint}</span>
            </Link>
            <Link href="/petition/my-petitions" className="flex items-center space-x-1 hover:text-amber-300 transition-colors">
              <ClipboardList className="w-4 h-4" />
              <span>{t.myPetitions}</span>
            </Link>
            <Link href="/officer/queue" className="flex items-center space-x-1 hover:text-amber-300 transition-colors">
              <Shield className="w-4 h-4" />
              <span>{t.officerPortal}</span>
            </Link>
            <Link href="/officer/triage" className="flex items-center space-x-1 hover:text-amber-300 transition-colors">
              <AlertCircle className="w-4 h-4" />
              <span>{t.triageQueue}</span>
            </Link>
            <Link href="/admin/dashboard" className="flex items-center space-x-1 hover:text-amber-300 transition-colors">
              <BarChart3 className="w-4 h-4" />
              <span>{t.adminDashboard}</span>
            </Link>
          </nav>

          {/* Language & Role Switcher */}
          <div className="flex items-center space-x-3">
            {/* Language Toggle */}
            <button
              onClick={() => setLanguage(language === 'en' ? 'ta' : 'en')}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-md bg-white/10 hover:bg-white/20 text-xs font-semibold border border-white/20 transition-all"
            >
              <Languages className="w-4 h-4 text-amber-300" />
              <span>{language === 'en' ? 'தமிழ்' : 'English'}</span>
            </button>

            {/* Local Role Switcher for Testing */}
            <div className="hidden lg:flex items-center bg-white/10 rounded-md px-2 py-1 text-xs border border-white/20">
              <UserCheck className="w-3.5 h-3.5 text-amber-300 mr-1.5" />
              <select
                value={currentRole}
                onChange={(e) => setCurrentRole(e.target.value)}
                className="bg-transparent text-white font-medium focus:outline-none cursor-pointer"
              >
                <option value="citizen" className="text-black">Role: Citizen</option>
                <option value="officer" className="text-black">Role: Officer</option>
                <option value="supervisor" className="text-black">Role: Supervisor</option>
                <option value="admin" className="text-black">Role: Admin</option>
                <option value="auditor" className="text-black">Role: Auditor</option>
              </select>
            </div>

            {/* Login / User Status */}
            {user ? (
              <button
                onClick={logout}
                className="px-3 py-1.5 rounded-md bg-red-600/80 hover:bg-red-700 text-xs font-semibold text-white transition-colors"
              >
                {t.logout}
              </button>
            ) : (
              <Link
                href="/login"
                className="px-3.5 py-1.5 rounded-md bg-amber-400 hover:bg-amber-300 text-tn-navy font-bold text-xs transition-colors shadow"
              >
                {t.login}
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
