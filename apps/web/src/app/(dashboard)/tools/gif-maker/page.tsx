'use client';
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Images, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import FileUpload from '@/components/shared/file-upload';
import ProcessingJobStatus from '@/components/tools/processing-job-status';
import { useProcessingSubmit } from '@/hooks/use-processing-submit';

export default function GifMakerPage(){const[file,setFile]=useState<File|null>(null);const[start,setStart]=useState(0);const[duration,setDuration]=useState(5);const{jobId,submitting,error,submit}=useProcessingSubmit('/api/worker/tools/gif/make');const run=async()=>{if(!file)return;const body=new FormData();body.append('file',file);body.append('start',String(start));body.append('duration',String(duration));body.append('fps','15');body.append('scale','480');if(await submit(body))setFile(null);};return <div className="space-y-6 max-w-2xl"><Link href="/tools" className="inline-flex items-center gap-1 text-xs text-slate-500"><ArrowLeft className="h-4 w-4"/>Back to Tools</Link><h1 className="flex items-center gap-2 text-2xl font-bold"><Images className="h-6 w-6 text-indigo-600"/>GIF Maker</h1><div className="space-y-5 rounded-2xl border bg-white p-6 dark:border-slate-800 dark:bg-slate-900"><FileUpload onFileSelect={setFile} selectedFile={file} accept={{'video/*':['.mp4','.mkv','.webm','.mov','.avi']}} label="Drop video to create GIF" hint="Creates a 480px, 15 FPS GIF"/>{file&&<><div className="grid grid-cols-2 gap-3"><Input type="number" min="0" value={start} onChange={(e)=>setStart(Number(e.target.value))}/><Input type="number" min="0.1" max="30" value={duration} onChange={(e)=>setDuration(Number(e.target.value))}/></div><Button className="w-full" disabled={submitting} onClick={run}>{submitting?'Uploading…':'Create GIF'}</Button></>}{error&&<p className="flex items-center gap-2 text-sm text-red-600"><AlertCircle className="h-4 w-4"/>{error}</p>}<ProcessingJobStatus jobId={jobId}/></div></div>;}
