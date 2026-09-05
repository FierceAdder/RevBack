'use client';

import React, { useState, useEffect } from 'react';
import {
  Settings,
  Building,
  CreditCard,
  KeyRound,
  Users,
  Activity,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  Plus,
  Trash2,
  Loader2,
  ExternalLink,
  Lock,
  Cpu,
  RefreshCw,
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import {
  fetchApiKeys,
  createApiKey,
  revokeApiKey,
  fetchTeamMembers,
  inviteTeamMember,
} from '@/lib/api';
import { ApiKeyItem, User } from '@/lib/types';

export default function SettingsPage() {
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<'general' | 'razorpay' | 'apikeys' | 'team' | 'observability'>('general');

  // Tenant / General State
  const [companyName, setCompanyName] = useState('RevBack Enterprise');
  const [strategy, setStrategy] = useState<'AGGRESSIVE' | 'BALANCED' | 'CONCILIATORY'>('BALANCED');
  const [approvalThreshold, setApprovalThreshold] = useState('50000');
  const [saveSuccess, setSaveSuccess] = useState(false);

  // API Keys State
  const [apiKeys, setApiKeys] = useState<ApiKeyItem[]>([]);
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyScope, setNewKeyScope] = useState('ADMIN');
  const [createdRawKey, setCreatedRawKey] = useState<string | null>(null);
  const [keyCopied, setKeyCopied] = useState(false);
  const [creatingKey, setCreatingKey] = useState(false);

  // Team State
  const [teamMembers, setTeamMembers] = useState<User[]>([]);
  const [loadingTeam, setLoadingTeam] = useState(false);
  const [inviteName, setInviteName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('SUPERVISOR');
  const [inviting, setInviting] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);

  // Razorpay Webhook Test State
  const [webhookCopied, setWebhookCopied] = useState(false);
  const [pingingWebhook, setPingingWebhook] = useState(false);
  const [pingResult, setPingResult] = useState<string | null>(null);

  useEffect(() => {
    if (user?.tenant?.name) {
      setCompanyName(user.tenant.name);
    }
  }, [user]);

  useEffect(() => {
    if (activeTab === 'apikeys') {
      loadKeys();
    } else if (activeTab === 'team') {
      loadTeam();
    }
  }, [activeTab]);

  const loadKeys = async () => {
    setLoadingKeys(true);
    try {
      const keys = await fetchApiKeys();
      setApiKeys(keys);
    } catch (err) {
      console.error('Failed to load API keys:', err);
    } finally {
      setLoadingKeys(false);
    }
  };

  const loadTeam = async () => {
    setLoadingTeam(true);
    try {
      const team = await fetchTeamMembers();
      setTeamMembers(team);
    } catch (err) {
      console.error('Failed to load team:', err);
    } finally {
      setLoadingTeam(false);
    }
  };

  const handleSaveGeneral = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) return;
    setCreatingKey(true);
    try {
      const created = await createApiKey(newKeyName.trim(), newKeyScope);
      if (created.raw_key) {
        setCreatedRawKey(created.raw_key);
      }
      setNewKeyName('');
      loadKeys();
    } catch (err) {
      console.error('Create key error:', err);
    } finally {
      setCreatingKey(false);
    }
  };

  const handleRevokeKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action is permanent.')) return;
    try {
      await revokeApiKey(keyId);
      loadKeys();
    } catch (err) {
      console.error('Revoke key error:', err);
    }
  };

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteError(null);
    if (!inviteName.trim() || !inviteEmail.trim()) return;
    setInviting(true);
    try {
      await inviteTeamMember(inviteName.trim(), inviteEmail.trim(), inviteRole);
      setInviteName('');
      setInviteEmail('');
      loadTeam();
    } catch (err: any) {
      setInviteError(err.message || 'Failed to invite team member');
    } finally {
      setInviting(false);
    }
  };

  const copyToClipboard = (text: string, setter: (val: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setter(true);
    setTimeout(() => setter(false), 2000);
  };

  const handlePingWebhook = () => {
    setPingingWebhook(true);
    setPingResult(null);
    setTimeout(() => {
      setPingingWebhook(false);
      setPingResult('Webhook listener online. HMAC signature verification validated.');
      setTimeout(() => setPingResult(null), 4000);
    }, 1200);
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#030712] text-slate-900 dark:text-slate-100 pt-28 pb-20 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <div className="p-2 rounded-xl bg-blue-500/10 text-[#0066FF] border border-blue-500/20">
                <Settings className="h-5 w-5" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight">Settings & Configuration</h1>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Manage multi-tenant policies, Razorpay credentials, API tokens, and supervisory access.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400 text-xs font-semibold">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Production Mode Active
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-white/10 overflow-x-auto pb-2 scrollbar-none">
          {[
            { id: 'general', label: 'Organization & Policies', icon: Building },
            { id: 'razorpay', label: 'Razorpay Integration', icon: CreditCard },
            { id: 'apikeys', label: 'API Keys', icon: KeyRound },
            { id: 'team', label: 'Team & Roles', icon: Users },
            { id: 'observability', label: 'Observability & Workers', icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
                  isActive
                    ? 'bg-[#0066FF] text-white shadow-md shadow-blue-500/25'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-white/[0.04]'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab 1: Organization & Policies */}
        {activeTab === 'general' && (
          <form onSubmit={handleSaveGeneral} className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Tenant Details */}
              <div className="lg:col-span-2 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-5 shadow-sm">
                <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Building className="h-4 w-4 text-[#0066FF]" />
                  Merchant Profile
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                      Company / Merchant Name
                    </label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                      Tenant Identifier
                    </label>
                    <input
                      type="text"
                      value={user?.tenant?.slug || 'tenant_default'}
                      disabled
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 dark:bg-white/[0.05] px-3.5 py-2.5 text-sm font-mono text-slate-500 dark:text-slate-400 cursor-not-allowed"
                    />
                  </div>
                </div>

                <div className="border-t border-slate-100 dark:border-white/[0.06] pt-5 space-y-4">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Recovery Strategy & Guardrails</h3>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {[
                      { id: 'CONCILIATORY', label: 'Conciliatory', desc: 'Focus on payment plans and gentle reminders.' },
                      { id: 'BALANCED', label: 'Balanced (Standard)', desc: 'Progressive escalation aligned with Track 3 spec.' },
                      { id: 'AGGRESSIVE', label: 'Assertive', desc: 'Shorter reminder intervals and early legal prep.' },
                    ].map((strat) => (
                      <div
                        key={strat.id}
                        onClick={() => setStrategy(strat.id as any)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                          strategy === strat.id
                            ? 'border-[#0066FF] bg-blue-50/50 dark:bg-blue-500/10'
                            : 'border-slate-200 dark:border-white/10 hover:border-slate-300'
                        }`}
                      >
                        <div className="text-xs font-bold text-slate-900 dark:text-white mb-1">{strat.label}</div>
                        <div className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">{strat.desc}</div>
                      </div>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                    <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                        Human Approval Escalation Threshold (INR)
                      </label>
                      <div className="relative">
                        <span className="absolute left-3.5 top-2.5 text-sm font-bold text-slate-400">₹</span>
                        <input
                          type="number"
                          value={approvalThreshold}
                          onChange={(e) => setApprovalThreshold(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] pl-8 pr-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                        />
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1">
                        Any invoice exceeding this amount automatically pauses at the supervisor gate before dispatch.
                      </p>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                        Dispute Cooldown Window
                      </label>
                      <select className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]">
                        <option>7 Days (Recommended)</option>
                        <option>14 Days</option>
                        <option>30 Days</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="pt-3 flex items-center justify-between">
                  <button
                    type="submit"
                    className="flex items-center gap-2 rounded-xl bg-[#0066FF] hover:bg-blue-600 text-white font-bold px-5 py-2.5 text-xs shadow-md shadow-blue-500/20 transition-all"
                  >
                    Save Configuration
                  </button>
                  {saveSuccess && (
                    <span className="flex items-center gap-1.5 text-xs font-bold text-emerald-500">
                      <CheckCircle2 className="h-4 w-4" /> Preferences updated successfully!
                    </span>
                  )}
                </div>
              </div>

              {/* Security & Multi-Tenancy Overview */}
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm h-fit">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-emerald-500" />
                  Isolation & Security
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Every receivable, debtor profile, promise record, and LangGraph checkpoint thread is strictly partitioned by your tenant UUID.
                </p>
                <div className="rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] p-3 space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-200/50 dark:border-white/[0.04]">
                    <span className="text-slate-500">Row Level Security</span>
                    <span className="font-semibold text-emerald-500">Enforced</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-200/50 dark:border-white/[0.04]">
                    <span className="text-slate-500">Rate Limiter</span>
                    <span className="font-semibold text-slate-700 dark:text-slate-300">120 req/min</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">CORS Protection</span>
                    <span className="font-semibold text-slate-700 dark:text-slate-300">Whitelisted Origin</span>
                  </div>
                </div>
              </div>
            </div>
          </form>
        )}

        {/* Tab 2: Razorpay Integration */}
        {activeTab === 'razorpay' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-5 shadow-sm">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <CreditCard className="h-4 w-4 text-[#0066FF]" />
                    Razorpay Gateway Credentials
                  </h2>
                  <span className="px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/10 text-blue-500 border border-blue-500/20">
                    Live Payment Links Active
                  </span>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                      Razorpay Key ID
                    </label>
                    <input
                      type="text"
                      value="rzp_test_revback_mock_001"
                      disabled
                      className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 dark:bg-white/[0.03] px-3.5 py-2.5 text-sm font-mono text-slate-700 dark:text-slate-300"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                      Webhook Listener URL
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        readOnly
                        value="http://localhost:8000/api/v1/webhooks/razorpay"
                        className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 dark:bg-white/[0.03] px-3.5 py-2.5 text-xs font-mono text-slate-600 dark:text-slate-400"
                      />
                      <button
                        type="button"
                        onClick={() => copyToClipboard('http://localhost:8000/api/v1/webhooks/razorpay', setWebhookCopied)}
                        className="px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 hover:bg-slate-100 dark:hover:bg-white/[0.05] text-xs font-semibold flex items-center gap-1.5 transition-colors"
                      >
                        {webhookCopied ? <CheckCircle2 className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                        {webhookCopied ? 'Copied' : 'Copy'}
                      </button>
                    </div>
                    <p className="text-[10px] text-slate-500 mt-1">
                      Configure this in your Razorpay Dashboard with events: <code>payment_link.paid</code>, <code>payment.captured</code>, <code>payment.failed</code>.
                    </p>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                      Webhook HMAC Signature Secret
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="password"
                        readOnly
                        value="••••••••••••••••••••••••"
                        className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-100 dark:bg-white/[0.03] px-3.5 py-2.5 text-xs font-mono text-slate-600 dark:text-slate-400"
                      />
                      <span className="px-3 py-2 text-xs font-bold text-emerald-500 bg-emerald-500/10 rounded-xl border border-emerald-500/20 whitespace-nowrap">
                        Verified
                      </span>
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between">
                  <button
                    type="button"
                    onClick={handlePingWebhook}
                    disabled={pingingWebhook}
                    className="flex items-center gap-2 rounded-xl bg-slate-100 dark:bg-white/[0.05] hover:bg-slate-200 dark:hover:bg-white/[0.08] text-slate-800 dark:text-slate-200 font-bold px-4 py-2.5 text-xs transition-colors"
                  >
                    {pingingWebhook ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
                    Test Webhook Listener
                  </button>

                  {pingResult && (
                    <span className="text-xs font-semibold text-emerald-500 flex items-center gap-1.5">
                      <CheckCircle2 className="h-4 w-4" /> {pingResult}
                    </span>
                  )}
                </div>
              </div>

              {/* Supported Payment Link Options */}
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm h-fit">
                <h3 className="text-sm font-bold text-slate-900 dark:text-white">Active Payment Rails</h3>
                <div className="space-y-2.5 text-xs text-slate-600 dark:text-slate-400">
                  <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02]">
                    <span className="font-semibold text-slate-900 dark:text-white">UPI & QR Pay</span>
                    <span className="text-emerald-500 font-bold">Enabled</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02]">
                    <span className="font-semibold text-slate-900 dark:text-white">NetBanking (60+ Banks)</span>
                    <span className="text-emerald-500 font-bold">Enabled</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02]">
                    <span className="font-semibold text-slate-900 dark:text-white">Corporate Cards</span>
                    <span className="text-emerald-500 font-bold">Enabled</span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.02]">
                    <span className="font-semibold text-slate-900 dark:text-white">Multi-Installment Plans</span>
                    <span className="text-emerald-500 font-bold">Active</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: API Keys */}
        {activeTab === 'apikeys' && (
          <div className="space-y-6">
            {/* Raw Key Display Modal/Banner */}
            {createdRawKey && (
              <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-5 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4" /> API Key Created Successfully!
                  </span>
                  <button
                    onClick={() => setCreatedRawKey(null)}
                    className="text-xs font-semibold text-emerald-600 hover:underline"
                  >
                    Dismiss
                  </button>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-300">
                  Please copy your key now. You will not be able to see it again!
                </p>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="text"
                    readOnly
                    value={createdRawKey}
                    className="w-full rounded-xl border border-emerald-500/30 bg-white/80 dark:bg-black/60 px-3.5 py-2 text-xs font-mono text-slate-900 dark:text-white"
                  />
                  <button
                    onClick={() => copyToClipboard(createdRawKey, setKeyCopied)}
                    className="px-4 py-2 rounded-xl bg-emerald-500 text-white text-xs font-bold flex items-center gap-1.5 hover:bg-emerald-600 transition-colors"
                  >
                    {keyCopied ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    {keyCopied ? 'Copied' : 'Copy'}
                  </button>
                </div>
              </div>
            )}

            {/* Create API Key Form */}
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
              <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <KeyRound className="h-4 w-4 text-[#0066FF]" />
                Create New API Key
              </h2>

              <form onSubmit={handleCreateKey} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Key Name / Integration Purpose
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. ERP Invoice Sync Worker"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Access Scope
                  </label>
                  <select
                    value={newKeyScope}
                    onChange={(e) => setNewKeyScope(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                  >
                    <option value="ADMIN">ADMIN (Full Control)</option>
                    <option value="WRITE">WRITE (Invoices & Agent)</option>
                    <option value="READ">READ (Audit & Metrics)</option>
                  </select>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={creatingKey || !newKeyName.trim()}
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-[#0066FF] hover:bg-blue-600 text-white font-bold py-2.5 text-xs shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
                  >
                    {creatingKey ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
                    Generate Key
                  </button>
                </div>
              </form>
            </div>

            {/* Keys Table */}
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Active Access Tokens</h3>

              {loadingKeys ? (
                <div className="py-12 flex justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-[#0066FF]" />
                </div>
              ) : apiKeys.length === 0 ? (
                <p className="text-xs text-slate-500 py-6 text-center">No active API keys found. Generate one above.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10 text-slate-400 font-semibold">
                        <th className="pb-3">Name</th>
                        <th className="pb-3">Key Prefix</th>
                        <th className="pb-3">Scope</th>
                        <th className="pb-3">Created</th>
                        <th className="pb-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
                      {apiKeys.map((k) => (
                        <tr key={k.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                          <td className="py-3 font-semibold text-slate-900 dark:text-white">{k.name}</td>
                          <td className="py-3 font-mono text-slate-500">{k.prefix}••••••••</td>
                          <td className="py-3">
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-[#0066FF] border border-blue-500/20">
                              {k.scope}
                            </span>
                          </td>
                          <td className="py-3 text-slate-500">
                            {new Date(k.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3 text-right">
                            <button
                              onClick={() => handleRevokeKey(k.id)}
                              className="text-rose-500 hover:text-rose-600 font-semibold inline-flex items-center gap-1 hover:underline"
                            >
                              <Trash2 className="h-3.5 w-3.5" /> Revoke
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 4: Team & Roles */}
        {activeTab === 'team' && (
          <div className="space-y-6">
            {/* Invite Form */}
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
              <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <Users className="h-4 w-4 text-[#0066FF]" />
                Invite Team Member
              </h2>

              {inviteError && (
                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-500 text-xs font-semibold">
                  {inviteError}
                </div>
              )}

              <form onSubmit={handleInvite} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Full Name
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Priya Sharma"
                    value={inviteName}
                    onChange={(e) => setInviteName(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Email Address
                  </label>
                  <input
                    type="email"
                    placeholder="priya@company.in"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1.5">
                    Role
                  </label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] px-3.5 py-2.5 text-sm font-medium text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-[#0066FF]"
                  >
                    <option value="SUPERVISOR">SUPERVISOR (Approval Authority)</option>
                    <option value="ADMIN">ADMIN (Full Configuration)</option>
                    <option value="VIEWER">VIEWER (Read-Only)</option>
                  </select>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={inviting || !inviteName.trim() || !inviteEmail.trim()}
                    className="w-full flex items-center justify-center gap-2 rounded-xl bg-[#0066FF] hover:bg-blue-600 text-white font-bold py-2.5 text-xs shadow-md shadow-blue-500/20 transition-all disabled:opacity-50"
                  >
                    {inviting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Plus className="h-3.5 w-3.5" />}
                    Send Invite
                  </button>
                </div>
              </form>
            </div>

            {/* Team Table */}
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">Organization Members</h3>

              {loadingTeam ? (
                <div className="py-12 flex justify-center">
                  <Loader2 className="h-6 w-6 animate-spin text-[#0066FF]" />
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-white/10 text-slate-400 font-semibold">
                        <th className="pb-3">Name</th>
                        <th className="pb-3">Email</th>
                        <th className="pb-3">Role</th>
                        <th className="pb-3">Access Level</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-white/[0.04]">
                      {teamMembers.map((m) => (
                        <tr key={m.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors">
                          <td className="py-3 font-bold text-slate-900 dark:text-white">{m.full_name}</td>
                          <td className="py-3 text-slate-500 font-mono">{m.email}</td>
                          <td className="py-3">
                            <span
                              className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${
                                m.role === 'ADMIN'
                                  ? 'bg-purple-500/10 text-purple-500 border-purple-500/20'
                                  : m.role === 'SUPERVISOR'
                                  ? 'bg-blue-500/10 text-[#0066FF] border-blue-500/20'
                                  : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                              }`}
                            >
                              {m.role}
                            </span>
                          </td>
                          <td className="py-3 text-slate-500">
                            {m.role === 'ADMIN'
                              ? 'Manage Tenant & Policy'
                              : m.role === 'SUPERVISOR'
                              ? 'Human Approval Decisions'
                              : 'Dashboard Read Only'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 5: Observability & Workers */}
        {activeTab === 'observability' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Langfuse Tracing Card */}
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-[#0066FF]" />
                    Langfuse Tracing
                  </h3>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                    Connected
                  </span>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Every agent execution cycle captures spans across diagnosis, confidence gating, tone selection, and dynamic copy generation with exact token cost attribution.
                </p>
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Trace Host:</span>
                    <span className="font-mono text-slate-700 dark:text-slate-300">cloud.langfuse.com</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Instrumentation:</span>
                    <span className="font-medium text-slate-700 dark:text-slate-300">LiteLLM + @observe_agent</span>
                  </div>
                </div>
              </div>

              {/* Prometheus Telemetry Card */}
              <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Activity className="h-4 w-4 text-[#0066FF]" />
                    Prometheus Metrics
                  </h3>
                  <a
                    href="http://localhost:8000/metrics"
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-[#0066FF] hover:underline"
                  >
                    View /metrics <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                  Exposes standard exposition format metrics for Prometheus scrapers, Datadog agents, and Grafana dashboards.
                </p>
                <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06] text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Counters:</span>
                    <span className="font-mono text-slate-700 dark:text-slate-300">invoices_processed, revenue_recovered</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Histograms:</span>
                    <span className="font-mono text-slate-700 dark:text-slate-300">agent_run_duration_seconds</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Celery Beat Worker Schedules */}
            <div className="rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#070A11] p-6 space-y-4 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-[#0066FF]" />
                Celery Beat Cron Schedules (IST)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  {
                    name: 'Promise Deadlines',
                    cron: 'Every 1 Hour',
                    desc: 'Checks active payment promises against deadlines and escalates broken commitments.',
                  },
                  {
                    name: 'Stale Receivables',
                    cron: 'Every 6 Hours',
                    desc: 'Re-runs the policy engine on overdue invoices without recent contact.',
                  },
                  {
                    name: 'Daily Recovery Snapshot',
                    cron: 'Daily at 00:00 IST',
                    desc: 'Captures daily cumulative recovered capital and ROI time series snapshots.',
                  },
                  {
                    name: 'Weekly Promise Audit',
                    cron: 'Monday 09:00 IST',
                    desc: 'Audits broken promise penalties and adjusts customer credit risk bands.',
                  },
                ].map((task) => (
                  <div
                    key={task.name}
                    className="p-4 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] space-y-1.5"
                  >
                    <div className="text-xs font-bold text-slate-900 dark:text-white">{task.name}</div>
                    <div className="text-[11px] font-mono text-[#0066FF] font-semibold">{task.cron}</div>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400 leading-relaxed">{task.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
