"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";

interface StartupOpportunity {
  id: string;
  service_record_id?: string;
  startup_name: string;
  domain?: string;
  website_url?: string;
  category: string;
  detected_signal: string;
  pain_point_description?: string;
  problem_explanation?: string;
  how_to_solve_strategy?: string;
  ai_insight?: string;
  ai_opportunity?: string;
  contact_email?: string;
  twitter_url?: string;
  linkedin_url?: string;
  github_url?: string;
  contact_page_url?: string;
  contact_info?: {
    email?: string;
    twitter?: string;
    linkedin?: string;
    github?: string;
    contact_page?: string;
  };
  urgency_score: number;
  score_explanation?: string;
  primary_source: string;
  source_url?: string;
  status: string;
  corroboration_count: number;
  has_conflicting_evidence: boolean;
  published_at: string;
  first_seen_at?: string;
}

export default function StartupIntelligenceDashboardPage() {
  const [opportunities, setOpportunities] = useState<StartupOpportunity[]>(() => {
    return fastCache.get<StartupOpportunity[]>("startups_all") || [];
  });
  const [loading, setLoading] = useState(() => {
    return (fastCache.get<StartupOpportunity[]>("startups_all") || []).length === 0;
  });
  const [isFiltering, setIsFiltering] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [degradedMessage, setDegradedMessage] = useState<string | null>(null);

  // Scan controls
  const [scanCategory, setScanCategory] = useState<string>("All");
  const [scanning, setScanning] = useState(false);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [minScore, setMinScore] = useState<number>(0);
  const [searchTerm, setSearchTerm] = useState("");

  // Auto-refresh and live states
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string>("Just now");
  const [pendingNewSignals, setPendingNewSignals] = useState<StartupOpportunity[]>([]);

  const fetchOpportunities = useCallback(async (isBackground = false) => {
    const cacheKey = `startups_${selectedCategory}_${minScore}_${searchTerm.trim()}`;
    if (!isBackground) {
      const cached = fastCache.get<StartupOpportunity[]>(cacheKey);
      if (cached && cached.length > 0) {
        setOpportunities(cached);
        setLoading(false);
        setIsFiltering(false);
      } else if (opportunities.length > 0) {
        setIsFiltering(true);
      } else {
        setLoading(true);
      }
    } else {
      setIsRefreshing(true);
    }

    setError(null);
    try {
      let url = "/startups?per_page=50";
      if (selectedCategory !== "All") url += `&category=${encodeURIComponent(selectedCategory)}`;
      if (minScore > 0) url += `&min_score=${minScore}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

      const res = await apiClient.get<any>(url);
      const fetched: StartupOpportunity[] = res.data || [];

      fastCache.set(cacheKey, fetched, 120000);
      if (selectedCategory === "All" && minScore === 0 && !searchTerm) {
        fastCache.set("startups_all", fetched, 120000);
      }

      if (isBackground) {
        setOpportunities(prev => {
          if (prev.length > 0) {
            const currentIds = new Set(prev.map(o => o.id));
            const newOnes = fetched.filter(o => !currentIds.has(o.id));
            if (newOnes.length > 0) {
              setPendingNewSignals(newOnes);
              return prev;
            }
          }
          return fetched;
        });
      } else {
        setOpportunities(fetched);
        setPendingNewSignals([]);
      }
      setLastRefreshedAt(new Date().toLocaleTimeString());
    } catch (err: any) {
      if (!isBackground && opportunities.length === 0) setError(err?.message || "Failed to load startup opportunities.");
    } finally {
      setLoading(false);
      setIsFiltering(false);
      setIsRefreshing(false);
    }
  }, [selectedCategory, minScore, searchTerm, opportunities.length]);

  const checkIntegration = useCallback(async () => {
    try {
      const res: any = await apiClient.get("/startups/integration-status");
      if (res?.upstream_health?.status === "degraded" || res?.circuit_breaker?.state === "OPEN") {
        setDegradedMessage(
          "Startup Intelligence satellite service is currently offline or unreachable. Circuit breaker is active; serving cached Core opportunities."
        );
      } else {
        setDegradedMessage(null);
      }
    } catch {
      setDegradedMessage(
        "Startup Intelligence service status probe timed out. Displaying Core-cached records."
      );
    }
  }, []);

  const applyPendingSignals = () => {
    setOpportunities(prev => [...pendingNewSignals, ...prev]);
    setPendingNewSignals([]);
  };

  useEffect(() => {
    fetchOpportunities(false);
    checkIntegration();
  }, [fetchOpportunities, checkIntegration]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchOpportunities(true);
    }, 25000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchOpportunities]);

  const handleScanLeads = async () => {
    setScanning(true);
    setError(null);
    try {
      const payload: any = { limit: 50 };
      if (scanCategory !== "All") payload.category = scanCategory;
      const res: any = await apiClient.post("/startups/scan-leads", payload);
      if (res?.degraded) {
        setDegradedMessage(res.message);
      } else {
        setDegradedMessage(null);
      }
      await fetchOpportunities();
    } catch (err: any) {
      setError(err?.message || "Failed to scan startup opportunities.");
    } finally {
      setScanning(false);
    }
  };

  const handleSave = async (oppId: string) => {
    try {
      await apiClient.post(`/startups/${oppId}/save`, { notes: "Bookmarked from dashboard" });
      alert("Opportunity saved to your bookmarks!");
    } catch (err: any) {
      alert("Failed to save opportunity: " + (err?.message || "Error"));
    }
  };

  // KPIs
  const totalCount = opportunities.length;
  const highUrgencyCount = opportunities.filter((o) => o.urgency_score >= 8).length;
  const devCount = opportunities.filter((o) => o.category === "Development").length;
  const perfCount = opportunities.filter((o) => o.category === "Performance").length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Page Title & Quick Links */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Startup Intelligence & Pain Point Explorer
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Discover real technical bottlenecks and hiring signals from early-stage platforms with verifiable evidence.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/startups/saved"
            className="neo-pill px-4 py-2 text-xs sm:text-sm font-bold text-slate-900 hover:text-indigo-600 rounded-xl transition-all shadow-sm"
          >
            Saved Bookmarks ★
          </Link>
          <button
            onClick={handleScanLeads}
            disabled={scanning}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50 shadow-sm flex items-center gap-2 transition-colors"
          >
            {scanning ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Scanning Feeds...
              </>
            ) : (
              "Scan & Refresh Signals"
            )}
          </button>
        </div>
      </div>

      {/* Live Auto-Refresh & Controls Bar */}
      <div className="neo-box flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl text-xs font-bold text-slate-800 border border-white/90">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
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
            className="neo-pill inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-slate-800 hover:text-indigo-600 font-bold transition-all disabled:opacity-50"
          >
            <span className={isRefreshing ? "animate-spin" : ""}>⟳</span>
            {isRefreshing ? "Refreshing..." : "Refresh Signals"}
          </button>
        </div>
      </div>

      {/* Floating / Inline Banner when new signals are discovered */}
      {pendingNewSignals.length > 0 && (
        <div className="p-4 rounded-xl bg-indigo-950/80 border border-indigo-700/80 text-white flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span>⚡</span>
            <span>{pendingNewSignals.length} new startup pain-point signals detected in background!</span>
          </div>
          <button
            onClick={applyPendingSignals}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold transition-colors shadow"
          >
            Load New Signals
          </button>
        </div>
      )}

      {/* Degraded State Banner */}
      {degradedMessage && (
        <div className="p-4 bg-amber-950/40 border border-amber-800/60 rounded-xl text-amber-300 flex items-start gap-3">
          <span className="text-xl">⚠️</span>
          <div>
            <h4 className="font-semibold text-sm">Degraded Resilience Mode Active</h4>
            <p className="text-xs mt-0.5 text-amber-400/90">{degradedMessage}</p>
          </div>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Total Opportunities
          </div>
          <div className="text-3xl font-black text-slate-900 mt-2">{totalCount}</div>
          <div className="text-xs text-slate-500 mt-1">Discovered across tech feeds</div>
        </div>
        <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-rose-400">
            High Urgency (8-10)
          </div>
          <div className="text-3xl font-black text-rose-800 mt-2">{highUrgencyCount}</div>
          <div className="text-xs text-rose-400/70 mt-1">Active hiring or critical bugs</div>
        </div>
        <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            Development Gaps
          </div>
          <div className="text-3xl font-black text-indigo-800 mt-2">{devCount}</div>
          <div className="text-xs text-indigo-400/70 mt-1">Founders seeking dev capacity</div>
        </div>
        <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Performance / Speed
          </div>
          <div className="text-3xl font-black text-emerald-800 mt-2">{perfCount}</div>
          <div className="text-xs text-emerald-400/70 mt-1">Latency & SEO vulnerabilities</div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="neo-box p-5 rounded-2xl border border-white/90 shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by startup name, problem statement, or tech keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchOpportunities()}
              className="w-full px-4 py-2.5 text-xs sm:text-sm neo-inset rounded-xl text-slate-900 font-bold focus:outline-none"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3.5 py-2 text-xs sm:text-sm neo-inset rounded-xl text-slate-900 font-bold focus:outline-none"
            >
              <option value="All">All Categories</option>
              <option value="Development">Development</option>
              <option value="Performance">Performance</option>
              <option value="UI/UX">UI/UX</option>
              <option value="SEO">SEO</option>
              <option value="AI">AI</option>
            </select>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="px-3.5 py-2 text-xs sm:text-sm neo-inset rounded-xl text-slate-900 font-bold focus:outline-none"
            >
              <option value={0}>Any Urgency Score</option>
              <option value={7}>Score 7+ (Urgent)</option>
              <option value={8}>Score 8+ (High Urgency)</option>
              <option value={9}>Score 9+ (Critical)</option>
            </select>
            <button
              onClick={() => fetchOpportunities(false)}
              className="neo-btn-primary px-5 py-2 text-xs sm:text-sm font-bold rounded-xl transition-all shadow-md cursor-pointer"
            >
              Filter Signals
            </button>
          </div>
        </div>
      </div>

      {/* Top Background Revalidation Glow Bar */}
      {(isFiltering || isRefreshing) && (
        <div className="fixed top-0 left-0 right-0 h-[2.5px] bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 animate-pulse z-50 shadow-sm" />
      )}

      {/* Opportunity Cards List */}
      {loading && opportunities.length === 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-sm">
          {error}
        </div>
      ) : opportunities.length === 0 ? (
        <div className="p-12 bg-slate-900/60 rounded-xl border border-slate-800 text-center">
          <p className="text-base font-semibold text-slate-300">No startup opportunities found</p>
          <p className="text-xs text-slate-500 mt-1">
            Try adjusting filters or click &quot;Scan & Refresh Signals&quot; to fetch live leads.
          </p>
        </div>
      ) : (
        <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 transition-opacity duration-150 ${isFiltering || isRefreshing ? "opacity-80" : "opacity-100"}`}>
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              className="p-5 neo-card neo-box-hover rounded-2xl border border-white/90 shadow-sm flex flex-col justify-between transition-all"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-900/50 text-purple-300 border border-purple-700/60">
                    {opp.category}
                  </span>
                  <span
                    className={`text-xs font-bold px-2 py-0.5 rounded-full border ${opp.urgency_score >= 8
                        ? "bg-rose-950/60 text-rose-300 border-rose-800/60"
                        : opp.urgency_score >= 6
                          ? "bg-amber-950/60 text-amber-300 border-amber-800/60"
                          : "bg-slate-800 text-slate-300 border-slate-700"
                      }`}
                  >
                    Urgency {opp.urgency_score}/10
                  </span>
                </div>

                <h3 className="font-bold text-white text-base leading-snug">
                  {opp.startup_name}
                </h3>
                {opp.domain && (
                  <p className="text-xs text-indigo-400 font-mono mt-0.5">{opp.domain}</p>
                )}

                <p className="text-xs text-slate-300 mt-3 line-clamp-2 leading-relaxed font-medium">
                  {opp.detected_signal}
                </p>

                {/* Problem Breakdown & How to Solve Highlights */}
                {opp.problem_explanation && (
                  <div className="mt-2.5 p-2 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] text-slate-300 leading-snug">
                    <span className="text-rose-400 font-semibold flex items-center gap-1 mb-0.5">
                      <span>🚨</span> Problem Root Cause:
                    </span>
                    <p className="line-clamp-2 text-slate-400">{opp.problem_explanation}</p>
                  </div>
                )}

                {opp.how_to_solve_strategy && (
                  <div className="mt-1.5 p-2 rounded-lg bg-indigo-950/40 border border-indigo-900/50 text-[11px] text-indigo-200 leading-snug">
                    <span className="text-emerald-400 font-semibold flex items-center gap-1 mb-0.5">
                      <span>🛠️</span> Action Plan:
                    </span>
                    <p className="line-clamp-2 text-slate-300">{opp.how_to_solve_strategy}</p>
                  </div>
                )}

                {/* Founder & Company Social Accounts */}
                {(() => {
                  const email = opp.contact_email || opp.contact_info?.email;
                  const twitter = opp.twitter_url || opp.contact_info?.twitter;
                  const linkedin = opp.linkedin_url || opp.contact_info?.linkedin;
                  const github = opp.github_url || opp.contact_info?.github;
                  const contactPage = opp.contact_page_url || opp.contact_info?.contact_page;
                  const hasSocial = email || twitter || linkedin || github || contactPage;

                  if (!hasSocial) return null;
                  return (
                    <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center gap-2 flex-wrap">
                      <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider mr-1">Social:</span>
                      {linkedin && (
                        <a
                          href={linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-950 text-blue-300 border border-blue-800/60 hover:bg-blue-900 transition-colors flex items-center gap-1"
                          title="LinkedIn Profile / Company"
                        >
                          <span>💼</span> LinkedIn
                        </a>
                      )}
                      {twitter && (
                        <a
                          href={twitter}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-950 text-sky-300 border border-sky-800/60 hover:bg-slate-800 transition-colors flex items-center gap-1"
                          title="Twitter / X Profile"
                        >
                          <span>𝕏</span> Twitter
                        </a>
                      )}
                      {github && (
                        <a
                          href={github}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-950 text-slate-200 border border-slate-700 hover:bg-slate-800 transition-colors flex items-center gap-1"
                          title="GitHub Repository / Organization"
                        >
                          <span>🐙</span> GitHub
                        </a>
                      )}
                      {email && (
                        <a
                          href={`mailto:${email}`}
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800/60 hover:bg-emerald-900 transition-colors flex items-center gap-1"
                          title={`Email founder: ${email}`}
                        >
                          <span>✉️</span> Email
                        </a>
                      )}
                      {contactPage && (
                        <a
                          href={contactPage}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2 py-0.5 rounded text-[11px] font-semibold bg-purple-950 text-purple-300 border border-purple-800/60 hover:bg-purple-900 transition-colors flex items-center gap-1"
                          title="Official Contact Page"
                        >
                          <span>🌐</span> Contact
                        </a>
                      )}
                    </div>
                  );
                })()}

                <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span>Source: {opp.primary_source}</span>
                  <span className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    {opp.corroboration_count} signal{opp.corroboration_count > 1 ? "s" : ""}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2">
                <Link
                  href={`/startups/${opp.id}`}
                  className="flex-1 text-center py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-colors"
                >
                  Explore Pain Point →
                </Link>
                <button
                  onClick={() => handleSave(opp.id)}
                  title="Bookmark opportunity"
                  className="neo-pill px-3.5 py-1.5 text-xs font-bold text-slate-900 hover:text-indigo-600 rounded-xl transition-all"
                >
                  ★ Save
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
