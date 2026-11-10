'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '../lib/auth';
import { translations } from '../lib/i18n';
import { FilePlus, Search, ShieldCheck, Cpu, MapPin, Users, CheckCircle, ArrowRight } from 'lucide-react';

export default function Home() {
  const { language } = useAuth();
  const t = translations[language];

  return (
    <div className="space-y-10 py-4">
      {/* Hero Section */}
      <section className="relative rounded-2xl bg-gradient-to-r from-tn-navy via-slate-900 to-tn-navy text-white p-8 sm:p-12 overflow-hidden shadow-xl border border-yellow-500/20">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-80 h-80 rounded-full bg-tn-gold/10 blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-3xl space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-400/40 text-amber-300 text-xs font-semibold">
            <ShieldCheck className="w-4 h-4" />
            <span>Official Government Digital Service | தமிழ்நாடு அரசு</span>
          </div>

          <div className="space-y-2">
            <p className="text-amber-300 text-sm sm:text-base font-bold uppercase tracking-[0.2em]">
              Makkal Kural
            </p>
            <p className="text-slate-300 text-xs sm:text-sm font-semibold uppercase tracking-[0.12em]">
              AI-Powered Unified Citizen Grievance Intelligence System
            </p>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            {language === 'ta'
              ? 'உங்கள் குறைக்கு விரைவான தீர்வு - குரல் மற்றும் உரை மூலமாக'
              : 'Empowering Citizens with Instant AI-Assisted Grievance Redressal'}
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            {language === 'ta'
              ? 'மின்சாரம், குடிநீர், சாக்கடை, போக்குவரத்து மற்றும் குப்பை தொடர்பான புகார்களை தமிழ் அல்லது ஆங்கிலத்தில் பதிவு செய்யுங்கள்.'
              : 'Submit civic grievances via Tamil/English voice recording or text. Auto-routed to the correct department with intelligent duplicate incident deduplication.'}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 pt-2">
            <Link
              href="/petition/new"
              className="flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-tn-navy font-bold text-sm shadow-lg transition-all transform hover:-translate-y-0.5"
            >
              <FilePlus className="w-5 h-5" />
              <span>{t.submitComplaint}</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              href="/petition/my-petitions"
              className="flex items-center justify-center space-x-2 px-6 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm border border-white/20 transition-all"
            >
              <Search className="w-5 h-5" />
              <span>{t.trackStatus}</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Core Principle Banner */}
      <section className="bg-amber-50 rounded-xl border border-amber-200 p-6 flex flex-col md:flex-row items-center justify-between gap-4 shadow-sm">
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-amber-500 text-white rounded-lg shadow">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-amber-950 text-base">
              {language === 'ta' ? 'முதன்மை விதிமுறை (Core Principle)' : 'Operational Single Incident Deduplication'}
            </h3>
            <p className="text-xs sm:text-sm text-amber-800 mt-1">
              "One real-world issue can have many private citizen petitions, but officers work from one shared operational incident."
            </p>
          </div>
        </div>
        <div className="px-4 py-2 bg-white rounded-lg border border-amber-300 text-xs font-bold text-amber-900 shadow-sm shrink-0">
          Privacy Preserved & PII Redacted
        </div>
      </section>

      {/* Department Quick Grid */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-slate-800">
          {language === 'ta' ? 'முக்கிய துறைகள் (TN Government Departments)' : 'Participating Departments'}
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { code: "GCC", name: "Chennai Corp", ta: "மாநகராட்சி", icon: "🏙️" },
            { code: "TANGEDCO", name: "Electricity", ta: "மின்சார வாரியம்", icon: "⚡" },
            { code: "CMWSSB", name: "Metro Water", ta: "குடிநீர் வாரியம்", icon: "💧" },
            { code: "TRAFFIC", name: "Traffic Police", ta: "போக்குவரத்து காவல்துறை", icon: "🚦" },
            { code: "REVENUE", name: "Revenue Dept", ta: "வருவாய் துறை", icon: "🏛️" },
            { code: "HEALTH", name: "Public Health", ta: "சுகாதாரத் துறை", icon: "🏥" },
          ].map((d) => (
            <div key={d.code} className="bg-white p-4 rounded-xl border border-slate-200 hover:border-tn-navy transition-all shadow-sm text-center space-y-2">
              <span className="text-2xl">{d.icon}</span>
              <h3 className="font-bold text-xs text-slate-800">{d.name}</h3>
              <p className="text-[11px] text-slate-500">{d.ta}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
