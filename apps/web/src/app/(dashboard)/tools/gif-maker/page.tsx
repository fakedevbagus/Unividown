'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Image, Sparkles, CheckCircle, AlertCircle, Film } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';
import { Input } from '@/components/ui/input';

export default function GifMakerPage() {
  const [file, setFile] = useState<File | null>(null);
  const [start, setStart] = useState(0);
  const [duration, setDuration] = useState(5);
  const [fps, setFps] = useState(15);
  const [scale, setScale] = useState(480);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleMakeGif = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('start', start.toString());
    formData.append('duration', duration.toString());
    formData.append('fps', fps.toString());
    formData.append('scale', scale.toString());

    try {
      const res = await fetch('/api/worker/tools/gif/make', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('GIF creation queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `GIF creation job #${data.job_id} queued! Processing in background.`,
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
          <Image className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>GIF Maker</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Create animated GIFs from video clips. Adjust start time, duration, frame rate, and size.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{
            'video/*': ['.mp4', '.mkv', '.webm', '.mov', '.avi']
          }}
          label="Drop video file to make GIF"
          hint="Supports MP4, MKV, WebM, MOV up to 500MB"
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
                  value={start}
                  onChange={(e) => setStart(Math.max(0, parseFloat(e.target.value) || 0))}
                  min="0"
                  step="0.1"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Duration (seconds)
                </label>
                <Input
                  type="number"
                  value={duration}
                  onChange={(e) => setDuration(Math.max(0.1, Math.min(30, parseFloat(e.target.value) || 0.1)))}
                  min="0.1"
                  max="30"
                  step="0.1"
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Frame Rate (FPS)
                </label>
                <select
                  value={fps}
                  onChange={(e) => setFps(parseInt(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="10">10 FPS (smaller)</option>
                  <option value="15">15 FPS (balanced)</option>
                  <option value="20">20 FPS (smoother)</option>
                  <option value="25">25 FPS (smooth)</option>
                  <option value="30">30 FPS (largest)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Width (px)
                </label>
                <select
                  value={scale}
                  onChange={(e) => setScale(parseInt(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="320">320 (small)</option>
                  <option value="480">480 (medium)</option>
                  <option value="640">640 (large)</option>
                  <option value="720">720 (HD)</option>
                </select>
              </div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-sm text-slate-600 dark:text-slate-400">
              <p className="font-medium text-slate-900 dark:text-slate-100 mb-1">Tips:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Keep duration under 10s for smaller file sizes</li>
                <li>15 FPS is a good balance between smoothness and file size</li>
                <li>480px width works well for most use cases</li>
              </ul>
            </div>

            <Button
              onClick={handleMakeGif}
              disabled={loading}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Creating GIF...</span>
                </>
              ) : (
                <>
                  <Film className="w-4 h-4 mr-1" />
                  <span>Create GIF</span>
                </>
              )}
            </Button>
          </div>
        )}

        {result && (
          <div
            className={result.success
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'}
          >
            {result.success ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span>{result.message}</span>
          </div>
        )}
      </div>
    </div>
  );
}
