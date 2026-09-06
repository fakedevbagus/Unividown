'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, QrCode, Download, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function QRGeneratorPage() {
  const [data, setData] = useState('https://unividown.dev');
  const [qr, setQr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const generateQR = async () => {
    if (!data.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/tools/qr?data=${encodeURIComponent(data.trim())}&size=320`);
      const result = await res.json();
      if (result.qr) {
        setQr(result.qr);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const downloadQR = () => {
    if (!qr) return;
    const link = document.createElement('a');
    link.href = qr;
    link.download = `qr-code-${Date.now()}.png`;
    link.click();
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
          <QrCode className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          <span>QR Code Generator</span>
        </h1>
        <p className="text-sm text-slate-500 mt-1">
          Generate high quality, downloadable QR codes for websites, texts, or contact info.
        </p>
      </div>

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
            Content (URL or Text)
          </label>
          <Input
            value={data}
            onChange={(e) => setData(e.target.value)}
            placeholder="Enter website URL or plain text..."
          />
        </div>

        <Button onClick={generateQR} disabled={loading || !data.trim()} className="w-full py-2.5">
          {loading ? (
            <>
              <Sparkles className="w-4 h-4 animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <QrCode className="w-4 h-4" />
              <span>Generate QR Code</span>
            </>
          )}
        </Button>

        {qr && (
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex flex-col items-center gap-4">
            <div className="p-4 bg-white rounded-xl shadow-md border border-slate-200">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={qr} alt="Generated QR Code" className="w-56 h-56 object-contain" />
            </div>
            <Button onClick={downloadQR} variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              <span>Download PNG</span>
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
