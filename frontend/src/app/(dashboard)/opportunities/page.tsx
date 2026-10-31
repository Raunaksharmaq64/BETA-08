"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface OpportunityEnvelope {
  schema_version: string;
  opportunity_id: string;
  opportunity_type: "JOB" | "FREELANCE" | "STARTUP_PAIN_POINT";
  title: string;
  short_description: string;
  organization_name: string;
  source_service: string;
  source_name: string;
  source_url?: string;
  location?: string;
  is_remote?: boolean;
  published_at?: string;
  freshness_state?: string;
  classification_state?: string;
  evidence_count?: number;
  is_saved?: boolean;
  type_specific_payload: any;
}

interface CountsByType {
  jobs: number;
  freelance: number;
  startup_pain_points: number;
  total: number;
}

interface ServiceAvailability {
  aggregation_state: string;
  core: string;
  leadhunter: string;
  startup_intelligence: string;
  is_partial_results: boolean;
}

export default function UnifiedOpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<OpportunityEnvelope[]>([]);
  const [counts, setCounts] = useState<CountsByType | null>(null);
  const [availability, setAvailability] = useState<ServiceAvailability | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [activeType, setActiveType] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [minScore, setMinScore] = useState<number>(0);

  // Candidate Relevance Feedback Modal
  const [feedbackItem, setFeedbackItem] = useState<OpportunityEnvelope | null>(null);
  const [feedbackCategory, setFeedbackCategory] = useState("WRONG_SKILLS");
  const [feedbackExplanation, setFeedbackExplanation] = useState("");
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
  const [feedbackStatusMsg, setFeedbackStatusMsg] = useState<string | null>(null);

  // Trust & Moderation Report Modal (Module G)
  const [reportItem, setReportItem] = useState<OpportunityEnvelope | null>(null);
  const [reportType, setReportType] = useState("SUSPICIOUS_JOB");
  const [reportNotes, setReportNotes] = useState("");
  const [submittingReport, setSubmittingReport] = useState(false);
  const [reportStatusMsg, setReportStatusMsg] = useState<string | null>(null);

  // Quick feedback toast indicator
  const [quickFeedbackId, setQuickFeedbackId] = useState<string | null>(null);

  // Saving state
  const [savingId, setSavingId] = useState<string | null>(null);

  // Auto-refresh and live polling states
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string>("Just now");
  const [pendingNewItems, setPendingNewItems] = useState<OpportunityEnvelope[]>([]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("rightfit_auto_refresh");
      if (saved !== null) {
        setAutoRefresh(saved === "true");
      }
    }
  }, []);

  const toggleAutoRefresh = () => {
    const nextVal = !autoRefresh;
    setAutoRefresh(nextVal);
    if (typeof window !== "undefined") {
      localStorage.setItem("rightfit_auto_refresh", String(nextVal));
    }
  };

  const fetchOpportunities = async (isBackground = false) => {
    if (!isBackground) setLoading(true);
    else setIsRefreshing(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (activeType !== "ALL") params.append("type", activeType);
      if (searchTerm.trim()) params.append("search", searchTerm.trim());
      if (selectedCategory !== "All") params.append("category", selectedCategory);
      if (minScore > 0) params.append("min_score", minScore.toString());
      params.append("per_page", "50");

      const res: any = await apiClient.get(`/opportunities/all?${params.toString()}`);
      const fetched: OpportunityEnvelope[] = res.data || [];

      if (isBackground && opportunities.length > 0) {
        const currentIds = new Set(opportunities.map(o => o.opportunity_id));
        const newOnes = fetched.filter(o => !currentIds.has(o.opportunity_id));
        if (newOnes.length > 0) {
          setPendingNewItems(newOnes);
        }
      } else {
        setOpportunities(fetched);
        setPendingNewItems([]);
      }

      setCounts(res.counts_by_type || null);
      setAvailability(res.service_availability || null);
      setLastRefreshedAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      if (!isBackground) setError(err?.message || "Failed to load opportunities.");
    } finally {
      if (!isBackground) setLoading(false);
      setIsRefreshing(false);
    }
  };

  const applyPendingNewItems = () => {
    setOpportunities(prev => [...pendingNewItems, ...prev]);
    setPendingNewItems([]);
  };

  useEffect(() => {
    fetchOpportunities(false);
  }, [activeType, selectedCategory, minScore]);

  // Background Auto-Refresh Poller (every 25 seconds when autoRefresh is enabled)
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchOpportunities(true);
    }, 25000);
    return () => clearInterval(interval);
  }, [autoRefresh, activeType, selectedCategory, minScore, opportunities]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchOpportunities();
  };

  const handleToggleSave = async (item: OpportunityEnvelope) => {
    setSavingId(item.opportunity_id);
    try {
      if (item.is_saved) {
        await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
        item.is_saved = false;
      } else {
        await apiClient.post(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`, {
          notes: "Saved from Unified Opportunities feed",
        });
        item.is_saved = true;
      }
      setOpportunities([...opportunities]);
    } catch (err: any) {
      alert(err?.message || "Failed to update bookmark.");
    } finally {
      setSavingId(null);
    }
  };

  const handleQuickFeedback = async (item: OpportunityEnvelope, category: string) => {
    setQuickFeedbackId(item.opportunity_id);
    try {
      await apiClient.post(
        `/opportunities/${item.opportunity_type}/${item.opportunity_id}/feedback`,
        {
          feedback_category: category,
          explanation: `Quick in-feed rating: ${category}`,
        }
      );
      if (item.type_specific_payload) {
        item.type_specific_payload.candidate_feedback_status = category;
      }
      setOpportunities([...opportunities]);
    } catch (err: any) {
      console.warn("Feedback save:", err);
    } finally {
      setTimeout(() => setQuickFeedbackId(null), 1200);
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackItem) return;
    setSubmittingFeedback(true);
    setFeedbackStatusMsg(null);
    try {
      await apiClient.post(
        `/opportunities/${feedbackItem.opportunity_type}/${feedbackItem.opportunity_id}/feedback`,
        {
          feedback_category: feedbackCategory,
          explanation: feedbackExplanation.trim() || undefined,
        }
      );
      if (feedbackItem.type_specific_payload) {
        feedbackItem.type_specific_payload.candidate_feedback_status = feedbackCategory;
      }
      setFeedbackStatusMsg("Feedback recorded. Ranking engine calibrated for you!");
      setTimeout(() => {
        setFeedbackItem(null);
        setFeedbackStatusMsg(null);
      }, 1400);
    } catch (err: any) {
      alert(err?.message || "Failed to record feedback.");
    } finally {
      setSubmittingFeedback(false);
    }
  };

  const handleSubmitReport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportItem) return;
    setSubmittingReport(true);
    setReportStatusMsg(null);
    try {
      await apiClient.post(`/opportunities/${reportItem.opportunity_id}/feedback`, {
        feedback_type: reportType,
        notes: reportNotes.trim() || "Reported via user interface",
      });
      setReportStatusMsg("Report received. Our moderation and verification system will review this listing.");
      setTimeout(() => {
        setReportItem(null);
        setReportStatusMsg(null);
        setReportNotes("");
      }, 1500);
    } catch (err: any) {
      alert(err?.message || "Failed to submit report.");
    } finally {
      setSubmittingReport(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Unified Opportunities Pipeline
            </h1>
            <span className="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800">
              Envelope v1.0
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Multi-source aggregation across Canonical Full-Time Jobs, LeadHunter Freelance Leads, and Startup Pain Points.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            ← Back to Dashboard
          </Link>
          <Link
            href="/saved-opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            Saved Bookmarks ★
          </Link>
        </div>
      </div>

      {/* Live Auto-Refresh & Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={toggleAutoRefresh}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg font-semibold transition-colors border ${autoRefresh
              ? "bg-emerald-950/60 border-emerald-800 text-emerald-400"
              : "bg-slate-800 border-slate-700 text-slate-400"
              }`}
          >
            <span className={`w-2 h-2 rounded-full ${autoRefresh ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
            Auto-Refresh: {autoRefresh ? "ON (25s)" : "PAUSED"}
          </button>

          <span className="text-slate-400">
            Last checked: <span className="text-slate-200 font-mono">{lastRefreshedAt}</span>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchOpportunities(false)}
            disabled={isRefreshing}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium border border-slate-700 transition-colors disabled:opacity-50"
          >
            <span className={isRefreshing ? "animate-spin" : ""}>⟳</span>
            {isRefreshing ? "Refreshing..." : "Refresh Feed"}
          </button>
        </div>
      </div>

      {/* Floating / Inline Banner when new background items are discovered */}
      {pendingNewItems.length > 0 && (
        <div className="p-4 rounded-xl bg-indigo-950/80 border border-indigo-700/80 text-white flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span>✨</span>
            <span>{pendingNewItems.length} new opportunities discovered in background!</span>
          </div>
          <button
            onClick={applyPendingNewItems}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold transition-colors shadow"
          >
            Load New Opportunities
          </button>
        </div>
      )}

      {/* Partial Outage Notice */}
      {availability && availability.is_partial_results && (
        <div className="rounded-xl border border-amber-800/60 bg-amber-950/40 p-4 text-sm text-amber-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-amber-400 animate-pulse" />
            <span>
              <strong>Partial Results Active:</strong> One or more ingestion satellites are temporarily degraded. Showing available records from operational systems.
            </span>
          </div>
          <div className="text-xs font-mono">
            Core: {availability.core} | LeadHunter: {availability.leadhunter} | Startup Intel: {availability.startup_intelligence}
          </div>
        </div>
      )}

      {/* Type Switcher Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "ALL", label: "All Opportunities", count: counts?.total },
          { id: "JOB", label: "Full-Time Jobs", count: counts?.jobs },
          { id: "FREELANCE", label: "Freelance Leads", count: counts?.freelance },
          { id: "STARTUP_PAIN_POINT", label: "Startup Pain Points", count: counts?.startup_pain_points },
        ].map((tab) => {
          const isActive = activeType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveType(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${isActive
                ? "bg-indigo-600 text-white shadow"
                : "bg-slate-900 text-slate-400 hover:bg-slate-800 hover:text-white border border-slate-800"
                }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${isActive ? "bg-indigo-800 text-indigo-200" : "bg-slate-800 text-slate-400"
                    }`}
                >
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Filters Form */}
      <form
        onSubmit={handleSearchSubmit}
        className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800"
      >
        <div className="md:col-span-2">
          <input
            type="text"
            placeholder="Search keywords, job role, company, or lead name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="All">All Categories</option>
            <option value="Engineering">Engineering / Development</option>
            <option value="Web Performance">Web Performance & SEO</option>
            <option value="Database">Database & Scalability</option>
            <option value="AI">AI & Machine Learning</option>
            <option value="Security">Security & Compliance</option>
          </select>
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            className="flex-1 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white transition-colors"
          >
            Search Pipeline
          </button>
          <button
            type="button"
            onClick={() => {
              setSearchTerm("");
              setSelectedCategory("All");
              setMinScore(0);
              fetchOpportunities();
            }}
            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium text-slate-300 border border-slate-700 transition-colors"
          >
            Reset
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/40 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Pipeline Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(9)].map((_, i) => (
            <div key={i} className="h-60 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : opportunities.length === 0 ? (
        <div className="text-center py-16 rounded-xl bg-slate-900 border border-slate-800 text-slate-400">
          <p className="text-base font-medium text-slate-300">No opportunities match the selected criteria.</p>
          <p className="text-xs text-slate-500 mt-1">Try broadening your search term or switching the category tab.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {opportunities.map((item) => {
            const isJob = item.opportunity_type === "JOB";
            const isFreelance = item.opportunity_type === "FREELANCE";
            const isStartup = item.opportunity_type === "STARTUP_PAIN_POINT";

            const badgeColor = isJob
              ? "bg-blue-950 text-blue-300 border-blue-800"
              : isFreelance
                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                : "bg-purple-950 text-purple-300 border-purple-800";

            const badgeText = isJob ? "Full-Time Job" : isFreelance ? "Freelance Lead" : "Startup Signal";

            return (
              <div
                key={`${item.opportunity_type}-${item.opportunity_id}`}
                className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 hover:border-slate-700 flex flex-col justify-between transition-all"
              >
                <div className="space-y-3">
                  {/* Top Badges */}
                  <div className="flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeColor}`}>
                        {badgeText}
                      </span>
                      {item.type_specific_payload?.is_cold_start && (
                        <span
                          className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border bg-amber-950/80 text-amber-300 border-amber-800 flex items-center gap-1"
                          title={item.type_specific_payload?.cold_start_explanation || "Cold-start recommendation calibrated from profile targets"}
                        >
                          ⚡ Cold-Start
                        </span>
                      )}
                      {item.type_specific_payload?.candidate_feedback_status && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                          Rated: {item.type_specific_payload.candidate_feedback_status}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-slate-400 truncate max-w-[140px]">
                      {item.source_name}
                    </span>
                  </div>

                  {/* Title & Organization */}
                  <div>
                    <h3 className="text-base font-bold text-white line-clamp-2 hover:text-indigo-300 transition-colors">
                      {item.title}
                    </h3>
                    <div className="text-xs font-medium text-indigo-400 mt-1">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>
                  </div>

                  {/* Description preview */}
                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                    {item.short_description}
                  </p>

                  {/* Type-Specific Discriminator Payload */}
                  <div className="pt-2 border-t border-slate-800/80 text-xs text-slate-300 space-y-1">
                    {isJob && (
                      <div className="flex flex-wrap items-center gap-2 font-mono">
                        {item.type_specific_payload.salary_min && (
                          <span className="bg-slate-800 px-2 py-0.5 rounded text-blue-300">
                            ${item.type_specific_payload.salary_min.toLocaleString()} - ${item.type_specific_payload.salary_max?.toLocaleString()}
                          </span>
                        )}
                        <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-400">
                          {item.type_specific_payload.employment_type}
                        </span>
                        {item.type_specific_payload.required_skills?.slice(0, 2).map((s: string) => (
                          <span key={s} className="bg-indigo-950 text-indigo-300 px-1.5 py-0.5 rounded border border-indigo-800">
                            {s}
                          </span>
                        ))}
                      </div>
                    )}

                    {isFreelance && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-emerald-400 font-medium">
                            Category: {item.type_specific_payload.service_category}
                          </span>
                          <span className="text-slate-400">
                            ★ {item.type_specific_payload.rating} ({item.type_specific_payload.reviews_count} reviews)
                          </span>
                        </div>
                        {item.type_specific_payload.is_broken_website && (
                          <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                            Broken Site Detected
                          </span>
                        )}
                      </div>
                    )}

                    {isStartup && (
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-xs font-mono">
                          <span className="text-purple-300 font-semibold">
                            Urgency: {item.type_specific_payload.urgency_score}/10
                          </span>
                          <span className="text-slate-400">
                            Corroborations: {item.type_specific_payload.corroboration_count}
                          </span>
                        </div>
                        {item.type_specific_payload.has_conflicting_evidence && (
                          <span className="inline-block text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
                            Conflicting Signals
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Rating & Footer Controls */}
                <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
                  <div className="flex items-center justify-between gap-1 text-[11px] text-slate-400">
                    <span>Quick rate fit:</span>
                    <div className="flex items-center gap-1">
                      <button
                        type="button"
                        onClick={() => handleQuickFeedback(item, "RELEVANT")}
                        title="Mark as Great Fit (Boosts ranking)"
                        className="px-2 py-0.5 rounded bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-800/60 text-emerald-300 transition-colors"
                      >
                        👍 Fit
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickFeedback(item, "WRONG_SKILLS")}
                        title="Wrong Skills (-50% score penalty)"
                        className="px-2 py-0.5 rounded bg-amber-950/60 hover:bg-amber-900 border border-amber-800/60 text-amber-300 transition-colors"
                      >
                        👎 Skills
                      </button>
                      <button
                        type="button"
                        onClick={() => handleQuickFeedback(item, "LOCATION_UNSUITABLE")}
                        title="Location Unsuitable (-40% penalty)"
                        className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                      >
                        📍 Loc
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center justify-between gap-2 pt-1 border-t border-slate-800/50">
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleToggleSave(item)}
                        disabled={savingId === item.opportunity_id}
                        className={`text-xs font-semibold px-2.5 py-1 rounded transition-colors ${item.is_saved
                          ? "bg-amber-900/60 text-amber-300 border border-amber-700/60"
                          : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                          }`}
                      >
                        {item.is_saved ? "★ Saved" : "☆ Save"}
                      </button>

                      <button
                        onClick={() => setFeedbackItem(item)}
                        className="text-xs font-medium text-slate-400 hover:text-slate-200 px-2 py-1 rounded bg-slate-800/40 hover:bg-slate-800 transition-colors"
                        title="Provide detailed candidate feedback"
                      >
                        Feedback
                      </button>

                      <button
                        onClick={() => setReportItem(item)}
                        className="text-xs font-medium text-rose-400/80 hover:text-rose-300 px-2 py-1 rounded bg-rose-950/30 hover:bg-rose-950/60 border border-rose-900/40 transition-colors"
                        title="Report job posting or suspicious content"
                      >
                        🚩 Report
                      </button>
                    </div>

                    {item.source_url ? (
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                      >
                        Apply / Visit →
                      </a>
                    ) : null}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Candidate Relevance Feedback Modal */}
      {feedbackItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Relevance & Match Calibration</h3>
              <button
                onClick={() => setFeedbackItem(null)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Personalize recommendations for: <strong className="text-white">{feedbackItem.title}</strong>
            </p>

            <form onSubmit={handleSubmitFeedback} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  How does this opportunity fit you?
                </label>
                <select
                  value={feedbackCategory}
                  onChange={(e) => setFeedbackCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="RELEVANT">Great Fit (Boost this type in feed)</option>
                  <option value="WRONG_SKILLS">Wrong Skills / Tech Stack mismatch (-50% penalty)</option>
                  <option value="LOCATION_UNSUITABLE">Unsuitable Location / Incompatible Timezone (-40% penalty)</option>
                  <option value="EXPERIENCE_TOO_HIGH">Experience requirement too high (Seniority mismatch)</option>
                  <option value="EXPERIENCE_TOO_LOW">Experience requirement too low (Below my seniority)</option>
                  <option value="WORK_MODE_UNSUITABLE">Work Mode Unsuitable (e.g. requires on-site)</option>
                  <option value="ALREADY_APPLIED">Already applied or interviewed</option>
                  <option value="DUPLICATE">Duplicate of another listing</option>
                  <option value="JOB_CLOSED">Position closed or expired</option>
                  <option value="NOT_RELEVANT">Not relevant to my career goals (Suppress)</option>
                  <option value="OTHER">Other Reason</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Optional Details
                </label>
                <textarea
                  value={feedbackExplanation}
                  onChange={(e) => setFeedbackExplanation(e.target.value)}
                  placeholder="e.g. I prefer Python backend roles over frontend..."
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              {feedbackStatusMsg && (
                <div className="p-3 rounded-lg bg-emerald-950 text-emerald-300 text-xs border border-emerald-800">
                  {feedbackStatusMsg}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setFeedbackItem(null)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingFeedback}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-sm"
                >
                  {submittingFeedback ? "Recording..." : "Save Calibration"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Trust & Moderation Report Modal (Module G) */}
      {reportItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>🚩</span> Report Listing Issue
              </h3>
              <button
                onClick={() => setReportItem(null)}
                className="text-slate-400 hover:text-white text-sm"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Report quality or trust concerns for: <strong className="text-white">{reportItem.title}</strong>
            </p>

            <form onSubmit={handleSubmitReport} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Report Category *
                </label>
                <select
                  value={reportType}
                  onChange={(e) => setReportType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-rose-500"
                >
                  <option value="SUSPICIOUS_JOB">Suspicious or Fraudulent Listing</option>
                  <option value="PAYMENT_REQUEST">Requires Payment or Sensitive Financial Info</option>
                  <option value="MISLEADING_DESCRIPTION">Misleading Job Title, Role, or Compensation</option>
                  <option value="BROKEN_LINK">Broken or Expired Application Link</option>
                  <option value="COMPANY_IMPERSONATION">Impersonating Known Brand / Fake Recruiter</option>
                  <option value="INCORRECT_LOCATION">Inaccurate Location / False Remote Claim</option>
                  <option value="INCORRECT_STATUS">Position Is Already Filled / Inactive</option>
                  <option value="OTHER">Other Quality or Security Issue</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Notes / Observed Evidence
                </label>
                <textarea
                  value={reportNotes}
                  onChange={(e) => setReportNotes(e.target.value)}
                  placeholder="Describe why this listing should be reviewed or moderated..."
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
                />
              </div>

              {reportStatusMsg && (
                <div className="p-3 rounded-lg bg-emerald-950 text-emerald-300 text-xs border border-emerald-800">
                  {reportStatusMsg}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setReportItem(null)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingReport}
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white shadow-sm"
                >
                  {submittingReport ? "Submitting..." : "Submit Report"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
