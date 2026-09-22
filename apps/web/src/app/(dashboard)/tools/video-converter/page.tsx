'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Film, Sparkles, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';
import ProcessingJobStatus from '@/components/tools/processing-job-status';

export default function VideoConverterPage() {
  const [file, setFile] = useState<File | null>(null);
  const [format, setFormat] = useState('mp4');
  const [submitting, setSubmitting] = useState(false);
  const [jobId, setJobId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleConvert = async () => {
    if (!file) return;
    setSubmitting(true); setError(null); setJobId(null);
    const body = new FormData(); body.append('file', file); body.append('format', format);
    try {
      const response = await fetch('/api/worker/tools/convert', { method: 'POST', body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || `Queue failed with HTTP ${response.status}`);
      setJobId(data.job_id); setFile(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not queue conversion');
    } finally { setSubmitting(false); }
  };

  return <div className="space-y-6 max-w-2xl">
    <Link href="/tools" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600"><ArrowLeft className="h-3.5 w-3.5" />Back to Tools</Link>
    <div><h1 className="flex items-center gap-2 text-2xl font-bold"><Film className="h-6 w-6 text-indigo-600" />Video Converter</h1><p className="mt-1 text-sm text-slate-500">Convert a video and download the completed result.</p></div>
    <div className="space-y-5 rounded-2xl border bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <FileUpload onFileSelect={setFile} selectedFile={file} accept={{ 'video/*': ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv'] }} label="Drop video file to convert" hint="MP4, MKV, WebM, AVI, MOV or FLV" />
      {file && <><select value={format} onChange={(event) => setFormat(event.target.value)} className="w-full rounded-lg border bg-white px-4 py-2.5 text-sm dark:border-slate-700 dark:bg-slate-800"><option value="mp4">MP4</option><option value="mkv">MKV</option><option value="webm">WebM</option><option value="avi">AVI</option><option value="mov">MOV</option></select><Button onClick={handleConvert} disabled={submitting} className="w-full">{submitting && <Sparkles className="h-4 w-4 animate-spin" />}{submitting ? 'Uploading…' : `Convert to ${format.toUpperCase()}`}</Button></>}
      {error && <div className="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"><AlertCircle className="h-4 w-4" />{error}</div>}
      <ProcessingJobStatus jobId={jobId} />
    </div>
  </div>;
}
