"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

interface AISuggestion {
  id: string;
  category: string;
  target_section: string;
  current_issue: string;
  why_it_matters: string;
  current_text: string | null;
  recommended_text: string;
  evidence_required_from_candidate: string;
  status: string;
  edited_content?: string | null;
}

interface SuggestionsResponse {
  resume_id: string;
  version_id: string;
  suggestions: AISuggestion[];
  provider_used: string;
  created_at: string;
}

export default function ResumeSuggestionsPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [data, setData] = useState<SuggestionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>("ALL");
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);

  // Inline editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [customText, setCustomText] = useState<string>("");

  const fetchSuggestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<SuggestionsResponse>(`/api/v1/resumes/${resumeId}/ai-suggestions`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load AI suggestions.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchSuggestions();
    }
  }, [resumeId]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2500);
  };

  const handleAction = async (suggestionId: string, action: string, editedText?: string) => {
    try {
      setActionInProgress(suggestionId);
      const res = await apiClient.post<any>(
        `/api/v1/resumes/${resumeId}/ai-suggestions/${suggestionId}/action`,
        {
          suggestion_id: suggestionId,
          action,
          edited_text: editedText
        }
      );
      if (res.success && data) {
        // Update local state immediately
        setData({
          ...data,
          suggestions: data.suggestions.map((s) => {
            if (s.id === suggestionId) {
              return {
                ...s,
                status: action === "ACCEPT" ? "ACCEPTED" : action === "REJECT" ? "REJECTED" : action === "EDIT" ? "EDITED" : s.status,
                edited_content: editedText || s.edited_content
              };
            }
            return s;
          })
        });
        setEditingId(null);
      }
    } catch (err: any) {
      alert("Action failed: " + err.message);
    } finally {
      setActionInProgress(null);
    }
  };

  const startEditing = (sug: AISuggestion) => {
    setEditingId(sug.id);
    setCustomText(sug.edited_content || sug.recommended_text);
  };

  const filteredSuggestions = data?.suggestions.filter((s) => {
    if (filterCategory === "ALL") return true;
    return s.category === filterCategory;
  }) || [];

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-6 pb-6 border-b border-slate-800">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
          ← Back to Resumes
        </Link>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Actionable AI Improvement & Rewrites</h1>
            <p className="mt-1 text-sm text-slate-400">
              Zero-hallucination structural rewrites. Generates active-verb phrasing with placeholders for your genuine metrics.
            </p>
          </div>
          {data?.provider_used && (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-950/80 border border-indigo-800 text-indigo-300 self-start sm:self-auto">
              Provider: {data.provider_used.replace(/_/g, " ")}
            </span>
          )}
        </div>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {/* Ethical Guardrail Disclaimer */}
      <div className="mb-8 p-4 rounded-xl bg-indigo-950/30 border border-indigo-800/60 text-xs text-indigo-200 flex items-start space-x-3">
        <span className="text-lg">🛡️</span>
        <div className="leading-relaxed">
          <p className="font-bold text-slate-200">Anti-Hallucination & Evidence Integrity Policy</p>
          <p className="mt-0.5 text-slate-300">
            RIGHT FIT never fabricates employment history, companies, dates, or quantitative results. All recommended rewrites contain bracketed placeholders (such as <code className="bg-indigo-900/60 px-1 py-0.5 rounded text-amber-300 font-mono">[X]%</code>) which require candidate verification and concrete real-world evidence before inclusion. Original resume content remains untouched until you explicitly accept or edit.
          </p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
          Analyzing resume bullets and synthesizing improvements...
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-2 pb-2">
            {["ALL", "BULLET_REWRITE", "SUMMARY_POLISH", "PORTFOLIO_PROOF", "MISSING_CONTEXT"].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${filterCategory === cat
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "bg-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-700"
                  }`}
              >
                {cat.replace(/_/g, " ")}
              </button>
            ))}
          </div>

          {filteredSuggestions.length === 0 ? (
            <div className="p-8 text-center bg-slate-900/40 border border-slate-800 rounded-xl text-slate-400 text-xs">
              No suggestions found for this category.
            </div>
          ) : (
            filteredSuggestions.map((sug) => {
              const isAccepted = sug.status === "ACCEPTED";
              const isRejected = sug.status === "REJECTED";
              const isEdited = sug.status === "EDITED";
              const isCopied = copiedId === sug.id;
              const isEditingThis = editingId === sug.id;

              return (
                <div
                  key={sug.id}
                  className={`rounded-xl border transition-all p-6 ${isAccepted
                    ? "bg-slate-900/40 border-emerald-800/80"
                    : isRejected
                      ? "bg-slate-900/30 border-rose-900/40 opacity-75"
                      : isEdited
                        ? "bg-slate-900/40 border-indigo-700/80"
                        : "bg-slate-900/70 border-slate-800 hover:border-slate-700"
                    }`}
                >
                  {/* Card Header */}
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 mb-4 border-b border-slate-800 gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[11px] font-bold px-2.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                        {sug.category.replace(/_/g, " ")}
                      </span>
                      <span className="text-xs font-semibold text-slate-300">
                        {sug.target_section}
                      </span>
                      {isAccepted && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                          ACCEPTED
                        </span>
                      )}
                      {isRejected && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                          REJECTED
                        </span>
                      )}
                      {isEdited && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700">
                          CUSTOMIZED
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-2">
                      <button
                        onClick={() => handleCopy(sug.id, sug.edited_content || sug.recommended_text)}
                        className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
                      >
                        {isCopied ? "✓ Copied" : "Copy"}
                      </button>

                      <button
                        onClick={() => startEditing(sug)}
                        className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-indigo-300 text-xs font-medium border border-slate-700 transition-colors"
                      >
                        ✎ Edit Facts
                      </button>

                      {!isAccepted && (
                        <button
                          disabled={actionInProgress === sug.id}
                          onClick={() => handleAction(sug.id, "ACCEPT")}
                          className="px-3 py-1 rounded text-xs font-semibold bg-emerald-950 hover:bg-emerald-900 border border-emerald-800 text-emerald-300 transition-colors"
                        >
                          Accept
                        </button>
                      )}

                      {!isRejected && (
                        <button
                          disabled={actionInProgress === sug.id}
                          onClick={() => handleAction(sug.id, "REJECT")}
                          className="px-3 py-1 rounded text-xs font-semibold bg-rose-950/40 hover:bg-rose-900/60 border border-rose-900/80 text-rose-300 transition-colors"
                        >
                          Reject
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Issue & Why it Matters */}
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-slate-100">{sug.current_issue}</p>
                    <p className="text-xs text-slate-400 mt-1 leading-relaxed">{sug.why_it_matters}</p>
                  </div>

                  {/* "Before vs. After" Diff Box */}
                  <div className="space-y-3 bg-slate-950/80 p-4 rounded-lg border border-slate-800/80">
                    {sug.current_text && (
                      <div>
                        <div className="flex items-center space-x-1.5 mb-1">
                          <span className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Before (Original Resume):</span>
                        </div>
                        <p className="text-xs text-slate-400 line-through opacity-80 pl-2 border-l-2 border-rose-700/60 font-mono">
                          {sug.current_text}
                        </p>
                      </div>
                    )}

                    <div>
                      <div className="flex items-center space-x-1.5 mb-1">
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">After (Proposed Formulation):</span>
                      </div>
                      <p className="text-xs text-slate-100 font-medium pl-2 border-l-2 border-emerald-500 font-mono leading-relaxed">
                        {sug.recommended_text}
                      </p>
                    </div>

                    {sug.edited_content && (
                      <div>
                        <div className="flex items-center space-x-1.5 mb-1">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Candidate Customized Formulation:</span>
                        </div>
                        <p className="text-xs text-indigo-200 font-medium pl-2 border-l-2 border-indigo-500 font-mono leading-relaxed">
                          {sug.edited_content}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Inline Edit Form */}
                  {isEditingThis && (
                    <div className="mt-4 p-4 rounded-lg bg-slate-950 border border-indigo-700/60">
                      <label className="block text-xs font-semibold text-indigo-300 mb-1">
                        Input Real Verified Metrics & Customize:
                      </label>
                      <textarea
                        rows={3}
                        value={customText}
                        onChange={(e) => setCustomText(e.target.value)}
                        className="w-full p-2.5 rounded-lg bg-slate-900 border border-slate-700 text-xs text-slate-100 font-mono focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        placeholder="Replace [X]% placeholders with your verified figures..."
                      />
                      <div className="mt-2 flex justify-end space-x-2">
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-3 py-1 rounded bg-slate-800 text-slate-300 text-xs"
                        >
                          Cancel
                        </button>
                        <button
                          disabled={actionInProgress === sug.id || !customText.trim()}
                          onClick={() => handleAction(sug.id, "EDIT", customText.trim())}
                          className="px-3 py-1 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                        >
                          Save Candidate Version
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Evidence Requirement Badge */}
                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-start space-x-2 text-xs">
                    <span className="text-amber-400 font-bold shrink-0">Proof Required:</span>
                    <span className="text-slate-300 leading-relaxed font-sans">
                      {sug.evidence_required_from_candidate}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      ) : null}
    </div>
  );
}
