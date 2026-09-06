'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Scissors, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import FileUpload from '@/components/shared/file-upload';

export default function VideoTrimmerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [start, setStart] = useState('0');
  const [end, setEnd] = useState('10');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleTrim = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('start', start);
    formData.append('end', end);

    try {
      const res = await fetch('/api/worker/tools/trim', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Trim queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `Trimming job #${data.job_id} queued! Processing in background.`,
      });
      setFile(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to worker';
      setResult({ success: false, message: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <Link
        href="/tools"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" /> Back to Tools
      </Link>

      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Scissors className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>Video Trimmer</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Cut segments from your video files accurately with start and end timestamps.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{ 'video/*': ['.mp4', '.mkv', '.webm', '.mov'] }}
          label="Drop video file to trim"
          hint="Supports MP4, MKV, WebM up to 2GB"
        />

        {file && (
          <div className="space-y-4 pt-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Start Time (seconds)
                </label>
                <Input
                  type="number"
                  min="0"
                  step="0.5"
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  End Time (seconds)
                </label>
                <Input
                  type="number"
                  min="0.1"
                  step="0.5"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                />
              </div>
            </div>

            <Button
              onClick={handleTrim}
              disabled={loading || Number(end) <= Number(start)}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Trimming...</span>
                </>
              ) : (
                <span>Trim Video ({Number(end) - Number(start)}s)</span>
              )}
            </Button>
          </div>
        )}

        {result && (
          <div
            className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
              result.success
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
            }`}
          >
            {result.success ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span>{result.message}</span>
          </div>
        )}
      </div>
    </div>
  );
}
