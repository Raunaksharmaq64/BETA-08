"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface CanonicalOpportunity {
  id: string;
  source_id: string;
  external_job_id: string;
  title: string;
  company_name: string;
  description_clean: string;
  employment_type: string;
  workplace_type: string;
  department: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  is_remote: boolean;
  min_salary: number | null;
  max_salary: number | null;
  currency: string | null;
  salary_period: string | null;
  is_salary_estimated: boolean;
  required_skills: string[];
  application_url: string;
  verification_status: string;
  freshness_state: string;
  is_suppressed: boolean;
  provenance: {
    provider?: string;
    source_key?: string;
    normalized_at?: string;
  };
  last_seen_at: string;
}

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<CanonicalOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [employmentType, setEmploymentType] = useState("");

  // Feedback Modal State
  const [selectedOppForFeedback, setSelectedOppForFeedback] = useState<CanonicalOpportunity | null>(null);
  const [feedbackType, setFeedbackType] = useState("BROKEN_LINK");
  const [feedbackNotes, setFeedbackNotes] = useState("");
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false);
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (search.trim()) params.append("search", search.trim());
      if (remoteOnly) params.append("remote_only", "true");
      if (employmentType) params.append("employment_type", employmentType);

      const queryStr = params.toString() ? `?${params.toString()}` : "";
      const res = await apiClient<CanonicalOpportunity[]>(`/opportunities${queryStr}`);
      setOpportunities(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load opportunities.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOpportunities();
  }, [remoteOnly, employmentType]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchOpportunities();
  };

  const handleOpenFeedback = (opp: CanonicalOpportunity) => {
    setSelectedOppForFeedback(opp);
    setFeedbackType("BROKEN_LINK");
    setFeedbackNotes("");
    setFeedbackSuccess(null);
    setFeedbackError(null);
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOppForFeedback) return;
    try {
      setFeedbackSubmitting(true);
      setFeedbackError(null);
      await apiClient(`/opportunities/${selectedOppForFeedback.id}/feedback`, {
        method: "POST",
        body: JSON.stringify({
          feedback_type: feedbackType,
          notes: feedbackNotes.trim() || undefined,
        }),
      });
      setFeedbackSuccess("Thank you! Your feedback was received and verification was initiated.");
      setTimeout(() => {
        setSelectedOppForFeedback(null);
        setFeedbackSuccess(null);
      }, 1800);
    } catch (err: any) {
      setFeedbackError(err?.message || "Failed to submit feedback.");
    } finally {
      setFeedbackSubmitting(false);
    }
  };

  const getFreshnessBadge = (opp: CanonicalOpportunity) => {
    if (opp.verification_status === "OPEN_CONFIRMED") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          Status confirmed open
        </span>
      );
    }
    if (opp.verification_status === "CLOSED_CONFIRMED" || opp.verification_status === "EXPIRED_CONFIRMED") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-950 text-rose-400 border border-rose-800">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
          Closed / Expired
        </span>
      );
    }
    if (opp.verification_status === "UNAVAILABLE") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-rose-950 text-rose-400 border border-rose-800">
          <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
          Link Unavailable
        </span>
      );
    }
    if (opp.freshness_state === "FRESH" || opp.freshness_state === "AGING") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-blue-950 text-blue-400 border border-blue-800">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
          Recently observed
        </span>
      );
    }
    if (opp.freshness_state === "STALE" || opp.freshness_state === "CHECK_OVERDUE") {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-950 text-amber-400 border border-amber-800">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          Listing may be outdated
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">
        Unverified
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Canonical Opportunities</h1>
          <p className="mt-2 text-sm text-slate-400 max-w-3xl">
            Verified, deduplicated career opportunities with independent freshness checks, source provenance,
            and evidentiary status auditing.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/quality"
            className="inline-flex items-center px-4 py-2 rounded-lg border border-slate-700 bg-slate-850 text-sm font-semibold text-indigo-400 hover:bg-slate-800 transition-colors"
          >
            Data Quality Dashboard &rarr;
          </Link>
          <Link
            href="/sources"
            className="inline-flex items-center px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-sm font-semibold text-slate-200 hover:bg-slate-700 transition-colors"
          >
            Manage Sources &rarr;
          </Link>
        </div>
      </div>

      {/* Search and Filters Bar */}
      <form onSubmit={handleSearchSubmit} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center gap-4">
        <div className="flex-1 w-full">
          <input
            type="text"
            placeholder="Search by job title, company, or skills (e.g. Python, Engineer)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex items-center space-x-4 w-full md:w-auto justify-between md:justify-start">
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none"
          >
            <option value="">All Employment Types</option>
            <option value="FULL_TIME">Full-Time</option>
            <option value="CONTRACT">Contract</option>
            <option value="INTERNSHIP">Internship</option>
            <option value="PART_TIME">Part-Time</option>
          </select>

          <label className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
            <input
              type="checkbox"
              checked={remoteOnly}
              onChange={(e) => setRemoteOnly(e.target.checked)}
              className="rounded bg-slate-950 border-slate-800 text-indigo-600"
            />
            <span>Remote Only</span>
          </label>

          <button
            type="submit"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors"
          >
            Search
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Opportunities List */}
      {loading ? (
        <div className="p-12 text-center text-slate-400">Loading opportunities...</div>
      ) : opportunities.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400 space-y-4">
          <p className="text-base text-slate-300">No career opportunities found matching your criteria.</p>
          <p className="text-xs">
            Try adjusting your search filters or{" "}
            <Link href="/sources" className="text-indigo-400 underline">trigger an ingestion run</Link> on an active source.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-slate-700 transition-all shadow-md space-y-4"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-3">
                    <Link
                      href={`/opportunities/${opp.id}`}
                      className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                    >
                      {opp.title}
                    </Link>
                    {opp.is_remote && (
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                        REMOTE
                      </span>
                    )}
                    {getFreshnessBadge(opp)}
                  </div>
                  <div className="text-sm font-semibold text-indigo-400">
                    {opp.company_name}
                    {opp.department && <span className="text-slate-400 font-normal"> &bull; {opp.department}</span>}
                    {(opp.city || opp.state || opp.country) && (
                      <span className="text-slate-400 font-normal">
                        {" "}
                        &bull; {[opp.city, opp.state, opp.country].filter(Boolean).join(", ")}
                      </span>
                    )}
                  </div>
                </div>

                <div className="text-right">
                  {opp.min_salary != null ? (
                    <div className="text-sm font-semibold text-white">
                      {opp.currency || "$"}
                      {opp.min_salary.toLocaleString()}
                      {opp.max_salary != null && ` - ${opp.max_salary.toLocaleString()}`}
                      <span className="text-xs text-slate-400 font-normal">
                        {opp.salary_period ? ` / ${opp.salary_period.toLowerCase()}` : " (explicit)"}
                      </span>
                    </div>
                  ) : (
                    <div className="text-xs text-slate-500 italic">Compensation not disclosed</div>
                  )}
                  <span className="text-[11px] text-slate-500 block mt-1">
                    Verified ATS listing &bull; {opp.employment_type}
                  </span>
                </div>
              </div>

              {/* Description Excerpt */}
              <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                {opp.description_clean}
              </p>

              {/* Skills Tags & Footer */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-4 border-t border-slate-800/80 gap-3">
                <div className="flex flex-wrap gap-1.5">
                  {opp.required_skills.length > 0 ? (
                    opp.required_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300 border border-slate-700/60"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-slate-500">No skill tags detected</span>
                  )}
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => handleOpenFeedback(opp)}
                    className="px-2.5 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-xs text-slate-300 hover:text-white transition-colors"
                  >
                    Report Issue
                  </button>
                  <Link
                    href={`/opportunities/${opp.id}`}
                    className="px-3 py-1.5 rounded-lg border border-indigo-700/60 bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 text-xs font-semibold transition-colors"
                  >
                    Verification Trail &rarr;
                  </Link>
                  <a
                    href={opp.application_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
                  >
                    Apply on Official Board &rarr;
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* User Listing Feedback Modal */}
      {selectedOppForFeedback && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Report Listing Inaccuracy</h3>
              <button
                onClick={() => setSelectedOppForFeedback(null)}
                className="text-slate-400 hover:text-white text-lg"
              >
                &times;
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Reporting: <strong className="text-white">{selectedOppForFeedback.title}</strong> at{" "}
              <strong className="text-white">{selectedOppForFeedback.company_name}</strong>.
              Your report initiates an automated evidentiary verification check.
            </p>

            <form onSubmit={handleSubmitFeedback} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Issue Category</label>
                <select
                  value={feedbackType}
                  onChange={(e) => setFeedbackType(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="BROKEN_LINK">Broken or 404 Application Link</option>
                  <option value="ALREADY_CLOSED">Role Already Filled / Closed</option>
                  <option value="INCORRECT_DETAILS">Inaccurate Title, Salary, or Location</option>
                  <option value="DUPLICATE_LISTING">Duplicate of another listing</option>
                  <option value="OTHER">Other Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Additional Context (Optional)</label>
                <textarea
                  value={feedbackNotes}
                  onChange={(e) => setFeedbackNotes(e.target.value)}
                  placeholder="Provide any details about what you observed..."
                  rows={3}
                  maxLength={500}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {feedbackError && (
                <div className="p-2.5 rounded bg-rose-950 border border-rose-800 text-rose-300 text-xs">
                  {feedbackError}
                </div>
              )}

              {feedbackSuccess && (
                <div className="p-2.5 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs">
                  {feedbackSuccess}
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setSelectedOppForFeedback(null)}
                  className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={feedbackSubmitting}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {feedbackSubmitting ? "Submitting..." : "Submit Report"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
