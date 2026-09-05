'use client';

import React, { useState } from 'react';
import { TrendingUp, ShieldAlert, Sparkles, CheckCircle2 } from 'lucide-react';

interface DataPoint {
  day: number;
  label: string;
  agentPct: number;
  baselinePct: number;
  agentInr: number;
  baselineInr: number;
  milestone?: string;
}

const TRAJECTORY_DATA: DataPoint[] = [
  { day: 0, label: 'Day 0', agentPct: 0, baselinePct: 0, agentInr: 0, baselineInr: 0 },
  { day: 3, label: 'Day 3', agentPct: 14.5, baselinePct: 8.2, agentInr: 1303550, baselineInr: 737180, milestone: 'Level 1 WhatsApp Reminder' },
  { day: 7, label: 'Day 7', agentPct: 22.8, baselinePct: 14.5, agentInr: 2049720, baselineInr: 1303550 },
  { day: 14, label: 'Day 14', agentPct: 34.2, baselinePct: 21.0, agentInr: 3074580, baselineInr: 1887900, milestone: 'Level 4 Dynamic Payment Plan Offered' },
  { day: 21, label: 'Day 21', agentPct: 41.5, baselinePct: 25.4, agentInr: 3730850, baselineInr: 2283460, milestone: 'Promise Deadline Tracking & Escalation' },
  { day: 28, label: 'Day 28', agentPct: 46.8, baselinePct: 27.8, agentInr: 4207320, baselineInr: 2499220, milestone: 'Level 6 Legal Notice Approved' },
  { day: 30, label: 'Day 30', agentPct: 48.5, baselinePct: 28.2, agentInr: 4360150, baselineInr: 2535180 },
];

export default function RecoveryChart() {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // SVG dimensions
  const width = 760;
  const height = 240;
  const paddingX = 45;
  const paddingY = 30;

  const graphWidth = width - paddingX * 2;
  const graphHeight = height - paddingY * 2;

  const maxPct = 55;

  const getX = (index: number) => paddingX + (index / (TRAJECTORY_DATA.length - 1)) * graphWidth;
  const getY = (pct: number) => height - paddingY - (pct / maxPct) * graphHeight;

  // Build SVG paths
  const agentPoints = TRAJECTORY_DATA.map((d, i) => `${getX(i)},${getY(d.agentPct)}`).join(' ');
  const baselinePoints = TRAJECTORY_DATA.map((d, i) => `${getX(i)},${getY(d.baselinePct)}`).join(' ');

  // Area path for gradient fill
  const areaPath = `M ${getX(0)},${getY(0)} ` +
    TRAJECTORY_DATA.map((d, i) => `L ${getX(i)},${getY(d.agentPct)}`).join(' ') +
    ` L ${getX(TRAJECTORY_DATA.length - 1)},${height - paddingY} L ${getX(0)},${height - paddingY} Z`;

  const activePoint = hoveredIdx !== null ? TRAJECTORY_DATA[hoveredIdx] : TRAJECTORY_DATA[TRAJECTORY_DATA.length - 1];

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-6 shadow-sm dark:shadow-2xl transition-all hover:border-blue-500/30">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-white/[0.08] pb-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h3 className="text-sm sm:text-base font-black tracking-tight text-slate-900 dark:text-white">
              Cumulative Recovery Trajectory
            </h3>
            <span className="rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-0.5 text-[10px] font-extrabold border border-emerald-500/20 uppercase tracking-wider flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              +20.3% Final Lift
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Head-to-head cash collection curve over 30 days across identical ₹89.9L receivables
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 text-xs font-semibold">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#0066FF] shadow-sm shadow-blue-500/50" />
            <span className="text-slate-800 dark:text-slate-200 font-bold">RevBack Agent</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 border-b-2 border-dashed border-slate-400 dark:border-slate-500" />
            <span className="text-slate-500 dark:text-slate-400">Static ERP Baseline</span>
          </div>
        </div>
      </div>

      {/* SVG Chart */}
      <div className="relative mt-4">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible select-none">
          <defs>
            {/* Area Gradient */}
            <linearGradient id="agentAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0066FF" stopOpacity="0.22" />
              <stop offset="100%" stopColor="#0066FF" stopOpacity="0.0" />
            </linearGradient>

            {/* Line Gradient */}
            <linearGradient id="agentLineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#0066FF" />
              <stop offset="60%" stopColor="#0099FF" />
              <stop offset="100%" stopColor="#10B981" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 15, 30, 45].map((pct) => (
            <g key={pct}>
              <line
                x1={paddingX}
                y1={getY(pct)}
                x2={width - paddingX}
                y2={getY(pct)}
                stroke="currentColor"
                className="text-slate-200 dark:text-white/[0.06] stroke-1"
                strokeDasharray="4 4"
              />
              <text
                x={paddingX - 8}
                y={getY(pct) + 3}
                textAnchor="end"
                className="text-[10px] fill-slate-400 dark:fill-slate-500 font-mono"
              >
                {pct}%
              </text>
            </g>
          ))}

          {/* Area Fill */}
          <path d={areaPath} fill="url(#agentAreaGrad)" />

          {/* Static Baseline Path */}
          <polyline
            points={baselinePoints}
            fill="none"
            stroke="#94A3B8"
            strokeWidth="2"
            strokeDasharray="5 5"
            strokeLinecap="round"
            className="opacity-50"
          />

          {/* RevBack Agent Path */}
          <polyline
            points={agentPoints}
            fill="none"
            stroke="url(#agentLineGrad)"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="filter drop-shadow-md"
          />

          {/* Data interactive nodes (Clean dots, zero ping bubbles) */}
          {TRAJECTORY_DATA.map((d, i) => {
            const cx = getX(i);
            const cy = getY(d.agentPct);
            const isHovered = hoveredIdx === i;

            return (
              <g
                key={i}
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
              >
                {/* Clean node circle without ping bubbles */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? "6" : "3.5"}
                  className="fill-white dark:fill-[#0A0D14] stroke-[#0066FF] stroke-2 transition-all duration-150"
                />
                {/* X Axis Labels */}
                <text
                  x={cx}
                  y={height - 8}
                  textAnchor="middle"
                  className="text-[10px] fill-slate-400 dark:fill-slate-500 font-medium"
                >
                  {d.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Dynamic Interactive Callout Tooltip */}
        <div className="mt-4 flex flex-wrap items-center justify-between rounded-2xl bg-slate-50/80 dark:bg-black/50 border border-slate-200/80 dark:border-white/[0.08] p-3.5 text-xs">
          <div className="flex items-center gap-2.5">
            <span className="font-extrabold text-white bg-[#0066FF] px-2.5 py-0.5 rounded-lg text-[11px] shadow-sm">
              {activePoint.label}
            </span>
            {activePoint.milestone && (
              <span className="text-slate-600 dark:text-slate-300 font-medium flex items-center gap-1.5 text-[11px]">
                <Sparkles className="h-3.5 w-3.5 text-amber-400" />
                {activePoint.milestone}
              </span>
            )}
          </div>

          <div className="flex items-center gap-4 text-xs font-semibold">
            <div>
              <span className="text-slate-400 font-normal">Agent: </span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                ₹{(activePoint.agentInr / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({activePoint.agentPct}%)
              </span>
            </div>
            <div>
              <span className="text-slate-400 font-normal">Baseline: </span>
              <span className="font-semibold text-slate-500 dark:text-slate-400">
                ₹{(activePoint.baselineInr / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({activePoint.baselinePct}%)
              </span>
            </div>
            <div className="rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-0.5 font-extrabold border border-emerald-500/20">
              Lift: +{(activePoint.agentPct - activePoint.baselinePct).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
