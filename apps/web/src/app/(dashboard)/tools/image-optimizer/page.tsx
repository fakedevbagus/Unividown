'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Image, Sparkles, CheckCircle, AlertCircle, SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';

export default function ImageOptimizerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [quality, setQuality] = useState(85);
  const [maxWidth, setMaxWidth] = useState(1920);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleOptimize = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('quality', quality.toString());
    formData.append('max_width', maxWidth.toString());

    try {
      const res = await fetch('/api/worker/tools/image/optimize', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Image optimization queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `Image optimization job #${data.job_id} queued! Processing in background.`,
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
          <Image className="w-6 h-6 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
          <span>Image Optimizer</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Optimize images for web - reduce file size while maintaining visual quality. Supports JPEG, PNG, WebP.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{ 'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp'] }}
          label="Drop image file to optimize"
          hint="Supports JPG, PNG, WebP, GIF up to 50MB"
        />

        {file && (
          <div className="space-y-4 pt-2">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Quality (1-100)
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="10"
                    max="100"
                    value={quality}
                    onChange={(e) => setQuality(parseInt(e.target.value))}
                    className="flex-1 h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none accent-indigo-600"
                  />
                  <span className="text-sm font-mono text-slate-700 dark:text-slate-300 w-10">{quality}</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Max Width (px)
                </label>
                <select
                  value={maxWidth}
                  onChange={(e) => setMaxWidth(parseInt(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="1920">1920 (Full HD)</option>
                  <option value="1280">1280 (HD)</option>
                  <option value="800">800 (Mobile)</option>
                  <option value="640">640 (Thumbnail)</option>
                </select>
              </div>
            </div>

            <Button
              onClick={handleOptimize}
              disabled={loading}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Optimizing...</span>
                </>
              ) : (
                <>
                  <SlidersHorizontal className="w-4 h-4 mr-1" />
                  <span>Optimize Image</span>
                </>
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