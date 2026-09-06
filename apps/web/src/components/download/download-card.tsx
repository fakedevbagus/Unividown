'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Film, Music, AlertCircle, CheckCircle2, Clock, RotateCw, Trash2, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

export interface DownloadJobData {
  id: number;
  url: string;
  title?: string | null;
  platform?: string | null;
  thumbnail_url?: string | null;
  status: string;
  progress: number;
  quality?: string | null;
  error_message?: string | null;
}

interface DownloadCardProps {
  job: DownloadJobData;
  onRetry?: (id: number) => void;
  onCancel?: (id: number) => void;
}

export default function DownloadCard({ job, onRetry, onCancel }: DownloadCardProps) {
  const statusConfig: Record<string, { label: string; badge: string; icon: React.ReactNode }> = {
    pending: {
      label: 'Queued',
      badge: 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300',
      icon: <Clock className="w-3 h-3 animate-spin" />,
    },
    processing: {
      label: 'Downloading',
      badge: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300',
      icon: <RotateCw className="w-3 h-3 animate-spin" />,
    },
    completed: {
      label: 'Completed',
      badge: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300',
      icon: <CheckCircle2 className="w-3 h-3" />,
    },
    failed: {
      label: 'Failed',
      badge: 'bg-red-100 text-red-800 dark:bg-red-950/60 dark:text-red-300',
      icon: <AlertCircle className="w-3 h-3" />,
    },
    cancelled: {
      label: 'Cancelled',
      badge: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
      icon: <Clock className="w-3 h-3" />,
    },
  };

  const statusInfo = statusConfig[job.status] || {
    label: job.status,
    badge: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    icon: <Clock className="w-3 h-3" />,
  };

  const isAudio = job.quality === 'mp3' || job.quality === 'audio';

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm"
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-2">
        <div className="flex items-center gap-3 min-w-0 flex-1">
          <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 text-slate-600 dark:text-slate-300 overflow-hidden">
            {job.thumbnail_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={job.thumbnail_url} alt={job.title || 'Thumbnail'} className="w-full h-full object-cover" />
            ) : isAudio ? (
              <Music className="w-5 h-5 text-indigo-500" />
            ) : (
              <Film className="w-5 h-5 text-purple-500" />
            )}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-slate-900 dark:text-slate-100 text-sm truncate">
              {job.title || job.url}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 truncate flex items-center gap-2 mt-0.5">
              <span>{job.platform || 'Media'}</span>
              <span>•</span>
              <span className="uppercase">{job.quality || 'best'}</span>
              <span>•</span>
              <a href={job.url} target="_blank" rel="noreferrer" className="hover:text-indigo-500 inline-flex items-center gap-0.5">
                Link <ExternalLink className="w-2.5 h-2.5" />
              </a>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 self-end sm:self-center">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${statusInfo.badge}`}>
            {statusInfo.icon}
            {statusInfo.label}
          </span>
          {job.status === 'failed' && onRetry && (
            <Button size="sm" variant="outline" onClick={() => onRetry(job.id)} title="Retry">
              <RotateCw className="w-3.5 h-3.5" />
            </Button>
          )}
          {onCancel && (
            <Button size="sm" variant="ghost" onClick={() => onCancel(job.id)} className="text-slate-400 hover:text-red-500">
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          )}
        </div>
      </div>

      {(job.status === 'processing' || job.status === 'pending') && (
        <div className="mt-3 space-y-1">
          <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
            <motion.div
              className="bg-indigo-600 h-full rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${Math.max(job.progress || 0, 4)}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>{job.status === 'pending' ? 'Queued...' : 'Downloading...'}</span>
            <span className="font-mono font-medium">{job.progress.toFixed(1)}%</span>
          </div>
        </div>
      )}

      {job.status === 'failed' && job.error_message && (
        <div className="mt-3 p-2 rounded-lg bg-red-50 dark:bg-red-950/40 text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span className="truncate">{job.error_message}</span>
        </div>
      )}
    </motion.div>
  );
}
