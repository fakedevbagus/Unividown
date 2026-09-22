'use client';

import { AlertCircle, CheckCircle2, Download, LoaderCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useProcessingJob } from '@/hooks/use-processing-job';

function workerProxyUrl(url: string) {
  return url.startsWith('/api/') ? `/api/worker/${url.slice('/api/'.length)}` : url;
}

export default function ProcessingJobStatus({ jobId }: { jobId: number | null }) {
  const { job, error, refresh } = useProcessingJob(jobId);
  if (jobId === null) return null;

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/40 dark:text-red-300">
        <div className="flex items-center gap-2"><AlertCircle className="h-4 w-4" />{error}</div>
        <Button size="sm" variant="outline" className="mt-2" onClick={() => void refresh()}><RefreshCw className="h-3.5 w-3.5" />Retry status</Button>
      </div>
    );
  }

  if (!job) {
    return <div className="flex items-center gap-2 rounded-lg border p-3 text-sm text-slate-500"><LoaderCircle className="h-4 w-4 animate-spin" />Loading job #{jobId}…</div>;
  }

  const active = job.status === 'pending' || job.status === 'processing';
  return (
    <div className="space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm font-medium">
          {active ? <LoaderCircle className="h-4 w-4 animate-spin text-indigo-500" /> : job.status === 'completed' ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <AlertCircle className="h-4 w-4 text-red-500" />}
          Job #{job.id}: {job.status}
        </div>
        <span className="text-xs text-slate-500">{Math.round(job.progress || 0)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700"><div className="h-full bg-indigo-500 transition-all" style={{ width: `${Math.max(2, job.progress || 0)}%` }} /></div>
      {job.error_message && <p className="text-sm text-red-600 dark:text-red-300">{job.error_message}</p>}
      {job.status === 'completed' && job.results.length === 0 && <p className="text-sm text-amber-700 dark:text-amber-300">Completed without a result file.</p>}
      {job.results.map((result) => (
        <a key={result.index} href={workerProxyUrl(result.download_url)} download={result.filename} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700">
          <Download className="h-4 w-4" />Download {result.filename}
        </a>
      ))}
    </div>
  );
}
