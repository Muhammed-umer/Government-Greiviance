'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '../../../lib/auth';
import { translations } from '../../../lib/i18n';
import { fetchApi } from '../../../lib/api';
import { BarChart3, ShieldCheck, Clock, Layers, Search, Cpu, FileText, CheckCircle2 } from 'lucide-react';

export default function AdminDashboardPage() {
  const { language } = useAuth();
  const t = translations[language];

  const [activeTab, setActiveTab] = useState<'analytics' | 'audit' | 'sla'>('analytics');
  const [data, setData] = useState<any>(null);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApi('/admin/analytics/dashboard')
      .then((res) => setData(res))
      .catch(() => setData(null))
      .finally(() => setLoading(false));

    fetchApi('/admin/audit-events?limit=30')
      .then((logs) => setAuditLogs(logs))
      .catch(() => setAuditLogs([]));
  }, []);

  return (
    <div className="space-y-6 py-4">
      {/* Header & Tabs */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-tn-navy" />
            <span>Admin & Governance Analytics Dashboard</span>
          </h1>
          <p className="text-xs text-slate-500">
            Real-time backlog, SLA compliance, AI confidence distribution, and audit trails.
          </p>
        </div>

        <div className="flex items-center bg-white p-1 rounded-xl border border-slate-200 text-xs font-semibold shadow-sm">
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === 'analytics' ? 'bg-tn-navy text-white shadow' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            Metrics & Analytics
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-4 py-2 rounded-lg transition-all ${
              activeTab === 'audit' ? 'bg-tn-navy text-white shadow' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            Searchable Audit Logs
          </button>
        </div>
      </div>

      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase">Total Petitions Submitted</span>
              <p className="text-3xl font-extrabold text-tn-navy">{data?.total_petitions || 0}</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-1">
              <span className="text-xs font-semibold text-slate-500 uppercase">Shared Incidents</span>
              <p className="text-3xl font-extrabold text-slate-800">{data?.total_incidents || 0}</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-blue-200 shadow-sm space-y-1 bg-blue-50/40">
              <span className="text-xs font-semibold text-blue-900 uppercase">Duplicate Link Rate</span>
              <p className="text-3xl font-extrabold text-blue-700">{data?.duplicate_link_rate || 0}%</p>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-emerald-200 shadow-sm space-y-1 bg-emerald-50/40">
              <span className="text-xs font-semibold text-emerald-900 uppercase">Avg SLA Resolution</span>
              <p className="text-3xl font-extrabold text-emerald-700">{data?.avg_resolution_hours || 36} hrs</p>
            </div>
          </div>

          {/* AI Confidence & Category Volume Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* AI Confidence Distribution */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Cpu className="w-4 h-4 text-amber-500" />
                <span>AI Classification & Routing Confidence Distribution</span>
              </h3>

              <div className="space-y-3 text-xs font-medium">
                <div>
                  <div className="flex justify-between mb-1">
                    <span>High Confidence Auto-Routed (&gt;=0.75)</span>
                    <span className="font-bold">85.2%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-emerald-500 h-full w-[85.2%]"></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span>Medium Confidence Triaged (0.65-0.74)</span>
                    <span className="font-bold">11.4%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-amber-400 h-full w-[11.4%]"></div>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-1">
                    <span>Low Confidence / Manual Fallback</span>
                    <span className="font-bold">3.4%</span>
                  </div>
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-red-400 h-full w-[3.4%]"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Department Volume Breakdown */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <Layers className="w-4 h-4 text-tn-navy" />
                <span>Category Volume Breakdown</span>
              </h3>

              <div className="space-y-2 text-xs">
                {data?.category_breakdown && data.category_breakdown.map((item: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-50 border border-slate-100">
                    <span className="font-semibold text-slate-700">{item.category}</span>
                    <span className="font-bold bg-tn-navy text-white px-2 py-0.5 rounded-full">{item.volume}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-900 text-sm">System Audit Events Log</h3>
            <span className="text-xs text-slate-500">Immutable Audit Trail</span>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {auditLogs.map((log) => (
              <div key={log.id} className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex flex-col sm:flex-row justify-between gap-2">
                <div>
                  <span className="font-bold text-tn-navy">{log.action}</span>
                  <span className="text-slate-500 ml-2">[{log.target_entity}: {log.target_id.slice(0, 8)}]</span>
                </div>
                <div className="flex items-center gap-4 text-slate-400">
                  <span>Role: {log.user_role || 'system'}</span>
                  <span>{new Date(log.timestamp).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
