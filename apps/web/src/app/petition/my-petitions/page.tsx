'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { Timeline } from '../../../components/Timeline';
import { FileText, Clock, ShieldCheck, ChevronRight, AlertCircle, PlusCircle } from 'lucide-react';

export default function MyPetitionsPage() {
  const { user, language } = useAuth();
  const t = translations[language];

  const [petitions, setPetitions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi('/petitions/me')
      .then((data) => setPetitions(data))
      .catch(() => setPetitions([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 py-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{t.myPetitions}</h1>
          <p className="text-xs text-slate-500">
            Track private petition progress & linked shared operational incident status.
          </p>
        </div>

        <Link
          href="/petition/new"
          className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-tn-navy hover:bg-slate-800 text-white text-xs font-bold shadow transition-all"
        >
          <PlusCircle className="w-4 h-4 text-amber-400" />
          <span>{t.submitComplaint}</span>
        </Link>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500 text-sm">Loading petitions...</div>
      ) : petitions.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-4">
          <FileText className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="font-bold text-slate-700">No Petitions Found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            You have not submitted any complaints yet. Submit a grievance to track progress.
          </p>
          <Link
            href="/petition/new"
            className="inline-block px-5 py-2.5 rounded-xl bg-amber-400 text-tn-navy font-bold text-xs shadow"
          >
            File New Complaint
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {petitions.map((p) => (
            <div key={p.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4 hover:border-tn-navy transition-all">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-tn-navy bg-slate-100 px-2.5 py-1 rounded">
                  {p.petition_number}
                </span>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  {p.status.toUpperCase()}
                </span>
              </div>

              <div>
                <h3 className="font-bold text-slate-800 text-base line-clamp-1">{p.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-2 mt-1">{p.description}</p>
              </div>

              <div className="flex items-center text-xs text-slate-500 gap-4 pt-2 border-t border-slate-100">
                <span>District: {p.district}</span>
                <span>Submitted: {new Date(p.created_at).toLocaleDateString()}</span>
              </div>

              {p.shared_incident_id && (
                <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-xs space-y-1">
                  <span className="font-bold text-amber-900 block flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                    <span>{t.sharedIncidentStatus}</span>
                  </span>
                  <p className="text-amber-800">
                    Linked to shared operational ticket. Field team dispatched. Privacy preserved.
                  </p>
                </div>
              )}

              <div className="pt-2">
                <Link
                  href={`/petition/${p.id}`}
                  className="flex items-center justify-between text-xs font-bold text-tn-navy hover:text-amber-600 transition-colors"
                >
                  <span>View Details & Feedback</span>
                  <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
