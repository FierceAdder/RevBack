'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Receipt,
  Search,
  Filter,
  Sparkles,
  ChevronRight,
  ExternalLink,
  RefreshCw,
  Clock,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { fetchInvoices, processInvoiceAgent } from '@/lib/api';
import { Invoice } from '@/lib/types';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [stageFilter, setStageFilter] = useState<string>('ALL');
  const [processingId, setProcessingId] = useState<string | null>(null);

  const loadInvoices = async () => {
    setLoading(true);
    try {
      const data = await fetchInvoices();
      setInvoices(data);
    } catch (err) {
      console.error('Failed to load invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInvoices();
  }, []);

  const handleProcess = async (id: string) => {
    setProcessingId(id);
    try {
      await processInvoiceAgent(id);
      await loadInvoices();
    } catch (err) {
      console.error('Process error:', err);
    } finally {
      setProcessingId(null);
    }
  };

  const filtered = invoices.filter((inv) => {
    const matchesSearch =
      inv.invoice_number.toLowerCase().includes(search.toLowerCase()) ||
      (inv.customer?.name || '').toLowerCase().includes(search.toLowerCase());

    if (stageFilter === 'ALL') return matchesSearch;
    if (stageFilter === 'DISPUTED') return matchesSearch && inv.status === 'DISPUTED';
    if (stageFilter === 'RECOVERED') return matchesSearch && inv.current_stage === 'RECOVERED';
    if (stageFilter === 'PROMISE') return matchesSearch && inv.current_stage === 'PROMISE_TRACKING';
    if (stageFilter === 'CRITICAL') return matchesSearch && inv.risk_score >= 70;
    return matchesSearch && inv.current_stage === stageFilter;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Receivables Ledger
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Complete inventory of commercial B2B invoices being monitored and recovered by RevBack.
          </p>
        </div>

        <button
          onClick={loadInvoices}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5 text-slate-400" />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#111622] p-3 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search invoice # or debtor company..."
            className="w-full rounded-lg bg-slate-900 border border-slate-750 pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
          {[
            { id: 'ALL', label: 'All Invoices' },
            { id: 'PROMISE', label: 'Promises Active' },
            { id: 'DISPUTED', label: 'Disputed' },
            { id: 'CRITICAL', label: 'Critical Risk' },
            { id: 'RECOVERED', label: 'Recovered' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStageFilter(tab.id)}
              className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
                stageFilter === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-[#111622] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/80 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="px-5 py-3">Invoice & Debtor</th>
                <th className="px-4 py-3">Amount (INR)</th>
                <th className="px-4 py-3">Due Date</th>
                <th className="px-4 py-3">Risk Assessment</th>
                <th className="px-4 py-3">P(Recovery)</th>
                <th className="px-4 py-3">Tone Persona</th>
                <th className="px-4 py-3">Stage / Level</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filtered.map((inv) => (
                <tr key={inv.id} className="hover:bg-slate-900/40 transition-colors">
                  {/* Invoice # & Customer */}
                  <td className="px-5 py-3.5">
                    <Link
                      href={`/invoices/${inv.id}`}
                      className="hover:underline font-semibold text-white flex items-center gap-1.5"
                    >
                      <span>{inv.invoice_number}</span>
                      {inv.status === 'DISPUTED' && (
                        <span className="rounded bg-rose-500/20 text-rose-300 px-1.5 py-0.2 text-[10px] font-bold border border-rose-500/30">
                          DISPUTED
                        </span>
                      )}
                    </Link>
                    <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                      <span>{inv.customer?.name || 'Customer'}</span>
                      <span className="rounded bg-slate-800 px-1 text-[10px] text-slate-300">
                        {inv.customer?.relationship_tier?.replace('_', ' ')}
                      </span>
                    </div>
                  </td>

                  {/* Amount */}
                  <td className="px-4 py-3.5">
                    <div className="font-semibold text-slate-100">
                      ₹{(inv.amount_paise / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                    </div>
                    {inv.amount_paid_paise > 0 && (
                      <div className="text-[10px] text-emerald-400 font-medium">
                        Paid: ₹{(inv.amount_paid_paise / 100).toLocaleString('en-IN')}
                      </div>
                    )}
                  </td>

                  {/* Due Date */}
                  <td className="px-4 py-3.5">
                    <div>{inv.due_date ? new Date(inv.due_date).toLocaleDateString('en-IN') : 'N/A'}</div>
                    <div className="text-[10px] text-slate-400">Overdue</div>
                  </td>

                  {/* Risk Score */}
                  <td className="px-4 py-3.5">
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold border ${
                        inv.risk_score >= 70
                          ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          : inv.risk_score >= 40
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                      }`}
                    >
                      {inv.risk_score >= 70 ? 'CRITICAL' : inv.risk_score >= 40 ? 'HIGH' : 'MEDIUM'} ({inv.risk_score.toFixed(0)})
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

                  {/* Optimal Tone */}
                  <td className="px-4 py-3.5">
                    <span className="rounded bg-slate-800 px-2 py-0.5 text-[11px] font-medium text-slate-300">
                      {inv.optimal_tone}
                    </span>
                  </td>

                  {/* Stage & Level */}
                  <td className="px-4 py-3.5">
                    <div className="font-semibold text-slate-200">{inv.current_stage}</div>
                    <div className="text-[10px] text-slate-400">Level {inv.current_level} / 7</div>
                  </td>

                  {/* Actions */}
                  <td className="px-4 py-3.5 text-right space-x-2">
                    <button
                      onClick={() => handleProcess(inv.id)}
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
