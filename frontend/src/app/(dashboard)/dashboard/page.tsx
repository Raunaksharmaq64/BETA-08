"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";
import VerificationProofModal, { VerificationItem } from "@/components/opportunities/VerificationProofModal";

interface SummaryMetrics {
  total_opportunities: number;
  total_jobs: number;
  total_freelance: number;
  total_startups: number;
  total_saved: number;
  active_applications: number;
  high_urgency_signals: number;
  new_this_week: number;
}

interface SourceHealth {
  core_career_engine: string;
  leadhunter_satellite: string;
  startup_intelligence_satellite: string;
  all_systems_operational: boolean;
}

interface OpportunityItem {
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
  is_saved?: boolean;
  is_new_signal?: boolean;
  opportunity_domain?: string;
  domain_display_name?: string;
  domain_icon?: string;
  candidate_fit?: {
    fit_score: number;
    fit_percentage: number;
    fit_rating: string;
    how_you_fit: string;
    matched_skills: string[];
    missing_skills: string[];
  };
  trust_metrics?: any;
  type_specific_payload: any;
}

export default function UnifiedDashboardPage() {
  const [metrics, setMetrics] = useState<SummaryMetrics | null>(() => {
    return fastCache.get<SummaryMetrics>("dash_metrics") || null;
  });
  const [health, setHealth] = useState<SourceHealth | null>(() => {
    return fastCache.get<SourceHealth>("dash_health") || null;
  });
  const [recentOpportunities, setRecentOpportunities] = useState<OpportunityItem[]>(() => {
    return fastCache.get<OpportunityItem[]>("dash_recent_opps") || [];
  });
  const [loading, setLoading] = useState(() => {
    return !fastCache.get<SummaryMetrics>("dash_metrics");
  });
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [proofItem, setProofItem] = useState<VerificationItem | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchDashboard = async (forceFresh = false) => {
    if (!metrics) setLoading(true);
    if (forceFresh) setIsRefreshing(true);
    setError(null);
    try {
      const url = forceFresh ? `/dashboard?refresh=true&_t=${Date.now()}` : "/dashboard";
      const res: any = await apiClient.get(url);
      const data = res.data;
      setMetrics(data.summary_metrics);
      setHealth(data.source_health);
      setRecentOpportunities(data.recent_opportunities || []);
      fastCache.set("dash_metrics", data.summary_metrics, 30000);
      fastCache.set("dash_health", data.source_health, 30000);
      fastCache.set("dash_recent_opps", data.recent_opportunities || [], 30000);
    } catch (err: any) {
      if (!metrics) setError(err?.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    // Always trigger fresh background sync on reload / navigation
    fetchDashboard(true);
  }, []);

  const handleToggleSave = async (item: OpportunityItem) => {
    setSavingId(item.opportunity_id);
    try {
      if (item.is_saved) {
        await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
        item.is_saved = false;
        if (metrics) setMetrics({ ...metrics, total_saved: Math.max(0, metrics.total_saved - 1) });
      } else {
        await apiClient.post(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`, {
          notes: "Saved from Unified Dashboard",
        });
        item.is_saved = true;
        if (metrics) setMetrics({ ...metrics, total_saved: metrics.total_saved + 1 });
      }
      setRecentOpportunities([...recentOpportunities]);
    } catch (err: any) {
      alert(err?.message || "Failed to update saved status.");
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Career Intelligence Dashboard
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Unified view across verified full-time jobs, freelance gigs, startup pain points, and applications.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchDashboard(true)}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors disabled:opacity-60"
            title="Fetch real-time updates and fresh metrics"
          >
            <span className={isRefreshing ? "animate-spin" : ""}>🔄</span>
            {isRefreshing ? "Refreshing..." : "Refresh Live Data"}
          </button>
          <Link
            href="/opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            Explore All Opportunities →
          </Link>
          <Link
            href="/saved-opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            View Bookmarks ({metrics?.total_saved ?? 0})
          </Link>
        </div>
      </div>

      {/* System Health Banner */}
      {health && (
        <div
          className={`rounded-xl border p-4 text-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 ${
            health.all_systems_operational
              ? "bg-emerald-950/40 border-emerald-800/60 text-emerald-300"
              : "bg-amber-950/40 border-amber-800/60 text-amber-300"
          }`}
        >
          <div className="flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                health.all_systems_operational ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
              }`}
            />
            <span className="font-semibold">
              {health.all_systems_operational
                ? "All Ingestion Satellites Operational"
                : "Partial Service Degradation — Returning Available Aggregates"}
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs font-mono">
            <span>Core: <strong className="text-white">{health.core_career_engine}</strong></span>
            <span>LeadHunter: <strong className="text-white">{health.leadhunter_satellite}</strong></span>
            <span>Startup Intel: <strong className="text-white">{health.startup_intelligence_satellite}</strong></span>
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-rose-800/60 bg-rose-950/40 p-4 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Summary KPI Grid */}
      {loading && !metrics ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 animate-pulse">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-28 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : metrics ? (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400">
            <span className="font-semibold tracking-wide uppercase text-slate-300">Live Opportunities Overview</span>
            <span className="bg-slate-850 px-2.5 py-1 rounded border border-slate-750 text-slate-300 font-mono text-[11px] sm:text-xs">
              Reconciled: {metrics.total_opportunities} = {metrics.total_jobs} (Jobs) + {metrics.total_freelance} (Freelance) + {metrics.total_startups} (Startups)
            </span>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* 1. Total Opportunities */}
            <Link
              href="/opportunities"
              className="p-5 rounded-xl bg-gradient-to-br from-indigo-900/40 to-slate-900 border border-indigo-700/50 hover:border-indigo-500 transition-all group"
            >
              <div className="text-xs font-medium text-indigo-300 uppercase tracking-wider">Total Opportunities</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-indigo-400 transition-colors">
                {metrics.total_opportunities}
              </div>
              <div className="mt-1 text-xs text-slate-400">Aggregated live openings</div>
            </Link>

            {/* 2. Canonical Jobs */}
            <Link
              href="/opportunities?type=JOB"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-blue-600 transition-all group"
            >
              <div className="text-xs font-medium text-blue-400 uppercase tracking-wider">Full-Time Jobs</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-blue-400 transition-colors">
                {metrics.total_jobs}
              </div>
              <div className="mt-1 text-xs text-slate-400">Verified canonical openings</div>
            </Link>

            {/* 3. Freelance Leads */}
            <Link
              href="/opportunities?type=FREELANCE"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-600 transition-all group"
            >
              <div className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Freelance Projects</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-emerald-400 transition-colors">
                {metrics.total_freelance}
              </div>
              <div className="mt-1 text-xs text-slate-400">Direct business outreach</div>
            </Link>

            {/* 4. Startup Pain Points */}
            <Link
              href="/opportunities?type=STARTUP_PAIN_POINT"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-600 transition-all group"
            >
              <div className="text-xs font-medium text-purple-400 uppercase tracking-wider">Startup Pain Points</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-purple-400 transition-colors">
                {metrics.total_startups}
              </div>
              <div className="mt-1 text-xs text-slate-400">Technical bottlenecks & demands</div>
            </Link>

            {/* 5. Total Bookmarks */}
            <Link
              href="/saved-opportunities"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-amber-600 transition-all group"
            >
              <div className="text-xs font-medium text-amber-400 uppercase tracking-wider">Saved Bookmarks</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-amber-400 transition-colors">
                {metrics.total_saved}
              </div>
              <div className="mt-1 text-xs text-slate-400">Cross-module saved items</div>
            </Link>

            {/* 6. Active CRM Applications */}
            <Link
              href="/applications"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-600 transition-all group"
            >
              <div className="text-xs font-medium text-cyan-400 uppercase tracking-wider">Active Applications</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-cyan-400 transition-colors">
                {metrics.active_applications}
              </div>
              <div className="mt-1 text-xs text-slate-400">Tracked in Application CRM</div>
            </Link>

            {/* 7. High Urgency Startups */}
            <Link
              href="/opportunities?type=STARTUP_PAIN_POINT"
              className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-rose-600 transition-all group"
            >
              <div className="text-xs font-medium text-rose-400 uppercase tracking-wider">High-Urgency Problems (≥8/10)</div>
              <div className="mt-2 text-3xl font-black text-white group-hover:text-rose-400 transition-colors">
                {metrics.high_urgency_signals}
              </div>
              <div className="mt-1 text-xs text-slate-400">High-conviction founders</div>
            </Link>

            {/* 8. New This Week */}
            <div className="p-5 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-xs font-medium text-teal-400 uppercase tracking-wider">Discovered This Week</div>
              <div className="mt-2 text-3xl font-black text-white">
                +{metrics.new_this_week}
              </div>
              <div className="mt-1 text-xs text-slate-400">Ingested past 7 days</div>
            </div>
          </div>
        </div>
      ) : null}

      {/* Recent Opportunities Across Modules */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-xl font-bold text-white">Recent Live Opportunities</h2>
            <p className="text-xs text-slate-400">Latest discovered positions and pain points across live job boards, freelance leads, and startup intelligence.</p>
          </div>
          <Link
            href="/opportunities"
            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View all opportunities →
          </Link>
        </div>

        {loading && recentOpportunities.length === 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-44 rounded-xl bg-slate-900 border border-slate-800 animate-pulse" />
            ))}
          </div>
        ) : recentOpportunities.length === 0 ? (
          <div className="text-center py-12 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 text-sm">
            No opportunities discovered yet. Trigger connectors or lead discovery to populate.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentOpportunities.map((item) => {
              const typeBadgeColors = {
                JOB: "bg-blue-900/60 text-blue-300 border-blue-700/60",
                FREELANCE: "bg-emerald-900/60 text-emerald-300 border-emerald-700/60",
                STARTUP_PAIN_POINT: "bg-purple-900/60 text-purple-300 border-purple-700/60",
              };

              const typeLabels = {
                JOB: "Full-Time Job",
                FREELANCE: "Freelance Lead",
                STARTUP_PAIN_POINT: "Startup Pain Point",
              };

              return (
                <div
                  key={`${item.opportunity_type}-${item.opportunity_id}`}
                  className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 flex flex-col justify-between transition-all"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                            typeBadgeColors[item.opportunity_type] || "bg-slate-800 text-slate-300 border-slate-700"
                          }`}
                        >
                          {typeLabels[item.opportunity_type]}
                        </span>
                        {item.domain_display_name && (
                          <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {item.domain_icon} {item.domain_display_name}
                          </span>
                        )}
                        {item.is_new_signal && (
                          <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 animate-pulse">
                            ✨ NEW
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-slate-400 font-medium">
                        {item.source_name}
                      </span>
                    </div>

                    <h3 className="text-base font-semibold text-white line-clamp-1">
                      {item.title}
                    </h3>
                    <div className="text-xs text-indigo-400 font-medium">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>

                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                      {item.short_description}
                    </p>

                    {/* Dynamic Candidate Fit */}
                    {item.candidate_fit && (
                      <div className="p-2 rounded-lg bg-slate-950/80 border border-indigo-950/80 text-[11px] space-y-1">
                        <div className="flex items-center justify-between font-bold text-white">
                          <span className="flex items-center gap-1">
                            <span
                              className={`w-1.5 h-1.5 rounded-full ${
                                item.candidate_fit.fit_percentage >= 80 ? "bg-emerald-400" : "bg-blue-400"
                              }`}
                            />
                            Fit: {item.candidate_fit.fit_percentage}% ({item.candidate_fit.fit_rating})
                          </span>
                          <span className="text-[10px] text-indigo-300 font-mono">Resume Synergy</span>
                        </div>
                        <p className="text-slate-300 line-clamp-1 text-[11px]">
                          {item.candidate_fit.how_you_fit}
                        </p>
                      </div>
                    )}

                    {/* Specific payload badges */}
                    <div className="text-xs text-slate-400 flex flex-wrap gap-2 pt-1 font-mono">
                      {item.opportunity_type === "JOB" && item.type_specific_payload.salary_min && (
                        <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-300">
                          ${item.type_specific_payload.salary_min.toLocaleString()} - ${item.type_specific_payload.salary_max?.toLocaleString()}
                        </span>
                      )}
                      {item.opportunity_type === "FREELANCE" && (
                        <span className="bg-slate-800 px-2 py-0.5 rounded text-emerald-300">
                          {item.type_specific_payload.service_category}
                        </span>
                      )}
                      {item.opportunity_type === "STARTUP_PAIN_POINT" && (
                        <span className="bg-slate-800 px-2 py-0.5 rounded text-rose-300">
                          Urgency: {item.type_specific_payload.urgency_score}/10
                        </span>
                      )}
                    </div>

                    {/* Trust Tier & Ghost Job Indicator */}
                    {item.trust_metrics && (
                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-1 flex-wrap text-[10px]">
                        <span className="inline-flex items-center gap-1 font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          {item.trust_metrics.trust_tier_label}
                        </span>
                        <span className="text-slate-400 font-mono">
                          👻 {item.trust_metrics.ghost_job_risk.urgency_label}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2 flex-wrap">
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => handleToggleSave(item)}
                        disabled={savingId === item.opportunity_id}
                        className={`text-xs font-semibold px-2.5 py-1 rounded transition-colors ${
                          item.is_saved
                            ? "bg-amber-900/60 text-amber-300 border border-amber-700/60"
                            : "bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
                        }`}
                      >
                        {item.is_saved ? "★ Bookmarked" : "☆ Save"}
                      </button>

                      <button
                        type="button"
                        onClick={() => setProofItem(item as any)}
                        className="text-xs font-semibold px-2 py-1 rounded bg-slate-800 hover:bg-slate-750 text-indigo-300 border border-indigo-700/50 hover:border-indigo-400 transition-colors flex items-center gap-1"
                        title="Inspect verifiable proof and ATS handshake"
                      >
                        <span>🛡️</span>
                        <span>Proof</span>
                      </button>

                      {item.opportunity_type === "JOB" && (
                        <Link
                          href={`/jobs/${item.opportunity_id}`}
                          className="text-xs font-semibold px-2 py-1 rounded bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 border border-indigo-700/60 transition-colors flex items-center gap-1"
                          title="View match breakdown and missing skills for your resume"
                        >
                          <span>🎯</span>
                          <span>Match & Gaps</span>
                        </Link>
                      )}
                    </div>

                    {item.source_url ? (
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors"
                      >
                        Apply / Source →
                      </a>
                    ) : (
                      <Link
                        href={`/opportunities?type=${item.opportunity_type}`}
                        className="text-xs font-medium text-slate-400 hover:text-white transition-colors"
                      >
                        Details →
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Authenticity & Verification Proof Modal */}
      <VerificationProofModal
        item={proofItem}
        onClose={() => setProofItem(null)}
      />
    </div>
  );
}

