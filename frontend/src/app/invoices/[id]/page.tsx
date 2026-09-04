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
} from 'lucide-react';
import {
  fetchInvoiceDetail,
  processInvoiceAgent,
  sendInboundMessage,
  fetchEvidenceBundle,
} from '@/lib/api';
import { InvoiceDetail } from '@/lib/types';

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
        `Agent executed: Level ${res.current_level} via ${res.selected_channel} with ${res.selected_tone} tone.`
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
    try {
      const res = await sendInboundMessage(invoiceId, text, simChannel);
      setActionAlert(res.agent_action_taken);
      setSimMessage('');
      await loadDetail();
    } catch (err) {
      console.error('Send inbound error:', err);
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
      <div className="mx-auto max-w-7xl px-4 py-16 text-center text-slate-400">
        <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-blue-400" />
        <p className="text-xs">Loading bitemporal receivable data...</p>
      </div>
    );
  }

  if (!invoice) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-16 text-center text-slate-400">
        <AlertTriangle className="h-8 w-8 text-amber-400 mx-auto mb-2" />
        <h2 className="text-base font-semibold text-white">Invoice Not Found</h2>
        <p className="text-xs mt-1">Receivable #{invoiceId} could not be located in database.</p>
        <Link href="/invoices" className="inline-block mt-4 text-xs font-semibold text-blue-400 hover:underline">
          Return to Ledger
        </Link>
      </div>
    );
  }

  const customer = invoice.customer;

  return (
    <div className="mx-auto max-w-7xl px-4 pt-6 sm:px-6 lg:px-8 space-y-6">
      {/* Top Breadcrumb & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <Link
            href="/invoices"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">{invoice.invoice_number}</h1>
              <span
                className={`rounded px-2 py-0.5 text-[11px] font-semibold border ${
                  invoice.status === 'PAID'
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                    : invoice.status === 'DISPUTED'
                    ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                    : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                }`}
              >
                {invoice.status}
              </span>
              <span className="rounded bg-blue-500/10 text-blue-400 px-2 py-0.5 text-[11px] font-semibold border border-blue-500/20">
                Level {invoice.current_level} / 7
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{customer?.name} · Claim registered via RevBack</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleOpenEvidence}
            className="flex items-center gap-1.5 rounded-lg border border-purple-500/30 bg-purple-500/10 px-3 py-1.5 text-xs font-semibold text-purple-300 hover:bg-purple-500/20 transition-colors"
          >
            <Scale className="h-3.5 w-3.5" />
            <span>Evidence Bundle</span>
          </button>

          <button
            onClick={handleProcessAgent}
            disabled={processing}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-500 transition-colors disabled:opacity-50"
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
        <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 p-3 text-xs text-blue-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-blue-400 shrink-0" />
            <span>{actionAlert}</span>
          </div>
          <button onClick={() => setActionAlert(null)} className="text-blue-300 hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* Header Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Claim Financials */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 space-y-3">
          <span className="text-xs font-medium text-slate-400">Total Claim Exposure</span>
          <div className="text-2xl font-bold text-white">
            ₹{(invoice.amount_paise / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
          </div>
          <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/80 text-slate-400">
            <span>Recovered:</span>
            <span className="font-semibold text-emerald-400">
              ₹{(invoice.amount_paid_paise / 100).toLocaleString('en-IN')}
            </span>
          </div>
          {invoice.active_payment_link_url && (
            <a
              href={invoice.active_payment_link_url}
              target="_blank"
              rel="noreferrer"
              className="mt-2 flex items-center justify-between rounded-lg bg-blue-600/10 border border-blue-500/20 px-3 py-2 text-xs font-semibold text-blue-300 hover:bg-blue-600/20 transition-colors"
            >
              <div className="flex items-center gap-2">
                <CreditCard className="h-3.5 w-3.5 text-blue-400" />
                <span>Razorpay Payment Link</span>
              </div>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          )}
        </div>

        {/* Debtor Profile */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 space-y-2">
          <span className="text-xs font-medium text-slate-400">Debtor Profile</span>
          <div className="font-semibold text-white text-sm">{customer?.name}</div>
          <div className="text-xs text-slate-400 space-y-1">
            <div className="flex justify-between">
              <span>Email:</span>
              <span className="text-slate-200">{customer?.email}</span>
            </div>
            <div className="flex justify-between">
              <span>Tier:</span>
              <span className="text-slate-200 font-medium">
                {customer?.relationship_tier?.replace('_', ' ')}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Credit Score:</span>
              <span className="text-slate-200 font-medium">{customer?.credit_score}</span>
            </div>
          </div>
        </div>

        {/* AI Diagnosis & Strategy */}
        <div className="rounded-xl border border-slate-800 bg-[#111622] p-4 space-y-2">
          <span className="text-xs font-medium text-slate-400">AI Risk & Strategy</span>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Risk Score:</span>
            <span
              className={`font-bold text-xs px-2 py-0.5 rounded border ${
                invoice.risk_score >= 70
                  ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                  : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
              }`}
            >
              {invoice.risk_score.toFixed(0)} / 100
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">P(Recovery):</span>
            <span className="font-bold text-xs text-blue-400">
              {Math.round(invoice.recovery_probability * 100)}%
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Tone Persona:</span>
            <span className="font-semibold text-xs text-slate-200">{invoice.optimal_tone}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">Confidence Gate:</span>
            <span className="font-semibold text-xs text-emerald-400">
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
          <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-400" />
                <h2 className="text-sm font-semibold text-white">Bitemporal Promise-to-Pay Intelligence</h2>
              </div>
              <span className="text-[11px] text-slate-400">
                {invoice.promises.length} Commitments Tracked
              </span>
            </div>

            {invoice.promises.length === 0 ? (
              <p className="text-xs text-slate-500 py-3 text-center">
                No payment commitments recorded yet. Debtor has not confirmed a promise date.
              </p>
            ) : (
              <div className="space-y-3">
                {invoice.promises.map((p) => (
                  <div
                    key={p.id}
                    className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={`rounded px-1.5 py-0.5 text-[10px] font-bold border ${
                            p.status === 'KEPT'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : p.status === 'BROKEN'
                              ? 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                              : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                          }`}
                        >
                          {p.status}
                        </span>
                        <span className="font-semibold text-white">
                          ₹{(p.promised_amount_paise / 100).toLocaleString('en-IN')}
                        </span>
                        <span className="text-slate-400">due by</span>
                        <span className="font-medium text-slate-200">
                          {new Date(p.promise_date).toLocaleDateString('en-IN')}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        Confidence: {(p.confidence * 100).toFixed(0)}%
                      </span>
                    </div>

                    {p.raw_quote && (
                      <p className="italic text-slate-400 text-[11px] bg-slate-950/60 p-2 rounded border border-slate-850">
                        &quot;{p.raw_quote}&quot;
                      </p>
                    )}

                    {/* Bitemporal Timestamp Display */}
                    <div className="flex items-center gap-4 text-[10px] text-slate-500 pt-1">
                      <span>Valid at (Debtor Commitment): {new Date(p.valid_at).toLocaleString('en-IN')}</span>
                      <span>·</span>
                      <span>Recorded at (System Ledger): {new Date(p.recorded_at).toLocaleString('en-IN')}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Structured Payment Plan (If active) */}
          {invoice.payment_plans.length > 0 && (
            <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-4">
              <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
                <CreditCard className="h-4 w-4 text-blue-400" />
                <h2 className="text-sm font-semibold text-white">Structured Payment Plan (Level 4 Negotiation)</h2>
              </div>
              {invoice.payment_plans.map((plan) => (
                <div key={plan.id} className="space-y-3">
                  <p className="text-xs text-slate-300">{plan.terms_summary}</p>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    {plan.installments.map((inst) => (
                      <div
                        key={inst.id}
                        className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs space-y-1"
                      >
                        <div className="flex justify-between font-semibold">
                          <span>Installment #{inst.installment_number}</span>
                          <span
                            className={
                              inst.status === 'PAID' ? 'text-emerald-400 font-bold' : 'text-slate-400'
                            }
                          >
                            {inst.status}
                          </span>
                        </div>
                        <div className="text-sm font-bold text-white">
                          ₹{(inst.amount_paise / 100).toLocaleString('en-IN')}
                        </div>
                        <div className="text-[10px] text-slate-400">
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
          <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-blue-400" />
                <h2 className="text-sm font-semibold text-white">Communications & Dispute Audit Thread</h2>
              </div>
              <span className="text-[11px] text-slate-400">
                {invoice.communications.length} Messages Dispatched
              </span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {invoice.communications.map((comm) => (
                <div
                  key={comm.id}
                  className={`rounded-lg border p-3.5 space-y-2 text-xs ${
                    comm.direction === 'INBOUND'
                      ? 'border-blue-500/30 bg-blue-950/20 ml-6'
                      : 'border-slate-800 bg-slate-900/60 mr-6'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                          comm.direction === 'INBOUND'
                            ? 'bg-blue-500/20 text-blue-300'
                            : 'bg-slate-800 text-slate-300'
                        }`}
                      >
                        {comm.direction} · {comm.channel}
                      </span>
                      <span className="font-medium text-slate-200">{comm.sender}</span>
                    </div>
                    <span className="rounded bg-slate-800/80 px-1.5 py-0.2 text-[10px] text-slate-400">
                      Tone: {comm.tone}
                    </span>
                  </div>

                  {comm.subject && (
                    <div className="font-semibold text-slate-100 text-xs">{comm.subject}</div>
                  )}

                  <p className="text-slate-300 whitespace-pre-wrap leading-relaxed text-[11px]">
                    {comm.content}
                  </p>

                  <div className="text-[10px] text-slate-500">
                    {comm.sent_at ? new Date(comm.sent_at).toLocaleString('en-IN') : 'Scheduled'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Col: Interactive Inbound Debtor Simulator */}
        <div className="space-y-6">
          <div className="rounded-xl border border-blue-500/30 bg-[#111622] p-5 space-y-4 shadow-sm">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <Sparkles className="h-4 w-4 text-blue-400" />
              <h2 className="text-sm font-semibold text-white">Debtor Inbound Simulator</h2>
            </div>
            <p className="text-xs text-slate-400">
              Type or select a debtor reply. The agent will parse intent, extract commitments bitemporally, or freeze
              collection on disputes!
            </p>

            {/* Quick Presets for Demo */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-slate-400">Demo Presets:</span>
              <button
                onClick={() =>
                  handleSendInbound('We will definitely transfer ₹1,50,000 by this Friday. Please hold off.')
                }
                className="w-full text-left rounded-md border border-slate-800 bg-slate-900 p-2 text-[11px] text-slate-300 hover:border-blue-500 hover:text-white transition-colors"
              >
                🤝 <span className="font-medium">Definite Promise:</span> &quot;We will transfer ₹1,50,000 by this Friday.&quot;
              </button>
              <button
                onClick={() =>
                  handleSendInbound('We might try to pay something next week if our clients clear bills.')
                }
                className="w-full text-left rounded-md border border-slate-800 bg-slate-900 p-2 text-[11px] text-slate-300 hover:border-amber-500 hover:text-white transition-colors"
              >
                ⚠️ <span className="font-medium">Hedged Promise (Confidence Gate):</span> &quot;We might try to pay...&quot;
              </button>
              <button
                onClick={() =>
                  handleSendInbound('This invoice is wrong! We never received 25 licenses. We dispute this.')
                }
                className="w-full text-left rounded-md border border-slate-800 bg-slate-900 p-2 text-[11px] text-slate-300 hover:border-rose-500 hover:text-white transition-colors"
              >
                🛑 <span className="font-medium">Invoice Dispute:</span> &quot;This invoice is wrong! We dispute this.&quot;
              </button>
            </div>

            {/* Custom Reply Box */}
            <div className="space-y-2 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Channel:</span>
                <select
                  value={simChannel}
                  onChange={(e) => setSimChannel(e.target.value)}
                  className="rounded bg-slate-900 border border-slate-800 px-2 py-1 text-slate-200 text-xs focus:outline-none"
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
                className="w-full rounded-lg bg-slate-900 border border-slate-800 p-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />

              <button
                onClick={() => handleSendInbound()}
                disabled={sendingMessage || !simMessage.trim()}
                className="w-full flex items-center justify-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-xs font-semibold text-white hover:bg-blue-500 transition-colors disabled:opacity-50"
              >
                {sendingMessage ? (
                  <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Send className="h-3.5 w-3.5" />
                )}
                <span>{sendingMessage ? 'Processing Inbound...' : 'Send Inbound Reply'}</span>
              </button>
            </div>
          </div>

          {/* Immutable Audit Log Preview */}
          <div className="rounded-xl border border-slate-800 bg-[#111622] p-5 space-y-3">
            <h2 className="text-xs font-semibold text-white uppercase tracking-wider">
              Immutable Audit Trail
            </h2>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              {invoice.audit_logs.map((log) => (
                <div key={log.id} className="rounded border border-slate-850 bg-slate-900/40 p-2 text-[11px] space-y-1">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="font-semibold text-blue-400">{log.actor}</span>
                    <span className="text-[10px]">{new Date(log.recorded_at).toLocaleTimeString('en-IN')}</span>
                  </div>
                  <p className="text-slate-300 text-[10px]">{log.action}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Legal Evidence Bundle Modal */}
      {showEvidenceModal && evidenceBundle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="max-w-3xl w-full rounded-xl border border-purple-500/30 bg-[#111622] p-6 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Scale className="h-5 w-5 text-purple-400" />
                <h2 className="text-base font-bold text-white">
                  Bitemporal Legal Evidence Bundle — #{evidenceBundle.evidence_bundle_id}
                </h2>
              </div>
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Certifying Statement */}
            <div className="rounded-lg border border-purple-500/30 bg-purple-950/20 p-3 text-xs text-purple-200">
              <span className="font-semibold">Certifying Statement:</span>
              <p className="mt-1 italic">{evidenceBundle.certifying_statement}</p>
            </div>

            {/* Debtor Profile */}
            <div className="grid grid-cols-2 gap-4 text-xs bg-slate-900/60 p-3 rounded-lg border border-slate-800">
              <div>
                <span className="text-slate-400">Debtor:</span>
                <p className="font-semibold text-white">{evidenceBundle.debtor_profile?.name}</p>
              </div>
              <div>
                <span className="text-slate-400">Total Claim:</span>
                <p className="font-semibold text-emerald-400">{evidenceBundle.debtor_profile?.total_claim_inr}</p>
              </div>
              <div>
                <span className="text-slate-400">Unkept Commitments:</span>
                <p className="font-semibold text-rose-400">{evidenceBundle.unkept_commitments_count} broken promises</p>
              </div>
              <div>
                <span className="text-slate-400">Generated At (UTC):</span>
                <p className="text-slate-300">{evidenceBundle.generated_at_utc}</p>
              </div>
            </div>

            {/* Raw JSON Preview */}
            <div className="space-y-1">
              <span className="text-xs font-semibold text-slate-400">Evidentiary Record (Tamper-Evident):</span>
              <pre className="rounded-lg bg-slate-950 p-3 text-[10px] text-slate-300 font-mono overflow-x-auto max-h-60 border border-slate-800">
                {JSON.stringify(evidenceBundle, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowEvidenceModal(false)}
                className="rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700"
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
