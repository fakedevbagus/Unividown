'use client';
import { useState } from 'react';

interface PlaylistEntry {
  id: string;
  title: string;
  url: string;
  duration?: number;
}

interface PlaylistSelectorProps {
  entries: PlaylistEntry[];
  onSelect: (selectedUrls: string[]) => void;
}

export default function PlaylistSelector({ entries, onSelect }: PlaylistSelectorProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const toggleSelect = (url: string) => {
    const newSelected = new Set(selected);
    if (newSelected.has(url)) newSelected.delete(url);
    else newSelected.add(url);
    setSelected(newSelected);
  };

  const selectAll = () => setSelected(new Set(entries.map((e) => e.url)));
  const deselectAll = () => setSelected(new Set());
  const handleDownload = () => onSelect(Array.from(selected));

  return (
    <div className="space-y-4 border border-indigo-200 dark:border-slate-700 rounded-xl p-4 bg-white dark:bg-slate-800">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
          {selected.size} / {entries.length} selected
        </p>
        <div className="flex gap-2">
          <button onClick={selectAll} className="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 hover:bg-slate-200">
            Select All
          </button>
          <button onClick={deselectAll} className="text-xs px-2 py-1 rounded bg-slate-100 dark:bg-slate-700 hover:bg-slate-200">
            Deselect
          </button>
        </div>
      </div>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {entries.map((entry) => (
          <label key={entry.id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 cursor-pointer">
            <input type="checkbox" checked={selected.has(entry.url)} onChange={() => toggleSelect(entry.url)} />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{entry.title || entry.id}</p>
              {entry.duration && <p className="text-xs text-slate-500">{Math.floor(entry.duration / 60)}:{String(entry.duration % 60).padStart(2, '0')}</p>}
            </div>
          </label>
        ))}
      </div>
      <button onClick={handleDownload} disabled={selected.size === 0} className="w-full py-2 rounded-lg bg-indigo-600 text-white disabled:opacity-50">
        Download Selected ({selected.size})
      </button>
    </div>
  );
}
