'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { Timeline } from '../../../components/Timeline';
import { FileText, Star, RotateCcw, CheckCircle, Shield } from 'lucide-react';

export default function PetitionDetailPage() {
  const params = useParams();
  const petitionId = params?.id as string;
  const { language } = useAuth();
  const t = translations[language];

  const [petition, setPetition] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const [rating, setRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  const [appealReason, setAppealReason] = useState('');
  const [appealSuccess, setAppealSuccess] = useState(false);

  useEffect(() => {
    if (petitionId) {
      fetchApi(`/petitions/${petitionId}`)
        .then((data) => setPetition(data))
        .catch(() => setPetition(null))
        .finally(() => setLoading(false));
    }
  }, [petitionId]);

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi(`/petitions/${petitionId}/feedback`, {
        method: 'POST',
        body: JSON.stringify({ rating, comments: feedbackComment })
      });
      setFeedbackSuccess(true);
    } catch (err: any) {
      alert(err.message || "Failed to submit feedback");
    }
  };

  const handleAppealSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi(`/petitions/${petitionId}/appeal`, {
        method: 'POST',
        body: JSON.stringify({ reason: appealReason })
      });
      setAppealSuccess(true);
      setPetition({ ...petition, status: 'reopened' });
    } catch (err: any) {
      alert(err.message || "Failed to submit appeal");
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Loading petition details...</div>;
  if (!petition) return <div className="p-8 text-center text-slate-500">Petition not found.</div>;

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-6">
      {/* Header Info */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <span className="text-xs font-mono font-bold text-tn-navy bg-slate-100 px-2.5 py-1 rounded">
              {petition.petition_number}
            </span>
            <h1 className="text-xl font-extrabold text-slate-900 mt-2">{petition.title}</h1>
          </div>
          <span className="text-xs font-bold px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 uppercase tracking-wider">
            {petition.status}
          </span>
        </div>

        <p className="text-sm text-slate-700 leading-relaxed">{petition.description}</p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-slate-500 pt-2">
          <div><span className="font-semibold block text-slate-700">District:</span> {petition.district}</div>
          <div><span className="font-semibold block text-slate-700">Landmark:</span> {petition.landmark || 'N/A'}</div>
          <div><span className="font-semibold block text-slate-700">Language:</span> {petition.language.toUpperCase()}</div>
          <div><span className="font-semibold block text-slate-700">Submitted:</span> {new Date(petition.created_at).toLocaleDateString()}</div>
        </div>
      </div>

      {/* Status History Timeline */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-800">{t.statusTimeline}</h3>
        <Timeline items={petition.history || []} />
      </div>

      {/* Feedback Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-800">{t.feedbackTitle}</h3>

        {feedbackSuccess ? (
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-semibold flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>Thank you for rating our resolution service!</span>
          </div>
        ) : (
          <form onSubmit={handleFeedbackSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Satisfaction Rating (1 to 5 Stars)</label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`p-2 rounded-lg text-sm font-bold flex items-center gap-1 ${
                      rating >= star ? 'bg-amber-400 text-tn-navy' : 'bg-slate-100 text-slate-400'
                    }`}
                  >
                    <Star className="w-4 h-4 fill-current" />
                    <span>{star}</span>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Feedback Comments</label>
              <textarea
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                rows={2}
                placeholder="Share your thoughts about the resolution..."
                className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-tn-navy focus:outline-none"
              />
            </div>

            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-xs shadow"
            >
              {t.submitFeedback}
            </button>
          </form>
        )}
      </div>

      {/* Appeal / Reopen Flow */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-800">{t.appealTitle}</h3>

        {appealSuccess ? (
          <div className="p-3 bg-blue-50 text-blue-700 rounded-lg text-xs font-semibold flex items-center gap-2">
            <CheckCircle className="w-4 h-4" />
            <span>Appeal request submitted! Reopened for senior supervisor review.</span>
          </div>
        ) : (
          <form onSubmit={handleAppealSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Reason for Reopening / Appeal</label>
              <textarea
                value={appealReason}
                onChange={(e) => setAppealReason(e.target.value)}
                rows={2}
                placeholder="Specify why the issue requires additional work or reopening..."
                className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-tn-navy focus:outline-none"
                required
              />
            </div>

            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow"
            >
              {t.submitAppeal}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
