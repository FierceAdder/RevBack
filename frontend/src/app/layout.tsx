import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/Navigation';

export const metadata: Metadata = {
  title: 'RevBack — AI Revenue Recovery & Escalation Agent',
  description:
    'Autonomous B2B revenue recovery agent: Detect, Recover, Verify, Escalate. Built for Razorpay Buildathon 2026 (Track 3).',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark h-full">
      <body className="min-h-full flex flex-col bg-[#0B0F17] text-slate-100 antialiased selection:bg-blue-600 selection:text-white">
        <Navigation />
        <main className="flex-1 pb-16">{children}</main>
        <footer className="border-t border-slate-900 bg-[#090C12] py-4 text-center text-xs text-slate-500">
          RevBack · Razorpay Buildathon 2026 (Track 3: AI Revenue Recovery) · Autonomous Agent Architecture
        </footer>
      </body>
    </html>
  );
}
