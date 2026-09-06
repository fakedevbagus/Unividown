'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Film, Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';

export default function VideoConverterPage() {
  const [file, setFile] = useState<File | null>(null);
  const [format, setFormat] = useState('mp4');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleConvert = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);

    try {
      const res = await fetch('/api/worker/tools/convert', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Conversion queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `Conversion job #${data.job_id} queued! Processing in background.`,
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
          <Film className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>Video Converter</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Convert video containers and formats using high efficiency FFmpeg encoders.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{ 'video/*': ['.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv'] }}
          label="Drop video file to convert"
          hint="Supports MP4, MKV, WebM, AVI, MOV up to 2GB"
        />

        {file && (
          <div className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Target Format
              </label>
              <select
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="mp4">MP4 (H.264 / AAC - Universal)</option>
                <option value="mkv">MKV (Matroska)</option>
                <option value="webm">WebM (VP9 / Opus - Web friendly)</option>
                <option value="avi">AVI</option>
                <option value="mov">QuickTime MOV</option>
              </select>
            </div>

            <Button
              onClick={handleConvert}
              disabled={loading}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Convert to {format.toUpperCase()}</span>
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
            {result.success ? (
              <CheckCircle className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            <span>{result.message}</span>
          </div>
        )}
      </div>
    </div>
  );
}
