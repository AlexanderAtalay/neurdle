import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Neurdle',
  description: 'Daily neuroanatomy guessing game; Identify brain regions in 3D',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,   // prevents iOS auto-zoom on input focus
  userScalable: false,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#1a1a2e] text-white overscroll-none">
        {children}
      </body>
    </html>
  );
}
