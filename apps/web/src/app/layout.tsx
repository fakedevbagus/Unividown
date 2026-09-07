import type { Metadata } from 'next';
import localFont from 'next/font/local';
import { ThemeProvider } from '@/providers/theme-provider';
import { ToastProvider } from '@/components/ui/toast';
import Sidebar from '@/components/layout/sidebar';
import Footer from '@/components/layout/footer';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import './globals.css';

const geistSans = localFont({
  src: './fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
});
const geistMono = localFont({
  src: './fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
});

export const metadata: Metadata = {
  title: 'Unividown - Media Downloader & Tools',
  description:
    'Universal media downloader and toolkit powered by yt-dlp & FFmpeg. Convert video, extract audio, and generate utilities locally.',
  keywords: ['download', 'video', 'audio', 'youtube', 'tiktok', 'converter', 'trimmer', 'ffmpeg', 'yt-dlp'],
  authors: [{ name: 'fakedevbagus', url: 'https://github.com/fakedevbagus' }],
  openGraph: {
    title: 'Unividown - Universal Media Downloader',
    description: 'High-speed media extraction and FFmpeg converter suite',
    type: 'website',
  },
  manifest: '/manifest.json',
  themeColor: '#4f46e5',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Unividown',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="apple-touch-icon" href="/icon-192.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#4f46e5" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased selection:bg-indigo-500 selection:text-white`}
      >
        <ThemeProvider>
          <ToastProvider>
            <div className="flex h-screen overflow-hidden">
              <Sidebar />
              <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
                <main className="flex-1 p-6 md:p-8">
                  <div className="max-w-6xl mx-auto w-full">
                    <ErrorBoundary>
                      {children}
                    </ErrorBoundary>
                  </div>
                </main>
                <Footer />
              </div>
            </div>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}


