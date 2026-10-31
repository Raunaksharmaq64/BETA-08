"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";

function OutreachDraftEditorContent() {
  const { opportunityId } = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const draftIdParam = searchParams.get("draftId");

  const [draft, setDraft] = useState<any>(null);
  const [recipient, setRecipient] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [approving, setApproving] = useState(false);
  const [sending, setSending] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Pitch generation options
  const [tone, setTone] = useState("professional");
  const [service, setService] = useState("Modern Responsive Web Rebuild & SEO");
  const [minWords, setMinWords] = useState(150);

  // Approval Modal State
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalConfirmed, setApprovalConfirmed] = useState(false);

  useEffect(() => {
    const fetchOrCreateDraft = async () => {
      setLoading(true);
      setError(null);
      try {
        if (draftIdParam) {
          const oppRes = await apiClient.get<any>(`/freelance/${opportunityId}`);
          const found = oppRes.data?.drafts?.find((d: any) => d.id === draftIdParam);
          if (found) {
            setDraft(found);
            setRecipient(found.recipient_contact || "");
            setSubject(found.subject || "");
            setBody(found.message_body || "");
            setLoading(false);
            return;
          }
        }
        // Otherwise generate a new draft
        const genRes = await apiClient.post<any>(
          `/freelance/${opportunityId}/draft?channel=EMAIL&tone=${tone}&service=${encodeURIComponent(service)}&min_words=${minWords}`,
          {}
        );
        const newDraft = genRes.data;
        setDraft(newDraft);
        setRecipient(newDraft.recipient_contact || "");
        setSubject(newDraft.subject || "");
        setBody(newDraft.message_body || "");
      } catch (err: any) {
        setError(err?.message || "Failed to load outreach draft.");
      } finally {
        setLoading(false);
      }
    };
    fetchOrCreateDraft();
  }, [opportunityId, draftIdParam]);

  const handleRegeneratePitch = async () => {
    setRegenerating(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await apiClient.post<any>(
        `/freelance/${opportunityId}/draft?channel=EMAIL&tone=${tone}&service=${encodeURIComponent(service)}&min_words=${minWords}`,
        {}
      );
      const newDraft = res.data;
      setDraft(newDraft);
      setRecipient(newDraft.recipient_contact || "");
      setSubject(newDraft.subject || "");
      setBody(newDraft.message_body || "");
      setSuccessMessage("✨ AI outreach pitch regenerated with selected tone and service focus!");
    } catch (err: any) {
      setError(err?.message || "Failed to regenerate outreach draft.");
    } finally {
      setRegenerating(false);
    }
  };

  const handleSaveEdits = async () => {
    if (!draft) return;
    setSaving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await apiClient.put<any>(`/freelance/drafts/${draft.id}`, {
        recipient_contact: recipient,
        subject: subject,
        message_body: body,
      });
      setDraft(res.data);
      setSuccessMessage("Changes saved. Any prior approval has been safely reset to PENDING_REVIEW.");
    } catch (err: any) {
      setError(err?.message || "Failed to save draft edits.");
    } finally {
      setSaving(false);
    }
  };

  const handleApprove = async () => {
    if (!draft) return;
    setApproving(true);
    setError(null);
    setSuccessMessage(null);
    try {
      const res = await apiClient.post<any>(`/freelance/drafts/${draft.id}/approve`, {});
      setDraft(res.data);
      setShowApprovalModal(false);
      setSuccessMessage("✓ Message explicitly approved and cryptographic integrity hash registered. Ready for dispatch.");
    } catch (err: any) {
      setError(err?.message || "Failed to approve draft.");
    } finally {
      setApproving(false);
    }
  };

  const handleSend = async () => {
    if (!draft) return;
    setSending(true);
    setError(null);
    setSuccessMessage(null);
    try {
      await apiClient.post<any>(`/freelance/drafts/${draft.id}/send`, {});
      setSuccessMessage("🚀 Outreach message successfully dispatched via SMTP gateway.");
      setTimeout(() => {
        router.push("/freelance/outreach");
      }, 1500);
    } catch (err: any) {
      setError(err?.message || "Failed to send outreach. Please verify suppression status or candidate SMTP settings.");
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Preparing candidate outreach draft...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Navigation Breadcrumb */}
        <div>
          <Link href={`/freelance/${opportunityId}`} className="text-xs font-semibold text-indigo-400 hover:underline">
            ← Back to Opportunity Detail
          </Link>
        </div>

        {/* Header */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
              Candidate Outreach Workbench
            </span>
            <h1 className="text-2xl font-bold text-white mt-1">Review & Approve Outreach Draft</h1>
            <p className="text-xs text-slate-400 mt-1">
              Candidate governance gate: AI drafts require explicit human review and approval before sending.
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span
              className={`text-xs px-3 py-1 rounded-full font-bold uppercase ${
                draft?.status === "APPROVED"
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                  : draft?.status === "SENT"
                  ? "bg-indigo-950 text-indigo-300 border border-indigo-700"
                  : "bg-amber-950 text-amber-300 border border-amber-700"
              }`}
            >
              {draft?.status || "DRAFT"}
            </span>
          </div>
        </div>

        {/* AI Pitch Configuration Bar */}
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-xl space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            Tailor AI Pitch Generation Parameters:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Tone & Voice</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="professional">Professional & Crisp</option>
                <option value="consultative">Consultative & Helpful</option>
                <option value="bold">Bold & Direct</option>
                <option value="technical">Technical & Detailed</option>
              </select>
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Service Value Proposition</label>
              <input
                type="text"
                value={service}
                onChange={(e) => setService(e.target.value)}
                placeholder="e.g. Modern Mobile Rebuild"
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-[11px] text-slate-400 mb-1">Target Word Count</label>
              <div className="flex gap-2">
                <select
                  value={minWords}
                  onChange={(e) => setMinWords(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value={100}>Short & Punchy (~100 words)</option>
                  <option value={150}>Standard Outreach (~150 words)</option>
                  <option value={250}>In-depth Proposal (~250 words)</option>
                </select>
                <button
                  onClick={handleRegeneratePitch}
                  disabled={regenerating}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg whitespace-nowrap transition"
                >
                  {regenerating ? "Writing..." : "Regenerate ⚡"}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Anti-Hallucination & Invalidation Warning */}
        <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-indigo-300 flex items-center gap-1.5">
            <span>🛡️</span> Grounding & Safety Rule
          </p>
          <p className="text-slate-400 leading-relaxed">
            This outreach draft references verified facts from your candidate profile and the public listing.
            Never promise artificial discounts or invent fake portfolio accomplishments.
            <strong className="text-amber-300"> Note: Any edit made to an approved draft automatically invalidates prior approval and returns status to PENDING_REVIEW.</strong>
          </p>
        </div>

        {/* Status Alerts */}
        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-600 rounded-xl text-rose-200 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
          </div>
        )}
        {successMessage && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm flex items-center justify-between">
            <span>{successMessage}</span>
            <button onClick={() => setSuccessMessage(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Editor Form */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-5">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Recipient Contact Email
            </label>
            <input
              type="text"
              value={recipient}
              onChange={(e) => setRecipient(e.target.value)}
              placeholder="e.g. contact@business.com"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
              Subject Line
            </label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Outreach subject line"
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
                Message Content
              </label>
              <span className="text-[11px] text-slate-500">
                Word Count: {body ? body.trim().split(/\s+/).length : 0} words
              </span>
            </div>
            <textarea
              rows={12}
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Compose your personalized pitch..."
              className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500 font-sans leading-relaxed"
            />
          </div>

          {/* Action Button Bar */}
          <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3">
            <button
              onClick={handleSaveEdits}
              disabled={saving}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
            >
              {saving ? "Saving Changes..." : "Save Edits"}
            </button>

            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => setShowApprovalModal(true)}
                disabled={approving || draft?.status === "APPROVED"}
                className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-white text-xs font-semibold rounded-lg transition"
              >
                {draft?.status === "APPROVED" ? "✓ Approved" : "Review & Approve Pitch"}
              </button>

              <button
                onClick={handleSend}
                disabled={sending || draft?.status !== "APPROVED"}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-semibold rounded-lg transition shadow-md shadow-indigo-900/40"
              >
                {sending ? "Sending..." : "Dispatch Outreach 🚀"}
              </button>
            </div>
          </div>
        </div>

        {/* Explicit Approval Modal Dialog */}
        {showApprovalModal && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-700 p-6 rounded-xl max-w-lg w-full space-y-4 shadow-2xl">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>✍️</span> Explicit Candidate Outreach Approval
                </h3>
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="text-slate-400 hover:text-white text-sm"
                >
                  ✕
                </button>
              </div>

              <div className="text-xs text-slate-300 space-y-2">
                <p>
                  Please confirm that you have reviewed the proposed outreach message:
                </p>
                <div className="bg-slate-950 p-3 rounded border border-slate-800 font-mono space-y-1">
                  <p><span className="text-slate-500">Recipient:</span> {recipient || "None"}</p>
                  <p><span className="text-slate-500">Subject:</span> {subject || "None"}</p>
                  <p><span className="text-slate-500">Length:</span> {body.trim().split(/\s+/).length} words</p>
                </div>
                <label className="flex items-start gap-2 pt-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={approvalConfirmed}
                    onChange={(e) => setApprovalConfirmed(e.target.checked)}
                    className="mt-0.5 rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0"
                  />
                  <span>
                    I confirm this pitch is truthful, professional, and compliant with all applicable outreach policies.
                  </span>
                </label>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  onClick={() => setShowApprovalModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
                >
                  Cancel
                </button>
                <button
                  onClick={handleApprove}
                  disabled={!approvalConfirmed || approving}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition"
                >
                  {approving ? "Approving..." : "Confirm & Approve Pitch"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function OutreachDraftPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-slate-950 text-slate-400 flex items-center justify-center">Loading workbench...</div>}>
      <OutreachDraftEditorContent />
    </Suspense>
  );
}
