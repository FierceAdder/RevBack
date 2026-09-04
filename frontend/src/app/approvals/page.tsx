'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  UserCheck,
  ShieldAlert,
  Scale,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
  Edit3,
  ExternalLink,
} from 'lucide-react';
import { fetchApprovals, resolveApproval } from '@/lib/api';
import { HumanApproval } from '@/lib/types';

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<HumanApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [reviewNotes, setReviewNotes] = useState<Record<string, string>>({});

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await fetchApprovals();
      setApprovals(data);
    } catch (err) {
      console.error('Failed to load approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleDecision = async (id: string, decision: 'APPROVED' | 'REJECTED') => {
    setResolvingId(id);
    try {
      await resolveApproval(id, decision, reviewNotes[id] || '');
      await loadApprovals();
    } catch (err) {
      console.error('Decision error:', err);
    } finally {
      setResolvingId(null);
    }
  };

  const pending = approvals.filter((a) => a.status === 'PENDING');
  const resolved = approvals.filter((a) => a.status !== 'PENDING');

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Human-in-the-Loop Review Queue
          </h1>
          <p className="mt-1 text-xs text-slate-400">
            Autonomous safety gating: formal legal notices and low-confidence AI decisions require supervisor authorization.
          </p>
        </div>

        <button
          onClick={loadApprovals}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
        >
          <RefreshCw className="h-3.5 w-3.5 text-slate-400" />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Pending Items Count Banner */}
      <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-blue-500/20 p-2 text-blue-400">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <span className="text-sm font-semibold text-white">
              {pending.length} Actions Awaiting Review
            </span>
            <p className="text-xs text-slate-400">
              Irreversible financial actions are bounded by policy and safely paused.
            </p>
          </div>
        </div>
      </div>

      {/* Approvals Cards */}
      <div className="space-y-4">
        {pending.length === 0 ? (
          <div className="rounded-xl border border-slate-800 bg-[#111622] p-12 text-center text-slate-400 space-y-2">
            <CheckCircle2 className="h-8 w-8 text-emerald-400 mx-auto" />
            <h3 className="text-sm font-semibold text-white">Queue Clear</h3>
            <p className="text-xs text-slate-400">
              All high-risk actions have been resolved or are operating within verified safety thresholds.
            </p>
          </div>
        ) : (
          pending.map((appr) => (
            <div
              key={appr.id}
              className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-4 shadow-sm"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`rounded px-2 py-0.5 text-xs font-bold border ${
                      appr.action_type === 'LEGAL_NOTICE'
                        ? 'bg-purple-500/10 text-purple-400 border-purple-500/30'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                    }`}
                  >
                    {appr.action_type}
                  </span>
                  <Link
                    href={`/invoices/${appr.invoice_id}`}
                    className="font-semibold text-sm text-white hover:underline flex items-center gap-1"
                  >
                    <span>Receivable #{appr.invoice_id.slice(0, 8)}...</span>
                    <ExternalLink className="h-3 w-3 text-slate-400" />
                  </Link>
                </div>
                <div className="text-xs text-slate-400">
                  Requested: {new Date(appr.requested_at).toLocaleString('en-IN')}
                </div>
              </div>

              {/* Confidence vs Threshold */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="rounded-lg bg-slate-900/60 p-3 border border-slate-800 space-y-1">
                  <div className="text-slate-400">Safety Gating Threshold</div>
                  <div className="flex items-center justify-between font-semibold">
                    <span>AI Confidence:</span>
                    <span
                      className={
                        appr.confidence < appr.threshold ? 'text-amber-400' : 'text-emerald-400'
                      }
                    >
                      {(appr.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Policy Threshold Required:</span>
                    <span>{(appr.threshold * 100).toFixed(0)}%</span>
                  </div>
                </div>

                <div className="rounded-lg bg-slate-900/60 p-3 border border-slate-800 space-y-1">
                  <div className="text-slate-400">Proposed Action Details</div>
                  <div className="text-slate-200">
                    Level: <span className="font-semibold">{appr.proposed_action_details?.level || 'Escalation'}</span>
                  </div>
                  <div className="text-slate-300 italic text-[11px] truncate">
                    Reason: {appr.proposed_action_details?.reason || 'Confidence safety gate triggered'}
                  </div>
                </div>
              </div>

              {/* Draft Message Preview if available */}
              {appr.proposed_action_details?.message_draft && (
                <div className="rounded-lg bg-slate-950 p-3 border border-slate-850 text-xs space-y-1">
                  <span className="text-[11px] font-semibold text-slate-400">Drafted Notice Content:</span>
                  <p className="text-slate-300 text-[11px] whitespace-pre-wrap">
                    {appr.proposed_action_details.message_draft}
                  </p>
                </div>
              )}

              {/* Supervisor Review Notes & Actions */}
              <div className="pt-2 border-t border-slate-800 space-y-3">
                <input
                  type="text"
                  placeholder="Supervisor review notes / instructions..."
                  value={reviewNotes[appr.id] || ''}
                  onChange={(e) =>
                    setReviewNotes({ ...reviewNotes, [appr.id]: e.target.value })
                  }
                  className="w-full rounded-lg bg-slate-900 border border-slate-800 px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />

                <div className="flex items-center justify-end gap-2">
                  <button
                    onClick={() => handleDecision(appr.id, 'REJECTED')}
                    disabled={resolvingId === appr.id}
                    className="flex items-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-1.5 text-xs font-semibold text-rose-300 hover:bg-rose-500/20 transition-colors disabled:opacity-50"
                  >
                    <XCircle className="h-4 w-4" />
                    <span>Reject / Halt Escalation</span>
                  </button>

                  <button
                    onClick={() => handleDecision(appr.id, 'APPROVED')}
                    disabled={resolvingId === appr.id}
                    className="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 transition-colors disabled:opacity-50 shadow-sm"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    <span>Authorize & Dispatch</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
