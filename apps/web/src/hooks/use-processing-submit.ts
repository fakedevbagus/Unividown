'use client';

import { useCallback, useState } from 'react';

export function useProcessingSubmit(endpoint: string) {
  const [jobId, setJobId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(async (body: FormData) => {
    setSubmitting(true); setError(null); setJobId(null);
    try {
      const response = await fetch(endpoint, { method: 'POST', body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || `Request failed with HTTP ${response.status}`);
      setJobId(data.job_id);
      return true;
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not queue processing job');
      return false;
    } finally { setSubmitting(false); }
  }, [endpoint]);

  return { jobId, submitting, error, submit };
}
