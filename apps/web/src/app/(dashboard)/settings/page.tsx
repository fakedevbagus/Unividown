'use client';

import React, { useState } from 'react';
import { Settings, Save, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function SettingsPage() {
  const [downloadDir, setDownloadDir] = useState('./data/downloads');
  const [maxConcurrent, setMaxConcurrent] = useState('3');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <Settings className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
          <span>Settings</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Manage local download preferences and worker parameters.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm max-w-2xl">
        <form onSubmit={handleSave} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Default Download Directory
            </label>
            <Input
              value={downloadDir}
              onChange={(e) => setDownloadDir(e.target.value)}
              placeholder="./data/downloads"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              Max Concurrent Downloads
            </label>
            <Input
              type="number"
              min="1"
              max="10"
              value={maxConcurrent}
              onChange={(e) => setMaxConcurrent(e.target.value)}
            />
          </div>

          <Button type="submit" className="gap-2">
            {saved ? <Check className="w-4 h-4 text-emerald-400" /> : <Save className="w-4 h-4" />}
            <span>{saved ? 'Saved!' : 'Save Settings'}</span>
          </Button>
        </form>
      </div>
    </div>
  );
}

