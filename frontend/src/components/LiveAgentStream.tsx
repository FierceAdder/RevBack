'use client';

import React, { useState } from 'react';
import {
  Terminal,
  Activity,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  Zap,
} from 'lucide-react';

interface AgentEvent {
  id: string;
  timestamp: string;
  type: 'DIAGNOSE' | 'PROMISE' | 'PAYMENT' | 'DISPUTE' | 'ESCALATION';
  invoiceNumber: string;
  summary: string;
  detail: string;
  badgeColor: string;
}

const INITIAL_EVENTS: AgentEvent[] = [
  {
    id: '1',
    timestamp: 'Just now',
    type: 'PAYMENT',
    invoiceNumber: 'INV-2026-0008',
    summary: 'Razorpay Webhook: Payment ₹2,25,000 Settled',
    detail: 'HMAC-SHA256 signature verified. Invoice moved to RECOVERED, promise marked KEPT.',
    badgeColor: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20',
  },
  {
    id: '2',
    timestamp: '2m ago',
    type: 'PROMISE',
    invoiceNumber: 'INV-2026-0019',
    summary: 'Debtor Commitment Extracted via Gemini',
    detail: 'Debtor promised: "We will definitely transfer ₹1,50,000 by this Friday" (Confidence: 100%).',
    badgeColor: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20',
  },
  {
    id: '3',
    timestamp: '6m ago',
    type: 'DISPUTE',
    invoiceNumber: 'INV-2026-0014',
    summary: 'Commercial Dispute Intercepted — Outreach Halted',
    detail: 'Debtor claimed "Goods damaged on arrival". Agent bound by Guardrails: escalated to Ops.',
    badgeColor: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20',
  },
  {
    id: '4',
    timestamp: '11m ago',
    type: 'ESCALATION',
    invoiceNumber: 'INV-2026-0002',
    summary: 'Statutory Notice Drafted -> Supervisor Queue',
    detail: 'Risk score 65 (Chronic Breacher, 74 days overdue). Level 6 escalation requires human signoff.',
    badgeColor: 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/20',
  },
  {
    id: '5',
    timestamp: '18m ago',
    type: 'DIAGNOSE',
    invoiceNumber: 'INV-2026-0021',
    summary: 'Debtor Archetype Diagnosed: FORGETFUL_SLOW',
    detail: 'P(Recovery) calculated at 84%. Dispatched polite WhatsApp reminder with Razorpay Link.',
    badgeColor: 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20',
  },
];

export default function LiveAgentStream() {
  const [events] = useState<AgentEvent[]>(INITIAL_EVENTS);

  return (
    <div className="h-full flex flex-col justify-between rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 shadow-sm dark:shadow-2xl transition-all hover:border-blue-500/30">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[#0066FF]/10 text-[#0066FF] dark:text-[#38BDF8] border border-[#0066FF]/20">
            <Terminal className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-black tracking-tight text-slate-900 dark:text-white">
                Autonomous Recovery Agent Feed
              </h3>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-black text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                STREAMING
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Live bitemporal ledger audits, tone adaptations, and signed webhook reconciliations
            </p>
          </div>
        </div>

        {/* Live Audio / Frequency Waveform Animation */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-black/50 border border-slate-200 dark:border-white/[0.08]">
          <span className="text-[10px] font-mono font-bold text-slate-500 dark:text-slate-400 mr-1">AI FREQ</span>
          <div className="flex items-end gap-0.5 h-4 w-9">
            <span className="w-1 bg-[#0066FF] rounded-full animate-wave-1" />
            <span className="w-1 bg-[#0099FF] rounded-full animate-wave-2" />
            <span className="w-1 bg-indigo-500 rounded-full animate-wave-3" />
            <span className="w-1 bg-emerald-500 rounded-full animate-wave-4" />
          </div>
        </div>
      </div>

      {/* Events List */}
      <div className="mt-4 flex-1 flex flex-col justify-between space-y-2">
        {events.map((ev) => (
          <div
            key={ev.id}
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 sm:p-3 rounded-2xl bg-slate-50/70 dark:bg-black/40 border border-slate-200/60 dark:border-white/[0.06] hover:border-slate-300 dark:hover:border-white/[0.12] transition-all text-xs"
          >
            <div className="flex items-start sm:items-center gap-3">
              <span className={`rounded-lg px-2.5 py-1 text-[10px] font-extrabold border shrink-0 uppercase tracking-wide ${ev.badgeColor}`}>
                {ev.type}
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 dark:text-white">{ev.summary}</span>
                  <span className="text-[11px] font-mono text-[#0066FF] dark:text-[#38BDF8] font-bold">
                    {ev.invoiceNumber}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">{ev.detail}</p>
              </div>
            </div>

            <div className="text-[10px] font-mono font-medium text-slate-400 dark:text-slate-500 shrink-0 self-end sm:self-center">
              {ev.timestamp}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
