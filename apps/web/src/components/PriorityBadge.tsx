'use client';

import React from 'react';
import { AlertTriangle, AlertCircle, ShieldAlert } from 'lucide-react';

interface PriorityBadgeProps {
  level: string; // high, medium, low
  score?: number;
  showScore?: boolean;
}

export function PriorityBadge({ level, score, showScore = true }: PriorityBadgeProps) {
  const normalizedLevel = level ? level.toLowerCase() : 'low';

  if (normalizedLevel === 'high') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-red-100 text-red-800 border border-red-300 shadow-sm">
        <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
        <span>HIGH</span>
        {showScore && score !== undefined && <span className="opacity-80">({score})</span>}
      </span>
    );
  }

  if (normalizedLevel === 'medium') {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
        <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
        <span>MEDIUM</span>
        {showScore && score !== undefined && <span className="opacity-80">({score})</span>}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 border border-slate-300">
      <ShieldAlert className="w-3.5 h-3.5 text-slate-500" />
      <span>LOW</span>
      {showScore && score !== undefined && <span className="opacity-80">({score})</span>}
    </span>
  );
}
