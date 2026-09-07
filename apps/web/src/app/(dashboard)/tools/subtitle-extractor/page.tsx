'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';

export default function SubtitleExtractorPage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleExtract = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/worker/tools/subtitle/extract', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Subtitle extraction queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `Subtitle extraction job #${data.job_id} queued! Processing in background.`,
      });
      setFile(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to media worker';
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
          <FileText className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>Subtitle Extractor</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Extract embedded subtitles from video files (MP4, MKV, WebM). Outputs WebVTT format.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{ 'video/*': ['.mp4', '.mkv', '.webm', '.mov', '.avi'] }}
          label="Drop video file with subtitles"
          hint="Supports MP4, MKV, WebM with embedded subtitle tracks"
        />

        {file && (
          <div className="space-y-4 pt-2">
            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-sm text-slate-600 dark:text-slate-400">
              <p className="font-medium text-slate-900 dark:text-slate-100 mb-1">How it works:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Extracts the first subtitle track found in the video</li>
                <li>Output format: WebVTT (.vtt) - compatible with all players</li>
                <li>If no subtitles found, job completes with empty result</li>
              </ul>
            </div>

            <Button
              onClick={handleExtract}
              disabled={loading}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Extracting...</span>
                </>
              ) : (
                <span>Extract Subtitles</span>
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