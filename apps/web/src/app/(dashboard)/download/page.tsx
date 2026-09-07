'use client';

import React, { useState } from 'react';
import { Download, Clipboard, Sparkles, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import DownloadQueue from '@/components/download/download-queue';
import PlaylistSelector from '@/components/download/playlist-selector';

export default function DownloadPage() {
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('best');
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [playlist, setPlaylist] = useState<{ title: string; entries: { id: string; title: string; url: string; duration?: number }[] } | null>(null);

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) setUrl(text);
    } catch {
      // Clipboard unsupported or permission denied
    }
  };

  const detectPlaylist = async (targetUrl: string) => {
    if (!targetUrl.trim()) { setPlaylist(null); return; }
    try {
      const res = await fetch(`/api/worker/downloads/info?url=${encodeURIComponent(targetUrl.trim())}`);
      if (!res.ok) { setPlaylist(null); return; }
      const data = await res.json();
      if (data.type === 'playlist' && data.entries?.length) setPlaylist(data);
      else setPlaylist(null);
    } catch { setPlaylist(null); }
  };

  const handleBatchDownload = async (selectedUrls: string[]) => {
    setSubmitting(true);
    setFeedback(null);
    try {
      const res = await fetch('/api/worker/downloads/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: selectedUrls, quality }),
      });
      if (!res.ok) throw new Error('Batch download failed');
      const data = await res.json();
      setFeedback({ type: 'success', message: data.message || `${selectedUrls.length} jobs queued!` });
      setUrl(''); setPlaylist(null);
      setRefreshTrigger((p) => p + 1);
    } catch (err: unknown) {
      setFeedback({ type: 'error', message: err instanceof Error ? err.message : 'Batch failed' });
    } finally { setSubmitting(false); }
  };

  const handleDownload = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!url.trim()) {
      setFeedback({ type: 'error', message: 'Please enter a valid media URL' });
      return;
    }

    setSubmitting(true);
    setFeedback(null);

    try {
      const res = await fetch('/api/worker/downloads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim(), quality }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Failed to create download' }));
        throw new Error(errorData.detail || 'Download request failed');
      }

      setFeedback({ type: 'success', message: 'Download queued successfully!' });
      setUrl('');
      setRefreshTrigger((prev) => prev + 1);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to connect to worker';
      setFeedback({ type: 'error', message: msg });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <Download className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          <span>Download Media</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Paste any video or audio URL from YouTube, TikTok, X, Instagram, SoundCloud, etc.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm">
        <form onSubmit={handleDownload} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Media URL
            </label>
            <div className="flex gap-2">
              <Input
                value={url}
                onChange={(e) => { setUrl(e.target.value); detectPlaylist(e.target.value); }}
                placeholder="https://www.youtube.com/watch?v=... or https://tiktok.com/@... or playlist URL"
              />
              <Button type="button" variant="outline" onClick={handlePaste} title="Paste from clipboard">
                <Clipboard className="w-4 h-4 mr-1" />
                Paste
              </Button>
            </div>
          </div>

          {playlist && <PlaylistSelector entries={playlist.entries} onSelect={handleBatchDownload} />}

          {!playlist && (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Quality / Format
                </label>
                <select
                  value={quality}
                  onChange={(e) => setQuality(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="best">Best Available (Video + Audio)</option>
                  <option value="1080">1080p Full HD</option>
                  <option value="720">720p HD</option>
                  <option value="480">480p SD</option>
                  <option value="mp3">Audio Only (MP3 192k)</option>
                </select>
              </div>

              <div className="flex items-end">
                <Button type="submit" size="md" disabled={submitting || !url.trim()} className="w-full py-2.5">
                  {submitting ? <Sparkles className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                  <span>{submitting ? 'Queuing...' : 'Start Download'}</span>
                </Button>
              </div>
            </div>
          )}

          {feedback && (
            <div
              className={`p-3 rounded-lg text-xs flex items-center gap-2 ${
                feedback.type === 'success'
                  ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
                  : 'bg-red-50 dark:bg-red-950/40 text-red-700 dark:text-red-300 border border-red-200 dark:border-red-800'
              }`}
            >
              {feedback.type === 'success' ? <CheckCircle className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
              <span>{feedback.message}</span>
            </div>
          )}
        </form>
      </div>

      <DownloadQueue refreshTrigger={refreshTrigger} />
    </div>
  );
}
