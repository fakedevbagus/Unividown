'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Image as ImageIcon, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';
import ProcessingJobStatus from '@/components/tools/processing-job-status';
import { useProcessingSubmit } from '@/hooks/use-processing-submit';

export default function ImageOptimizerPage() {
  const [file,setFile]=useState<File|null>(null); const [quality,setQuality]=useState(85); const [maxWidth,setMaxWidth]=useState(1920);
  const {jobId,submitting,error,submit}=useProcessingSubmit('/api/worker/tools/image/optimize');
  const run=async()=>{if(!file)return;const body=new FormData();body.append('file',file);body.append('quality',String(quality));body.append('max_width',String(maxWidth));if(await submit(body))setFile(null);};
  return <div className="space-y-6 max-w-2xl"><Link href="/tools" className="inline-flex items-center gap-1 text-xs text-slate-500"><ArrowLeft className="h-4 w-4" />Back to Tools</Link><h1 className="flex items-center gap-2 text-2xl font-bold"><ImageIcon className="h-6 w-6 text-indigo-600" />Image Optimizer</h1><div className="space-y-5 rounded-2xl border bg-white p-6 dark:border-slate-800 dark:bg-slate-900"><FileUpload onFileSelect={setFile} selectedFile={file} accept={{'image/*':['.jpg','.jpeg','.png','.webp','.gif']}} label="Drop image to optimize" hint="JPEG, PNG, WebP or GIF" />{file&&<><label className="text-sm">Quality: {quality}<input className="w-full" type="range" min="10" max="100" value={quality} onChange={(e)=>setQuality(Number(e.target.value))}/></label><select className="w-full rounded-lg border p-2 dark:bg-slate-800" value={maxWidth} onChange={(e)=>setMaxWidth(Number(e.target.value))}><option value="1920">1920px</option><option value="1280">1280px</option><option value="800">800px</option><option value="640">640px</option></select><Button className="w-full" disabled={submitting} onClick={run}>{submitting?'Uploading…':'Optimize Image'}</Button></>}{error&&<p className="flex items-center gap-2 text-sm text-red-600"><AlertCircle className="h-4 w-4" />{error}</p>}<ProcessingJobStatus jobId={jobId}/></div></div>;
}
