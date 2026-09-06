'use client';

import React from 'react';
import { History } from 'lucide-react';
import DownloadQueue from '@/components/download/download-queue';

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <History className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          <span>Download & Processing History</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Review previous media downloads and processing jobs saved locally.
        </p>
      </div>

      <DownloadQueue />
    </div>
  );
}

