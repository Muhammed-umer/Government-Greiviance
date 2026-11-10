'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { useAuth } from '../../../../lib/auth';
import { translations } from '../../../../lib/i18n';
import { fetchApi } from '../../../../lib/api';
import { PriorityBadge } from '../../../../components/PriorityBadge';
import { Shield, AlertTriangle, Users, FileText, CheckCircle, RefreshCw, Lock } from 'lucide-react';

export default function OfficerIncidentDetailPage() {
  const params = useParams();
  const incidentId = params?.id as string;
  const { language } = useAuth();
  const t = translations[language];

  const [incident, setIncident] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Priority Override Modal
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [newPriority, setNewPriority] = useState('high');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSuccess, setOverrideSuccess] = useState<string | null>(null);

  // Officer Action Form
  const [actionNotes, setActionNotes] = useState('');
  const [actionType, setActionType] = useState('resolution');

  useEffect(() => {
    if (incidentId) {
      fetchApi(`/incidents/${incidentId}`)
        .then((data) => setIncident(data))
        .catch(() => setIncident(null))
        .finally(() => setLoading(false));
    }
  }, [incidentId]);

  const handlePriorityOverrideSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason || overrideReason.length < 5) {
      alert("Mandatory reason required for officer priority override!");
      return;
    }

    try {
      const res = await fetchApi(`/incidents/${incidentId}/priority-override`, {
        method: 'POST',
        body: JSON.stringify({ new_priority: newPriority, reason: overrideReason })
      });
      setOverrideSuccess(`Priority overridden to ${newPriority.toUpperCase()}. Saved to audit log.`);
      setShowOverrideModal(false);
      setIncident({ ...incident, priority_level: newPriority });
    } catch (err: any) {
      alert(err.message || "Failed to override priority.");
    }
  };

  const handleLogActionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetchApi(`/incidents/${incidentId}/actions`, {
        method: 'POST',
        body: JSON.stringify({ action_type: actionType, notes: actionNotes })
      });
      alert("Officer action & resolution logged successfully!");
      if (actionType === 'resolution') setIncident({ ...incident, status: 'resolved' });
    } catch (err: any) {
      alert(err.message || "Failed to log action.");
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Loading shared incident...</div>;
  if (!incident) return <div className="p-8 text-center text-slate-500">Incident not found.</div>;

  return (
    <div className="max-w-5xl mx-auto py-4 space-y-6">
      {/* Top Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-100 pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-bold text-tn-navy bg-slate-100 px-2.5 py-1 rounded">
                {incident.incident_number}
              </span>
              <PriorityBadge level={incident.priority_level} score={incident.priority_score} />
            </div>
            <h1 className="text-2xl font-extrabold text-slate-900">{incident.title}</h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowOverrideModal(true)}
              className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-tn-navy font-bold text-xs shadow transition-all flex items-center gap-1.5"
            >
              <AlertTriangle className="w-4 h-4" />
              <span>Override Priority</span>
            </button>

            <span className="px-3 py-1.5 rounded-full bg-blue-100 text-blue-800 text-xs font-bold uppercase">
              {incident.status}
            </span>
          </div>
        </div>

        {overrideSuccess && (
          <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-semibold flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600" />
            <span>{overrideSuccess}</span>
          </div>
        )}

        <p className="text-sm text-slate-700 leading-relaxed">{incident.summary}</p>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs text-slate-500 pt-2">
          <div><span className="font-semibold block text-slate-700">Department:</span> {incident.department_name}</div>
          <div><span className="font-semibold block text-slate-700">Category:</span> {incident.category_name}</div>
          <div><span className="font-semibold block text-slate-700">District:</span> {incident.district}</div>
          <div><span className="font-semibold block text-slate-700">Linked Petitions:</span> <strong className="text-tn-navy font-bold text-sm">{incident.linked_petitions_count}</strong></div>
        </div>
      </div>

      {/* Linked Petitions Anonymized Privacy View */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
            <Users className="w-5 h-5 text-tn-navy" />
            <span>Linked Private Petitions ({incident.linked_petitions_count})</span>
          </h3>
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <Lock className="w-3.5 h-3.5 text-amber-600" />
            <span>PII Anonymized</span>
          </span>
        </div>

        <div className="space-y-3">
          {incident.petitions && incident.petitions.map((p: any, idx: number) => (
            <div key={idx} className="p-3.5 bg-slate-50 rounded-xl border border-slate-200 text-xs flex items-center justify-between">
              <div>
                <span className="font-mono font-bold text-tn-navy">{p.petition_number}</span>
                <span className="ml-3 text-slate-600">Landmark: {p.landmark || 'Area main road'}</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-slate-500 font-medium">Citizen: {p.citizen_name}</span>
                <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold uppercase">{p.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Officer Action & Field Visit Logger */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-800">Field Action & Status Update Log</h3>

        <form onSubmit={handleLogActionSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Action Type</label>
              <select
                value={actionType}
                onChange={(e) => setActionType(e.target.value)}
                className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-tn-navy focus:outline-none"
              >
                <option value="resolution">Mark Issue as RESOLVED</option>
                <option value="field_visit">Record Field Visit Inspection</option>
                <option value="status_update">Status Update Note</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Inspection / Resolution Notes *</label>
            <textarea
              value={actionNotes}
              onChange={(e) => setActionNotes(e.target.value)}
              rows={3}
              placeholder="Describe work completed, field team findings, or resolution proof..."
              className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-tn-navy focus:outline-none"
              required
            />
          </div>

          <button
            type="submit"
            className="px-6 py-2.5 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-xs shadow"
          >
            Submit Action Log
          </button>
        </form>
      </div>

      {/* Priority Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl border border-slate-300">
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              <span>Officer Priority Score Override</span>
            </h3>

            <form onSubmit={handlePriorityOverrideSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">New Priority Level</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-tn-navy focus:outline-none font-bold"
                >
                  <option value="high">HIGH (Urgent / Life Safety)</option>
                  <option value="medium">MEDIUM (Standard SLA)</option>
                  <option value="low">LOW (Routine Maintenance)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-red-700 mb-1">
                  Mandatory Reason for Override * (Saved to Audit Log)
                </label>
                <textarea
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  rows={3}
                  placeholder="Explain why priority is being modified (e.g. Field inspection confirmed high public hazard)..."
                  className="w-full p-2.5 rounded-lg border border-red-300 text-xs focus:ring-2 focus:ring-red-500 focus:outline-none"
                  required
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowOverrideModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-semibold text-xs hover:bg-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-tn-navy font-bold text-xs shadow"
                >
                  Save Override & Audit Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
