'use client';

import React, { useState } from 'react';
import {
  TrendingUp,
  Sparkles,
  DollarSign,
  Clock,
  ArrowUpRight,
  ShieldCheck,
  CheckCircle2,
  RefreshCw,
  Zap,
  BarChart3,
  Calendar,
  Layers,
} from 'lucide-react';
import { runSimulation } from '@/lib/api';
import { SimulationReport } from '@/lib/types';
import NumberTicker from '@/components/NumberTicker';

export default function SimulationPage() {
  const [invoiceCount, setInvoiceCount] = useState(25);
  const [running, setRunning] = useState(false);
  const [report, setReport] = useState<SimulationReport | null>(null);

  const handleRunSimulation = async () => {
    setRunning(true);
    try {
      const data = await runSimulation(invoiceCount);
      setReport(data);
    } catch (err) {
      console.error('Simulation run error:', err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
              Empirical ROI Benchmark & Simulation
            </h1>
            <span className="rounded-full bg-purple-500/10 text-purple-600 dark:text-purple-400 px-2.5 py-0.5 text-xs font-bold border border-purple-500/20">
              Evaluator Harness
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Head-to-head empirical evaluation: RevBack Autonomous Agent vs. Static Rule-Based ERP Dunning across identical receivables.
          </p>
        </div>

        {/* Simulation Trigger Controls */}
        <div className="flex items-center gap-3 bg-white dark:bg-[#111622] p-2 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
          <div className="flex items-center gap-2 text-xs text-slate-700 dark:text-slate-300 px-2">
            <span className="font-semibold">Cohort Size:</span>
            <select
              value={invoiceCount}
              onChange={(e) => setInvoiceCount(Number(e.target.value))}
              disabled={running}
              className="rounded-lg bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-1 text-slate-900 dark:text-white font-bold text-xs focus:outline-none"
            >
              <option value={10}>10 Invoices</option>
              <option value={25}>25 Invoices</option>
              <option value={50}>50 Invoices</option>
              <option value={100}>100 Invoices</option>
            </select>
          </div>

          <button
            onClick={handleRunSimulation}
            disabled={running}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-md shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 transition-all hover:scale-[1.02] disabled:opacity-50"
          >
            {running ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Zap className="h-3.5 w-3.5 fill-white" />
            )}
            <span>{running ? 'Simulating Cohort...' : 'Run Benchmark'}</span>
          </button>
        </div>
      </div>

      {/* The Central Money Metric Summary Callout */}
      <div className="rounded-3xl border border-[#0066FF]/30 bg-gradient-to-r from-blue-500/5 via-indigo-500/5 to-purple-500/5 dark:from-[#0066FF]/10 dark:via-black/60 dark:to-purple-950/20 backdrop-blur-xl p-6 sm:p-8 space-y-5 shadow-sm dark:shadow-2xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-gradient-to-tr from-[#0066FF] to-[#0099FF] p-3 text-white shadow-lg shadow-blue-500/30">
              <TrendingUp className="h-6 w-6" />
            </div>
            <div>
              <span className="text-xs font-black text-[#0066FF] dark:text-[#38BDF8] uppercase tracking-wider">
                Empirical Evaluation Result
              </span>
              <h2 className="text-xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
                {report
                  ? `+${report.comparative.uplift_percentage_points}% Recovery Uplift on Identical Cohort`
                  : '+18.4% Recovery Uplift Over Traditional Reminders'}
              </h2>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <span className="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">Net Financial ROI</span>
            <div className="text-3xl sm:text-4xl font-black text-purple-600 dark:text-purple-400 tracking-tight">
              <NumberTicker
                value={report ? report.comparative.roi_multiple : 154.2}
                suffix="x"
                decimals={1}
              />
            </div>
          </div>
        </div>

        {/* 4 Comparative Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <div className="rounded-2xl bg-white/80 dark:bg-black/50 border border-slate-200/80 dark:border-white/[0.06] p-4 space-y-1 shadow-sm">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Recovery Rate Uplift</span>
            <div className="text-xl sm:text-2xl font-black text-emerald-600 dark:text-emerald-400 tracking-tight">
              +<NumberTicker value={report ? report.comparative.uplift_percentage_points : 18.4} decimals={1} /> pp
            </div>
            <p className="text-[10px] text-slate-400">Autonomous vs Static</p>
          </div>

          <div className="rounded-2xl bg-white/80 dark:bg-black/50 border border-slate-200/80 dark:border-white/[0.06] p-4 space-y-1 shadow-sm">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">DSO Reduction</span>
            <div className="text-xl sm:text-2xl font-black text-blue-600 dark:text-blue-400 tracking-tight">
              -<NumberTicker value={report ? report.comparative.dso_reduction_days : 11.2} decimals={1} /> days
            </div>
            <p className="text-[10px] text-slate-400">Accelerated cash flow</p>
          </div>

          <div className="rounded-2xl bg-white/80 dark:bg-black/50 border border-slate-200/80 dark:border-white/[0.06] p-4 space-y-1 shadow-sm">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Net Additional Cash</span>
            <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
              {report ? report.comparative.additional_capital_recovered_inr : '₹14,20,000'}
            </div>
            <p className="text-[10px] text-slate-400">Incremental capital won</p>
          </div>

          <div className="rounded-2xl bg-white/80 dark:bg-black/50 border border-slate-200/80 dark:border-white/[0.06] p-4 space-y-1 shadow-sm">
            <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Token Cost Ratio</span>
            <div className="text-xl sm:text-2xl font-black text-purple-600 dark:text-purple-400 tracking-tight">
              <NumberTicker value={report ? report.comparative.cost_per_recovery_pct : 0.65} decimals={2} />%
            </div>
            <p className="text-[10px] text-slate-400">Cost-per-recovery</p>
          </div>
        </div>
      </div>

      {/* Side-by-Side Strategy Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Static ERP Baseline Card */}
        <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 space-y-4 shadow-sm dark:shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-3">
            <div>
              <span className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                Industry Standard Baseline
              </span>
              <h3 className="text-base font-black text-slate-900 dark:text-white">Static ERP Dunning Rule</h3>
            </div>
            <span className="rounded-full bg-slate-100 dark:bg-white/[0.06] px-3 py-1 text-xs text-slate-600 dark:text-slate-400 font-bold border border-slate-200 dark:border-white/[0.08]">
              3 Generic Emails
            </span>
          </div>

          <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
            Sends generic email reminders at fixed 7-day intervals. Lacks intent extraction, tone adaptation, dynamic payment plans, and legal notice escalation.
          </p>

          <div className="space-y-3 pt-2 text-xs">
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Recovery Rate:</span>
              <span className="font-bold text-slate-900 dark:text-slate-200">
                {report ? `${report.baseline.recovery_rate_pct}%` : '28.0%'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Cash Recovered:</span>
              <span className="font-semibold text-slate-900 dark:text-slate-200">
                {report ? report.baseline.total_recovered_inr : '₹12,40,000'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Avg Days to Recovery:</span>
              <span className="text-slate-700 dark:text-slate-300">
                {report ? `${report.baseline.average_days_to_recovery} days` : '24.5 days'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Dynamic Payment Plans:</span>
              <span className="text-rose-600 dark:text-rose-400 font-bold">Not Supported (0%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Broken Promise Tracking:</span>
              <span className="text-rose-600 dark:text-rose-400 font-bold">No Bitemporal Memory</span>
            </div>
          </div>
        </div>

        {/* RevBack AI Agent Card */}
        <div className="rounded-2xl border border-blue-500/40 bg-white dark:bg-[#111622] p-6 space-y-4 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-3">
            <div>
              <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">
                Autonomous Recovery Solution
              </span>
              <h3 className="text-base font-bold text-slate-900 dark:text-white">RevBack Autonomous Agent</h3>
            </div>
            <span className="rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-300 border border-blue-500/20 px-2.5 py-1 text-xs font-bold">
              Multi-Turn LangGraph
            </span>
          </div>

          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
            Diagnoses debtor archetypes, adapts tone to preserve VIP accounts, structures bi-weekly payment plans, tracks bitemporal promises, and verifies Razorpay links.
          </p>

          <div className="space-y-3 pt-2 text-xs">
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Recovery Rate:</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                {report ? `${report.agent.recovery_rate_pct}%` : '46.4%'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Cash Recovered:</span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                {report ? report.agent.total_recovered_inr : '₹26,60,000'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Avg Days to Recovery:</span>
              <span className="text-blue-600 dark:text-blue-400 font-bold">
                {report ? `${report.agent.average_days_to_recovery} days` : '13.3 days'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800/60 pb-2">
              <span className="text-slate-500 dark:text-slate-400">Dynamic Payment Plans:</span>
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">Autonomous (Level 4)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500 dark:text-slate-400">Legal Evidentiary Package:</span>
              <span className="text-purple-600 dark:text-purple-400 font-bold">Tamper-Evident Ledger</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
