"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface FeedbackItem {
  id: string;
  category: string;
  severity: string;
  subject?: string;
  description: string;
  expected_behavior?: string | null;
  triage_status?: string;
  review_status?: string;
  related_feature?: string;
  resolution_notes?: string | null;
  created_at: string;
  resolved_at?: string | null;
}

export default function BetaFeedbackPage() {
  const [feedbackList, setFeedbackList] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form fields
  const [category, setCategory] = useState("UX_CONFUSION");
  const [severity, setSeverity] = useState("MEDIUM");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [expectedBehavior, setExpectedBehavior] = useState("");
  const [consentDiagnostic, setConsentDiagnostic] = useState(true);

  const fetchFeedback = async () => {
    try {
      setLoading(true);
      const res: any = await apiClient("/beta/feedback");
      if (res && res.data) {
        const rawList = Array.isArray(res.data)
          ? res.data
          : Array.isArray(res.data.items)
          ? res.data.items
          : [];
        setFeedbackList(rawList);
      } else {
        setFeedbackList([]);
      }
    } catch (err: any) {
      console.error("Failed to load beta feedback history", err);
      setFeedbackList([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeedback();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) {
      setErrorMsg("Please fill in both subject and description.");
      return;
    }

    try {
      setSubmitting(true);
      setErrorMsg(null);
      setSuccessMsg(null);

      const payload = {
        category,
        severity,
        subject: subject.trim(),
        description: description.trim(),
        expected_behavior: expectedBehavior.trim() || null,
        metadata_json: {
          submitted_url: typeof window !== "undefined" ? window.location.pathname : "",
          user_agent: typeof navigator !== "undefined" ? navigator.userAgent : "",
          diagnostic_consent: consentDiagnostic,
        },
      };

      const res = await apiClient<FeedbackItem>("/beta/feedback", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (res && res.data) {
        setSuccessMsg("Thank you! Your beta feedback has been logged for engineering triage.");
        setSubject("");
        setDescription("");
        setExpectedBehavior("");
        fetchFeedback();
      }
    } catch (err: any) {
      setErrorMsg(err?.message || "Failed to submit beta feedback.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 mb-2">
            Beta Continuous Improvement
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Beta Feedback & Issue Reporting
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Report bugs, usability friction, and opportunity relevance discrepancies directly to our engineering team.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Link
            href="/quality/connectors"
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200"
          >
            Connector Metrics
          </Link>
          <Link
            href="/beta/release-notes"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Release Notes
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Column */}
        <div className="lg:col-span-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Submit New Feedback
          </h2>

          {successMsg && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-400 text-sm">
              {successMsg}
            </div>
          )}

          {errorMsg && (
            <div className="mb-4 p-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-400 text-sm">
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="BUG">Software Bug / Error</option>
                <option value="DATA_QUALITY">Data Quality (Stale / Broken Link)</option>
                <option value="UX_CONFUSION">UX Confusion / Usability</option>
                <option value="OPPORTUNITY_RELEVANCE">Opportunity Relevance Discrepancy</option>
                <option value="FEATURE_REQUEST">Feature Request</option>
                <option value="OTHER">Other Beta Observation</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Severity
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="LOW">Low (Cosmetic / Minor Enhancement)</option>
                <option value="MEDIUM">Medium (Unexpected behavior, has workaround)</option>
                <option value="HIGH">High (Major feature impaired)</option>
                <option value="CRITICAL">Critical (Blocks core workflow)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Subject
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Brief summary of the issue..."
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Observed Behavior / Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                placeholder="Describe what occurred, steps to reproduce, or why the match was inaccurate..."
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Expected Behavior (Optional)
              </label>
              <textarea
                value={expectedBehavior}
                onChange={(e) => setExpectedBehavior(e.target.value)}
                rows={2}
                placeholder="What did you expect to happen instead?"
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div className="flex items-start gap-2 pt-2">
              <input
                type="checkbox"
                id="diagnosticConsent"
                checked={consentDiagnostic}
                onChange={(e) => setConsentDiagnostic(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="diagnosticConsent" className="text-xs text-slate-600 dark:text-slate-400">
                Include non-sensitive browser environment metadata to assist debugging (Retained under 90-day beta privacy rules).
              </label>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full mt-4 py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium text-sm transition-colors shadow-sm"
            >
              {submitting ? "Submitting..." : "Submit Feedback"}
            </button>
          </form>
        </div>

        {/* History Column */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Triage & Feedback Status ({feedbackList.length})
            </h2>
            <button
              onClick={fetchFeedback}
              className="text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              Refresh
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
              Loading feedback history...
            </div>
          ) : feedbackList.length === 0 ? (
            <div className="p-8 text-center text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
              No feedback submitted yet. Report your first observation using the form on the left!
            </div>
          ) : (
            <div className="space-y-3">
              {feedbackList.map((item) => (
                <div
                  key={item.id}
                  className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm space-y-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-900 dark:text-white text-base">
                        {item.subject || (item.category + (item.related_feature ? ` · ${item.related_feature}` : ""))}
                      </span>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                          item.severity === "CRITICAL"
                            ? "bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300"
                            : item.severity === "HIGH"
                            ? "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                            : item.severity === "MEDIUM"
                            ? "bg-sky-100 text-sky-800 dark:bg-sky-950/60 dark:text-sky-300"
                            : "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300"
                        }`}
                      >
                        {item.severity}
                      </span>
                      <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                        {item.category}
                      </span>
                    </div>
                    <span
                      className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${
                        (item.triage_status || item.review_status) === "RESOLVED"
                          ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                          : (item.triage_status || item.review_status) === "IN_PROGRESS" || (item.triage_status || item.review_status) === "TRIAGED"
                          ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300"
                          : "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                      }`}
                    >
                      Status: {item.triage_status || item.review_status || "NEW"}
                    </span>
                  </div>

                  <p className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                    {item.description}
                  </p>

                  {item.expected_behavior && (
                    <div className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800">
                      <strong className="text-slate-700 dark:text-slate-300">Expected: </strong>
                      {item.expected_behavior}
                    </div>
                  )}

                  {item.resolution_notes && (
                    <div className="text-xs text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30 p-3 rounded-lg border border-emerald-200 dark:border-emerald-800">
                      <strong className="text-emerald-800 dark:text-emerald-300">Engineer Resolution: </strong>
                      {item.resolution_notes}
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span>Logged on {new Date(item.created_at).toLocaleString()}</span>
                    <span>ID: {item.id}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

