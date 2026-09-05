'use client';

import React, { useState } from 'react';
import { TrendingUp, Sparkles, ArrowUpRight, Zap } from 'lucide-react';

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
  { day: 14, label: 'Day 14', agentPct: 34.2, baselinePct: 21.0, agentInr: 3074580, baselineInr: 1887900, milestone: 'Level 4 Dynamic Settlement Plan' },
  { day: 21, label: 'Day 21', agentPct: 41.5, baselinePct: 25.4, agentInr: 3730850, baselineInr: 2283460, milestone: 'Promise Deadline Tracking' },
  { day: 28, label: 'Day 28', agentPct: 46.8, baselinePct: 27.8, agentInr: 4207320, baselineInr: 2499220, milestone: 'Level 6 Legal Notice Signed' },
  { day: 30, label: 'Day 30', agentPct: 48.5, baselinePct: 28.2, agentInr: 4360150, baselineInr: 2535180, milestone: 'Cycle Reconciliation Complete' },
];

export default function RecoveryChart() {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);

  // SVG dimensions
  const width = 760;
  const height = 280;
  const paddingX = 42;
  const paddingTop = 22;
  const paddingBottom = 34;

  const graphWidth = width - paddingX * 2;
  const graphHeight = height - paddingTop - paddingBottom;
  const stepWidth = graphWidth / (TRAJECTORY_DATA.length - 1);

  const maxPct = 52;

  const getX = (index: number) => paddingX + (index / (TRAJECTORY_DATA.length - 1)) * graphWidth;
  const getY = (pct: number) => height - paddingBottom - (pct / maxPct) * graphHeight;

  // Build SVG paths
  const agentPoints = TRAJECTORY_DATA.map((d, i) => `${getX(i)},${getY(d.agentPct)}`).join(' ');
  const baselinePoints = TRAJECTORY_DATA.map((d, i) => `${getX(i)},${getY(d.baselinePct)}`).join(' ');

  // Area path for gradient fill
  const areaPath =
    `M ${getX(0)},${getY(0)} ` +
    TRAJECTORY_DATA.map((d, i) => `L ${getX(i)},${getY(d.agentPct)}`).join(' ') +
    ` L ${getX(TRAJECTORY_DATA.length - 1)},${height - paddingBottom} L ${getX(0)},${height - paddingBottom} Z`;

  const activePoint = hoveredIdx !== null ? TRAJECTORY_DATA[hoveredIdx] : TRAJECTORY_DATA[TRAJECTORY_DATA.length - 1];

  return (
    <div className="h-full flex flex-col justify-between rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-5 sm:p-6 shadow-sm dark:shadow-2xl transition-all hover:border-blue-500/30 gap-3 sm:gap-4">
      {/* 1. Header with Title and Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-white/[0.08] pb-3.5 shrink-0">
        <div>
          <div className="flex items-center gap-2.5">
            <h3 className="text-sm sm:text-base font-black tracking-tight text-slate-900 dark:text-white flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-[#0066FF] dark:text-[#38BDF8]" />
              Cumulative Recovery Trajectory
            </h3>
            <span className="rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2.5 py-0.5 text-[10px] font-extrabold border border-emerald-500/20 uppercase tracking-wider flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              +20.3% Lift
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Head-to-head cash collection curve over 30 days across identical ₹89.9L receivables
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3.5 text-xs font-semibold shrink-0">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-[#0066FF] shadow-sm shadow-blue-500/50" />
            <span className="text-slate-800 dark:text-slate-200 font-bold text-[11px]">RevBack Agent</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="h-0.5 w-3 border-b-2 border-dashed border-slate-400 dark:border-slate-500" />
            <span className="text-slate-500 dark:text-slate-400 text-[11px]">Static ERP Baseline</span>
          </div>
        </div>
      </div>

      {/* 2. Executive KPI Ribbon: Rich financial benchmarks */}
      <div className="grid grid-cols-3 gap-2 sm:gap-2.5 shrink-0">
        <div className="p-2.5 sm:p-3 rounded-2xl bg-slate-50/80 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.05]">
          <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Agent Recovered
          </div>
          <div className="text-base sm:text-lg font-black text-emerald-600 dark:text-emerald-400 tracking-tight mt-0.5">
            ₹43.60 Lakh
          </div>
          <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            48.5% recovered
          </div>
        </div>

        <div className="p-2.5 sm:p-3 rounded-2xl bg-slate-50/80 dark:bg-white/[0.03] border border-slate-200/60 dark:border-white/[0.05]">
          <div className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Static ERP Baseline
          </div>
          <div className="text-base sm:text-lg font-black text-slate-700 dark:text-slate-300 tracking-tight mt-0.5">
            ₹25.35 Lakh
          </div>
          <div className="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            28.2% manual followup
          </div>
        </div>

        <div className="p-2.5 sm:p-3 rounded-2xl bg-blue-50/80 dark:bg-[#0066FF]/10 border border-blue-200/60 dark:border-[#0066FF]/20">
          <div className="text-[10px] font-semibold text-[#0066FF] dark:text-[#38BDF8] uppercase tracking-wider flex items-center gap-1">
            <Zap className="h-3 w-3" />
            Cash Velocity Alpha
          </div>
          <div className="text-base sm:text-lg font-black text-[#0066FF] dark:text-[#38BDF8] tracking-tight mt-0.5">
            +₹18.25 Lakh
          </div>
          <div className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold mt-0.5 flex items-center gap-0.5">
            <ArrowUpRight className="h-3 w-3" />
            +20.3% Net Lift
          </div>
        </div>
      </div>

      {/* 3. Responsive SVG Trajectory Canvas */}
      <div className="relative flex-1 w-full min-h-[220px] flex items-center">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto overflow-visible select-none"
          onMouseLeave={() => setHoveredIdx(null)}
        >
          <defs>
            {/* Area Gradient */}
            <linearGradient id="agentAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#0066FF" stopOpacity="0.25" />
              <stop offset="60%" stopColor="#0099FF" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#0066FF" stopOpacity="0.0" />
            </linearGradient>

            {/* Line Gradient */}
            <linearGradient id="agentLineGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#0066FF" />
              <stop offset="50%" stopColor="#0099FF" />
              <stop offset="100%" stopColor="#10B981" />
            </linearGradient>

            <filter id="glowShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#0066FF" floodOpacity="0.3" />
            </filter>
          </defs>

          {/* Grid lines spanning 0% to 50% */}
          {[0, 15, 30, 45, 50].map((pct) => (
            <g key={pct} className="pointer-events-none">
              <line
                x1={paddingX}
                y1={getY(pct)}
                x2={width - paddingX}
                y2={getY(pct)}
                stroke="currentColor"
                className="text-slate-200 dark:text-white/[0.07] stroke-1"
                strokeDasharray="4 4"
              />
              <text
                x={paddingX - 8}
                y={getY(pct) + 3}
                textAnchor="end"
                className="text-[10px] fill-slate-400 dark:fill-slate-500 font-mono font-semibold"
              >
                {pct}%
              </text>
            </g>
          ))}

          {/* Area Fill */}
          <path d={areaPath} fill="url(#agentAreaGrad)" className="pointer-events-none" />

          {/* Static Baseline Path */}
          <polyline
            points={baselinePoints}
            fill="none"
            stroke="#94A3B8"
            strokeWidth="2"
            strokeDasharray="5 5"
            strokeLinecap="round"
            className="opacity-60 pointer-events-none"
          />

          {/* RevBack Agent Path */}
          <polyline
            points={agentPoints}
            fill="none"
            stroke="url(#agentLineGrad)"
            strokeWidth="3.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            filter="url(#glowShadow)"
            className="pointer-events-none"
          />

          {/* Active Crosshair Vertical Guide Line */}
          {hoveredIdx !== null && (
            <line
              x1={getX(hoveredIdx)}
              y1={paddingTop}
              x2={getX(hoveredIdx)}
              y2={height - paddingBottom}
              stroke="#0066FF"
              strokeWidth="1.5"
              strokeDasharray="3 3"
              className="opacity-50 pointer-events-none"
            />
          )}

          {/* Render Visual Markers & Labels (Pointer-events none to avoid mouse jitter) */}
          {TRAJECTORY_DATA.map((d, i) => {
            const cx = getX(i);
            const cy = getY(d.agentPct);
            const isHovered = hoveredIdx === i;
            const hasMilestone = Boolean(d.milestone);

            return (
              <g key={`node-${i}`} className="pointer-events-none">
                {/* Milestone Halo */}
                {hasMilestone && (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={isHovered ? 11 : 8}
                    className="fill-blue-500/15 stroke-blue-500/40 stroke-1 transition-all duration-150"
                  />
                )}

                {/* Core node circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 6 : hasMilestone ? 4.5 : 3.5}
                  className={`transition-all duration-150 ${
                    isHovered
                      ? 'fill-[#0066FF] stroke-white dark:stroke-[#0A0D14] stroke-2 shadow-lg'
                      : 'fill-white dark:fill-[#0A0D14] stroke-[#0066FF] stroke-2'
                  }`}
                />

                {/* X Axis Labels */}
                <text
                  x={cx}
                  y={height - 10}
                  textAnchor="middle"
                  className={`text-[10px] transition-colors duration-150 ${
                    isHovered
                      ? 'fill-blue-600 dark:fill-blue-400 font-bold'
                      : 'fill-slate-400 dark:fill-slate-500 font-medium'
                  }`}
                >
                  {d.label}
                </text>
              </g>
            );
          })}

          {/* Full-Height Vertical Hit Targets (Zero jitter: wide invisible slices) */}
          {TRAJECTORY_DATA.map((d, i) => {
            const cx = getX(i);
            const isFirst = i === 0;
            const isLast = i === TRAJECTORY_DATA.length - 1;
            const sliceX = isFirst ? paddingX : cx - stepWidth / 2;
            const sliceW = isFirst || isLast ? stepWidth / 2 + 10 : stepWidth;

            return (
              <rect
                key={`hit-${i}`}
                x={sliceX}
                y={0}
                width={sliceW}
                height={height}
                fill="transparent"
                className="cursor-pointer"
                onMouseEnter={() => setHoveredIdx(i)}
              />
            );
          })}
        </svg>
      </div>

      {/* 4. Rock-Solid Fixed-Height Interactive Callout (Zero Layout Shift) */}
      <div className="h-12 min-h-[48px] max-h-[48px] flex items-center justify-between rounded-2xl bg-slate-50/90 dark:bg-black/40 border border-slate-200/80 dark:border-white/[0.08] px-3 sm:px-4 text-xs select-none shrink-0 overflow-hidden">
        {/* Left: Day Badge + Milestone text with truncate safety */}
        <div className="flex items-center gap-2 sm:gap-2.5 min-w-0 flex-1 mr-2">
          <span className="font-extrabold text-white bg-[#0066FF] px-2.5 py-1 rounded-lg text-[11px] shadow-sm shrink-0 font-mono">
            {activePoint.label}
          </span>
          <div className="flex items-center gap-1.5 min-w-0 truncate">
            {activePoint.milestone ? (
              <>
                <Sparkles className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                <span className="text-slate-700 dark:text-slate-300 font-semibold text-[11px] truncate">
                  {activePoint.milestone}
                </span>
              </>
            ) : (
              <span className="text-slate-500 dark:text-slate-400 text-[11px] truncate">
                Autonomous Cadence Checkpoint
              </span>
            )}
          </div>
        </div>

        {/* Right: Numbers and Lift Badge (Guaranteed to remain on single line) */}
        <div className="flex items-center gap-2.5 sm:gap-3 text-xs font-semibold shrink-0">
          <div className="text-right">
            <span className="text-slate-400 font-normal hidden sm:inline">Agent: </span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400 font-mono text-[11px] sm:text-xs">
              ₹{(activePoint.agentInr / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({activePoint.agentPct}%)
            </span>
          </div>
          <div className="hidden md:inline text-right">
            <span className="text-slate-400 font-normal">Base: </span>
            <span className="font-semibold text-slate-500 dark:text-slate-400 font-mono text-[11px] sm:text-xs">
              ₹{(activePoint.baselineInr / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
          </div>
          <div className="rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 font-extrabold border border-emerald-500/20 text-[10px] sm:text-[11px] font-mono shrink-0">
            +{(activePoint.agentPct - activePoint.baselinePct).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
}


