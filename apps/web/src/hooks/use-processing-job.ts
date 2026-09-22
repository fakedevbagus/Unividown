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

  const refresh = useCallback(async () => {
    if (jobId === null) return;
    try {
      const response = await fetch(`/api/worker/tools/jobs/${jobId}`, { cache: 'no-store' });
      if (!response.ok) throw new Error(`Status request failed with HTTP ${response.status}`);
      setJob(await response.json());
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not load processing status');
    }
  }, [jobId]);

  useEffect(() => {
    setJob(null);
    setError(null);
    if (jobId === null) return;
    void refresh();
    const timer = window.setInterval(() => void refresh(), 1500);
    return () => window.clearInterval(timer);
  }, [jobId, refresh]);

  useEffect(() => {
    if (job?.status !== 'completed' && job?.status !== 'failed') return;
    // Terminal status remains visible; polling requests are inexpensive but no longer needed.
  }, [job?.status]);

  return { job, error, refresh };
}
