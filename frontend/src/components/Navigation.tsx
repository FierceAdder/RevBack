'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Receipt,
  UserCheck,
  TrendingUp,
  Sparkles,
  Database,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { fetchMetrics, seedDatabase } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';

export default function Navigation() {
  const pathname = usePathname();
  const [pendingApprovals, setPendingApprovals] = useState(0);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState(false);
  const [apiConnected, setApiConnected] = useState(true);

  useEffect(() => {
    async function loadQuickStats() {
      try {
        const metrics = await fetchMetrics();
        setPendingApprovals(metrics.pending_approvals_count);
        setApiConnected(true);
      } catch {
        setApiConnected(false);
      }
    }
    loadQuickStats();
    const interval = setInterval(loadQuickStats, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleSeed = async () => {
    setIsSeeding(true);
    setSeedSuccess(false);
    try {
      await seedDatabase(25, true);
      setSeedSuccess(true);
      setTimeout(() => setSeedSuccess(false), 3000);
      window.location.reload();
    } catch (err) {
      console.error('Seed error:', err);
    } finally {
      setIsSeeding(false);
    }
  };

  const navItems = [
    { href: '/', label: 'Overview', icon: LayoutDashboard },
    { href: '/invoices', label: 'Ledger', icon: Receipt },
    {
      href: '/approvals',
      label: 'Approvals',
      icon: UserCheck,
      badge: pendingApprovals > 0 ? pendingApprovals : undefined,
    },
    { href: '/simulation', label: 'Benchmark', icon: TrendingUp },
  ];

  return (
    <header className="fixed top-3 sm:top-4 left-0 right-0 z-50 flex justify-center px-3 sm:px-4 pointer-events-none">
      <div className="pointer-events-auto flex items-center justify-between gap-3 max-w-6xl w-full px-4 sm:px-5 py-2.5 rounded-full border border-slate-200/80 dark:border-white/10 bg-white/90 dark:bg-[#070A11]/85 backdrop-blur-2xl shadow-xl dark:shadow-[0_12px_40px_rgba(0,0,0,0.7)] transition-all">
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-[#0066FF] to-[#0099FF] shadow-md shadow-blue-500/30 group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-base font-black tracking-tight text-slate-900 dark:text-white">RevBack</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[9px] font-black text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                Autonomous AI
              </span>
            </div>
          </Link>

          {/* Live System Indicator */}
          <div className="hidden lg:flex items-center gap-1.5 rounded-full bg-slate-100 dark:bg-white/[0.04] px-2.5 py-1 text-xs border border-slate-200 dark:border-white/[0.06]">
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                apiConnected ? 'bg-emerald-500 shadow-sm shadow-emerald-500/50' : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-600 dark:text-slate-400 font-semibold text-[10px] tracking-wide">
              {apiConnected ? 'Razorpay Webhooks Active' : 'Offline'}
            </span>
          </div>
        </div>

        {/* Center Nav Links (Pill Style) */}
        <nav className="flex items-center gap-1 bg-slate-100/80 dark:bg-white/[0.04] p-1 rounded-full border border-slate-200/60 dark:border-white/[0.06]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-white dark:bg-[#0066FF] text-[#0066FF] dark:text-white shadow-sm dark:shadow-md dark:shadow-blue-500/30'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">{item.label}</span>
                {item.badge !== undefined && (
                  <span className="rounded-full bg-rose-500 px-1.5 py-0.2 text-[9px] font-black text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Actions: Theme Toggle + Seed Data */}
        <div className="flex items-center gap-2">
          <ThemeToggle />

          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="flex items-center gap-1.5 rounded-full border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.04] px-3 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-all disabled:opacity-50"
            title="Seed 25 realistic Indian B2B receivables across all 5 debtor archetypes"
          >
            {isSeeding ? (
              <Loader2 className="h-3 w-3 animate-spin text-[#0066FF]" />
            ) : seedSuccess ? (
              <CheckCircle2 className="h-3 w-3 text-emerald-500" />
            ) : (
              <Database className="h-3 w-3 text-slate-400" />
            )}
            <span className="hidden sm:inline">{isSeeding ? 'Seeding...' : seedSuccess ? 'Seeded' : 'Seed Data'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
