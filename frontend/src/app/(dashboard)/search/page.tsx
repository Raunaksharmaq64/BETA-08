"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface JobItem {
  id: string;
  title: string;
  company_name: string;
  city?: string;
  state?: string;
  country?: string;
  workplace_type: string;
  is_remote: boolean;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
  currency?: string;
  salary_period?: string;
  required_skills: string[];
  application_url: string;
  verification_status: string;
  freshness_state: string;
  first_seen_at: string;
  last_verified_at?: string;
  source_name: string;
  is_saved: boolean;
  saved_job_id?: string;
  skill_fit_score?: number;
  eligibility_status?: string;
  matched_skills_preview: string[];
  missing_skills_preview: string[];
}

interface SourceCoverage {
  total_configured_sources: number;
  healthy_sources_count: number;
  degraded_sources_count: number;
  is_partial_results: boolean;
  coverage_details: Array<{
    source_key: string;
    display_name: string;
    status: string;
    records_count: number;
    outage_reason?: string;
  }>;
}

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  // Search filter states
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [role, setRole] = useState(searchParams.get("role") || "");
  const [company, setCompany] = useState(searchParams.get("company") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [isRemoteOnly, setIsRemoteOnly] = useState(searchParams.get("remote") === "true");
  const [sortBy, setSortBy] = useState(searchParams.get("sort_by") || "BEST_FIT");
  const [verificationFilter, setVerificationFilter] = useState(searchParams.get("verification") || "");
  const [page, setPage] = useState(Number(searchParams.get("page") || 1));

  // Result states
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [coverage, setCoverage] = useState<SourceCoverage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Save Search Modal state
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState("");
  const [alertFrequency, setAlertFrequency] = useState("DAILY");
  const [isSavingSearch, setIsSavingSearch] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const fetchJobs = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (query) params.set("q", query);
      if (role) params.set("role", role);
      if (company) params.set("company", company);
      if (city) params.set("city", city);
      if (isRemoteOnly) params.set("is_remote", "true");
      if (verificationFilter) params.append("verification_statuses", verificationFilter);
      params.set("sort_by", sortBy);
      params.set("page", page.toString());
      params.set("page_size", "15");

      const res = await apiClient<any>(`/search/jobs?${params.toString()}`);
      if (res.data) {
        setJobs(res.data.items || []);
        setTotalCount(res.data.total_count || 0);
        setTotalPages(res.data.total_pages || 1);
        setCoverage(res.data.source_coverage || null);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load job listings.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [page, sortBy]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleToggleSaveJob = async (job: JobItem) => {
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      if (job.is_saved) {
        await apiClient(`/saved-jobs/${job.id}`, { method: "DELETE" });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: false, saved_job_id: undefined } : j))
        );
      } else {
        const res = await apiClient<any>("/saved-jobs", {
          method: "POST",
          body: JSON.stringify({ opportunity_id: job.id }),
        });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: true, saved_job_id: res.data.id } : j))
        );
      }
    } catch (err: any) {
      alert("Failed to update saved job status: " + err.message);
    }
  };

  const handleSaveSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      router.push("/login");
      return;
    }
    if (!saveSearchName.trim()) return;

    setIsSavingSearch(true);
    setSaveSuccessMsg(null);
    try {
      await apiClient("/saved-searches", {
        method: "POST",
        body: JSON.stringify({
          name: saveSearchName,
          query: query || undefined,
          filters: {
            role: role || undefined,
            company: company || undefined,
            city: city || undefined,
            is_remote: isRemoteOnly || undefined,
            verification_status: verificationFilter || undefined,
          },
          alert_enabled: true,
          alert_frequency: alertFrequency,
        }),
      });
      setSaveSuccessMsg("Search and alert notifications saved successfully!");
      setTimeout(() => {
        setIsSaveModalOpen(false);
        setSaveSuccessMsg(null);
        setSaveSearchName("");
      }, 1500);
    } catch (err: any) {
      alert("Failed to save search: " + err.message);
    } finally {
      setIsSavingSearch(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header & Save Search Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Job Discovery & Matching</h1>
          <p className="text-sm text-slate-400 mt-1">
            Search verified career opportunities evaluated with transparent, evidence-based candidate matching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSaveModalOpen(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-indigo-500/30 text-sm font-medium transition-colors"
          >
            <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Save Search & Alerts
          </button>
        </div>
      </div>

      {/* Partial Coverage Transparency Banner */}
      {coverage && coverage.is_partial_results && (
        <div className="mt-4 p-4 rounded-xl bg-amber-950/40 border border-amber-600/40 text-amber-200 flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div className="font-semibold text-amber-300">Notice: Partial Upstream Source Coverage</div>
            <p className="text-xs text-amber-200/90 mt-0.5">
              One or more upstream source connectors ({coverage.degraded_sources_count} of {coverage.total_configured_sources})
              are currently degraded or in circuit breaker cooldown. Zero matches on certain queries may reflect upstream provider outages rather than a lack of market openings.
            </p>
          </div>
        </div>
      )}

      {/* Main Grid: Filters Sidebar + Results */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-6 bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
          <form onSubmit={handleSearchSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Keywords
              </label>
              <input
                type="text"
                placeholder="Title, skill, or company..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Role / Title
              </label>
              <input
                type="text"
                placeholder="e.g. Backend Engineer"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Company
              </label>
              <input
                type="text"
                placeholder="e.g. Stripe, Acme"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Location
              </label>
              <input
                type="text"
                placeholder="City, State, or Country"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="pt-2">
              <label className="flex items-center gap-2 cursor-pointer text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={isRemoteOnly}
                  onChange={(e) => setIsRemoteOnly(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500"
                />
                Remote Only
              </label>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">
                Verification Status
              </label>
              <select
                value={verificationFilter}
                onChange={(e) => setVerificationFilter(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-sm focus:outline-none focus:border-indigo-500"
              >
                <option value="">All Listings</option>
                <option value="OPEN_CONFIRMED">Open Confirmed</option>
                <option value="UNVERIFIED">Unverified Only</option>
              </select>
            </div>

            <button
              type="submit"
              className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-indigo-600/20"
            >
              Apply Filters
            </button>
          </form>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-3 space-y-4">
          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 px-4 py-3 rounded-xl border border-slate-800">
            <div className="text-sm text-slate-400">
              Showing <span className="font-semibold text-white">{jobs.length}</span> of{" "}
              <span className="font-semibold text-white">{totalCount}</span> opportunities
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <label>Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1.5 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="BEST_FIT">Best Fit (Match & Verified)</option>
                <option value="MOST_RECENT">Most Recent</option>
                <option value="HIGHEST_SALARY">Highest Compensation</option>
                <option value="SKILL_MATCH">Skill Match %</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-600/40 text-red-300 text-sm">
              {errorMsg}
            </div>
          )}

          {/* Loading Skeleton */}
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/40 rounded-2xl p-6 border border-slate-800 h-44" />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/30 rounded-2xl border border-slate-800">
              <p className="text-base font-medium text-slate-300">No opportunities matching your criteria</p>
              <p className="text-xs text-slate-500 mt-1">Try broadening your keywords or removing location filters.</p>
            </div>
          ) : (
            /* Opportunity Cards */
            <div className="space-y-4">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-slate-900/80 hover:bg-slate-900 transition-colors rounded-2xl p-6 border border-slate-800 hover:border-slate-700 space-y-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Link
                          href={`/jobs/${job.id}`}
                          className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                        >
                          {job.title}
                        </Link>
                        {job.is_remote && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                            Remote
                          </span>
                        )}
                        <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                          {job.workplace_type}
                        </span>
                      </div>
                      <div className="text-sm text-slate-400 mt-1 flex items-center gap-3 flex-wrap">
                        <span className="font-medium text-slate-200">{job.company_name}</span>
                        <span>•</span>
                        <span>{job.city ? `${job.city}, ${job.country || ""}` : job.country || "Worldwide"}</span>
                        <span>•</span>
                        <span className="text-xs text-slate-500">Source: {job.source_name}</span>
                      </div>
                    </div>

                    {/* Save / Bookmark Button */}
                    <button
                      onClick={() => handleToggleSaveJob(job)}
                      title={job.is_saved ? "Remove from saved jobs" : "Save this job"}
                      className={`p-2 rounded-xl border transition-colors ${
                        job.is_saved
                          ? "bg-rose-950/50 border-rose-700/60 text-rose-400 hover:bg-rose-900/50"
                          : "bg-slate-800/80 border-slate-700 text-slate-400 hover:text-white hover:bg-slate-700"
                      }`}
                    >
                      <svg className="w-5 h-5 fill-current" viewBox="0 0 20 20">
                        <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
                      </svg>
                    </button>
                  </div>

                  {/* Badges: Verification, Freshness, Skill Fit & Eligibility */}
                  <div className="flex items-center gap-3 flex-wrap text-xs pt-1">
                    {/* Verification Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-medium border ${
                        job.verification_status === "OPEN_CONFIRMED"
                          ? "bg-emerald-950/50 border-emerald-800/70 text-emerald-300"
                          : job.verification_status === "UNVERIFIED"
                          ? "bg-slate-800/80 border-slate-700 text-slate-400"
                          : "bg-amber-950/50 border-amber-800/70 text-amber-300"
                      }`}
                    >
                      {job.verification_status === "OPEN_CONFIRMED" ? "✓ Open Confirmed" : job.verification_status}
                    </span>

                    {/* Freshness Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-medium border ${
                        job.freshness_state === "FRESH"
                          ? "bg-blue-950/50 border-blue-800/70 text-blue-300"
                          : job.freshness_state === "RECENT"
                          ? "bg-cyan-950/50 border-cyan-800/70 text-cyan-300"
                          : "bg-slate-800 border-slate-700 text-slate-400"
                      }`}
                    >
                      Freshness: {job.freshness_state}
                    </span>

                    {/* Skill Fit Badge */}
                    {job.skill_fit_score !== undefined && job.skill_fit_score !== null && (
                      <span className="px-2.5 py-1 rounded-md font-semibold bg-indigo-950/60 border border-indigo-700/60 text-indigo-300">
                        ★ {job.skill_fit_score}% Skill Fit
                      </span>
                    )}

                    {/* Mandatory Eligibility Badge */}
                    {job.eligibility_status && (
                      <span
                        className={`px-2.5 py-1 rounded-md font-medium border ${
                          job.eligibility_status === "MEETS_REQUIREMENTS"
                            ? "bg-emerald-950/40 border-emerald-700/60 text-emerald-400"
                            : job.eligibility_status === "UNKNOWN"
                            ? "bg-slate-800 border-slate-700 text-slate-400"
                            : "bg-rose-950/40 border-rose-800/60 text-rose-400"
                        }`}
                      >
                        Eligibility: {job.eligibility_status.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>

                  {/* Skills Preview */}
                  <div className="space-y-1.5 pt-1">
                    {job.matched_skills_preview.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap text-xs">
                        <span className="text-slate-400">Matched Skills:</span>
                        {job.matched_skills_preview.map((s, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded bg-emerald-950/50 text-emerald-300 border border-emerald-800/40"
                          >
                            ✓ {s}
                          </span>
                        ))}
                      </div>
                    )}
                    {job.missing_skills_preview.length > 0 && (
                      <div className="flex items-center gap-1.5 flex-wrap text-xs">
                        <span className="text-slate-400">Missing Skills:</span>
                        {job.missing_skills_preview.map((s, idx) => (
                          <span
                            key={idx}
                            className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700"
                          >
                            {s}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Card Footer: Salary & Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-sm">
                    <div className="font-semibold text-slate-200">
                      {job.min_salary || job.max_salary ? (
                        <>
                          {job.currency || "$"}
                          {job.min_salary?.toLocaleString()} - {job.max_salary?.toLocaleString()}{" "}
                          <span className="text-xs text-slate-400 font-normal">/ {job.salary_period || "year"}</span>
                        </>
                      ) : (
                        <span className="text-xs text-slate-500 font-normal">Salary not disclosed</span>
                      )}
                    </div>
                    <div className="flex items-center gap-3">
                      <Link
                        href={`/jobs/${job.id}`}
                        className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 transition-colors"
                      >
                        Match Breakdown →
                      </Link>
                      <a
                        href={job.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                      >
                        Apply Site ↗
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-slate-800">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
              >
                ← Previous
              </button>
              <span className="text-xs text-slate-400">
                Page <span className="text-white font-semibold">{page}</span> of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="px-4 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Save Search & Alert Modal */}
      {isSaveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Save Search & Configure Alerts</h3>
            <p className="text-xs text-slate-400 mt-1">
              Receive automatic notifications when fresh opportunities matching your filters are ingested.
            </p>

            <form onSubmit={handleSaveSearch} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Search Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Remote Backend Python Roles"
                  value={saveSearchName}
                  onChange={(e) => setSaveSearchName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Notification Cadence</label>
                <select
                  value={alertFrequency}
                  onChange={(e) => setAlertFrequency(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="INSTANT">Instant (Real-Time Ingestion)</option>
                  <option value="DAILY">Daily Digest</option>
                  <option value="WEEKLY">Weekly Summary</option>
                </select>
              </div>

              {saveSuccessMsg && (
                <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800/60 text-emerald-300 text-xs">
                  {saveSuccessMsg}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsSaveModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingSearch}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white disabled:opacity-50"
                >
                  {isSavingSearch ? "Saving..." : "Save Subscription"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function JobSearchPage() {
  return (
    <React.Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-16 text-slate-400 text-sm">
          Loading Job Discovery & Matching...
        </div>
      }
    >
      <SearchContent />
    </React.Suspense>
  );
}
