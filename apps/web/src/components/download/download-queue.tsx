'use client';

import React, { useEffect, useState, useCallback } from 'react';
import DownloadCard, { DownloadJobData } from './download-card';
import { RefreshCw, Inbox, Radio, WifiOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useWebSocket } from '@/hooks/use-websocket';

interface DownloadQueueProps {
  refreshTrigger?: number;
}

const CONNECTED_POLL_INTERVAL_MS = 15000;
const FALLBACK_POLL_INTERVAL_MS = 2000;

export default function DownloadQueue({ refreshTrigger }: DownloadQueueProps) {
  const [jobs, setJobs] = useState<DownloadJobData[]>([]);
  const [loading, setLoading] = useState(true);
  const { connected, joinJob, onProgress, onCompleted, onStatus, onError } = useWebSocket();

  const fetchJobs = useCallback(async () => {
    try {
      const res = await fetch('/api/worker/downloads', { cache: 'no-store' });
      if (!res.ok) return;
      const data: DownloadJobData[] = await res.json();
      setJobs(data);
      data.forEach((job) => {
        if (job.status === 'processing' || job.status === 'pending') joinJob(job.id);
      });
    } catch (err) {
      console.warn('Could not fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  }, [joinJob]);

  useEffect(() => {
    void fetchJobs();
    const pollInterval = connected ? CONNECTED_POLL_INTERVAL_MS : FALLBACK_POLL_INTERVAL_MS;
    const interval = window.setInterval(() => void fetchJobs(), pollInterval);
    return () => window.clearInterval(interval);
  }, [connected, fetchJobs, refreshTrigger]);

  useEffect(() => {
    const unsubProgress = onProgress((data) => {
      setJobs((prev) => prev.map((job) =>
        job.id === data.jobId ? { ...job, progress: data.progress, status: 'processing' } : job
      ));
    });

    const unsubStatus = onStatus((data) => {
      setJobs((prev) => prev.map((job) =>
        job.id === data.jobId ? { ...job, status: data.status } : job
      ));
      if (['cancelled', 'failed'].includes(data.status)) void fetchJobs();
    });

    const unsubCompleted = onCompleted((data) => {
      setJobs((prev) => prev.map((job) =>
        job.id === data.jobId
          ? { ...job, status: 'completed', progress: 100, title: data.title || job.title }
          : job
      ));
      void fetchJobs();
    });

    const unsubError = onError((data) => {
      setJobs((prev) => prev.map((job) =>
        job.id === data.jobId ? { ...job, status: 'failed', error_message: data.error } : job
      ));
      void fetchJobs();
    });

    return () => {
      unsubProgress();
      unsubStatus();
      unsubCompleted();
      unsubError();
    };
  }, [fetchJobs, onProgress, onStatus, onCompleted, onError]);

  const handleRetry = async (jobId: number) => {
    try {
      const response = await fetch(`/api/worker/downloads/${jobId}/retry`, { method: 'POST' });
      if (!response.ok) throw new Error(`Retry failed with HTTP ${response.status}`);
      joinJob(jobId);
      await fetchJobs();
    } catch (err) {
      console.error('Retry failed:', err);
    }
  };

  const handleCancel = async (jobId: number) => {
    try {
      const response = await fetch(`/api/worker/downloads/${jobId}`, { method: 'DELETE' });
      if (!response.ok) throw new Error(`Cancel failed with HTTP ${response.status}`);
      await fetchJobs();
    } catch (err) {
      console.error('Cancel failed:', err);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Download Queue</h2>
          {jobs.length > 0 && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-medium">
              {jobs.length}
            </span>
          )}
          <span
            className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-[11px] font-medium ${
              connected
                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
            }`}
            title={connected ? 'Socket.IO connected; periodic reconciliation remains enabled' : 'Socket.IO disconnected; queue refreshes every 2 seconds'}
          >
            {connected ? <Radio className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
            {connected ? 'Live updates' : 'Polling fallback'}
          </span>
        </div>
        <Button size="sm" variant="outline" onClick={() => void fetchJobs()} className="text-xs" disabled={loading}>
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
            <DownloadCard key={job.id} job={job} onRetry={handleRetry} onCancel={handleCancel} />
          ))}
        </div>
      )}
    </div>
  );
}
