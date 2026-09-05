'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Clock,
  ArrowUpRight,
  Receipt,
  Scale,
  Sparkles,
  ExternalLink,
  ChevronRight,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
  Zap,
  Activity,
  ShieldCheck,
  Cpu,
} from 'lucide-react';
import { fetchMetrics, fetchInvoices, processInvoiceAgent } from '@/lib/api';
import { DashboardMetrics, Invoice } from '@/lib/types';
import NumberTicker from '@/components/NumberTicker';
import RecoveryChart from '@/components/RecoveryChart';
import PipelineVisualizer from '@/components/PipelineVisualizer';
import LiveAgentStream from '@/components/LiveAgentStream';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [selectedStage, setSelectedStage] = useState<string | null>(null);

  const loadData = async () => {
    try {
      const [m, inv] = await Promise.all([fetchMetrics(), fetchInvoices()]);
      setMetrics(m);
      setInvoices(inv);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleProcessSingle = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    e.preventDefault();
    setProcessingId(id);
    try {
      await processInvoiceAgent(id);
      await loadData();
    } catch (err) {
      console.error('Process error:', err);
    } finally {
      setProcessingId(null);
    }
  };

  const displayedInvoices = selectedStage
    ? invoices.filter((inv) => inv.current_stage === selectedStage)
    : invoices;

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-5">
      {/* 1. Hero Bento Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Hero Card (8 cols) */}
        <div className="lg:col-span-8 rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 sm:p-8 shadow-sm dark:shadow-2xl relative overflow-hidden flex flex-col justify-between">
          <div className="relative z-10">
            {/* Pill Eyebrow */}
            <div className="inline-flex items-center gap-2 rounded-full bg-[#0066FF]/10 dark:bg-[#0066FF]/20 px-3 py-1 text-xs font-black text-[#0066FF] dark:text-[#38BDF8] border border-[#0066FF]/30 uppercase tracking-wider mb-3">
              <span className="h-1.5 w-1.5 rounded-full bg-[#0066FF] dark:bg-[#38BDF8] animate-pulse" />
              Autonomous Revenue Recovery Engine
            </div>

            <h1 className="text-2xl sm:text-4xl font-black tracking-tight text-slate-900 dark:text-white leading-tight">
              Self-Driving B2B Debt Chaser & Webhook Reconciliation
            </h1>
            <p className="mt-2 text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-2xl leading-relaxed">
              Detect at-risk invoices early, adapt communication tone to debtor archetype, track promises with bitemporal precision, and verify instant settlements via signed Razorpay links.
            </p>
          </div>

          <div className="mt-6 pt-5 border-t border-slate-100 dark:border-white/[0.08] flex flex-wrap items-center gap-3 relative z-10">
            <Link
              href="/simulation"
              className="flex items-center gap-2 rounded-full bg-gradient-to-r from-[#0066FF] to-[#0099FF] px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-500/25 hover:from-blue-600 hover:to-sky-600 transition-all hover:scale-[1.02]"
            >
              <Zap className="h-4 w-4 fill-white" />
              <span>Run ROI Benchmark</span>
            </Link>

            <Link
              href="/invoices"
              className="flex items-center gap-1.5 rounded-full border border-slate-200 dark:border-white/10 bg-slate-100/80 dark:bg-white/[0.04] px-4 py-2.5 text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-200 dark:hover:bg-white/[0.08] transition-all"
            >
              <Receipt className="h-3.5 w-3.5" />
              <span>View Ledger ({invoices.length})</span>
            </Link>

            <button
              onClick={loadData}
              className="flex items-center gap-1.5 rounded-full border border-slate-200 dark:border-white/10 bg-slate-100/80 dark:bg-white/[0.04] px-4 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/[0.08] transition-all"
            >
              <RefreshCw className="h-3.5 w-3.5 text-slate-400" />
              <span>Sync</span>
            </button>
          </div>
        </div>

        {/* Right Status Bento Card (4 cols) */}
        <div className="lg:col-span-4 rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 shadow-sm dark:shadow-2xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3">
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-[#0066FF] dark:text-[#38BDF8]" />
                <span className="text-xs font-black tracking-wider uppercase text-slate-900 dark:text-white">
                  Engine Telemetry
                </span>
              </div>
              <span className="rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 text-[10px] font-bold border border-emerald-500/20">
                ACTIVE
              </span>
            </div>

            <div className="mt-4 space-y-3 text-xs">
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-black/40 border border-slate-200/60 dark:border-white/[0.04]">
                <span className="text-slate-500 dark:text-slate-400">Agent Framework</span>
                <span className="font-bold text-slate-900 dark:text-white">LangGraph StateLoop</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-black/40 border border-slate-200/60 dark:border-white/[0.04]">
                <span className="text-slate-500 dark:text-slate-400">Webhook Gating</span>
                <span className="font-bold text-emerald-600 dark:text-emerald-400">HMAC-SHA256</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-black/40 border border-slate-200/60 dark:border-white/[0.04]">
                <span className="text-slate-500 dark:text-slate-400">Active Commitments</span>
                <span className="font-bold text-amber-500">{metrics?.active_promises_count || 6} bitemporal</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-black/40 border border-slate-200/60 dark:border-white/[0.04]">
                <span className="text-slate-500 dark:text-slate-400">Supervisor Queue</span>
                <span className="font-bold text-rose-500">{metrics?.pending_approvals_count || 2} awaiting</span>
              </div>
            </div>
          </div>

          <div className="mt-4 text-[11px] text-slate-400 dark:text-slate-500 text-center font-mono">
            Zero-hallucination deterministic bounds
          </div>
        </div>
      </div>

      {/* 2. Financial KPI Bento Block (4 Cards) */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Outstanding */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-5 shadow-sm dark:shadow-2xl transition-all hover:border-amber-500/40 group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Total Outstanding
            </span>
            <div className="rounded-2xl bg-amber-500/10 p-2.5 text-amber-500 border border-amber-500/20 group-hover:scale-105 transition-transform">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              <NumberTicker
                value={metrics?.total_outstanding_inr || 8990000}
                prefix="₹"
                isCurrency={true}
              />
            </div>
            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
              <span>Receivables at Risk</span>
              <span className="font-bold text-amber-600 dark:text-amber-400">
                {metrics?.active_recovering_count || 17} active
              </span>
            </div>
          </div>
        </div>

        {/* Capital Recovered */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-5 shadow-sm dark:shadow-2xl transition-all hover:border-emerald-500/40 group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Cash Recovered
            </span>
            <div className="rounded-2xl bg-emerald-500/10 p-2.5 text-emerald-500 border border-emerald-500/20 group-hover:scale-105 transition-transform">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight">
              <NumberTicker
                value={metrics?.total_recovered_inr || 1740000}
                prefix="₹"
                isCurrency={true}
              />
            </div>
            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
              <span>Settled via Razorpay</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                {metrics?.recovered_count || 8} reconciled
              </span>
            </div>
          </div>
        </div>

        {/* Recovery Rate % */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-5 shadow-sm dark:shadow-2xl transition-all hover:border-[#0066FF]/40 group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Recovery Rate
            </span>
            <div className="rounded-2xl bg-[#0066FF]/10 p-2.5 text-[#0066FF] dark:text-[#38BDF8] border border-[#0066FF]/20 group-hover:scale-105 transition-transform">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              <NumberTicker
                value={metrics?.recovery_rate_pct || 34.8}
                suffix="%"
                decimals={1}
              />
            </div>
            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
              <span>Uplift vs ERP</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5">
                <ArrowUpRight className="h-3 w-3" />
                +18.4%
              </span>
            </div>
          </div>
        </div>

        {/* Cost-per-Recovery ROI */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-5 shadow-sm dark:shadow-2xl transition-all hover:border-purple-500/40 group">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Cost-per-Recovery ROI
            </span>
            <div className="rounded-2xl bg-purple-500/10 p-2.5 text-purple-500 border border-purple-500/20 group-hover:scale-105 transition-transform">
              <Sparkles className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl sm:text-3xl font-black text-purple-600 dark:text-purple-400 tracking-tight">
              <NumberTicker
                value={metrics?.estimated_roi_multiple || 154.2}
                suffix="x"
                decimals={1}
              />
            </div>
            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400">
              <span>Token Spend Ratio</span>
              <span className="font-bold text-purple-600 dark:text-purple-400">
                0.65% fee
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Analytics & Streaming Feed Bento Block */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
        <div className="lg:col-span-7 flex flex-col">
          <RecoveryChart />
        </div>
        <div className="lg:col-span-5 flex flex-col">
          <LiveAgentStream />
        </div>
      </div>

      {/* 4. Lifecycle Pipeline Visualizer Bento Card */}
      <PipelineVisualizer
        stageBreakdown={metrics?.stage_breakdown}
        selectedStage={selectedStage}
        onSelectStage={setSelectedStage}
      />

      {/* 5. Priority Receivables Bento Table */}
      <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 shadow-sm dark:shadow-2xl overflow-hidden transition-all hover:border-blue-500/20">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-4 gap-2">
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base sm:text-lg font-black tracking-tight text-slate-900 dark:text-white">
                Receivables Priority Queue
              </h2>
              {selectedStage && (
                <span className="rounded-full bg-[#0066FF]/10 text-[#0066FF] dark:text-[#38BDF8] px-2.5 py-0.5 text-[10px] font-extrabold border border-[#0066FF]/30">
                  Stage: {selectedStage}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Dynamically prioritized by composite Risk Scorer (overdue severity, exposure, promise history)
            </p>
          </div>
          <Link
            href="/invoices"
            className="flex items-center gap-1 text-xs font-bold text-[#0066FF] dark:text-[#38BDF8] hover:underline"
          >
            <span>View Full Ledger ({invoices.length})</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto mt-2">
          <table className="w-full text-left text-xs">
            <thead className="text-slate-400 dark:text-slate-500 uppercase tracking-wider font-extrabold border-b border-slate-100 dark:border-white/[0.06]">
              <tr>
                <th className="py-3 px-2">Invoice & Customer</th>
                <th className="py-3 px-2">Claim Amount</th>
                <th className="py-3 px-2">Due Date</th>
                <th className="py-3 px-2">Risk Band</th>
                <th className="py-3 px-2">P(Recovery)</th>
                <th className="py-3 px-2">Stage</th>
                <th className="py-3 px-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04] text-slate-700 dark:text-slate-300">
              {displayedInvoices.slice(0, 10).map((inv) => (
                <tr
                  key={inv.id}
                  className="hover:bg-slate-50/70 dark:hover:bg-white/[0.02] transition-colors group"
                >
                  {/* Invoice # & Customer */}
                  <td className="py-3.5 px-2">
                    <Link
                      href={`/invoices/${inv.id}`}
                      className="font-bold text-slate-900 dark:text-white hover:text-[#0066FF] dark:hover:text-[#38BDF8] flex items-center gap-1.5"
                    >
                      <span>{inv.invoice_number}</span>
                      {inv.status === 'DISPUTED' && (
                        <span className="rounded bg-rose-500/10 text-rose-600 dark:text-rose-400 px-1.5 py-0.2 text-[9px] font-black border border-rose-500/20">
                          DISPUTE
                        </span>
                      )}
                    </Link>
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5">
                      <span className="font-medium text-slate-700 dark:text-slate-300">
                        {inv.customer?.name || 'Customer'}
                      </span>
                      <span className="rounded-full bg-slate-100 dark:bg-white/[0.06] px-1.5 text-[9px] font-bold text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-white/[0.08]">
                        {inv.customer?.relationship_tier?.replace('_', ' ') || 'STANDARD'}
                      </span>
                    </div>
                  </td>

                  {/* Amount */}
                  <td className="py-3.5 px-2">
                    <div className="font-extrabold text-slate-900 dark:text-white">
                      ₹{(inv.amount_paise / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </div>
                    {inv.amount_paid_paise > 0 && (
                      <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">
                        Paid: ₹{(inv.amount_paid_paise / 100).toLocaleString('en-IN')}
                      </div>
                    )}
                  </td>

                  {/* Due Date */}
                  <td className="py-3.5 px-2">
                    <div className="font-medium text-slate-700 dark:text-slate-300">
                      {inv.due_date ? new Date(inv.due_date).toLocaleDateString('en-IN') : 'N/A'}
                    </div>
                    <div className="text-[10px] text-amber-600 dark:text-amber-400 font-bold">
                      Overdue
                    </div>
                  </td>

                  {/* Risk Score */}
                  <td className="py-3.5 px-2">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-lg text-[10px] font-black border ${
                        inv.risk_score >= 70
                          ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30'
                          : inv.risk_score >= 40
                          ? 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      {inv.risk_score >= 70 ? 'CRITICAL' : inv.risk_score >= 40 ? 'HIGH' : 'MEDIUM'} ({inv.risk_score.toFixed(0)})
                    </span>
                  </td>

                  {/* Recovery Probability */}
                  <td className="py-3.5 px-2">
                    <div className="flex items-center gap-2">
                      <div className="w-14 bg-slate-200 dark:bg-black/50 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-[#0066FF] h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${Math.round(inv.recovery_probability * 100)}%` }}
                        />
                      </div>
                      <span className="text-[10px] font-bold text-slate-700 dark:text-slate-300">
                        {Math.round(inv.recovery_probability * 100)}%
                      </span>
                    </div>
                  </td>

                  {/* Stage */}
                  <td className="py-3.5 px-2">
                    <div className="font-extrabold text-slate-900 dark:text-slate-100">{inv.current_stage}</div>
                    <div className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">Level {inv.current_level} / 7</div>
                  </td>

                  {/* Actions */}
                  <td className="py-3.5 px-2 text-right space-x-2">
                    <button
                      onClick={(e) => handleProcessSingle(e, inv.id)}
                      disabled={processingId === inv.id}
                      className="inline-flex items-center gap-1 rounded-full bg-[#0066FF]/10 dark:bg-[#0066FF]/20 border border-[#0066FF]/30 px-3 py-1 text-[11px] font-bold text-[#0066FF] dark:text-[#38BDF8] hover:bg-[#0066FF]/25 transition-colors disabled:opacity-50"
                    >
                      {processingId === inv.id ? (
                        <RefreshCw className="h-3 w-3 animate-spin" />
                      ) : (
                        <Sparkles className="h-3 w-3" />
                      )}
                      <span>{processingId === inv.id ? 'Running...' : 'Run Agent'}</span>
                    </button>
                    <Link
                      href={`/invoices/${inv.id}`}
                      className="inline-flex items-center gap-0.5 rounded-full bg-slate-100 dark:bg-white/[0.04] px-2.5 py-1 text-[11px] font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/[0.08] transition-colors"
                    >
                      <span>Deep Dive</span>
                      <ChevronRight className="h-3 w-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
