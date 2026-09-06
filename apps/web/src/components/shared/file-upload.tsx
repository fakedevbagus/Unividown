'use client';

import React from 'react';
import { useDropzone, Accept } from 'react-dropzone';
import { UploadCloud, File, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface FileUploadProps {
  onFileSelect: (file: File | null) => void;
  selectedFile?: File | null;
  accept?: Accept;
  label?: string;
  hint?: string;
}

export default function FileUpload({
  onFileSelect,
  selectedFile,
  accept,
  label = 'Drop file here or click to browse',
  hint = 'Supports media files up to 2GB',
}: FileUploadProps) {
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (files) => {
      if (files.length > 0) onFileSelect(files[0]);
    },
    accept,
    maxFiles: 1,
  });

  if (selectedFile) {
    const sizeMb = (selectedFile.size / (1024 * 1024)).toFixed(2);
    return (
      <div className="border border-indigo-200 dark:border-indigo-900/60 bg-indigo-50/50 dark:bg-indigo-950/20 rounded-xl p-4 flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-lg bg-indigo-600 text-white flex items-center justify-center shrink-0">
            <File className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-semibold truncate text-slate-900 dark:text-slate-100">
              {selectedFile.name}
            </p>
            <p className="text-xs text-slate-500">{sizeMb} MB</p>
          </div>
        </div>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onFileSelect(null)}
          className="text-slate-400 hover:text-red-500"
        >
          <X className="w-4 h-4" />
        </Button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
        isDragActive
          ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/30 scale-[1.01]'
          : 'border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 bg-slate-50/50 dark:bg-slate-900/50'
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloud className="w-10 h-10 mx-auto mb-3 text-indigo-500/80" />
      <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">
        {isDragActive ? 'Drop the file here' : label}
      </p>
      <p className="text-xs text-slate-500 mt-1">{hint}</p>
    </div>
  );
}
