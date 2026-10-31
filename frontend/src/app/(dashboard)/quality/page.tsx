"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SourceQualityBreakdown {
  source_id: string;
  name: string;
  provider: string;
  enabled: boolean;
  circuit_breaker_state: string;
  total_opportunities: number;
  confirmed_open: number;
  fresh_rate: number;
}

interface QualityMetrics {
  total_opportunities: number;
  fresh_opportunities: number;
  aging_opportunities: number;
  stale_opportunities: number;
  confirmed_open_count: number;
  confirmed_closed_count: number;
  unavailable_count: number;
  ambiguous_count: number;
  freshness_rate: number;
  verification_coverage: number;
  confirmed_open_rate: number;
  link_unavailable_rate: number;
  duplicate_candidates_count: number;
  confirmed_merges_count: number;
  user_feedback_count: number;
  source_breakdown: SourceQualityBreakdown[];
  generated_at: string;
}

export default function QualityDashboardPage() {
  const [metrics, setMetrics] = useState<QualityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient<QualityMetrics>("/quality/metrics");
      setMetrics(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load data quality metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Data Quality & Freshness Dashboard</h1>
          <p className="mt-2 text-sm text-slate-400 max-w-3xl">
            Live operational intelligence on career opportunity freshness, evidentiary verification coverage,
            circuit breaker health, and cross-source deduplication status.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Link
            href="/quality/duplicates"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white transition-colors shadow-lg shadow-indigo-950"
          >
            Review Duplicates Workbench &rarr;
          </Link>
          <button
            onClick={fetchMetrics}
            className="px-3 py-2 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 transition-colors"
          >
            Refresh Metrics
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="p-16 text-center text-slate-400">Loading data quality intelligence metrics...</div>
      ) : metrics ? (
        <>
          {/* Top 4 KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Freshness Rate
              </span>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-black text-emerald-400">{metrics.freshness_rate}%</span>
                <span className="text-xs text-slate-500">of active listings</span>
              </div>
              <p className="text-[11px] text-slate-400">
                {metrics.fresh_opportunities} fresh &bull; {metrics.aging_opportunities} aging &bull; {metrics.stale_opportunities} stale
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Verification Coverage
              </span>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-black text-indigo-400">{metrics.verification_coverage}%</span>
                <span className="text-xs text-slate-500">audited listings</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Verified via direct provider API or bounded URL probe
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Confirmed Open Rate
              </span>
              <div className="flex items-baseline space-x-2">
                <span className="text-3xl font-black text-cyan-400">{metrics.confirmed_open_rate}%</span>
                <span className="text-xs text-slate-500">open confirmed</span>
              </div>
              <p className="text-[11px] text-slate-400">
                {metrics.confirmed_open_count} verified actively accepting applications
              </p>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-2">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                Link Unavailable Rate
              </span>
              <div className="flex items-baseline space-x-2">
                <span className={`text-3xl font-black ${metrics.link_unavailable_rate > 5 ? "text-rose-400" : "text-slate-300"}`}>
                  {metrics.link_unavailable_rate}%
                </span>
                <span className="text-xs text-slate-500">broken links</span>
              </div>
              <p className="text-[11px] text-slate-400">
                {metrics.unavailable_count} confirmed 404 / 410 / domain dead
              </p>
            </div>
          </div>

          {/* Secondary Status Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block">Total Opportunities</span>
                <span className="text-xl font-bold text-white">{metrics.total_opportunities}</span>
              </div>
              <Link href="/opportunities" className="text-xs text-indigo-400 hover:underline">
                Explore &rarr;
              </Link>
            </div>

            <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block">Duplicate Candidates</span>
                <span className="text-xl font-bold text-amber-400">{metrics.duplicate_candidates_count}</span>
              </div>
              <Link href="/quality/duplicates" className="text-xs text-indigo-400 hover:underline">
                Review &rarr;
              </Link>
            </div>

            <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block">Confirmed Merges</span>
                <span className="text-xl font-bold text-emerald-400">{metrics.confirmed_merges_count}</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Auditable</span>
            </div>

            <div className="bg-slate-900/70 border border-slate-800/80 rounded-xl p-4 flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400 block">User Feedback Reports</span>
                <span className="text-xl font-bold text-purple-400">{metrics.user_feedback_count}</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">Candidate verified</span>
            </div>
          </div>

          {/* Source Breakdown Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white">Source Ingestion & Health Breakdown</h2>
                <p className="text-xs text-slate-400">
                  Per-source operational health, circuit breaker state, and open confirmation rates.
                </p>
              </div>
              <Link href="/sources" className="text-xs text-indigo-400 hover:underline">
                Manage Sources Registry &rarr;
              </Link>
            </div>

            {metrics.source_breakdown.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500 italic bg-slate-950 rounded-xl">
                No active job sources registered. Visit the Sources page to configure one.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Source Name</th>
                      <th className="py-3 px-4">Provider</th>
                      <th className="py-3 px-4">Circuit Breaker</th>
                      <th className="py-3 px-4">Total Listings</th>
                      <th className="py-3 px-4">Confirmed Open</th>
                      <th className="py-3 px-4">Freshness Rate</th>
                      <th className="py-3 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/70">
                    {metrics.source_breakdown.map((s) => (
                      <tr key={s.source_id} className="hover:bg-slate-850">
                        <td className="py-3 px-4 font-semibold text-white">{s.name}</td>
                        <td className="py-3 px-4 font-mono text-indigo-400">{s.provider}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              s.circuit_breaker_state === "CLOSED"
                                ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                                : s.circuit_breaker_state === "OPEN"
                                ? "bg-rose-950 text-rose-400 border border-rose-800"
                                : "bg-amber-950 text-amber-400 border border-amber-800"
                            }`}
                          >
                            {s.circuit_breaker_state}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono">{s.total_opportunities}</td>
                        <td className="py-3 px-4 font-mono text-cyan-400">{s.confirmed_open}</td>
                        <td className="py-3 px-4 font-semibold text-emerald-400">{s.fresh_rate}%</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                              s.enabled ? "text-emerald-400" : "text-slate-500"
                            }`}
                          >
                            {s.enabled ? "Active" : "Disabled"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}

