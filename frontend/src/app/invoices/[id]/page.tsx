'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  Calendar,
  Clock,
  ShieldAlert,
  Send,
  Sparkles,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  FileText,
  CreditCard,
  MessageSquare,
  Scale,
  RefreshCw,
  Building,
  User,
  Check,
  X,
  Activity,
  Bot,
} from 'lucide-react';
import {
  fetchInvoiceDetail,
  processInvoiceAgent,
  sendInboundMessage,
  fetchEvidenceBundle,
} from '@/lib/api';
import { InvoiceDetail } from '@/lib/types';
import NumberTicker from '@/components/NumberTicker';

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const invoiceId = params.id as string;

  const [invoice, setInvoice] = useState<InvoiceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [simMessage, setSimMessage] = useState('');
  const [simChannel, setSimChannel] = useState('EMAIL');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [simTrace, setSimTrace] = useState<string | null>(null);
  const [evidenceBundle, setEvidenceBundle] = useState<any | null>(null);
  const [showEvidenceModal, setShowEvidenceModal] = useState(false);
  const [actionAlert, setActionAlert] = useState<string | null>(null);

  const loadDetail = async () => {
    try {
      const data = await fetchInvoiceDetail(invoiceId);
      setInvoice(data);
    } catch (err) {
      console.error('Failed to load invoice detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDetail();
  }, [invoiceId]);

  const handleProcessAgent = async () => {
    setProcessing(true);
    setActionAlert(null);
    try {
      const res = await processInvoiceAgent(invoiceId);
      setActionAlert(
        `Autonomous Agent executed: Level ${res.current_level} via ${res.selected_channel} with ${res.selected_tone} tone.`
      );
      await loadDetail();
    } catch (err) {
      console.error('Process agent error:', err);
    } finally {
      setProcessing(false);
    }
  };

  const handleSendInbound = async (textToSend?: string) => {
    const text = textToSend || simMessage;
    if (!text.trim()) return;

    setSendingMessage(true);
    setActionAlert(null);
    setSimTrace('Perceiving debtor reply -> Extracting intent & bitemporal commitments -> Evaluating policy...');
    try {
      const res = await sendInboundMessage(invoiceId, text, simChannel);
      setActionAlert(res.agent_action_taken);
      setSimMessage('');
      setSimTrace(`Result: ${res.intent} (Confidence ${(res.intent_confidence * 100).toFixed(0)}%) | Action: ${res.agent_action_taken}`);
      await loadDetail();
    } catch (err) {
      console.error('Send inbound error:', err);
      setSimTrace('Error processing inbound message');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleOpenEvidence = async () => {
    try {
      const bundle = await fetchEvidenceBundle(invoiceId);
      setEvidenceBundle(bundle);
      setShowEvidenceModal(true);
    } catch (err) {
      console.error('Evidence error:', err);
    }
  };

  if (loading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center text-slate-500 dark:text-slate-400">
        <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-blue-500" />
        <p className="text-xs">Loading bitemporal receivable data...</p>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center text-slate-500 dark:text-slate-400">
        <AlertTriangle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
        <h2 className="text-base font-bold text-slate-900 dark:text-white">Invoice Not Found</h2>
        <p className="text-xs mt-1">Receivable #{invoiceId} could not be located in database.</p>
        <Link href="/invoices" className="inline-block mt-4 text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">
          Return to Ledger
        </Link>
      </div>
    );
  }

  const customer = invoice.customer;

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/invoices"
            className="flex h-9 w-9 items-center justify-center rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors shadow-sm"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-black tracking-tight text-slate-900 dark:text-white">
                {invoice.invoice_number}
              </h1>
              <span
                className={`rounded-md px-2 py-0.5 text-[11px] font-bold border ${
                  invoice.status === 'PAID'
                    ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                    : invoice.status === 'DISPUTED'
                    ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30'
                    : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30'
                }`}
              >
                {invoice.status}
              </span>
              <span className="rounded-md bg-blue-500/10 text-blue-600 dark:text-blue-400 px-2 py-0.5 text-[11px] font-bold border border-blue-500/20">
                Level {invoice.current_level} / 7
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {customer?.name} · B2B claim registered in RevBack ledger
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleOpenEvidence}
            className="flex items-center gap-1.5 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-bold text-purple-700 dark:text-purple-300 hover:bg-purple-500/20 transition-colors shadow-sm"
          >
            <Scale className="h-3.5 w-3.5" />
            <span>Evidence Bundle</span>
          </button>

          <button
            onClick={handleProcessAgent}
            disabled={processing}
            className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-xs font-bold text-white shadow-md shadow-blue-500/20 hover:from-blue-500 hover:to-indigo-500 transition-all disabled:opacity-50"
          >
            {processing ? (
              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Sparkles className="h-3.5 w-3.5" />
            )}
            <span>{processing ? 'Evaluating...' : 'Run Agent Cycle'}</span>
          </button>
        </div>
      </div>

      {/* Action Notification Alert */}
      {actionAlert && (
        <div className="rounded-xl border border-blue-500/30 bg-blue-50 dark:bg-blue-950/40 p-3.5 text-xs text-blue-900 dark:text-blue-200 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-2.5">
            <Sparkles className="h-4 w-4 text-blue-500 shrink-0" />
            <span className="font-semibold">{actionAlert}</span>
          </div>
          <button onClick={() => setActionAlert(null)} className="text-blue-500 hover:text-blue-700 dark:hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Header Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Claim Financials */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 space-y-3 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Total Claim Exposure
          </span>
          <div className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            <NumberTicker
              value={invoice.amount_paise / 100}
              prefix="₹"
              isCurrency={true}
            />
          </div>
          <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100 dark:border-slate-800/80 text-slate-500 dark:text-slate-400">
            <span>Recovered:</span>
            <span className="font-bold text-emerald-600 dark:text-emerald-400">
              ₹{(invoice.amount_paid_paise / 100).toLocaleString('en-IN')}
            </span>
          </div>
          {invoice.active_payment_link_url && (
            <a
              href={invoice.active_payment_link_url}
              target="_blank"
              rel="noreferrer"
              className="mt-2 flex items-center justify-between rounded-xl bg-blue-50 dark:bg-blue-600/10 border border-blue-200 dark:border-blue-500/20 px-3.5 py-2.5 text-xs font-bold text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-600/20 transition-colors shadow-sm"
            >
              <div className="flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-blue-500" />
                <span>Razorpay Payment Link</span>
              </div>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>

        {/* Debtor Profile */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 space-y-2.5 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Debtor Profile
          </span>
          <div className="font-bold text-slate-900 dark:text-white text-sm sm:text-base">{customer?.name}</div>
          <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1.5 pt-1 border-t border-slate-100 dark:border-slate-800/80">
            <div className="flex justify-between">
              <span>Contact:</span>
              <span className="text-slate-800 dark:text-slate-200 font-medium">{customer?.email}</span>
            </div>
            <div className="flex justify-between">
              <span>Tier:</span>
              <span className="text-slate-800 dark:text-slate-200 font-bold">
                {customer?.relationship_tier?.replace('_', ' ')}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Credit Score:</span>
              <span className="text-slate-800 dark:text-slate-200 font-bold">{customer?.credit_score}</span>
            </div>
          </div>
        </div>

        {/* AI Diagnosis & Strategy */}
        <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 space-y-2.5 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            AI Diagnosis & Safety
          </span>
          <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800/80">
            <span className="text-xs text-slate-500 dark:text-slate-400">Risk Score:</span>
            <span
              className={`font-bold text-xs px-2 py-0.5 rounded border ${
                invoice.risk_score >= 70
                  ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30'
                  : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30'
              }`}
            >
              {invoice.risk_score.toFixed(0)} / 100
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 dark:text-slate-400">P(Recovery):</span>
            <span className="font-bold text-xs text-blue-600 dark:text-blue-400">
              {Math.round(invoice.recovery_probability * 100)}%
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 dark:text-slate-400">Tone Persona:</span>
            <span className="font-bold text-xs text-slate-800 dark:text-slate-200">{invoice.optimal_tone}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-500 dark:text-slate-400">Confidence Gate:</span>
            <span className="font-bold text-xs text-emerald-600 dark:text-emerald-400">
              {(invoice.confidence_score * 100).toFixed(0)}% (PASSED)
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Column (Promises + Communications), Right Column (Simulator + Payment Plans) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Bitemporal Promises & Communications Audit */}
        <div className="lg:col-span-2 space-y-6">
          {/* Bitemporal Promise-to-Pay Tracker */}
          <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 sm:p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-500" />
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Bitemporal Promise-to-Pay Intelligence
                </h2>
              </div>
              <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                {invoice.promises.length} Commitments Tracked
              </span>
            </div>

            {invoice.promises.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">
                No payment commitments recorded yet. Debtor has not confirmed a promise date.
              </p>
            ) : (
              <div className="space-y-3">
                {invoice.promises.map((p) => (
                  <div
                    key={p.id}
                    className="rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 p-3.5 space-y-2 text-xs shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-bold border ${
                            p.status === 'KEPT'
                              ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30'
                              : p.status === 'BROKEN'
                              ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/30'
                              : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30'
                          }`}
                        >
                          {p.status}
                        </span>
                        <span className="font-black text-slate-900 dark:text-white">
                          ₹{(p.promised_amount_paise / 100).toLocaleString('en-IN')}
                        </span>
                        <span className="text-slate-500 dark:text-slate-400">due by</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">
                          {new Date(p.promise_date).toLocaleDateString('en-IN')}
                        </span>
                      </div>
                      <span className="text-[10px] font-semibold text-slate-500 dark:text-slate-400">
                        Confidence: {(p.confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    {p.raw_quote && (
                      <p className="italic text-slate-600 dark:text-slate-300 text-[11px] bg-white dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                        &quot;{p.raw_quote}&quot;
                      </p>
                    )}

                    {/* Bitemporal Timestamp Display */}
                    <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-500 pt-1 font-mono">
                      <span>Valid at: {new Date(p.valid_at).toLocaleString('en-IN')}</span>
                      <span>·</span>
                      <span>Recorded at: {new Date(p.recorded_at).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Structured Payment Plan (If active) */}
          {invoice.payment_plans.length > 0 && (
            <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 sm:p-6 space-y-4 shadow-sm">
              <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800/80 pb-3">
                <CreditCard className="h-4 w-4 text-blue-500" />
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Structured Payment Plan (Level 4 Negotiation)
                </h2>
              </div>
              {invoice.payment_plans.map((plan) => (
                <div key={plan.id} className="space-y-3">
                  <p className="text-xs text-slate-600 dark:text-slate-300 font-medium">{plan.terms_summary}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                    {plan.installments.map((inst) => (
                      <div
                        key={inst.id}
                        className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 p-3 text-xs space-y-1"
                      >
                        <div className="flex justify-between font-bold">
                          <span className="text-slate-700 dark:text-slate-300">Installment #{inst.installment_number}</span>
                          <span
                            className={
                              inst.status === 'PAID' ? 'text-emerald-600 dark:text-emerald-400 font-black' : 'text-slate-400'
                            }
                          >
                            {inst.status}
                          </span>
                        </div>
                        <div className="text-sm font-black text-slate-900 dark:text-white">
                          ₹{(inst.amount_paise / 100).toLocaleString('en-IN')}
                        </div>
                        <div className="text-[10px] text-slate-500 dark:text-slate-400">
                          Due: {new Date(inst.due_date).toLocaleDateString('en-IN')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Multi-Channel Communications Thread */}
          <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 sm:p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-blue-500" />
                <h2 className="text-sm font-bold text-slate-900 dark:text-white">
                  Communications & Dispute Audit Thread
                </h2>
              </div>
              <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400">
                {invoice.communications.length} Messages Dispatched
              </span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {invoice.communications.map((comm) => (
                <div
                  key={comm.id}
                  className={`rounded-xl border p-4 space-y-2 text-xs ${
                    comm.direction === 'INBOUND'
                      ? 'border-blue-500/30 bg-blue-50/50 dark:bg-blue-950/20 ml-6'
                      : 'border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-900/60 mr-6'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                          comm.direction === 'INBOUND'
                            ? 'bg-blue-500/20 text-blue-700 dark:text-blue-300'
                            : 'bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300'
                        }`}
                      >
                        {comm.direction} · {comm.channel}
                      </span>
                      <span className="font-bold text-slate-800 dark:text-slate-200">{comm.sender}</span>
                    </div>
                    <span className="rounded bg-slate-200/80 dark:bg-slate-800/80 px-1.5 py-0.2 text-[10px] font-semibold text-slate-600 dark:text-slate-400">
                      Tone: {comm.tone}
                    </span>
                  </div>

                  {comm.subject && (
                    <div className="font-bold text-slate-900 dark:text-white text-xs">{comm.subject}</div>
                  )}

                  <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed text-[11px]">
                    {comm.content}
                  </p>

                  <div className="text-[10px] text-slate-400 font-mono">
                    {comm.sent_at ? new Date(comm.sent_at).toLocaleString('en-IN') : 'Scheduled'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Interactive Inbound Debtor Simulator */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-blue-500/30 bg-white dark:bg-[#111622] p-5 sm:p-6 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800/80 pb-3">
              <Bot className="h-4 w-4 text-blue-500" />
              <h2 className="text-sm font-bold text-slate-900 dark:text-white">Debtor Inbound Simulator</h2>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Type or select a debtor reply. The agent will parse intent, extract commitments bitemporally, or freeze
              collection on disputes!
            </p>

            {/* Quick Presets for Demo */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400">Demo Presets:</span>
              <button
                onClick={() =>
                  handleSendInbound('We will definitely transfer ₹1,50,000 by this Friday. Please hold off.')
                }
                className="w-full text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 p-2.5 text-[11px] text-slate-700 dark:text-slate-300 hover:border-blue-500 hover:text-blue-600 dark:hover:text-white transition-colors"
              >
                🤝 <span className="font-bold">Definite Commitment:</span> &quot;We will transfer ₹1,50,000 by this Friday.&quot;
              </button>
              <button
                onClick={() =>
                  handleSendInbound('We might try to pay something next week if our clients clear bills.')
                }
                className="w-full text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 p-2.5 text-[11px] text-slate-700 dark:text-slate-300 hover:border-amber-500 hover:text-amber-600 dark:hover:text-white transition-colors"
              >
                ⚠️ <span className="font-bold">Hedged Promise (Confidence Gate):</span> &quot;We might try to pay...&quot;
              </button>
              <button
                onClick={() =>
                  handleSendInbound('This invoice is wrong! We never received 25 licenses. We dispute this.')
                }
                className="w-full text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 p-2.5 text-[11px] text-slate-700 dark:text-slate-300 hover:border-rose-500 hover:text-rose-600 dark:hover:text-white transition-colors"
              >
                🛑 <span className="font-bold">Invoice Dispute:</span> &quot;This invoice is wrong! We dispute this.&quot;
              </button>
            </div>

            {/* Custom Reply Box */}
            <div className="space-y-2.5 pt-2 border-t border-slate-100 dark:border-slate-800/80">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-500 dark:text-slate-400">Channel:</span>
                <select
                  value={simChannel}
                  onChange={(e) => setSimChannel(e.target.value)}
                  className="rounded-lg bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-2 py-1 text-slate-800 dark:text-slate-200 text-xs focus:outline-none"
                >
                  <option value="EMAIL">Email</option>
                  <option value="WHATSAPP">WhatsApp</option>
                  <option value="SMS">SMS</option>
                </select>
              </div>

              <textarea
                value={simMessage}
                onChange={(e) => setSimMessage(e.target.value)}
                placeholder="Type debtor response..."
                rows={3}
                className="w-full rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-3 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />

              <button
                onClick={() => handleSendInbound()}
                disabled={sendingMessage || !simMessage.trim()}
                className="w-full flex items-center justify-center gap-1.5 rounded-xl bg-blue-600 px-4 py-2.5 text-xs font-bold text-white hover:bg-blue-500 transition-colors disabled:opacity-50 shadow-md shadow-blue-500/20"
              >
                {sendingMessage ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Send className="h-3.5 w-3.5" />
                )}
                <span>{sendingMessage ? 'Agent Reasoning...' : 'Send Inbound Reply'}</span>
              </button>

              {simTrace && (
                <div className="rounded-lg bg-slate-100 dark:bg-slate-900/90 p-2.5 text-[10px] text-slate-600 dark:text-slate-300 font-mono border border-slate-200 dark:border-slate-800 flex items-start gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-blue-500 shrink-0 mt-0.5" />
                  <span>{simTrace}</span>
                </div>
              )}
            </div>
          </div>

          {/* Immutable Audit Log Preview */}
          <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#111622] p-5 sm:p-6 space-y-3 shadow-sm">
            <h2 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Immutable Audit Trail
            </h2>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {invoice.audit_logs.map((log) => (
                <div key={log.id} className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/40 p-2.5 text-[11px] space-y-1">
                  <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
                    <span className="font-bold text-blue-600 dark:text-blue-400">{log.actor}</span>
                    <span className="text-[10px]">{new Date(log.recorded_at).toLocaleTimeString('en-IN')}</span>
                  </div>
                  <p className="text-slate-700 dark:text-slate-300 text-[10px] leading-relaxed">{log.action}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Legal Evidence Bundle Modal */}
      {showEvidenceModal && evidenceBundle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md p-4">
          <div className="max-w-3xl w-full rounded-2xl border border-purple-500/30 bg-white dark:bg-[#111622] p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-purple-500" />
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  Bitemporal Legal Evidence Bundle — #{evidenceBundle.evidence_bundle_id}
                </h2>
              </div>
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="text-slate-400 hover:text-slate-900 dark:hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Certifying Statement */}
            <div className="rounded-xl border border-purple-500/30 bg-purple-50 dark:bg-purple-950/20 p-3.5 text-xs text-purple-900 dark:text-purple-200 leading-relaxed">
              <span className="font-bold">Certifying Statement:</span>
              <p className="mt-1 italic">{evidenceBundle.certifying_statement}</p>
            </div>

            {/* Debtor Profile */}
            <div className="grid grid-cols-2 gap-4 text-xs bg-slate-50 dark:bg-slate-900/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
              <div>
                <span className="text-slate-500 dark:text-slate-400">Debtor:</span>
                <p className="font-bold text-slate-900 dark:text-white">{evidenceBundle.debtor_profile?.name}</p>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400">Total Claim:</span>
                <p className="font-bold text-emerald-600 dark:text-emerald-400">{evidenceBundle.debtor_profile?.total_claim_inr}</p>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400">Unkept Commitments:</span>
                <p className="font-bold text-rose-600 dark:text-rose-400">{evidenceBundle.unkept_commitments_count} broken promises</p>
              </div>
              <div>
                <span className="text-slate-500 dark:text-slate-400">Generated At (UTC):</span>
                <p className="text-slate-700 dark:text-slate-300 font-mono">{evidenceBundle.generated_at_utc}</p>
              </div>
            </div>

            {/* Raw JSON Preview */}
            <div className="space-y-1">
              <span className="text-xs font-bold text-slate-500 dark:text-slate-400">Evidentiary Record (Tamper-Evident Ledger):</span>
              <pre className="rounded-xl bg-slate-950 p-4 text-[10px] text-slate-300 font-mono overflow-x-auto max-h-60 border border-slate-800">
                {JSON.stringify(evidenceBundle, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-200 dark:border-slate-800">
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="rounded-xl bg-slate-200 dark:bg-slate-800 px-4 py-2 text-xs font-bold text-slate-800 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
              >
                Close Package
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
