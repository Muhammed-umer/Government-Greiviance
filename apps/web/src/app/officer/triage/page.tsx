'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { AlertCircle, CheckCircle, RefreshCw, Layers, ArrowRight } from 'lucide-react';

export default function TriageQueuePage() {
  const { language } = useAuth();
  const t = translations[language];

  const [tasks, setTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi('/triage/tasks')
      .then((data) => setTasks(data))
      .catch(() => setTasks([]))
      .finally(() => setLoading(false));
  }, []);

  const handleResolve = async (taskId: string, action: string, candidateIncidentId?: string) => {
    try {
      await fetchApi(`/triage/tasks/${taskId}/resolve`, {
        method: 'POST',
        body: JSON.stringify({
          action,
          target_incident_id: candidateIncidentId
        })
      });
      alert("Triage decision saved!");
      setTasks(tasks.filter(t => t.id !== taskId));
    } catch (err: any) {
      alert(err.message || "Failed to resolve triage task");
    }
  };

  return (
    <div className="space-y-6 py-4">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <AlertCircle className="w-6 h-6 text-amber-500" />
          <span>Human Triage Queue</span>
        </h1>
        <p className="text-xs text-slate-500">
          Review grievances flagged due to low AI routing confidence (&lt;0.75) or candidate duplicate similarity.
        </p>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading triage queue...</div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-500 space-y-2">
          <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto" />
          <h3 className="font-bold text-slate-800">Triage Queue Clear!</h3>
          <p className="text-xs text-slate-500">No pending AI routing or duplicate verification tasks require manual review.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <div key={task.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold px-2.5 py-1 rounded bg-amber-100 text-amber-900 border border-amber-300">
                  Task Type: {task.task_type.toUpperCase().replace(/_/g, ' ')}
                </span>
                <span className="text-xs font-mono font-bold text-slate-600">
                  AI Confidence: {(task.confidence_score * 100).toFixed(0)}%
                </span>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 text-base">{task.petition_title}</h3>
                <p className="text-xs text-slate-500 mt-1">Petition ID: {task.petition_id}</p>
              </div>

              <div className="flex flex-wrap gap-3 pt-2">
                {task.candidate_incident_id && (
                  <button
                    onClick={() => handleResolve(task.id, 'link', task.candidate_incident_id)}
                    className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow"
                  >
                    Confirm & Link to Incident ({task.candidate_incident_id.slice(0, 8)})
                  </button>
                )}

                <button
                  onClick={() => handleResolve(task.id, 'create_new')}
                  className="px-4 py-2 rounded-xl bg-tn-navy hover:bg-slate-800 text-white font-bold text-xs shadow"
                >
                  Create New Shared Incident
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
