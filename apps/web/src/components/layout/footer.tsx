import React from 'react';
import { Heart, Coffee, ExternalLink } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-xs py-6 mt-auto">
      <div className="max-w-6xl mx-auto px-4 md:px-8">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-500 fill-red-500 inline" />
            <span>by</span>
            <a
              href="https://github.com/fakedevbagus"
              target="_blank"
              rel="noopener noreferrer"
              className="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline inline-flex items-center gap-0.5"
            >
              fakedevbagus
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="https://trakteer.id/fakedevbagus"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-red-500 hover:bg-red-600 text-white text-xs font-semibold shadow-xs transition-colors"
            >
              <Coffee className="w-3.5 h-3.5" />
              <span>Trakteer</span>
            </a>

            <a
              href="https://saweria.co/fakedevbagus"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold shadow-xs transition-colors"
            >
              <Coffee className="w-3.5 h-3.5" />
              <span>Saweria</span>
            </a>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800/60 text-center text-xs text-slate-500 dark:text-slate-400">
          <p>Unividown v1.0.0 • Personal Use & Media Workflow Engine</p>
          <p className="mt-1">
            Please respect copyright regulations and each platform&apos;s Terms of Service.
          </p>
        </div>
      </div>
    </footer>
  );
}
