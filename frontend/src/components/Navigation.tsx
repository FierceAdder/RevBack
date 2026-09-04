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
    { href: '/invoices', label: 'Receivables Ledger', icon: Receipt },
    {
      href: '/approvals',
      label: 'Supervisor Queue',
      icon: UserCheck,
      badge: pendingApprovals > 0 ? pendingApprovals : undefined,
    },
    { href: '/simulation', label: 'ROI Benchmark', icon: TrendingUp },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600 shadow-sm shadow-blue-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-white">RevBack</span>
                <span className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[11px] font-semibold text-blue-400 border border-blue-500/20">
                  Track 3
                </span>
              </div>
              <p className="text-[11px] font-medium text-slate-400">Autonomous Revenue Recovery</p>
            </div>
          </Link>

          {/* Live System Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 rounded-full bg-slate-900 px-2.5 py-1 text-xs border border-slate-800 ml-4">
            <span
              className={`h-2 w-2 rounded-full ${
                apiConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-300 font-medium text-[11px]">
              {apiConnected ? 'Razorpay Webhooks Active' : 'Offline / Standalone Mode'}
            </span>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`relative flex items-center gap-2 rounded-md px-3 py-1.5 text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-slate-800 text-white shadow-sm'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
                {item.badge !== undefined && (
                  <span className="ml-1 rounded-full bg-rose-500/20 px-1.5 py-0.2 text-[10px] font-bold text-rose-300 border border-rose-500/30">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Quick Action Button */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="flex items-center gap-1.5 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-800 transition-colors disabled:opacity-50"
            title="Seed 25 realistic Indian B2B receivables across all 5 debtor archetypes"
          >
            {isSeeding ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-400" />
            ) : seedSuccess ? (
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
            ) : (
              <Database className="h-3.5 w-3.5 text-slate-400" />
            )}
            <span>{isSeeding ? 'Seeding...' : seedSuccess ? 'Seeded!' : 'Seed Demo Data'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
