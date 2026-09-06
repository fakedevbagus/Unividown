'use client';

import React from 'react';
import ToolCard from '@/components/tools/tool-card';
import { Film, Scissors, Music, QrCode, KeyRound, Wrench } from 'lucide-react';

const tools = [
  {
    icon: Film,
    title: 'Video Converter',
    description: 'Convert videos between MP4, MKV, WebM, AVI and FLV formats with FFmpeg.',
    href: '/tools/video-converter',
    badge: 'FFmpeg',
  },
  {
    icon: Scissors,
    title: 'Video Trimmer',
    description: 'Cut start and end timestamps from media clips quickly without re-encoding.',
    href: '/tools/video-trimmer',
    badge: 'Fast Cut',
  },
  {
    icon: Music,
    title: 'Audio Converter',
    description: 'Extract and transcode audio to MP3, AAC, WAV, FLAC, and OGG formats.',
    href: '/tools/audio-converter',
    badge: 'Audio',
  },
  {
    icon: QrCode,
    title: 'QR Code Generator',
    description: 'Generate high resolution downloadable QR codes for links, text, or WiFi.',
    href: '/tools/qr',
    badge: 'Utility',
  },
  {
    icon: KeyRound,
    title: 'Password Generator',
    description: 'Generate strong cryptographically secure random passwords and phrases.',
    href: '/tools/password',
    badge: 'Security',
  },
];

export default function ToolsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <Wrench className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          <span>Media & Utility Tools</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Perform video conversions, audio extractions, trimming, and utilities powered by local services.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {tools.map((tool) => (
          <ToolCard key={tool.title} {...tool} />
        ))}
      </div>
    </div>
  );
}
