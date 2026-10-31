"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface FreelanceOpportunity {
  id: string;
  business_name: string;
  opportunity_title: string;
  service_category: string;
  description?: string;
  city: string;
  location?: string;
  website?: string;
  is_broken_website: boolean;
  rating: number;
  reviews_count: number;
  phone?: string;
  email?: string;
  required_skills: string[];
  suggested_service?: string;
  priority?: "HIGH" | "MEDIUM" | "LOW" | "IGNORE";
  classification_state: string;
  classification_reason?: string;
  relevance_score: number;
  discovered_at: string;
}

interface SearchHistoryItem {
  id: string;
  query: string;
  city: string;
  results_count: number;
  leads_count: number;
  deep_scan: boolean;
  searched_at: string;
}

export default function FreelanceDashboardPage() {
  const [opportunities, setOpportunities] = useState<FreelanceOpportunity[]>([]);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // Scan controls
  const [scanQuery, setScanQuery] = useState("Dentists");
  const [scanCity, setScanCity] = useState("Indore");
  const [maxResults, setMaxResults] = useState(20);
  const [includeWithWebsite, setIncludeWithWebsite] = useState(false);
  const [deepScan, setDeepScan] = useState(true);
  const [scanning, setScanning] = useState(false);

  // Filters
  const [selectedState, setSelectedState] = useState<string>("ALL");
  const [selectedPriority, setSelectedPriority] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchOpportunities = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<any>("/freelance?per_page=50");
      setOpportunities(res.data || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load freelance opportunities.");
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await apiClient.get<any>("/freelance/history?limit=6");
      setHistory(res.data || []);
    } catch {
      // Non-blocking
    }
  };

  useEffect(() => {
    fetchOpportunities();
    fetchHistory();
  }, []);

  const handleScan = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!scanQuery || !scanCity) return;
    setScanning(true);
    setError(null);
    setSuccessNotice(null);
    try {
      const res: any = await apiClient.post("/freelance/scan-leads", {
        query: scanQuery,
        city: scanCity,
        max_results: maxResults,
        include_with_website: includeWithWebsite,
        deep_scan: deepScan,
      });

      const count = res?.stats?.leads_imported ?? res?.leads_created ?? res?.data?.length ?? 0;
      const highCount = res?.stats?.high_priority ?? res?.data?.filter((d: any) => d.priority === "HIGH")?.length ?? 0;
      setSuccessNotice(`Discovery complete: Discovered and ingested ${count} leads (${highCount} High Priority) classified by AI intelligence!`);
      await fetchOpportunities();
      await fetchHistory();
    } catch (err: any) {
      setError(err?.message || "Scan failed. Please verify provider API keys or configuration.");
    } finally {
      setScanning(false);
    }
  };

  const handleQuickHistoryClick = (item: SearchHistoryItem) => {
    setScanQuery(item.query);
    setScanCity(item.city);
    setDeepScan(item.deep_scan);
  };

  const filtered = opportunities.filter((opp) => {
    const matchesState = selectedState === "ALL" || opp.classification_state === selectedState;
    const matchesPriority = selectedPriority === "ALL" || opp.priority === selectedPriority;
    const matchesSearch =
      searchTerm === "" ||
      opp.business_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.service_category.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesState && matchesPriority && matchesSearch;
  });

  // KPI counts
  const totalCount = opportunities.length;
  const highPriorityCount = opportunities.filter((o) => o.priority === "HIGH").length;
  const mediumPriorityCount = opportunities.filter((o) => o.priority === "MEDIUM").length;
  const brokenWebsitesCount = opportunities.filter((o) => o.is_broken_website).length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header & Sub-Navigation */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">
              Freelance Intelligence Engine
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Autonomous local business discovery, 100-point website health diagnostics, and candidate-governed outreach pitches.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href="/freelance/saved"
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
            >
              Saved Leads
            </Link>
            <Link
              href="/freelance/outreach"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition shadow-md shadow-indigo-900/30"
            >
              Outreach & Settings →
            </Link>
          </div>
        </div>

        {/* Global Feedback Alert */}
        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-600 rounded-xl text-rose-200 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
          </div>
        )}
        {successNotice && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm flex items-center justify-between">
            <span>{successNotice}</span>
            <button onClick={() => setSuccessNotice(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
          </div>
        )}

        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Opportunities
            </p>
            <p className="text-3xl font-bold text-white mt-2">{totalCount}</p>
            <p className="text-xs text-slate-500 mt-1">Cataloged across local target markets</p>
          </div>
          <div className="bg-slate-900/80 border border-rose-900/40 p-5 rounded-xl shadow">
            <p className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1">
              <span>⚡ High Priority Leads</span>
            </p>
            <p className="text-3xl font-bold text-rose-300 mt-2">{highPriorityCount}</p>
            <p className="text-xs text-rose-400/80 mt-1">No site or broken site with under 50 reviews</p>
          </div>
          <div className="bg-slate-900/80 border border-amber-900/40 p-5 rounded-xl shadow">
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
              Medium Priority Leads
            </p>
            <p className="text-3xl font-bold text-amber-300 mt-2">{mediumPriorityCount}</p>
            <p className="text-xs text-slate-500 mt-1">No website with 50-200 reviews</p>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-xl shadow">
            <p className="text-xs font-semibold text-rose-400 uppercase tracking-wider">
              Broken Sites Found
            </p>
            <p className="text-3xl font-bold text-rose-300 mt-2">{brokenWebsitesCount}</p>
            <p className="text-xs text-slate-500 mt-1">Failed DNS, SSL, or HTTP status probes</p>
          </div>
        </div>

        {/* Discovery Scan Controller */}
        <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-xl shadow-lg space-y-4">
          <div>
            <h2 className="text-base font-semibold text-white">
              Launch Native Local Business Discovery
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Directly queries Google Maps via native SerpApi / Apify collectors, verifies website health, and enriches public contacts.
            </p>
          </div>

          <form onSubmit={handleScan} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1 font-medium">Business Niche / Category</label>
                <input
                  type="text"
                  value={scanQuery}
                  onChange={(e) => setScanQuery(e.target.value)}
                  placeholder="e.g. Dentists, Bakeries, Plumbers, Accountants"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1 font-medium">Target City / Metro Area</label>
                <input
                  type="text"
                  value={scanCity}
                  onChange={(e) => setScanCity(e.target.value)}
                  placeholder="e.g. Austin, TX or Indore"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1 font-medium">Max Lead Count</label>
                <select
                  value={maxResults}
                  onChange={(e) => setMaxResults(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value={10}>10 Leads</option>
                  <option value={20}>20 Leads (Standard)</option>
                  <option value={40}>40 Leads (Broad Scan)</option>
                </select>
              </div>
            </div>

            {/* Advanced Scan Toggles */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800">
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 text-xs text-slate-300">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={deepScan}
                    onChange={(e) => setDeepScan(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0"
                  />
                  <span>Deep Scan (Proactive contact page email discovery)</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeWithWebsite}
                    onChange={(e) => setIncludeWithWebsite(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0"
                  />
                  <span>Include businesses with active websites</span>
                </label>
              </div>

              <button
                type="submit"
                disabled={scanning}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-2 px-6 rounded-lg text-xs transition shadow-md shadow-indigo-900/30"
              >
                {scanning ? "Scanning Local Maps..." : "Scan & Ingest Leads ⚡"}
              </button>
            </div>
          </form>

          {/* Recent Search History Chips */}
          {history.length > 0 && (
            <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center gap-2">
              <span className="text-[11px] text-slate-500 font-semibold uppercase">Recent Searches:</span>
              {history.map((h) => (
                <button
                  key={h.id}
                  onClick={() => handleQuickHistoryClick(h)}
                  className="text-xs px-2.5 py-1 bg-slate-950 hover:bg-slate-800 text-slate-300 rounded-full border border-slate-800 transition flex items-center space-x-1.5"
                >
                  <span>{h.query} in {h.city}</span>
                  <span className="text-[10px] text-indigo-400">({h.leads_count})</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Filter & Search Bar */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-3">
          {/* Priority Filter Chips */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
            <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">
              Lead Priority Classification:
            </span>
            <div className="flex flex-wrap gap-2">
              {[
                { id: "ALL", label: "All Priorities", color: "bg-slate-800 text-slate-200" },
                { id: "HIGH", label: "⚡ High Priority", color: "bg-rose-950 text-rose-300 border border-rose-700 font-bold" },
                { id: "MEDIUM", label: "Medium Priority", color: "bg-amber-950 text-amber-300 border border-amber-700" },
                { id: "LOW", label: "Low Priority", color: "bg-slate-900 text-slate-400 border border-slate-700" },
              ].map((p) => (
                <button
                  key={p.id}
                  onClick={() => setSelectedPriority(p.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs transition ${selectedPriority === p.id
                      ? "ring-2 ring-indigo-500 bg-indigo-600 text-white font-bold"
                      : p.color
                    }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Search & State Filter Row */}
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-center pt-1">
            <div className="w-full sm:w-72">
              <input
                type="text"
                placeholder="Filter by business, city, or niche..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div className="flex flex-wrap gap-2 w-full sm:w-auto">
              {["ALL", "VERIFIED_OPPORTUNITY", "POTENTIAL_FREELANCE_OPPORTUNITY", "DISCOVERED_LEAD"].map((st) => (
                <button
                  key={st}
                  onClick={() => setSelectedState(st)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${selectedState === st
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                    }`}
                >
                  {st === "ALL" ? "All Statuses" : st.replace(/_/g, " ")}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Opportunities Listing */}
        {loading ? (
          <div className="text-center py-16 text-slate-400">Loading freelance opportunities...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 bg-slate-900/40 rounded-xl border border-dashed border-slate-800 text-slate-400">
            No freelance opportunities match your criteria. Launch a discovery scan above!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filtered.map((opp) => (
              <div
                key={opp.id}
                className={`bg-slate-900 border transition rounded-xl p-6 flex flex-col justify-between shadow-sm ${opp.priority === "HIGH"
                    ? "border-rose-900/60 hover:border-rose-600 ring-1 ring-rose-950/40"
                    : opp.priority === "MEDIUM"
                      ? "border-amber-900/50 hover:border-amber-600"
                      : "border-slate-800 hover:border-slate-700"
                  }`}
              >
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${opp.priority === "HIGH"
                              ? "bg-rose-950 text-rose-300 border border-rose-600 shadow-sm shadow-rose-950"
                              : opp.priority === "MEDIUM"
                                ? "bg-amber-950 text-amber-300 border border-amber-600"
                                : "bg-slate-800 text-slate-400 border border-slate-700"
                            }`}
                        >
                          {opp.priority === "HIGH" ? "⚡ HIGH PRIORITY" : `${opp.priority || "MEDIUM"} PRIORITY`}
                        </span>
                        <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400">
                          {opp.service_category}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-white mt-0.5">{opp.business_name}</h3>
                      <p className="text-xs text-slate-400">{opp.city}</p>
                    </div>
                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-semibold ${opp.is_broken_website
                          ? "bg-rose-950 text-rose-300 border border-rose-700"
                          : !opp.website
                            ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                            : "bg-slate-800 text-slate-300"
                        }`}
                    >
                      {opp.is_broken_website
                        ? "Broken Website"
                        : !opp.website
                          ? "No Website"
                          : "Active Website"}
                    </span>
                  </div>

                  <p className="text-sm font-medium text-slate-200 mt-3">{opp.opportunity_title}</p>
                  <p className="text-xs text-slate-400 mt-1 line-clamp-2">{opp.description}</p>

                  {/* Skills badges */}
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {opp.required_skills?.map((sk, idx) => (
                      <span
                        key={idx}
                        className="text-[11px] px-2 py-0.5 bg-slate-800/80 text-slate-300 rounded border border-slate-700"
                      >
                        {sk}
                      </span>
                    ))}
                  </div>

                  {/* Contacts Summary */}
                  <div className="mt-4 pt-3 border-t border-slate-800/60 flex items-center justify-between text-xs text-slate-400">
                    <div>
                      {opp.phone && <span className="mr-3 font-mono">📞 {opp.phone}</span>}
                      {opp.email && <span className="font-mono">✉️ {opp.email}</span>}
                    </div>
                    {opp.rating > 0 && <span>⭐ {opp.rating} ({opp.reviews_count})</span>}
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">
                    Match Score: <span className="text-indigo-400">{opp.relevance_score}%</span>
                  </span>
                  <Link
                    href={`/freelance/${opp.id}`}
                    className="text-xs font-semibold px-4 py-2 bg-indigo-600/90 hover:bg-indigo-600 text-white rounded-lg transition"
                  >
                    View Details & Outreach →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
