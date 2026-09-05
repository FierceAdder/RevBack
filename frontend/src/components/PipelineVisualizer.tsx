'use client';

import React from 'react';
import {
  Inbox,
  Activity,
  Send,
  Clock,
  AlertOctagon,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';

interface StageConfig {
  id: string;
  name: string;
  count: number;
  level: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  textColor: string;
  badgeBg: string;
  description: string;
}

interface PipelineVisualizerProps {
  stageBreakdown?: Record<string, number>;
  selectedStage?: string | null;
  onSelectStage?: (stageId: string | null) => void;
}

export default function PipelineVisualizer({
  stageBreakdown = {},
  selectedStage = null,
  onSelectStage,
}: PipelineVisualizerProps) {
  const stages: StageConfig[] = [
    {
      id: 'INTAKE',
      name: '1. Ingestion',
      count: stageBreakdown.INTAKE || 0,
      level: 'Level 0',
      icon: Inbox,
      color: 'border-slate-300 dark:border-white/10',
      textColor: 'text-slate-600 dark:text-slate-300',
      badgeBg: 'bg-slate-100 dark:bg-white/[0.06]',
      description: 'Receivable ingested from ERP / Razorpay. Awaiting anomaly & risk calculation.',
    },
    {
      id: 'DIAGNOSE',
      name: '2. Diagnosis',
      count: stageBreakdown.DIAGNOSE || 0,
      level: 'Risk Scored',
      icon: Activity,
      color: 'border-blue-400 dark:border-blue-500/30',
      textColor: 'text-[#0066FF] dark:text-[#38BDF8]',
      badgeBg: 'bg-blue-50 dark:bg-[#0066FF]/10',
      description: 'Archetype diagnosed, recovery probability P(Recovery) predicted via logistic model.',
    },
    {
      id: 'ACT',
      name: '3. Intervention',
      count: stageBreakdown.ACT || 0,
      level: 'Levels 1–3',
      icon: Send,
      color: 'border-cyan-400 dark:border-cyan-500/30',
      textColor: 'text-cyan-600 dark:text-cyan-400',
      badgeBg: 'bg-cyan-50 dark:bg-cyan-500/10',
      description: 'Tone-adapted communication dispatched via WhatsApp/Email with Razorpay payment link.',
    },
    {
      id: 'PROMISE_TRACKING',
      name: '4. Commitments',
      count: stageBreakdown.PROMISE_TRACKING || 0,
      level: 'Bitemporal',
      icon: Clock,
      color: 'border-amber-400 dark:border-amber-500/30',
      textColor: 'text-amber-600 dark:text-amber-400',
      badgeBg: 'bg-amber-50 dark:bg-amber-500/10',
      description: 'Debtor promise-to-pay tracked with valid_at & recorded_at. Monitored for deadline breach.',
    },
    {
      id: 'ESCALATION',
      name: '5. Escalation',
      count: stageBreakdown.ESCALATION || 0,
      level: 'Levels 5–7',
      icon: AlertOctagon,
      color: 'border-rose-400 dark:border-rose-500/30',
      textColor: 'text-rose-600 dark:text-rose-400',
      badgeBg: 'bg-rose-50 dark:bg-rose-500/10',
      description: 'Multi-breach accounts routed to supervisor queue for formal statutory legal notice review.',
    },
    {
      id: 'RECOVERED',
      name: '6. Settled',
      count: stageBreakdown.RECOVERED || 0,
      level: 'Verified',
      icon: CheckCircle2,
      color: 'border-emerald-400 dark:border-emerald-500/30',
      textColor: 'text-emerald-600 dark:text-emerald-400',
      badgeBg: 'bg-emerald-50 dark:bg-emerald-500/10',
      description: 'Razorpay webhook cryptographically confirmed payment. Case closed with zero harassment.',
    },
  ];

  const total = Object.values(stageBreakdown).reduce((acc, v) => acc + v, 0) || 1;

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 shadow-sm dark:shadow-2xl transition-all hover:border-blue-500/30 space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-white/[0.08] pb-4">
        <div>
          <h3 className="text-sm sm:text-base font-black tracking-tight text-slate-900 dark:text-white">
            Autonomous Recovery Lifecycle
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Deterministic state machine with bitemporal memory and policy cooldowns
          </p>
        </div>
        {selectedStage && (
          <button
            onClick={() => onSelectStage?.(null)}
            className="text-xs font-bold text-[#0066FF] dark:text-[#38BDF8] hover:underline"
          >
            Clear Filter (Show All)
          </button>
        )}
      </div>

      {/* Progress Bar Ribbon */}
      <div className="w-full bg-slate-100 dark:bg-black/60 rounded-full h-2 overflow-hidden flex shadow-inner">
        <div style={{ width: `${((stageBreakdown.INTAKE || 0) / total) * 100}%` }} className="bg-slate-400 transition-all duration-500" />
        <div style={{ width: `${((stageBreakdown.DIAGNOSE || 0) / total) * 100}%` }} className="bg-[#0066FF] transition-all duration-500" />
        <div style={{ width: `${((stageBreakdown.ACT || 0) / total) * 100}%` }} className="bg-cyan-500 transition-all duration-500" />
        <div style={{ width: `${((stageBreakdown.PROMISE_TRACKING || 0) / total) * 100}%` }} className="bg-amber-500 transition-all duration-500" />
        <div style={{ width: `${((stageBreakdown.ESCALATION || 0) / total) * 100}%` }} className="bg-rose-500 transition-all duration-500" />
        <div style={{ width: `${((stageBreakdown.RECOVERED || 0) / total) * 100}%` }} className="bg-emerald-500 transition-all duration-500" />
      </div>

      {/* 6 Stage Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-1">
        {stages.map((st) => {
          const Icon = st.icon;
          const isSelected = selectedStage === st.id;

          return (
            <div
              key={st.id}
              onClick={() => onSelectStage?.(isSelected ? null : st.id)}
              className={`group relative rounded-2xl border p-3.5 transition-all cursor-pointer select-none ${
                st.color
              } ${
                isSelected
                  ? 'ring-2 ring-[#0066FF] bg-[#0066FF]/10 dark:bg-[#0066FF]/20 shadow-md shadow-blue-500/20'
                  : 'bg-slate-50/60 dark:bg-black/40 hover:bg-slate-100/80 dark:hover:bg-white/[0.04]'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className={`rounded-xl p-1.5 ${st.badgeBg} ${st.textColor}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-[9px] font-extrabold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                  {st.level}
                </span>
              </div>

              <div className="mt-2.5">
                <div className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight">
                  {st.count}
                </div>
                <div className={`text-xs font-bold mt-0.5 truncate ${st.textColor}`}>
                  {st.name}
                </div>
              </div>

              <div className="mt-2 text-[10px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-tight">
                {st.description}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
