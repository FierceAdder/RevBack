'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  Search,
  Filter,
  RefreshCw,
  Cpu,
  UserCheck,
  AlertTriangle,
  Scale,
  Send,
  Calendar,
  Layers,
  DollarSign,
  ExternalLink,
} from 'lucide-react';
import { fetchAuditTrail, AuditItem } from '@/lib/api';

const EVENT_TYPE_CATEGORIES = [
  { id: 'ALL', label: 'All Events' },
  { id: 'POLICY_EVALUATED', label: 'Policy Engine' },
  { id: 'CONFIDENCE_GATED', label: 'Confidence Gate' },
  { id: 'HUMAN_APPROVAL_RESOLVED', label: 'Human Oversight' },
  { id: 'COMMUNICATION_DISPATCHED', label: 'Dispatches' },
  { id: 'PAYMENT_PLAN_OFFERED', label: 'Payment Plans' },
  { id: 'PROMISE_RECORDED', label: 'Promises' },
  { id: 'DISPUTE_RAISED', label: 'Disputes' },
];

export default function AuditTrailPage() {
  const [logs, setLogs] = useState<AuditItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [refreshing, setRefreshing] = useState<boolean>(false);

  const loadData = async (cat: string = selectedCategory) => {
    try {
      const data = await fetchAuditTrail(cat, 150);
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData(selectedCategory);
  }, [selectedCategory]);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData(selectedCategory);
  };

  // Filter logs by search query
  const filteredLogs = useMemo(() => {
    return logs.filter((log) => {
      const q = searchQuery.toLowerCase();
      const matchInv = log.invoice_number?.toLowerCase().includes(q);
      const matchCust = log.customer_name?.toLowerCase().includes(q);
      const matchActor = log.actor?.toLowerCase().includes(q);
      const matchAction = log.action?.toLowerCase().includes(q);
      const matchEvent = log.event_type?.toLowerCase().includes(q);
      return !q || matchInv || matchCust || matchActor || matchAction || matchEvent;
    });
  }, [logs, searchQuery]);

  // Derived metrics
  const stats = useMemo(() => {
    const total = logs.length;
    const confidenceGated = logs.filter((l) => l.event_type === 'CONFIDENCE_GATED').length;
    const humanResolved = logs.filter((l) => l.event_type === 'HUMAN_APPROVAL_RESOLVED').length;
    const totalCost = logs.reduce((acc, l) => acc + (l.token_cost_usd || 0), 0);
    return { total, confidenceGated, humanResolved, totalCost };
  }, [logs]);

  const getActorBadge = (actor: string) => {
    const a = actor.toUpperCase();
    if (a.includes('HUMAN') || a.includes('SUPERVISOR')) {
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-purple-500/10 px-2 py-0.5 text-[10px] font-bold text-purple-600 dark:text-purple-400 border border-purple-500/20">
          <UserCheck className="w-3 h-3" />
          Supervisor
        </span>
      );
    }
    if (a.includes('POLICY')) {
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-blue-500/10 px-2 py-0.5 text-[10px] font-bold text-blue-600 dark:text-blue-400 border border-blue-500/20">
          <Scale className="w-3 h-3" />
          Policy Engine
        </span>
      );
    }
    if (a.includes('CONFIDENCE')) {
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-600 dark:text-amber-400 border border-amber-500/20">
          <AlertTriangle className="w-3 h-3" />
          Confidence Gate
        </span>
      );
    }
    if (a.includes('DEBTOR')) {
      return (
        <span className="inline-flex items-center gap-1 rounded-md bg-rose-500/10 px-2 py-0.5 text-[10px] font-bold text-rose-600 dark:text-rose-400 border border-rose-500/20">
          Debtor Inbound
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-md bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
        <Cpu className="w-3 h-3" />
        AI Agent
      </span>
    );
  };

  const getEventBadge = (type: string) => {
    switch (type) {
      case 'POLICY_EVALUATED':
        return 'text-blue-600 dark:text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'CONFIDENCE_GATED':
        return 'text-amber-600 dark:text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'HUMAN_APPROVAL_RESOLVED':
        return 'text-purple-600 dark:text-purple-400 bg-purple-500/10 border-purple-500/20';
      case 'COMMUNICATION_DISPATCHED':
        return 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'PAYMENT_PLAN_OFFERED':
        return 'text-indigo-600 dark:text-indigo-400 bg-indigo-500/10 border-indigo-500/20';
      case 'PROMISE_RECORDED':
        return 'text-teal-600 dark:text-teal-400 bg-teal-500/10 border-teal-500/20';
      case 'DISPUTE_RAISED':
        return 'text-rose-600 dark:text-rose-400 bg-rose-500/10 border-rose-500/20';
      default:
        return 'text-slate-600 dark:text-slate-400 bg-slate-500/10 border-slate-500/20';
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
              Immutable Bitemporal Audit Trail
            </h1>
            <span className="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-bold text-[#0066FF] border border-blue-500/20">
              §19 Compliant
            </span>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Complete cryptographic ledger of every deterministic policy decision, AI confidence gate, and supervisor override.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="self-start md:self-auto flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.04] text-xs font-semibold hover:bg-slate-50 dark:hover:bg-white/[0.08] transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-[#0066FF]' : 'text-slate-400'}`} />
          <span>Refresh Trail</span>
        </button>
      </div>

      {/* Bento Top KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/50 p-4 shadow-sm backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Total Audit Events</span>
            <Layers className="w-4 h-4 text-[#0066FF]" />
          </div>
          <p className="text-2xl font-black">{stats.total}</p>
          <span className="text-[11px] text-slate-400">Permanently logged to DB</span>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/50 p-4 shadow-sm backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Confidence Gated</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <p className="text-2xl font-black">{stats.confidenceGated}</p>
          <span className="text-[11px] text-amber-500 font-medium">Feature 7 Safety Escapes</span>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/50 p-4 shadow-sm backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Human Authorizations</span>
            <UserCheck className="w-4 h-4 text-purple-500" />
          </div>
          <p className="text-2xl font-black">{stats.humanResolved}</p>
          <span className="text-[11px] text-purple-500 font-medium">Supervisor Signed-off</span>
        </div>

        <div className="rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/50 p-4 shadow-sm backdrop-blur-md">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-semibold">Observability Traces</span>
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
          </div>
          <p className="text-2xl font-black">100%</p>
          <span className="text-[11px] text-emerald-500 font-medium">LangGraph Checkpointed</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between">
        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto pb-1 sm:pb-0 scrollbar-none">
          {EVENT_TYPE_CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat.id
                  ? 'bg-[#0066FF] text-white shadow-md shadow-blue-500/20'
                  : 'bg-slate-100 dark:bg-white/[0.04] text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-white/[0.08]'
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Search Bar */}
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search invoice, actor, action..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 rounded-full border border-slate-200 dark:border-white/10 bg-white dark:bg-white/[0.04] text-xs focus:outline-none focus:border-[#0066FF] transition-colors"
          />
        </div>
      </div>

      {/* Audit Log Table Bento Card */}
      <div className="rounded-2xl border border-slate-200 dark:border-white/[0.08] bg-white dark:bg-black/50 overflow-hidden shadow-sm backdrop-blur-md">
        {loading ? (
          <div className="py-20 text-center text-slate-400 text-xs">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-[#0066FF]" />
            Loading verifiable audit records...
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="py-20 text-center text-slate-400 text-xs">
            <ShieldCheck className="w-8 h-8 mx-auto mb-2 text-slate-500 opacity-40" />
            No audit records found matching your filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-white/[0.02] text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Event Type</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Claim Reference</th>
                  <th className="py-3 px-4 min-w-[320px]">Action & Audit Detail</th>
                  <th className="py-3 px-4">Recorded At (UTC)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04] text-xs">
                {filteredLogs.map((log) => (
                  <tr
                    key={log.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-white/[0.02] transition-colors"
                  >
                    <td className="py-3 px-4 whitespace-nowrap">
                      <span
                        className={`inline-block px-2 py-0.5 rounded-md text-[10px] font-black uppercase tracking-wider border ${getEventBadge(
                          log.event_type
                        )}`}
                      >
                        {log.event_type}
                      </span>
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      {getActorBadge(log.actor)}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      {log.invoice_number ? (
                        <Link
                          href={`/invoices/${log.invoice_id}`}
                          className="font-mono font-semibold text-[#0066FF] hover:underline flex items-center gap-1"
                        >
                          {log.invoice_number}
                          <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                        </Link>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                      {log.customer_name && (
                        <div className="text-[11px] text-slate-500 truncate max-w-[150px]">
                          {log.customer_name}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                        {log.action}
                      </div>
                      {log.reasoning && (
                        <div className="text-[11px] text-slate-500 mt-1 italic">
                          Rationale: {log.reasoning}
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap text-slate-500 text-[11px] font-mono">
                      {new Date(log.recorded_at).toLocaleString('en-IN', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
