import type { Metadata } from 'next';
import './globals.css';
import Navigation from '@/components/Navigation';
import { ThemeProvider } from '@/context/ThemeContext';

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
    <html lang="en" className="dark h-full" suppressHydrationWarning>
      <body className="min-h-full flex flex-col bg-[#F8FAFC] dark:bg-black text-slate-900 dark:text-[#FAFAFA] antialiased selection:bg-[#0066FF] selection:text-white transition-colors duration-200">
        <ThemeProvider>
          <Navigation />
          <main className="flex-1 pt-20 sm:pt-24 pb-20">{children}</main>
          <footer className="border-t border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/90 py-6 text-center text-xs text-slate-500 transition-colors">
            RevBack · Razorpay Buildathon 2026 (Track 3: AI Revenue Recovery) · Autonomous Agent Architecture
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
