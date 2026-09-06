'use client';

import React, { useEffect, useState, useCallback } from 'react';
import DownloadCard, { DownloadJobData } from './download-card';
import { RefreshCw, Inbox } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DownloadQueueProps {
  refreshTrigger?: number;
}

export default function DownloadQueue({ refreshTrigger }: DownloadQueueProps) {
  const [jobs, setJobs] = useState<DownloadJobData[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchJobs = useCallback(async () => {
    try {
      const res = await fetch('/api/worker/downloads');
      if (res.ok) {
        const data = await res.json();
        setJobs(data);
      }
    } catch (err) {
      console.warn('Could not fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 3000);
    return () => clearInterval(interval);
  }, [fetchJobs, refreshTrigger]);

  const handleRetry = async (jobId: number) => {
    try {
      await fetch(`/api/worker/downloads/${jobId}/retry`, { method: 'POST' });
      fetchJobs();
    } catch (err) {
      console.error('Retry failed:', err);
    }
  };

  const handleCancel = async (jobId: number) => {
    try {
      await fetch(`/api/worker/downloads/${jobId}`, { method: 'DELETE' });
      fetchJobs();
    } catch (err) {
      console.error('Cancel failed:', err);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <span>Download Queue</span>
          {jobs.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-medium">
              {jobs.length}
            </span>
          )}
        </h2>
        <Button
          size="sm"
          variant="outline"
          onClick={fetchJobs}
          className="text-xs"
          disabled={loading}
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {jobs.length === 0 ? (
        <div className="text-center py-12 px-4 rounded-xl border border-dashed border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/40">
          <Inbox className="w-10 h-10 mx-auto text-slate-400 mb-3" />
          <p className="font-medium text-slate-700 dark:text-slate-300 text-sm">No download jobs yet</p>
          <p className="text-xs text-slate-500 mt-1">Paste a video or audio URL above to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {jobs.map((job) => (
            <DownloadCard
              key={job.id}
              job={job}
              onRetry={handleRetry}
              onCancel={handleCancel}
            />
          ))}
        </div>
      )}
    </div>
  );
}
