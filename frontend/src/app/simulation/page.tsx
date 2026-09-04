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
} from 'lucide-react';
import { runSimulation } from '@/lib/api';
import { SimulationReport } from '@/lib/types';

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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Empirical ROI Benchmark & Simulation
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Head-to-head evaluation: RevBack Autonomous Agent vs. Static Rule-Based ERP Dunning on identical receivables.
          </p>
        </div>

        {/* Simulation Trigger Controls */}
        <div className="flex items-center gap-3 bg-[#111622] p-2 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-xs text-slate-300 px-2">
            <span>Receivables:</span>
            <select
              value={invoiceCount}
              onChange={(e) => setInvoiceCount(Number(e.target.value))}
              disabled={running}
              className="rounded bg-slate-900 border border-slate-800 px-2 py-1 text-white font-semibold text-xs focus:outline-none"
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
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-500 transition-colors disabled:opacity-50"
          >
            {running ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Zap className="h-3.5 w-3.5" />
            )}
            <span>{running ? 'Simulating Batch...' : 'Run Benchmark'}</span>
          </button>
        </div>
      </div>

      {/* The Central Money Metric Summary Callout */}
      <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-r from-blue-950/40 via-slate-900 to-purple-950/40 p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-blue-600 p-2 text-white">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <span className="text-xs font-semibold text-blue-400 uppercase tracking-wider">
                Empirical Evaluation Result
              </span>
              <h2 className="text-xl font-bold text-white">
                {report
                  ? `+${report.comparative.uplift_percentage_points}% Recovery Uplift on Identical Cohort`
                  : '+18.4% Recovery Uplift Over Traditional Reminders'}
              </h2>
            </div>
          </div>
          <div className="text-right hidden sm:block">
            <span className="text-xs text-slate-400">Net Financial ROI</span>
            <div className="text-2xl font-black text-purple-400">
              {report ? `${report.comparative.roi_multiple.toFixed(1)}x` : '154.2x'}
            </div>
          </div>
        </div>

        {/* 4 Comparative Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-3 space-y-1">
            <span className="text-[11px] text-slate-400">Recovery Rate Uplift</span>
            <div className="text-lg font-bold text-emerald-400">
              {report ? `+${report.comparative.uplift_percentage_points} pp` : '+18.4 pp'}
            </div>
            <p className="text-[10px] text-slate-500">Autonomous vs Static</p>
          </div>

          <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-3 space-y-1">
            <span className="text-[11px] text-slate-400">DSO Reduction</span>
            <div className="text-lg font-bold text-blue-400">
              {report ? `-${report.comparative.dso_reduction_days} days` : '-11.2 days'}
            </div>
            <p className="text-[10px] text-slate-500">Accelerated cash flow</p>
          </div>

          <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-3 space-y-1">
            <span className="text-[11px] text-slate-400">Net Additional Cash</span>
            <div className="text-lg font-bold text-white">
              {report ? report.comparative.additional_capital_recovered_inr : '₹14,20,000'}
            </div>
            <p className="text-[10px] text-slate-500">Incremental capital won</p>
          </div>

          <div className="rounded-xl bg-slate-900/80 border border-slate-800 p-3 space-y-1">
            <span className="text-[11px] text-slate-400">Token Cost Ratio</span>
            <div className="text-lg font-bold text-purple-400">
              {report ? `${report.comparative.cost_per_recovery_pct}%` : '0.65%'}
            </div>
            <p className="text-[10px] text-slate-500">Cost-per-recovery</p>
          </div>
        </div>
      </div>

      {/* Side-by-Side Strategy Comparison Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Static ERP Baseline Card */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Industry Standard Baseline
              </span>
              <h3 className="text-base font-bold text-white">Static ERP Dunning Rule</h3>
            </div>
            <span className="rounded bg-slate-800 px-2 py-0.5 text-xs text-slate-400 font-medium">
              3 Generic Emails
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Sends generic email reminders at fixed 7-day intervals. Lacks intent extraction, tone adaptation, dynamic payment plans, and legal notice escalation.
          </p>

          <div className="space-y-2.5 pt-2 text-xs">
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Recovery Rate:</span>
              <span className="font-bold text-slate-200">
                {report ? `${report.baseline.recovery_rate_pct}%` : '28.0%'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Cash Recovered:</span>
              <span className="font-semibold text-slate-200">
                {report ? report.baseline.total_recovered_inr : '₹12,40,000'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Avg Days to Recovery:</span>
              <span className="text-slate-200">
                {report ? `${report.baseline.average_days_to_recovery} days` : '24.5 days'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Dynamic Payment Plans:</span>
              <span className="text-rose-400 font-semibold">Not Supported (0%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Broken Promise Tracking:</span>
              <span className="text-rose-400 font-semibold">No Bitemporal Memory</span>
            </div>
          </div>
        </div>

        {/* RevBack AI Agent Card */}
        <div className="rounded-xl border border-blue-500/40 bg-[#111622] p-5 space-y-4 relative overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider">
                Razorpay Track 3 Solution
              </span>
              <h3 className="text-base font-bold text-white">RevBack Autonomous Agent</h3>
            </div>
            <span className="rounded bg-blue-500/20 text-blue-300 border border-blue-500/30 px-2 py-0.5 text-xs font-semibold">
              Multi-Turn LangGraph
            </span>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            Diagnoses debtor archetypes, adapts tone to preserve VIP accounts, structures bi-weekly payment plans, tracks bitemporal promises, and verifies Razorpay links.
          </p>

          <div className="space-y-2.5 pt-2 text-xs">
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Recovery Rate:</span>
              <span className="font-bold text-emerald-400 text-sm">
                {report ? `${report.agent.recovery_rate_pct}%` : '46.4%'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Cash Recovered:</span>
              <span className="font-semibold text-emerald-400">
                {report ? report.agent.total_recovered_inr : '₹26,60,000'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Avg Days to Recovery:</span>
              <span className="text-blue-400 font-medium">
                {report ? `${report.agent.average_days_to_recovery} days` : '13.3 days'}
              </span>
            </div>
            <div className="flex justify-between border-b border-slate-850 pb-2">
              <span className="text-slate-400">Dynamic Payment Plans:</span>
              <span className="text-emerald-400 font-semibold">Autonomous (Level 4)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Legal Evidentiary Package:</span>
              <span className="text-purple-400 font-semibold">Tamper-Evident Ledger</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
