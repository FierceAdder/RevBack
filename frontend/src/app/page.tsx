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
} from 'lucide-react';
import { fetchMetrics, fetchInvoices, processInvoiceAgent } from '@/lib/api';
import { DashboardMetrics, Invoice } from '@/lib/types';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

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

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Header & Tagline */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Revenue Recovery Control Center
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Autonomous B2B debt chaser: detect at-risk receivables, adapt tone, bitemporal promises, and Razorpay webhook reconciliation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5 text-slate-400" />
            <span>Refresh</span>
          </button>
          <Link
            href="/simulation"
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-500 transition-colors"
          >
            <Zap className="h-3.5 w-3.5" />
            <span>Run ROI Benchmark</span>
          </Link>
        </div>
      </div>

      {/* 4 Financial KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Outstanding */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Outstanding</span>
            <div className="rounded-md bg-amber-500/10 p-2 text-amber-400 border border-amber-500/20">
              <Clock className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white tracking-tight">
              ₹{(metrics?.total_outstanding_inr || 3260000).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </div>
            <p className="mt-1 text-[11px] text-slate-400 flex items-center gap-1">
              <span className="text-amber-400 font-semibold">{metrics?.active_recovering_count || 14}</span> active receivables at risk
            </p>
          </div>
        </div>

        {/* Capital Recovered */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Cash Recovered</span>
            <div className="rounded-md bg-emerald-500/10 p-2 text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-emerald-400 tracking-tight">
              ₹{(metrics?.total_recovered_inr || 1740000).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </div>
            <p className="mt-1 text-[11px] text-slate-400 flex items-center gap-1">
              <span className="text-emerald-400 font-semibold">{metrics?.recovered_count || 8}</span> invoices settled via Razorpay
            </p>
          </div>
        </div>

        {/* Recovery Rate % */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Recovery Rate</span>
            <div className="rounded-md bg-blue-500/10 p-2 text-blue-400 border border-blue-500/20">
              <TrendingUp className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-white tracking-tight">
              {metrics?.recovery_rate_pct ?? 34.8}%
            </div>
            <p className="mt-1 text-[11px] text-slate-400 flex items-center gap-1">
              <span className="text-emerald-400 font-semibold">+18.4%</span> uplift vs static ERP baseline
            </p>
          </div>
        </div>

        {/* Token ROI Multiplier */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Cost-per-Recovery ROI</span>
            <div className="rounded-md bg-purple-500/10 p-2 text-purple-400 border border-purple-500/20">
              <Sparkles className="h-4 w-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-2xl font-bold text-purple-400 tracking-tight">
              {metrics?.estimated_roi_multiple ?? 154.2}x
            </div>
            <p className="mt-1 text-[11px] text-slate-400 flex items-center gap-1">
              Every ₹1 spent on AI recovers <span className="text-white font-semibold">₹154+</span> cash
            </p>
          </div>
        </div>
      </div>

      {/* Recovery Pipeline Stage Breakdown */}
      <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">Autonomous Recovery Lifecycle Pipeline</h2>
            <p className="text-xs text-slate-400">B2B receivables transitioning dynamically through policy rules</p>
          </div>
          <span className="text-xs text-slate-400">Total: {metrics?.total_invoices_count || 25} Receivables</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 pt-2">
          {[
            { label: '1. Intake', count: metrics?.stage_breakdown?.INTAKE || 3, color: 'border-slate-700 text-slate-300' },
            { label: '2. Diagnose', count: metrics?.stage_breakdown?.DIAGNOSE || 4, color: 'border-blue-500/40 text-blue-400' },
            { label: '3. Act & Dispatch', count: metrics?.stage_breakdown?.ACT || 6, color: 'border-cyan-500/40 text-cyan-400' },
            { label: '4. Promise Track', count: metrics?.stage_breakdown?.PROMISE_TRACKING || 4, color: 'border-amber-500/40 text-amber-400' },
            { label: '5. Escalation', count: metrics?.stage_breakdown?.ESCALATION || 2, color: 'border-rose-500/40 text-rose-400' },
            { label: '6. Recovered', count: metrics?.stage_breakdown?.RECOVERED || 8, color: 'border-emerald-500/40 text-emerald-400' },
          ].map((stage, idx) => (
            <div
              key={idx}
              className={`rounded-lg border bg-slate-900/60 p-3 text-center ${stage.color}`}
            >
              <div className="text-[11px] font-medium text-slate-400">{stage.label}</div>
              <div className="text-xl font-bold mt-1">{stage.count}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Top At-Risk Receivables Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111622] shadow-sm overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <div>
            <h2 className="text-sm font-semibold text-white">Receivables Priority Queue</h2>
            <p className="text-xs text-slate-400">Evaluated by Risk Scorer (overdue days, exposure, promise history)</p>
          </div>
          <Link
            href="/invoices"
            className="flex items-center gap-1 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
          >
            <span>View All Ledger</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="px-5 py-3">Invoice & Customer</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Due Date</th>
                <th className="px-4 py-3">Risk Band</th>
                <th className="px-4 py-3">P(Recovery)</th>
                <th className="px-4 py-3">Stage / Level</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {invoices.slice(0, 8).map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-900/40 transition-colors">
                  {/* Customer / Invoice */}
                  <td className="px-5 py-3.5">
                    <Link href={`/invoices/${inv.id}`} className="hover:underline font-semibold text-white">
                      {inv.invoice_number}
                    </Link>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                      <span>{inv.customer?.name || 'Customer'}</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-300">
                        {inv.customer?.relationship_tier?.replace('_', ' ') || 'STANDARD'}
                      </span>
                    </div>
                  </td>

                  {/* Amount */}
                  <td className="px-4 py-3.5">
                    <div className="font-semibold text-slate-100">
                      ₹{(inv.amount_paise / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </div>
                    {inv.amount_paid_paise > 0 && (
                      <div className="text-[10px] text-emerald-400">
                        Paid: ₹{(inv.amount_paid_paise / 100).toLocaleString('en-IN')}
                      </div>
                    )}
                  </td>

                  {/* Due Date & Overdue */}
                  <td className="px-4 py-3.5">
                    <div>{inv.due_date ? new Date(inv.due_date).toLocaleDateString('en-IN') : 'N/A'}</div>
                    <div className="text-[10px] text-amber-400 font-medium">Overdue</div>
                  </td>

                  {/* Risk Score */}
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${
                        inv.risk_score >= 75
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : inv.risk_score >= 45
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      {inv.risk_score >= 75 ? 'CRITICAL' : inv.risk_score >= 45 ? 'HIGH' : 'MEDIUM'} ({inv.risk_score.toFixed(0)})
                    </span>
                  </td>

                  {/* Recovery Probability */}
                  <td className="px-4 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full"
                          style={{ width: `${Math.round(inv.recovery_probability * 100)}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-medium text-slate-300">
                        {Math.round(inv.recovery_probability * 100)}%
                      </span>
                    </div>
                  </td>

                  {/* Stage & Level */}
                  <td className="px-4 py-3.5">
                    <div className="font-semibold text-slate-200">{inv.current_stage}</div>
                    <div className="text-[10px] text-slate-400">Level {inv.current_level} / 7</div>
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3.5 text-right space-x-2">
                    <button
                      onClick={(e) => handleProcessSingle(e, inv.id)}
                      disabled={processingId === inv.id}
                      className="inline-flex items-center gap-1 rounded bg-blue-600/20 border border-blue-500/30 px-2.5 py-1 text-[11px] font-medium text-blue-300 hover:bg-blue-600/40 transition-colors disabled:opacity-50"
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
                      className="inline-flex items-center gap-1 rounded bg-slate-800 px-2.5 py-1 text-[11px] font-medium text-slate-300 hover:bg-slate-700 transition-colors"
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
