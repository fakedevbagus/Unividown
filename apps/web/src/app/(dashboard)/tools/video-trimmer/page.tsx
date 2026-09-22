'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Scissors, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import FileUpload from '@/components/shared/file-upload';
import ProcessingJobStatus from '@/components/tools/processing-job-status';
import { useProcessingSubmit } from '@/hooks/use-processing-submit';

export default function VideoTrimmerPage() {
  const [file, setFile] = useState<File | null>(null); const [start, setStart] = useState('0'); const [end, setEnd] = useState('10');
  const { jobId, submitting, error, submit } = useProcessingSubmit('/api/worker/tools/trim');
  const run = async () => { if (!file) return; const body = new FormData(); body.append('file', file); body.append('start', start); body.append('end', end); if (await submit(body)) setFile(null); };
  return <div className="space-y-6 max-w-2xl"><Link href="/tools" className="inline-flex items-center gap-1 text-xs text-slate-500"><ArrowLeft className="h-4 w-4" />Back to Tools</Link><h1 className="flex items-center gap-2 text-2xl font-bold"><Scissors className="h-6 w-6 text-indigo-600" />Video Trimmer</h1><div className="space-y-5 rounded-2xl border bg-white p-6 dark:border-slate-800 dark:bg-slate-900"><FileUpload onFileSelect={setFile} selectedFile={file} accept={{'video/*':['.mp4','.mkv','.webm','.mov']}} label="Drop video to trim" hint="MP4, MKV, WebM or MOV" />{file && <><div className="grid grid-cols-2 gap-3"><Input type="number" min="0" value={start} onChange={(e)=>setStart(e.target.value)} /><Input type="number" min="0.1" value={end} onChange={(e)=>setEnd(e.target.value)} /></div><Button className="w-full" disabled={submitting || Number(end)<=Number(start)} onClick={run}>{submitting?'Uploading…':'Trim Video'}</Button></>}{error && <p className="flex items-center gap-2 text-sm text-red-600"><AlertCircle className="h-4 w-4" />{error}</p>}<ProcessingJobStatus jobId={jobId} /></div></div>;
}
