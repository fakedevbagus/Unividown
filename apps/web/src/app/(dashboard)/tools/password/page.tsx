'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, KeyRound, Copy, Check, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function PasswordGeneratorPage() {
  const [password, setPassword] = useState('');
  const [length, setLength] = useState(16);
  const [includeNumbers, setIncludeNumbers] = useState(true);
  const [includeSymbols, setIncludeSymbols] = useState(true);
  const [includeUppercase, setIncludeUppercase] = useState(true);
  const [copied, setCopied] = useState(false);

  const generatePassword = async () => {
    const params = new URLSearchParams({
      length: length.toString(),
      numbers: includeNumbers.toString(),
      symbols: includeSymbols.toString(),
      uppercase: includeUppercase.toString(),
    });

    try {
      const res = await fetch(`/api/tools/password?${params.toString()}`);
      const data = await res.json();
      setPassword(data.password);
      setCopied(false);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    generatePassword();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [length, includeNumbers, includeSymbols, includeUppercase]);

  const copyPassword = () => {
    if (!password) return;
    navigator.clipboard.writeText(password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
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
          <KeyRound className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>Password Generator</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Generate cryptographically strong passwords locally on your machine.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        {/* Output Display */}
        <div className="flex items-center gap-2 p-3.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
          <code className="flex-1 font-mono text-sm sm:text-base text-slate-900 dark:text-slate-100 break-all select-all px-1">
            {password || 'Generating...'}
          </code>
          <Button
            size="sm"
            variant="outline"
            onClick={copyPassword}
            title="Copy to clipboard"
            className="shrink-0"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={generatePassword}
            title="Regenerate"
            className="shrink-0"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
        </div>

        {/* Controls */}
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
              <span>Password Length</span>
              <span className="font-mono text-indigo-600 dark:text-indigo-400">{length} characters</span>
            </div>
            <input
              type="range"
              min="8"
              max="64"
              value={length}
              onChange={(e) => setLength(parseInt(e.target.value, 10))}
              className="w-full accent-indigo-600 cursor-pointer"
            />
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            <label className="flex items-center gap-2.5 text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={includeUppercase}
                onChange={(e) => setIncludeUppercase(e.target.checked)}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
              <span>Include Uppercase Letters (A-Z)</span>
            </label>

            <label className="flex items-center gap-2.5 text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={includeNumbers}
                onChange={(e) => setIncludeNumbers(e.target.checked)}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
              <span>Include Numbers (0-9)</span>
            </label>

            <label className="flex items-center gap-2.5 text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
              <input
                type="checkbox"
                checked={includeSymbols}
                onChange={(e) => setIncludeSymbols(e.target.checked)}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
              <span>Include Symbols (!@#$%^&*)</span>
            </label>
          </div>
        </div>

        <Button onClick={generatePassword} className="w-full py-2.5">
          <RefreshCw className="w-4 h-4 mr-2" /> Generate New Password
        </Button>
      </div>
    </div>
  );
}
