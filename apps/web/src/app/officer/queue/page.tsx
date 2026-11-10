'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { PriorityBadge } from '../../../components/PriorityBadge';
import { Shield, Filter, AlertTriangle, Clock, Layers, ChevronRight, Search } from 'lucide-react';

export default function OfficerQueuePage() {
  const { language } = useAuth();
  const t = translations[language];

  const [metrics, setMetrics] = useState({ open_incidents: 0, high_priority_incidents: 0, sla_at_risk_incidents: 0 });
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  useEffect(() => {
    fetchApi('/officer/queue')
      .then((res) => {
        setMetrics(res.metrics);
        setQueue(res.queue);
      })
      .catch(() => setQueue([]))
      .finally(() => setLoading(false));
  }, []);

  const filteredQueue = queue.filter((inc) => {
    if (statusFilter && inc.status !== statusFilter) return false;
    if (priorityFilter && inc.priority_level !== priorityFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Shield className="w-6 h-6 text-tn-navy" />
            <span>Officer Operational Incident Queue</span>
          </h1>
          <p className="text-xs text-slate-500">
            Work from deduplicated shared incidents representing real-world civic issues.
          </p>
        </div>
      </div>

      {/* Metrics Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
          <span className="text-xs font-semibold text-slate-500 uppercase">Open Incidents</span>
          <p className="text-3xl font-extrabold text-tn-navy">{metrics.open_incidents}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-red-200 shadow-sm space-y-1 bg-red-50/40">
          <span className="text-xs font-semibold text-red-800 uppercase flex items-center gap-1">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span>High Priority / Immediate Safety</span>
          </span>
          <p className="text-3xl font-extrabold text-red-600">{metrics.high_priority_incidents}</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-amber-200 shadow-sm space-y-1 bg-amber-50/40">
          <span className="text-xs font-semibold text-amber-800 uppercase flex items-center gap-1">
            <Clock className="w-4 h-4 text-amber-600" />
            <span>SLA At Risk / Breached</span>
          </span>
          <p className="text-3xl font-extrabold text-amber-600">{metrics.sla_at_risk_incidents}</p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4 text-xs font-semibold">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-slate-400" />
          <span>Filters:</span>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="p-2 rounded-lg border border-slate-300 bg-white"
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="p-2 rounded-lg border border-slate-300 bg-white"
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <span className="text-slate-500">Showing {filteredQueue.length} Shared Incidents</span>
      </div>

      {/* Incident List */}
      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading incident queue...</div>
      ) : filteredQueue.length === 0 ? (
        <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-500">
          No shared incidents found matching active filters.
        </div>
      ) : (
        <div className="space-y-3">
          {filteredQueue.map((inc) => (
            <div
              key={inc.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:border-tn-navy transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold text-tn-navy bg-slate-100 px-2.5 py-1 rounded">
                    {inc.incident_number}
                  </span>
                  <PriorityBadge level={inc.priority_level} score={inc.priority_score} />
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <span className="font-bold text-slate-700 bg-blue-50 text-blue-800 px-2.5 py-1 rounded border border-blue-200">
                    Linked Petitions: {inc.linked_petitions_count}
                  </span>
                  <span className="uppercase font-bold text-slate-500">{inc.status}</span>
                </div>
              </div>

              <div>
                <h3 className="font-bold text-slate-900 text-base">{inc.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-2 mt-1">{inc.summary}</p>
              </div>

              <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
                <div className="flex gap-4">
                  <span>Dept: <strong className="text-slate-700">{inc.department_name}</strong></span>
                  <span>District: <strong className="text-slate-700">{inc.district}</strong></span>
                </div>

                <Link
                  href={`/officer/incident/${inc.id}`}
                  className="flex items-center space-x-1 text-xs font-bold text-tn-navy hover:text-amber-600 transition-colors"
                >
                  <span>Manage Incident & Override</span>
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
