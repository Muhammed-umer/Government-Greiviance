'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../../lib/auth';
import { translations } from '../../lib/i18n';
import { fetchApi } from '../../lib/api';
import { Phone, KeyRound, ShieldCheck, ArrowRight } from 'lucide-react';

export default function LoginPage() {
  const [phone, setPhone] = useState('9876543210');
  const [otp, setOtp] = useState('123456');
  const [step, setStep] = useState<'request' | 'verify'>('request');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const { loginWithOtp, language } = useAuth();
  const router = useRouter();
  const t = translations[language];

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetchApi('/auth/request-otp', {
        method: 'POST',
        body: JSON.stringify({ phone_number: phone, role_requested: 'citizen' })
      });
      setMessage(res.message || 'OTP sent');
      setStep('verify');
    } catch (err: any) {
      setMessage(err.message || 'Failed to request OTP');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await loginWithOtp(phone, otp);
      router.push('/petition/my-petitions');
    } catch (err: any) {
      setMessage(err.message || 'Invalid OTP code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-12">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xl p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-full bg-tn-navy text-amber-300 mx-auto flex items-center justify-center font-bold text-xl shadow">
            TN
          </div>
          <h2 className="text-xl font-bold text-slate-800">
            {language === 'ta' ? 'உள்நுழைவு (Passwordless OTP Login)' : 'Citizen & Officer OTP Sign In'}
          </h2>
          <p className="text-xs text-slate-500">
            Local Dev Mock Flow: OTP defaults to <span className="font-bold text-amber-700 bg-amber-100 px-1 rounded">123456</span>
          </p>
        </div>

        {message && (
          <div className="p-3 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold border border-blue-200 text-center">
            {message}
          </div>
        )}

        {step === 'request' ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Mobile Phone Number (10 Digits)
              </label>
              <div className="relative">
                <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="9876543210"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-sm shadow transition-all flex items-center justify-center gap-2"
            >
              <span>Request OTP Code</span>
              <ArrowRight className="w-4 h-4 text-amber-400" />
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Enter 6-Digit OTP Code
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="123456"
                  className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-tn-navy focus:outline-none font-mono text-center tracking-widest text-lg font-bold"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-tn-navy font-bold text-sm shadow transition-all flex items-center justify-center gap-2"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Verify & Access Portal</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
