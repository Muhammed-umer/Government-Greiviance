'use client';

import React from 'react';
import { CheckCircle2, Clock, AlertCircle, FileCheck, ArrowRight } from 'lucide-react';

interface TimelineItem {
  id: string;
  from_status?: string;
  to_status: string;
  remarks?: string;
  created_at: string;
}

interface TimelineProps {
  items: TimelineItem[];
  language?: 'en' | 'ta';
}

export function Timeline({ items }: TimelineProps) {
  if (!items || items.length === 0) {
    return <p className="text-xs text-slate-500 italic">No history logged yet.</p>;
  }

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
      {items.map((item, idx) => {
        const isResolved = item.to_status === 'resolved';
        const isLinked = item.to_status === 'linked';
        
        return (
          <div key={item.id || idx} className="relative flex items-start space-x-3">
            <div className={`absolute -left-6 top-0.5 w-5 h-5 rounded-full flex items-center justify-center text-white text-xs ${
              isResolved ? 'bg-emerald-600' : isLinked ? 'bg-blue-600' : 'bg-tn-navy'
            }`}>
              {isResolved ? <CheckCircle2 className="w-3.5 h-3.5" /> : <Clock className="w-3.5 h-3.5" />}
            </div>

            <div className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm w-full space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-tn-navy">
                  Status: {item.to_status.replace('_', ' ')}
                </span>
                <span className="text-[11px] text-slate-400">
                  {new Date(item.created_at).toLocaleString()}
                </span>
              </div>
              {item.remarks && (
                <p className="text-xs text-slate-600 font-medium">
                  {item.remarks}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
