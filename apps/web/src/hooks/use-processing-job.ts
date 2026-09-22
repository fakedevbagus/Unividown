'use client';

import { useCallback, useEffect, useState } from 'react';

export interface ProcessingResult {
  index: number;
  filename: string;
  file_size?: number | null;
  download_url: string;
}

export interface ProcessingJob {
  id: number;
  tool_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  error_message?: string | null;
  results: ProcessingResult[];
}

export function useProcessingJob(jobId: number | null) {
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const refresh = useCallback(() => setRefreshToken((value) => value + 1), []);

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;
    setJob(null);
    setError(null);
    if (jobId === null) return;

    const poll = async () => {
      try {
        const response = await fetch(`/api/worker/tools/jobs/${jobId}`, { cache: 'no-store' });
        if (!response.ok) throw new Error(`Status request failed with HTTP ${response.status}`);
        const nextJob: ProcessingJob = await response.json();
        if (cancelled) return;
        setJob(nextJob);
        setError(null);
        if (nextJob.status === 'pending' || nextJob.status === 'processing') {
          timer = window.setTimeout(poll, 1500);
        }
      } catch (reason) {
        if (cancelled) return;
        setError(reason instanceof Error ? reason.message : 'Could not load processing status');
      }
    };

    void poll();
    return () => {
      cancelled = true;
      if (timer !== undefined) window.clearTimeout(timer);
    };
  }, [jobId, refreshToken]);

  return { job, error, refresh };
}
