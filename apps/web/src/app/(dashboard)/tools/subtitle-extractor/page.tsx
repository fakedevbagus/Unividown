'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';
import ProcessingJobStatus from '@/components/tools/processing-job-status';
import { useProcessingSubmit } from '@/hooks/use-processing-submit';

export default function SubtitleExtractorPage(){const[file,setFile]=useState<File|null>(null);const{jobId,submitting,error,submit}=useProcessingSubmit('/api/worker/tools/subtitle/extract');const run=async()=>{if(!file)return;const body=new FormData();body.append('file',file);if(await submit(body))setFile(null);};return <div className="space-y-6 max-w-2xl"><Link href="/tools" className="inline-flex items-center gap-1 text-xs text-slate-500"><ArrowLeft className="h-4 w-4"/>Back to Tools</Link><h1 className="flex items-center gap-2 text-2xl font-bold"><FileText className="h-6 w-6 text-indigo-600"/>Subtitle Extractor</h1><div className="space-y-5 rounded-2xl border bg-white p-6 dark:border-slate-800 dark:bg-slate-900"><FileUpload onFileSelect={setFile} selectedFile={file} accept={{'video/*':['.mp4','.mkv','.webm','.mov','.avi']}} label="Drop video with embedded subtitles" hint="Result is provided as WebVTT"/>{file&&<Button className="w-full" disabled={submitting} onClick={run}>{submitting?'Uploading…':'Extract Subtitles'}</Button>}{error&&<p className="flex items-center gap-2 text-sm text-red-600"><AlertCircle className="h-4 w-4"/>{error}</p>}<ProcessingJobStatus jobId={jobId}/></div></div>;}
