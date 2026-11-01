"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient, API_BASE_URL } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";

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
  instagram?: string;
  facebook?: string;
  linkedin?: string;
  twitter?: string;
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
  const [opportunities, setOpportunities] = useState<FreelanceOpportunity[]>(() => {
    return fastCache.get<FreelanceOpportunity[]>("freelance_opportunities") || [];
  });
  const [history, setHistory] = useState<SearchHistoryItem[]>(() => {
    return fastCache.get<SearchHistoryItem[]>("freelance_history") || [];
  });
  const [loading, setLoading] = useState(() => {
    return (fastCache.get<FreelanceOpportunity[]>("freelance_opportunities") || []).length === 0;
  });
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);

  // View Mode: Cards or Table
  const [viewMode, setViewMode] = useState<"cards" | "table">("cards");
  const [exportingExcel, setExportingExcel] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);
  const [enrichingId, setEnrichingId] = useState<string | null>(null);

  // Scan controls
  const [scanQuery, setScanQuery] = useState("Dentists");
  const [scanCity, setScanCity] = useState("Indore");
  const [maxResults, setMaxResults] = useState(20);
  const [includeWithWebsite, setIncludeWithWebsite] = useState(true);
  const [deepScan, setDeepScan] = useState(true);
  const [scanning, setScanning] = useState(false);

  // Filters
  const [selectedState, setSelectedState] = useState<string>("ALL");
  const [selectedPriority, setSelectedPriority] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchOpportunities = async () => {
    if (opportunities.length === 0) setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<any>("/freelance?per_page=100");
      const data = res.data || [];
      setOpportunities(data);
      fastCache.set("freelance_opportunities", data, 120000);
    } catch (err: any) {
      if (opportunities.length === 0) setError(err?.message || "Failed to load freelance opportunities.");
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await apiClient.get<any>("/freelance/history?limit=6");
      const data = res.data || [];
      setHistory(data);
      fastCache.set("freelance_history", data, 120000);
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
      setSuccessNotice(`Discovery complete: Ingested ${count} leads (${highCount} High Priority) classified by AI intelligence!`);
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

  const handleExportExcel = async () => {
    setExportingExcel(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/freelance/export/excel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          city: scanCity || undefined,
          category: scanQuery || undefined,
          priority: selectedPriority === "ALL" ? undefined : selectedPriority,
          query: searchTerm || undefined,
        }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => null);
        throw new Error(errJson?.detail || "Excel export failed.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `freelance_leads_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      setSuccessNotice("✓ Excel spreadsheet (.xlsx) downloaded successfully!");
      setTimeout(() => setSuccessNotice(null), 4000);
    } catch (err: any) {
      setError(err?.message || "Failed to download Excel spreadsheet.");
    } finally {
      setExportingExcel(false);
    }
  };

  const handleExportCsv = async () => {
    setExportingCsv(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/freelance/export/csv`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          city: scanCity || undefined,
          category: scanQuery || undefined,
          priority: selectedPriority === "ALL" ? undefined : selectedPriority,
          query: searchTerm || undefined,
        }),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => null);
        throw new Error(errJson?.detail || "CSV export failed.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `freelance_leads_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      setSuccessNotice("✓ CSV spreadsheet downloaded successfully!");
      setTimeout(() => setSuccessNotice(null), 4000);
    } catch (err: any) {
      setError(err?.message || "Failed to download CSV spreadsheet.");
    } finally {
      setExportingCsv(false);
    }
  };

  const handleEnrichContact = async (oppId: string) => {
    setEnrichingId(oppId);
    setError(null);
    try {
      const res: any = await apiClient.post(`/freelance/${oppId}/enrich-contacts`, {});
      if (res?.data) {
        const newSocials = Object.keys(res.data.newly_added_socials || {}).length;
        setSuccessNotice(
          `Enrichment complete: Verified email (${res.data.email || "none"}) & discovered ${newSocials} new social handle(s)!`
        );
        setTimeout(() => setSuccessNotice(null), 4000);
        await fetchOpportunities();
      }
    } catch (err: any) {
      setError(err?.message || "Failed to enrich contact details.");
    } finally {
      setEnrichingId(null);
    }
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
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 animate-fade-in text-slate-900">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header & Sub-Navigation */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-700/60 font-mono">
                v2.5 Intelligence Engine
              </span>
              <span className="text-xs text-slate-500 font-medium">Native Monolith Integration</span>
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">
              Freelance Intelligence Engine
            </h1>
            <p className="text-sm text-slate-700 font-semibold mt-1">
              Autonomous local business discovery, multi-platform email & social scraping, and candidate-governed outreach pitches.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Export Buttons */}
            <div className="flex items-center space-x-2">
              <button
                onClick={handleExportExcel}
                disabled={exportingExcel || filtered.length === 0}
                className="neo-pill px-4 py-2 text-emerald-800 hover:text-emerald-950 text-xs font-bold rounded-xl transition-all shadow flex items-center space-x-1.5"
                title="Download formatted Excel workbook with formulas protected"
              >
                <span>📊</span>
                <span>{exportingExcel ? "Generating .xlsx..." : "Export Excel (.xlsx)"}</span>
              </button>

              <button
                onClick={handleExportCsv}
                disabled={exportingCsv || filtered.length === 0}
                className="neo-pill px-3.5 py-2 text-slate-800 hover:text-indigo-600 text-xs font-bold rounded-xl transition-all"
                title="Download clean UTF-8 CSV spreadsheet"
              >
                <span>{exportingCsv ? "Exporting..." : "CSV"}</span>
              </button>
            </div>

            <Link
              href="/freelance/saved"
              className="neo-pill px-4 py-2 text-slate-800 hover:text-indigo-600 text-xs font-bold rounded-xl transition-all flex items-center space-x-1"
            >
              <span>★</span>
              <span>Saved Leads</span>
            </Link>

            <Link
              href="/freelance/outreach"
              className="neo-btn-primary px-4 py-2 text-xs font-bold rounded-xl transition-all shadow-md"
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
          <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Opportunities
            </p>
            <p className="text-3xl font-black text-slate-900 mt-2">{totalCount}</p>
            <p className="text-xs text-slate-500 mt-1">Cataloged across local target markets</p>
          </div>
          <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
            <p className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1">
              <span>⚡ High Priority Leads</span>
            </p>
            <p className="text-3xl font-black text-rose-800 mt-2">{highPriorityCount}</p>
            <p className="text-xs text-rose-400/80 mt-1">No site or broken site with under 50 reviews</p>
          </div>
          <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
            <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider">
              Medium Priority Leads
            </p>
            <p className="text-3xl font-black text-amber-800 mt-2">{mediumPriorityCount}</p>
            <p className="text-xs text-slate-500 mt-1">No website with 50-200 reviews</p>
          </div>
          <div className="neo-card neo-box-hover p-5 rounded-2xl border border-white/90 shadow-sm">
            <p className="text-xs font-semibold text-rose-400 uppercase tracking-wider">
              Broken Sites Found
            </p>
            <p className="text-3xl font-black text-rose-800 mt-2">{brokenWebsitesCount}</p>
            <p className="text-xs text-slate-500 mt-1">Failed DNS, SSL, or HTTP status probes</p>
          </div>
        </div>

        {/* Discovery Scan Controller */}
        <div className="neo-box p-6 rounded-2xl border border-white/90 shadow-sm space-y-4">
          <div>
            <h2 className="text-base font-black text-slate-900">
              Launch Native Local Business Discovery
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Directly queries Google Maps via native discovery collectors, verifies website health, and enriches public contacts.
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
                  className="w-full neo-inset rounded-xl px-4 py-2 text-xs font-bold text-slate-900 placeholder:text-slate-500 focus:outline-none"
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
                  className="w-full neo-inset rounded-xl px-4 py-2 text-xs font-bold text-slate-900 placeholder:text-slate-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1 font-medium">Max Lead Count</label>
                <select
                  value={maxResults}
                  onChange={(e) => setMaxResults(Number(e.target.value))}
                  className="w-full neo-inset rounded-xl px-4 py-2 text-xs font-bold text-slate-900 placeholder:text-slate-500 focus:outline-none"
                >
                  <option value={10}>10 Leads</option>
                  <option value={20}>20 Leads (Standard)</option>
                  <option value={40}>40 Leads (Broad Scan)</option>
                </select>
              </div>
            </div>

            {/* Advanced Scan Toggles */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-slate-800">
              <div className="flex items-center space-x-6 text-xs text-slate-300">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={deepScan}
                    onChange={(e) => setDeepScan(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-700 text-indigo-600 focus:ring-0"
                  />
                  <span>Deep Scan (Proactive contact page email & socials discovery)</span>
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

        {/* Filter & View Switcher Bar */}
        <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800 space-y-3">
          {/* Top Row: Priorities & View Switcher */}
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider mr-1">
                Priority:
              </span>
              {[
                { id: "ALL", label: "All Priorities", color: "neo-pill text-slate-900 font-bold" },
                { id: "HIGH", label: "⚡ High Priority", color: "bg-rose-950 text-rose-300 border border-rose-700 font-bold" },
                { id: "MEDIUM", label: "Medium Priority", color: "bg-amber-950 text-amber-300 border border-amber-700" },
                { id: "LOW", label: "Low Priority", color: "neo-inset text-slate-700 font-bold" },
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

            {/* View Mode Toggle: Cards vs Table */}
            <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800">
              <button
                onClick={() => setViewMode("cards")}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition flex items-center space-x-1 ${viewMode === "cards"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
                  }`}
              >
                <span>🎴</span>
                <span>Cards View</span>
              </button>
              <button
                onClick={() => setViewMode("table")}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition flex items-center space-x-1 ${viewMode === "table"
                  ? "bg-indigo-600 text-white shadow"
                  : "text-slate-400 hover:text-slate-200"
                  }`}
              >
                <span>📊</span>
                <span>Table Spreadsheet</span>
              </button>
            </div>
          </div>

          {/* Bottom Row: Search & Status Filters */}
          <div className="flex flex-col sm:flex-row gap-3 justify-between items-center pt-1">
            <div className="w-full sm:w-80">
              <input
                type="text"
                placeholder="Search business, city, niche, or contact..."
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
        {loading && opportunities.length === 0 ? (
          <div className="text-center py-16 text-slate-400">Loading freelance opportunities...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 bg-slate-900/40 rounded-xl border border-dashed border-slate-800 text-slate-400">
            No freelance opportunities match your criteria. Launch a discovery scan above!
          </div>
        ) : viewMode === "table" ? (
          /* ================================================================ */
          /* TABLE / SPREADSHEET VIEW                                        */
          /* ================================================================ */
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="neo-box border-b border-slate-300/80 text-slate-900 font-black uppercase tracking-wider">
                    <th className="py-3 px-4">Business / Niche</th>
                    <th className="py-3 px-4">City</th>
                    <th className="py-3 px-4">Website Gap</th>
                    <th className="py-3 px-4">Priority & Fit</th>
                    <th className="py-3 px-4">Direct Contacts</th>
                    <th className="py-3 px-4">Social Profiles</th>
                    <th className="py-3 px-4">Rating</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {filtered.map((opp) => {
                    const phoneDigits = opp.phone ? opp.phone.replace(/\D/g, "") : "";
                    return (
                      <tr key={opp.id} className="hover:bg-slate-800/40 transition">
                        {/* Business & Niche */}
                        <td className="py-3.5 px-4">
                          <div className="font-bold text-white text-sm">{opp.business_name}</div>
                          <div className="text-indigo-400 text-[11px] font-medium">{opp.service_category}</div>
                        </td>

                        {/* City */}
                        <td className="py-3.5 px-4 text-slate-300 font-medium">
                          {opp.city}
                        </td>

                        {/* Website Gap */}
                        <td className="py-3.5 px-4">
                          <span
                            className={`inline-block text-[11px] px-2 py-0.5 rounded font-semibold ${opp.is_broken_website
                              ? "bg-rose-950 text-rose-300 border border-rose-700"
                              : !opp.website
                                ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                                : "bg-slate-800 text-slate-300"
                              }`}
                          >
                            {opp.is_broken_website
                              ? "Broken Site"
                              : !opp.website
                                ? "No Website"
                                : "Active Site"}
                          </span>
                        </td>

                        {/* Priority & Fit */}
                        <td className="py-3.5 px-4">
                          <div className="flex items-center space-x-1.5">
                            <span
                              className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${opp.priority === "HIGH"
                                ? "bg-rose-950 text-rose-300 border border-rose-600"
                                : opp.priority === "MEDIUM"
                                  ? "bg-amber-950 text-amber-300 border border-amber-600"
                                  : "bg-slate-800 text-slate-400"
                                }`}
                            >
                              {opp.priority}
                            </span>
                            <span className="text-indigo-400 font-mono font-bold text-[11px]">
                              {opp.relevance_score}%
                            </span>
                          </div>
                        </td>

                        {/* Direct Contacts */}
                        <td className="py-3.5 px-4">
                          <div className="space-y-1">
                            {opp.email ? (
                              <div className="text-emerald-400 font-mono flex items-center space-x-1">
                                <span>✉</span>
                                <span className="truncate max-w-[150px]">{opp.email}</span>
                              </div>
                            ) : (
                              <span className="text-slate-500 italic">No email</span>
                            )}

                            {opp.phone && (
                              <div className="text-slate-300 font-mono flex items-center space-x-1">
                                <span>📞</span>
                                <span>{opp.phone}</span>
                              </div>
                            )}

                            {phoneDigits && (
                              <a
                                href={`https://wa.me/${phoneDigits}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center space-x-1 text-[10px] font-bold text-emerald-400 hover:text-emerald-300 transition"
                              >
                                <span>📲 Chat WhatsApp</span>
                              </a>
                            )}
                          </div>
                        </td>

                        {/* Social Profiles */}
                        <td className="py-3.5 px-4">
                          <div className="flex flex-wrap items-center gap-1.5">
                            {opp.instagram && (
                              <a
                                href={opp.instagram}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-1.5 py-0.5 bg-pink-950/80 hover:bg-pink-900 text-pink-300 border border-pink-700/60 rounded text-[10px] font-bold"
                                title="Instagram Profile"
                              >
                                IG
                              </a>
                            )}
                            {opp.facebook && (
                              <a
                                href={opp.facebook}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-1.5 py-0.5 bg-blue-950/80 hover:bg-blue-900 text-blue-300 border border-blue-700/60 rounded text-[10px] font-bold"
                                title="Facebook Page"
                              >
                                FB
                              </a>
                            )}
                            {opp.linkedin && (
                              <a
                                href={opp.linkedin}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-1.5 py-0.5 bg-sky-950/80 hover:bg-sky-900 text-sky-300 border border-sky-700/60 rounded text-[10px] font-bold"
                                title="LinkedIn Profile"
                              >
                                LI
                              </a>
                            )}
                            {opp.twitter && (
                              <a
                                href={opp.twitter}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600 rounded text-[10px] font-bold"
                                title="Twitter / X"
                              >
                                X
                              </a>
                            )}
                            {!opp.instagram && !opp.facebook && !opp.linkedin && !opp.twitter && (
                              <span className="text-slate-500 text-[11px]">—</span>
                            )}
                            {opp.website && (
                              <button
                                onClick={() => handleEnrichContact(opp.id)}
                                disabled={enrichingId === opp.id}
                                className="text-[10px] text-indigo-400 hover:text-indigo-300 underline font-semibold ml-1"
                              >
                                {enrichingId === opp.id ? "Scraping..." : "Enrich"}
                              </button>
                            )}
                          </div>
                        </td>

                        {/* Rating */}
                        <td className="py-3.5 px-4 text-slate-300">
                          {opp.rating > 0 ? (
                            <span className="font-semibold text-amber-300">
                              ⭐ {opp.rating} <span className="text-slate-500 font-normal">({opp.reviews_count})</span>
                            </span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>

                        {/* Actions */}
                        <td className="py-3.5 px-4 text-right">
                          <Link
                            href={`/freelance/${opp.id}`}
                            className="px-3 py-1.5 bg-indigo-600/90 hover:bg-indigo-600 text-white rounded-lg text-xs font-semibold transition inline-block"
                          >
                            Outreach →
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* ================================================================ */
          /* CARDS VIEW                                                       */
          /* ================================================================ */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filtered.map((opp) => {
              const phoneDigits = opp.phone ? opp.phone.replace(/\D/g, "") : "";
              return (
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
                          className="text-[11px] px-2.5 py-0.5 neo-pill text-slate-900 font-bold rounded-lg border border-white/90"
                        >
                          {sk}
                        </span>
                      ))}
                    </div>

                    {/* Socials & Contacts Row */}
                    <div className="mt-4 pt-3 border-t border-slate-800/60 space-y-2 text-xs">
                      <div className="flex flex-wrap items-center justify-between gap-2 text-slate-400">
                        <div>
                          {opp.phone && <span className="mr-3 font-mono">📞 {opp.phone}</span>}
                          {opp.email && <span className="font-mono text-emerald-400">✉️ {opp.email}</span>}
                        </div>
                        {opp.rating > 0 && <span className="text-amber-300 font-semibold">⭐ {opp.rating} ({opp.reviews_count})</span>}
                      </div>

                      {/* Social Badges and WhatsApp */}
                      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-800/40">
                        <div className="flex items-center space-x-2">
                          {opp.instagram && (
                            <a
                              href={opp.instagram}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 bg-pink-950/80 text-pink-300 border border-pink-700/60 rounded text-[10px] font-bold"
                            >
                              Instagram
                            </a>
                          )}
                          {opp.facebook && (
                            <a
                              href={opp.facebook}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 bg-blue-950/80 text-blue-300 border border-blue-700/60 rounded text-[10px] font-bold"
                            >
                              Facebook
                            </a>
                          )}
                          {opp.linkedin && (
                            <a
                              href={opp.linkedin}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 bg-sky-950/80 text-sky-300 border border-sky-700/60 rounded text-[10px] font-bold"
                            >
                              LinkedIn
                            </a>
                          )}
                          {opp.twitter && (
                            <a
                              href={opp.twitter}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 bg-slate-800 text-slate-200 border border-slate-600 rounded text-[10px] font-bold"
                            >
                              Twitter
                            </a>
                          )}
                          {phoneDigits && (
                            <a
                              href={`https://wa.me/${phoneDigits}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 rounded text-[10px] font-bold"
                            >
                              📲 WhatsApp
                            </a>
                          )}
                        </div>

                        {opp.website && (
                          <button
                            onClick={() => handleEnrichContact(opp.id)}
                            disabled={enrichingId === opp.id}
                            className="text-[11px] text-indigo-400 hover:text-indigo-300 font-semibold underline"
                          >
                            {enrichingId === opp.id ? "Crawling Contacts..." : "🔍 Scrape Socials & Email"}
                          </button>
                        )}
                      </div>
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
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
