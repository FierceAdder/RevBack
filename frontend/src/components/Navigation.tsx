'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
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
  ShieldCheck,
  LogIn,
  LogOut,
  User as UserIcon,
  Settings as SettingsIcon,
} from 'lucide-react';
import { fetchMetrics, seedDatabase } from '@/lib/api';
import ThemeToggle from '@/components/ThemeToggle';
import { useAuth } from '@/context/AuthContext';

export default function Navigation() {
  const pathname = usePathname();
  const router = useRouter();
  const [pendingApprovals, setPendingApprovals] = useState(0);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState(false);
  const [apiConnected, setApiConnected] = useState(true);

  // 1. Page Persistence: Restore last visited route on root load
  useEffect(() => {
    try {
      if (typeof window !== 'undefined' && pathname === '/') {
        const savedRoute = localStorage.getItem('revback_active_page');
        if (savedRoute && savedRoute !== '/' && !savedRoute.startsWith('/auth')) {
          router.replace(savedRoute);
        }
      }
    } catch {
      // LocalStorage access error
    }
  }, []);

  // 2. Page Persistence: Record current route whenever pathname changes
  useEffect(() => {
    if (pathname && !pathname.startsWith('/auth')) {
      try {
        localStorage.setItem('revback_active_page', pathname);
      } catch {
        // LocalStorage access error
      }
    }
  }, [pathname]);

  const handleNavClick = (href: string) => {
    try {
      localStorage.setItem('revback_active_page', href);
    } catch {
      // LocalStorage access error
    }
  };

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

  const { user, logout, isAuthenticated } = useAuth();

  const navItems = [
    { href: '/', label: 'Overview', icon: LayoutDashboard },
    { href: '/invoices', label: 'Ledger', icon: Receipt },
    {
      href: '/approvals',
      label: 'Approvals',
      icon: UserCheck,
      badge: pendingApprovals > 0 ? pendingApprovals : undefined,
    },
    { href: '/audit', label: 'Audit', icon: ShieldCheck },
    { href: '/simulation', label: 'Benchmark', icon: TrendingUp },
    { href: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  return (
    <header className="fixed top-2.5 sm:top-4 left-0 right-0 z-50 flex justify-center px-2.5 sm:px-4 pointer-events-none">
      <div className="pointer-events-auto relative flex items-center justify-between gap-2 sm:gap-3 max-w-7xl w-full px-3 sm:px-5 py-2 sm:py-2.5 rounded-full border border-white/60 dark:border-white/10 bg-white/70 dark:bg-[#070A11]/70 backdrop-blur-2xl shadow-[0_8px_32px_rgba(0,0,0,0.06)] dark:shadow-[0_12px_40px_rgba(0,0,0,0.7)] transition-all overflow-hidden before:absolute before:inset-x-8 before:top-0 before:h-[1px] before:bg-gradient-to-r before:from-transparent before:via-white/80 dark:before:via-white/15 before:to-transparent">
        {/* Brand & Track Badge */}
        <div className="flex items-center gap-2 sm:gap-3 shrink-0">
          <Link
            href="/"
            onClick={() => handleNavClick('/')}
            className="flex items-center gap-2 group"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-tr from-[#0066FF] to-[#0099FF] shadow-md shadow-blue-500/30 group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm sm:text-base font-black tracking-tight text-slate-900 dark:text-white">RevBack</span>
              <span className="rounded-full bg-emerald-500/10 px-1.5 sm:px-2 py-0.5 text-[8px] sm:text-[9px] font-black text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 uppercase tracking-wider">
                Autonomous AI
              </span>
            </div>
          </Link>

          {/* Live System Indicator */}
          <div className="hidden 2xl:flex items-center gap-1.5 rounded-full bg-slate-100/80 dark:bg-white/[0.04] px-2.5 py-1 text-xs border border-slate-200/70 dark:border-white/[0.06]">
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
        <nav className="flex items-center gap-0.5 sm:gap-1 bg-slate-100/80 dark:bg-white/[0.04] p-1 rounded-full border border-slate-200/60 dark:border-white/[0.06] shrink-0">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => handleNavClick(item.href)}
                className={`relative flex items-center gap-1.5 rounded-full px-2.5 sm:px-3 py-1 text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-white dark:bg-[#0066FF] text-[#0066FF] dark:text-white shadow-sm dark:shadow-md dark:shadow-blue-500/30'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <Icon className="h-3.5 w-3.5 shrink-0" />
                <span className="hidden md:inline">{item.label}</span>
                {item.badge !== undefined && (
                  <span className="rounded-full bg-rose-500 px-1.5 py-0.2 text-[9px] font-black text-white">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Actions: Sleek Theme Toggle + Seed Data + User Profile */}
        <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
          <ThemeToggle />

          <button
            onClick={handleSeed}
            disabled={isSeeding}
            className="flex items-center gap-1.5 rounded-full border border-slate-200/80 dark:border-white/10 bg-slate-50/80 dark:bg-white/[0.04] px-2.5 sm:px-3 py-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.08] transition-all disabled:opacity-50 shrink-0"
            title="Seed 25 realistic Indian B2B receivables across all 5 debtor archetypes"
          >
            {isSeeding ? (
              <Loader2 className="h-3 w-3 animate-spin text-[#0066FF]" />
            ) : seedSuccess ? (
              <CheckCircle2 className="h-3 w-3 text-emerald-500" />
            ) : (
              <Database className="h-3 w-3 text-slate-400" />
            )}
            <span className="hidden lg:inline">{isSeeding ? 'Seeding...' : seedSuccess ? 'Seeded' : 'Seed Data'}</span>
          </button>

          {/* Auth Status & Account Control */}
          {isAuthenticated && user ? (
            <div className="flex items-center gap-1.5 sm:gap-2 pl-1 sm:pl-2 border-l border-slate-200/80 dark:border-white/10 shrink-0">
              <div className="flex items-center gap-1.5">
                <div className="h-7 w-7 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white text-[11px] font-black shadow-sm shrink-0">
                  {user.full_name?.charAt(0) || 'U'}
                </div>
                <div className="hidden xl:flex flex-col items-start leading-tight max-w-[110px]">
                  <span className="text-[11px] font-bold text-slate-800 dark:text-slate-200 truncate w-full" title={user.full_name}>
                    {user.full_name}
                  </span>
                  <span className="text-[9px] text-slate-500 dark:text-slate-400 font-medium truncate w-full" title={user.tenant?.name || 'Merchant'}>
                    {user.tenant?.name || 'Merchant'}
                  </span>
                </div>
              </div>

              <button
                onClick={logout}
                className="flex items-center justify-center h-7 w-7 sm:h-8 sm:w-8 rounded-full border border-slate-200/80 dark:border-white/10 bg-slate-50/80 dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:border-red-300 dark:hover:border-red-500/30 transition-all shrink-0"
                title="Sign Out"
              >
                <LogOut className="h-3.5 w-3.5" />
              </button>
            </div>
          ) : (
            <Link
              href="/auth/login"
              className="flex items-center gap-1.5 rounded-full bg-[#0066FF] hover:bg-blue-500 text-white px-3 sm:px-3.5 py-1.5 text-xs font-bold shadow-md shadow-blue-500/20 transition-all shrink-0"
            >
              <LogIn className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Sign In</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

