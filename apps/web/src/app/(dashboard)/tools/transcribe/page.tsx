'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Sparkles, CheckCircle, AlertCircle, Mic, Languages } from 'lucide-react';
import { Button } from '@/components/ui/button';
import FileUpload from '@/components/shared/file-upload';

export default function TranscribePage() {
  const [file, setFile] = useState<File | null>(null);
  const [model, setModel] = useState('tiny');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleTranscribe = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', model);

    try {
      const res = await fetch('/api/worker/tools/transcribe', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Transcription queue failed');
      const data = await res.json();
      setResult({
        success: true,
        message: `Transcription job #${data.job_id} queued! Model: ${data.model}. Processing in background.`,
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
          <span>AI Transcription</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Transcribe audio/video to text using OpenAI Whisper. Supports 99+ languages.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <FileUpload
          onFileSelect={setFile}
          selectedFile={file}
          accept={{
            'audio/*': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            'video/*': ['.mp4', '.mkv', '.webm', '.mov', '.avi']
          }}
          label="Drop audio or video file to transcribe"
          hint="Supports audio and video files up to 500MB"
        />

        {file && (
          <div className="space-y-4 pt-2">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                Whisper Model
              </label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="tiny">Tiny (~39 MB) - Fastest, English only</option>
                <option value="base">Base (~74 MB) - Fast, multilingual</option>
                <option value="small">Small (~244 MB) - Better accuracy</option>
                <option value="medium">Medium (~769 MB) - Good accuracy</option>
                <option value="large">Large (~1550 MB) - Best accuracy</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-sm text-slate-600 dark:text-slate-400">
                <p className="font-medium text-slate-900 dark:text-slate-100 mb-1 flex items-center gap-1">
                  <Mic className="w-3.5 h-3.5" />
                  Audio extracted automatically from video
                </p>
              </div>
              <div className="bg-slate-50 dark:bg-slate-800/50 rounded-lg p-4 text-sm text-slate-600 dark:text-slate-400">
                <p className="font-medium text-slate-900 dark:text-slate-100 mb-1 flex items-center gap-1">
                  <Languages className="w-3.5 h-3.5" />
                  99+ languages supported
                </p>
              </div>
            </div>

            <div className="bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg p-4 text-sm text-amber-800 dark:text-amber-200">
              <p className="font-medium text-amber-900 dark:text-amber-100 mb-1">Note:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Larger models take significantly longer but are more accurate</li>
                <li>First run downloads model weights (~39 MB for tiny)</li>
                <li>Output: .txt transcript + .json segments with timestamps</li>
              </ul>
            </div>

            <Button
              onClick={handleTranscribe}
              disabled={loading}
              className="w-full py-2.5"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Queuing transcription...</span>
                </>
              ) : (
                <>
                  <Mic className="w-4 h-4 mr-1" />
                  <span>Transcribe to Text</span>
                </>
              )}
            </Button>
          </div>
        )}

        {result && (
          <div
            className={result.success
                ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 p-3 rounded-lg text-xs flex items-center gap-2"
                : "bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800 p-3 rounded-lg text-xs flex items-center gap-2"}
          >
            {result.success ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
            <span>{result.message}</span>
          </div>
        )}
      </div>
    </div>
  );
}
