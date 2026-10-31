"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface StartupOpportunity {
  id: string;
  service_record_id?: string;
  startup_name: string;
  domain?: string;
  website_url?: string;
  category: string;
  detected_signal: string;
  pain_point_description?: string;
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
  const [opportunities, setOpportunities] = useState<StartupOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
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
    if (!isBackground) setLoading(true);
    else setIsRefreshing(true);
    setError(null);
    try {
      let url = "/startups?per_page=50";
      if (selectedCategory !== "All") url += `&category=${encodeURIComponent(selectedCategory)}`;
      if (minScore > 0) url += `&min_score=${minScore}`;
      if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

      const res = await apiClient.get<any>(url);
      const fetched: StartupOpportunity[] = res.data || [];

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
      if (!isBackground) setError(err?.message || "Failed to load startup opportunities.");
    } finally {
      if (!isBackground) setLoading(false);
      setIsRefreshing(false);
    }
  }, [selectedCategory, minScore, searchTerm]);

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

  useEffect(() => {
    fetchOpportunities(false);
    checkIntegration();
  }, [fetchOpportunities, checkIntegration]);

  // Periodic polling for realtime detection
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchOpportunities(true);
    }, 25000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchOpportunities]);

  const applyPendingSignals = () => {
    setOpportunities(prev => {
      const currentIds = new Set(prev.map(o => o.id));
      const newlyAdded = pendingNewSignals.filter(o => !currentIds.has(o.id));
      return [...newlyAdded, ...prev];
    });
    setPendingNewSignals([]);
  };

  const handleScanLeads = async () => {
    setScanning(true);
    setError(null);
    try {
      const payload: any = {};
      if (scanCategory !== "All") payload.category = scanCategory;
      await apiClient.post("/startups/scan", payload);
      await fetchOpportunities(false);
    } catch (err: any) {
      setError(err?.message || "Failed to trigger real-time signal detection scan.");
    } finally {
      setScanning(false);
    }
  };

  const handleSave = async (oppId: string) => {
    try {
      await apiClient.post(`/startups/${oppId}/save`, { notes: "Bookmarked from explorer" });
      alert("Opportunity bookmarked to your saved list!");
    } catch (err: any) {
      alert("Failed to bookmark opportunity: " + (err?.message || "Error"));
    }
  };

  // KPIs
  const totalCount = opportunities.length;
  const highUrgencyCount = opportunities.filter((o) => o.urgency_score >= 8).length;
  const devCount = opportunities.filter((o) => o.category === "Development").length;
  const perfCount = opportunities.filter((o) => o.category === "Performance").length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
        <div className="flex flex-wrap items-center gap-3">
          <Link
            href="/startups/saved"
            className="px-4 py-2 text-sm font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition"
          >
            Saved Opportunities
          </Link>
          <button
            onClick={handleScanLeads}
            disabled={scanning}
            className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 disabled:opacity-50 shadow-sm flex items-center gap-2 transition"
          >
            {scanning ? (
              <>
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                Scanning Feeds...
              </>
            ) : (
              "Scan & Refresh Signals ⚡"
            )}
          </button>
        </div>
      </div>

      {/* Live Auto-Refresh & Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg font-semibold transition-colors border ${
              autoRefresh
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
            {isRefreshing ? "Refreshing..." : "Refresh Signals"}
          </button>
        </div>
      </div>

      {/* Floating / Inline Banner when new signals are discovered */}
      {pendingNewSignals.length > 0 && (
        <div className="p-4 rounded-xl bg-indigo-950/80 border border-indigo-700/80 text-white flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <span>⚡</span>
            <span>{pendingNewSignals.length} new startup pain-point signals detected in background!</span>
          </div>
          <button
            onClick={applyPendingSignals}
            className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold transition-colors shadow shrink-0"
          >
            Load New Signals
          </button>
        </div>
      )}

      {/* Degraded State Banner */}
      {degradedMessage && (
        <div className="p-4 bg-amber-950/40 border border-amber-800/80 rounded-xl text-amber-200 flex items-start gap-3 text-xs">
          <span className="text-base">⚠️</span>
          <div>
            <h4 className="font-semibold text-sm text-amber-300">Degraded Resilience Mode Active</h4>
            <p className="mt-0.5 text-amber-200/90 leading-relaxed">{degradedMessage}</p>
          </div>
        </div>
      )}

      {/* KPI Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Total Opportunities
          </div>
          <div className="text-3xl font-black text-white mt-1">{totalCount}</div>
          <div className="text-xs text-slate-500 mt-1">Discovered across 12 platforms</div>
        </div>
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-rose-400">
            High Urgency (8-10)
          </div>
          <div className="text-3xl font-black text-rose-400 mt-1">{highUrgencyCount}</div>
          <div className="text-xs text-slate-500 mt-1">Active hiring or critical bugs</div>
        </div>
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
            Development Gaps
          </div>
          <div className="text-3xl font-black text-indigo-300 mt-1">{devCount}</div>
          <div className="text-xs text-slate-500 mt-1">Founders seeking dev capacity</div>
        </div>
        <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Performance / Speed
          </div>
          <div className="text-3xl font-black text-emerald-400 mt-1">{perfCount}</div>
          <div className="text-xs text-slate-500 mt-1">Latency & SEO vulnerabilities</div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm space-y-3">
        <div className="flex flex-col md:flex-row gap-3">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by startup name, problem statement, or tech keywords..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && fetchOpportunities(false)}
              className="w-full px-3.5 py-2 text-sm bg-slate-950 border border-slate-800 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div className="flex flex-col sm:flex-row gap-2">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 text-sm border border-slate-800 bg-slate-950 text-slate-200 rounded-lg focus:outline-none focus:border-indigo-500"
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
              className="px-3 py-2 text-sm border border-slate-800 bg-slate-950 text-slate-200 rounded-lg focus:outline-none focus:border-indigo-500"
            >
              <option value={0}>Any Urgency Score</option>
              <option value={7}>Score 7+ (Urgent)</option>
              <option value={8}>Score 8+ (High Urgency)</option>
              <option value={9}>Score 9+ (Critical)</option>
            </select>
            <button
              onClick={() => fetchOpportunities(false)}
              className="px-4 py-2 text-sm font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition"
            >
              Filter
            </button>
          </div>
        </div>
      </div>

      {/* Opportunity Cards List */}
      {loading ? (
        <div className="p-16 text-center text-slate-400">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          Loading verified startup opportunities...
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-sm">
          {error}
        </div>
      ) : opportunities.length === 0 ? (
        <div className="p-16 bg-slate-900 border border-slate-800 rounded-xl text-center text-slate-400">
          <p className="text-base font-semibold text-slate-300">No startup opportunities found</p>
          <p className="text-xs text-slate-500 mt-1">
            Try adjusting filters or click &quot;Scan & Refresh Signals&quot; to fetch live leads.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {opportunities.map((opp) => (
            <div
              key={opp.id}
              className="p-5 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition flex flex-col justify-between shadow-sm space-y-4"
            >
              <div className="space-y-2.5">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                    {opp.category}
                  </span>
                  <span
                    className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${
                      opp.urgency_score >= 8
                        ? "bg-rose-950/80 text-rose-300 border-rose-800"
                        : opp.urgency_score >= 6
                        ? "bg-amber-950/80 text-amber-300 border-amber-800"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}
                  >
                    Urgency {opp.urgency_score}/10
                  </span>
                </div>

                <h3 className="font-bold text-white text-base leading-snug line-clamp-1">
                  {opp.startup_name}
                </h3>
                {opp.domain && (
                  <p className="text-xs text-slate-400 font-mono">{opp.domain}</p>
                )}

                <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                  {opp.detected_signal}
                </p>

                <div className="pt-2 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
                  <span>Source: {opp.primary_source}</span>
                  <span>{opp.corroboration_count} signal{opp.corroboration_count > 1 ? "s" : ""}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center gap-2">
                <Link
                  href={`/startups/${opp.id}`}
                  className="flex-1 text-center py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition"
                >
                  Explore Pain Point →
                </Link>
                <button
                  onClick={() => handleSave(opp.id)}
                  title="Bookmark opportunity"
                  className="px-3 py-2 text-xs text-slate-300 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 transition"
                >
                  Bookmark
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
