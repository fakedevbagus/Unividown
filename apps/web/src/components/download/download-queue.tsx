'use client';

import React, { useEffect, useState, useCallback } from 'react';
import DownloadCard, { DownloadJobData } from './download-card';
import { RefreshCw, Inbox } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useWebSocket } from '@/hooks/use-websocket';

interface DownloadQueueProps {
  refreshTrigger?: number;
}

export default function DownloadQueue({ refreshTrigger }: DownloadQueueProps) {
  const [jobs, setJobs] = useState<DownloadJobData[]>([]);
  const [loading, setLoading] = useState(true);
  const { joinJob, onProgress, onCompleted, onStatus, onError } = useWebSocket();

  const fetchJobs = useCallback(async () => {
    try {
      const res = await fetch('/api/worker/downloads');
      if (res.ok) {
        const data: DownloadJobData[] = await res.json();
        setJobs(data);
        // Automatically join rooms for active downloads
        data.forEach((job) => {
          if (job.status === 'processing' || job.status === 'pending') {
            joinJob(job.id);
          }
        });
      }
    } catch (err) {
      console.warn('Could not fetch jobs:', err);
    } finally {
      setLoading(false);
    }
  }, [joinJob]);

  // Initial fetch and occasional background sync
  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000);
    return () => clearInterval(interval);
  }, [fetchJobs, refreshTrigger]);

  // WebSocket real-time event listeners
  useEffect(() => {
    const unsubProgress = onProgress((data) => {
      setJobs((prev) =>
        prev.map((job) =>
          job.id === data.jobId
            ? { ...job, progress: data.progress, status: 'processing' }
            : job
        )
      );
    });

    const unsubStatus = onStatus((data) => {
      setJobs((prev) =>
        prev.map((job) =>
          job.id === data.jobId ? { ...job, status: data.status } : job
        )
      );
    });

    const unsubCompleted = onCompleted((data) => {
      setJobs((prev) =>
        prev.map((job) =>
          job.id === data.jobId
            ? { ...job, status: 'completed', progress: 100, title: data.title || job.title }
            : job
        )
      );
    });

    const unsubError = onError((data) => {
      setJobs((prev) =>
        prev.map((job) =>
          job.id === data.jobId
            ? { ...job, status: 'failed', error_message: data.error }
            : job
        )
      );
    });

    return () => {
      unsubProgress();
      unsubStatus();
      unsubCompleted();
      unsubError();
    };
  }, [onProgress, onStatus, onCompleted, onError]);

  const handleRetry = async (jobId: number) => {
    try {
      await fetch(`/api/worker/downloads/${jobId}/retry`, { method: 'POST' });
      joinJob(jobId);
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

