import Link from 'next/link';
import { Download, Wrench, Sparkles, Zap, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  return (
    <div className="space-y-10 py-6">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 text-white p-8 md:p-12 shadow-xl">
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm text-xs font-medium text-indigo-200">
            <Sparkles className="w-3.5 h-3.5" />
            Universal Media Downloader & Toolkit
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight">
            Download & Process Media in Seconds.
          </h1>
          <p className="text-slate-200 text-sm md:text-base leading-relaxed">
            High performance media downloader powered by yt-dlp and FFmpeg. Extract high-resolution video, convert audio, trim clips, and generate QR codes seamlessly.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link href="/download">
              <Button size="lg" className="bg-white text-indigo-950 hover:bg-slate-100 font-semibold shadow-lg">
                <Download className="w-5 h-5 mr-2" /> Start Downloading
              </Button>
            </Link>
            <Link href="/tools">
              <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10">
                <Wrench className="w-5 h-5 mr-2" /> Explore Tools
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Feature Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-lg">Multi-Platform Engine</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Supports YouTube, TikTok, Twitter/X, Instagram, SoundCloud and 1000+ sources with quality selection up to 4K.
          </p>
        </div>

        <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 flex items-center justify-center">
            <Wrench className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-lg">FFmpeg Media Tools</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Convert MP4, WebM, MKV, MP3, trim videos, and compress file sizes right from your local worker.
          </p>
        </div>

        <div className="p-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-3">
          <div className="w-10 h-10 rounded-lg bg-pink-50 dark:bg-pink-950/60 text-pink-600 dark:text-pink-400 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-lg">Fast & Self-Hosted</h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            Privacy-first local storage, WebSocket real-time progress, SQLite queue, and zero external trackers.
          </p>
        </div>
      </div>
    </div>
  );
}

