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
  AlertOctagon,
  FileText,
  Trash2,
  SendHorizontal,
} from 'lucide-react';
import { fetchApprovals, resolveApproval } from '@/lib/api';
import { HumanApproval } from '@/lib/types';
import NumberTicker from '@/components/NumberTicker';

interface ActionToast {
  type: 'APPROVED' | 'REJECTED';
  title: string;
  message: string;
  invoiceRef?: string;
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<HumanApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState<string | null>(null);
  const [animatingId, setAnimatingId] = useState<string | null>(null);
  const [animatingAction, setAnimatingAction] = useState<'APPROVED' | 'REJECTED' | null>(null);
  const [toast, setToast] = useState<ActionToast | null>(null);
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

  const handleDecision = async (id: string, decision: 'APPROVED' | 'REJECTED', invoiceRef?: string) => {
    setResolvingId(id);
    setAnimatingId(id);
    setAnimatingAction(decision);

    if (decision === 'APPROVED') {
      setToast({
        type: 'APPROVED',
        title: 'Notice Dispatched to Debtor',
        message: 'Statutory notice sent with signed Razorpay payment link. Webhook listener active.',
        invoiceRef,
      });
    } else {
      setToast({
        type: 'REJECTED',
        title: 'Escalation Halted & Deleted',
        message: 'Supervisor halted outreach. Case deleted from active queue and archived.',
        invoiceRef,
      });
    }

    try {
      await resolveApproval(id, decision, reviewNotes[id] || '');
      // Match the exact duration of the CSS animation for zero-jank dismissal
      const animDuration = decision === 'APPROVED' ? 750 : 700;
      setTimeout(async () => {
        await loadApprovals();
        setAnimatingId(null);
        setAnimatingAction(null);
      }, animDuration);
    } catch (err) {
      console.error('Decision error:', err);
      setAnimatingId(null);
      setAnimatingAction(null);
    } finally {
      setResolvingId(null);
      setTimeout(() => setToast(null), 3500);
    }
  };

  const pending = approvals.filter((a) => a.status === 'PENDING');
  const resolved = approvals.filter((a) => a.status !== 'PENDING');

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6 relative">
      {/* Ultra-Smooth Floating Notification Toast */}
      {toast && (
        <div
          className={`fixed top-20 right-4 sm:right-6 z-50 max-w-sm w-full p-3.5 rounded-2xl backdrop-blur-2xl shadow-2xl border transition-all animate-toast-smooth ${
            toast.type === 'APPROVED'
              ? 'bg-[#071A12]/95 border-emerald-500/40 shadow-emerald-500/20 text-white'
              : 'bg-[#1C0A0E]/95 border-rose-500/40 shadow-rose-500/20 text-white'
          }`}
        >
          <div className="flex items-start gap-3">
            <div
              className={`rounded-xl p-2 shrink-0 ${
                toast.type === 'APPROVED'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
              }`}
            >
              {toast.type === 'APPROVED' ? (
                <SendHorizontal className="h-4 w-4" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
            </div>
            <div className="flex-1 text-xs">
              <div className="font-bold tracking-tight text-slate-100 flex items-center justify-between">
                <span>{toast.title}</span>
                <span
                  className={`text-[9px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider ${
                    toast.type === 'APPROVED'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  {toast.type === 'APPROVED' ? 'Sent' : 'Deleted'}
                </span>
              </div>
              <p className="mt-0.5 text-slate-300 text-[11px] leading-relaxed">
                {toast.message}
              </p>
              {toast.invoiceRef && (
                <p className="mt-1 font-mono text-[9px] text-slate-400">
                  Ref #{toast.invoiceRef.slice(0, 8)}...
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-black tracking-tight text-slate-900 dark:text-white">
              Supervisor Approval Queue
            </h1>
            <span className="rounded-full bg-rose-500/10 text-rose-600 dark:text-rose-400 px-2.5 py-0.5 text-xs font-bold border border-rose-500/20">
              <NumberTicker value={pending.length} /> Pending Review
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Autonomous safety gating: formal legal notices and low-confidence AI decisions require explicit supervisor authorization.
          </p>
        </div>

        <button
          onClick={loadApprovals}
          disabled={loading}
          className="flex items-center gap-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 text-slate-400 ${loading ? 'animate-spin text-blue-500' : ''}`} />
          <span>{loading ? 'Refreshing...' : 'Refresh Queue'}</span>
        </button>
      </div>

      {/* Pending Items Count Banner */}
      <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-500/10 dark:bg-blue-500/20 p-2.5 text-blue-600 dark:text-blue-400 border border-blue-500/20">
            <UserCheck className="h-5 w-5" />
          </div>
          <div>
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              {pending.length} Critical Actions Awaiting Review
            </span>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Irreversible legal actions and threshold violations are safely halted until signed off.
            </p>
          </div>
        </div>
      </div>

      {/* Approvals Cards */}
      <div className="space-y-4">
        {pending.length === 0 ? (
          <div className="rounded-3xl border border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 backdrop-blur-xl p-12 text-center text-slate-400 space-y-2 shadow-sm dark:shadow-2xl">
            <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">Queue Clear</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              All high-risk actions have been resolved or are operating within verified autonomous policy bounds.
            </p>
          </div>
        ) : (
          pending.map((appr) => {
            const isThisAnimating = animatingId === appr.id;
            const isApproved = isThisAnimating && animatingAction === 'APPROVED';
            const isRejected = isThisAnimating && animatingAction === 'REJECTED';

            return (
              <div
                key={appr.id}
                className={`rounded-3xl border backdrop-blur-xl p-6 space-y-4 shadow-sm dark:shadow-2xl transition-all duration-300 relative overflow-hidden ${
                  isApproved
                    ? 'animate-warp-send border-emerald-500/50 bg-[#071912]/95 shadow-[0_0_35px_rgba(16,185,129,0.25),inset_0_0_25px_rgba(16,185,129,0.12)] ring-1 ring-emerald-500/40'
                    : isRejected
                    ? 'animate-warp-reject border-rose-500/50 bg-[#19070B]/95 shadow-[0_0_35px_rgba(244,63,94,0.25),inset_0_0_25px_rgba(244,63,94,0.12)] ring-1 ring-rose-500/40'
                    : 'border-slate-200/80 dark:border-white/10 bg-white/80 dark:bg-[#0A0D14]/80 hover:border-emerald-500/30 dark:hover:border-emerald-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.06)]'
                }`}
              >
                {/* Slight Green Glow Accent Inside the Card */}
                {isApproved && (
                  <div className="pointer-events-none absolute inset-0 rounded-3xl bg-[radial-gradient(ellipse_at_top_right,rgba(16,185,129,0.2),transparent_70%)] ring-1 ring-inset ring-emerald-500/40 shadow-[inset_0_0_30px_rgba(16,185,129,0.15)] animate-pulse" />
                )}

                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-white/[0.08] pb-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`rounded-lg px-2.5 py-0.5 text-xs font-bold border ${
                        appr.action_type === 'LEGAL_NOTICE'
                          ? 'bg-purple-500/10 text-purple-600 dark:text-purple-400 border-purple-500/30'
                          : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30'
                      }`}
                    >
                      {appr.action_type}
                    </span>
                    <Link
                      href={`/invoices/${appr.invoice_id}`}
                      className="font-bold text-sm text-slate-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1"
                    >
                      <span>Receivable #{appr.invoice_id.slice(0, 8)}...</span>
                      <ExternalLink className="h-3 w-3 text-slate-400" />
                    </Link>
                  </div>
                  <div className="text-xs text-slate-400 dark:text-slate-500">
                    Requested: {new Date(appr.requested_at).toLocaleString('en-IN')}
                  </div>
                </div>

                {/* Confidence vs Threshold */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="rounded-xl bg-slate-50 dark:bg-slate-900/60 p-3.5 border border-slate-200/60 dark:border-slate-800 space-y-1">
                    <div className="text-slate-500 dark:text-slate-400 font-semibold">Safety Gating Threshold</div>
                    <div className="flex items-center justify-between font-bold">
                      <span className="text-slate-700 dark:text-slate-300">AI Confidence:</span>
                      <span
                        className={
                          appr.confidence < appr.threshold ? 'text-amber-600 dark:text-amber-400' : 'text-emerald-600 dark:text-emerald-400'
                        }
                      >
                        {(appr.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                      <span>Policy Threshold Required:</span>
                      <span className="font-semibold">{(appr.threshold * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  <div className="rounded-xl bg-slate-50 dark:bg-slate-900/60 p-3.5 border border-slate-200/60 dark:border-slate-800 space-y-1">
                    <div className="text-slate-500 dark:text-slate-400 font-semibold">Proposed Action Details</div>
                    <div className="text-slate-800 dark:text-slate-200">
                      Level: <span className="font-bold">{appr.proposed_action_details?.level || 'Escalation'}</span>
                    </div>
                    <div className="text-slate-600 dark:text-slate-400 italic text-[11px] truncate">
                      Reason: {appr.proposed_action_details?.reason || 'Confidence safety gate triggered'}
                    </div>
                  </div>
                </div>

                {/* Draft Message Preview if available */}
                {appr.proposed_action_details?.message_draft && (
                  <div className="rounded-xl bg-slate-50 dark:bg-slate-950 p-4 border border-slate-200 dark:border-slate-800 text-xs space-y-1.5 relative overflow-hidden">
                    {isApproved && (
                      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-emerald-500 via-teal-300 to-emerald-400 animate-pulse" />
                    )}
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-slate-700 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <FileText className="h-3.5 w-3.5 text-blue-500" />
                        Drafted Notice Content:
                      </span>
                      {isApproved && (
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1 animate-pulse">
                          <SendHorizontal className="h-3 w-3 animate-plane-takeoff" />
                          Sending...
                        </span>
                      )}
                    </div>
                    <p className="text-slate-700 dark:text-slate-300 text-[11px] whitespace-pre-wrap font-mono leading-relaxed bg-white dark:bg-slate-900/60 p-3 rounded-lg border border-slate-200/60 dark:border-slate-800">
                      {appr.proposed_action_details.message_draft}
                    </p>
                  </div>
                )}

                {/* Supervisor Review Notes & Actions */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 space-y-3">
                  <input
                    type="text"
                    placeholder="Supervisor review notes / instructions..."
                    value={reviewNotes[appr.id] || ''}
                    onChange={(e) =>
                      setReviewNotes({ ...reviewNotes, [appr.id]: e.target.value })
                    }
                    className="w-full rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3.5 py-2 text-xs text-slate-900 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500 transition-colors"
                  />

                  <div className="flex items-center justify-end gap-2.5">
                    <button
                      onClick={() => handleDecision(appr.id, 'REJECTED', appr.invoice_id)}
                      disabled={resolvingId === appr.id}
                      className="group flex items-center gap-1.5 rounded-xl border border-rose-500/30 bg-rose-500/10 px-3.5 py-2 text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-500/20 active:scale-95 transition-all disabled:opacity-50"
                    >
                      <Trash2
                        className={`h-4 w-4 transition-transform ${
                          isRejected ? 'animate-trash-snappy text-rose-500' : 'group-hover:scale-110'
                        }`}
                      />
                      <span>{isRejected ? 'Deleting...' : 'Reject / Halt Escalation'}</span>
                    </button>

                    <button
                      onClick={() => handleDecision(appr.id, 'APPROVED', appr.invoice_id)}
                      disabled={resolvingId === appr.id}
                      className="group flex items-center gap-1.5 rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-500 transition-all shadow-md shadow-emerald-600/20 disabled:opacity-50 active:scale-95 hover:shadow-emerald-500/40"
                    >
                      <SendHorizontal
                        className={`h-4 w-4 transition-transform ${
                          isApproved ? 'animate-plane-takeoff' : 'group-hover:translate-x-0.5'
                        }`}
                      />
                      <span>{isApproved ? 'Sending Notice...' : 'Authorize & Dispatch'}</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
