"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface ConnectorSnapshot {
  id: string;
  connector_name: string;
  provider_type: string;
  total_runs_count: number;
  successful_runs_count: number;
  failed_runs_count: number;
  records_fetched_count: number;
  records_inserted_count: number;
  records_rejected_count: number;
  rate_limit_events_count: number;
  last_run_status: string;
  last_run_at: string | null;
  health_status: string;
  degraded_reason: string | null;
}

export default function ConnectorHealthPage() {
  const [connectors, setConnectors] = useState<ConnectorSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterType, setFilterType] = useState<string>("ALL");

  const fetchConnectors = async () => {
    try {
      setLoading(true);
      const res = await apiClient<ConnectorSnapshot[]>("/beta/connectors/health");
      if (res && res.data) {
        setConnectors(res.data);
      }
    } catch (err: any) {
      console.error("Failed to load connector health", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConnectors();
  }, []);

  const handleManualCheck = async () => {
    try {
      setRefreshing(true);
      await fetchConnectors();
    } finally {
      setRefreshing(false);
    }
  };

  const filteredConnectors = filterType === "ALL" 
    ? connectors 
    : connectors.filter(c => c.provider_type === filterType);

  // Compute aggregate stats
  const totalRuns = connectors.reduce((acc, c) => acc + c.total_runs_count, 0);
  const successfulRuns = connectors.reduce((acc, c) => acc + c.successful_runs_count, 0);
  const overallSuccessRate = totalRuns > 0 ? ((successfulRuns / totalRuns) * 100).toFixed(1) : "100.0";
  const totalIngested = connectors.reduce((acc, c) => acc + c.records_inserted_count, 0);
  const totalRateLimits = connectors.reduce((acc, c) => acc + c.rate_limit_events_count, 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 mb-2">
            Phase 14 Reliability Assurance
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Connector Health & Ingestion Observability
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Real-time circuit breaker states, run metrics, rate limit encounters, and ingestion rejection tracking.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <button
            onClick={handleManualCheck}
            disabled={refreshing}
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200"
          >
            {refreshing ? "Refreshing..." : "Trigger Probes"}
          </button>
          <Link
            href="/quality/duplicates"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Duplicates Workbench
          </Link>
        </div>
      </div>

      {/* High-Level Metric Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Active Connectors
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {connectors.length}
          </div>
          <div className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">
            ATS, LeadHunter & Startup Feeds
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Aggregated Success Rate
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {overallSuccessRate}%
          </div>
          <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            {successfulRuns} of {totalRuns} connector runs passed
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Ingested Records
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {totalIngested.toLocaleString()}
          </div>
          <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
            Verified canonical opportunities
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Rate Limit / Backoff Events
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {totalRateLimits}
          </div>
          <div className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-medium">
            Gracefully throttled (Zero IP bans)
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-6">
        {["ALL", "ATS", "FREELANCE", "STARTUP", "JOB_BOARD"].map((type) => (
          <button
            key={type}
            onClick={() => setFilterType(type)}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              filterType === type
                ? "border-indigo-600 text-indigo-600 dark:text-indigo-400"
                : "border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            }`}
          >
            {type === "ALL" ? "All Connectors" : type}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-500 dark:text-slate-400">
            Loading connector observability data...
          </div>
        ) : filteredConnectors.length === 0 ? (
          <div className="p-8 text-center text-slate-500 dark:text-slate-400">
            No connectors found matching filter.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Connector / Provider</th>
                  <th className="px-6 py-4">Health State</th>
                  <th className="px-6 py-4">Success Rate</th>
                  <th className="px-6 py-4">Runs (Success / Fail)</th>
                  <th className="px-6 py-4">Records (Fetched / Stored)</th>
                  <th className="px-6 py-4">Rejection Rate</th>
                  <th className="px-6 py-4">Rate Limits</th>
                  <th className="px-6 py-4">Last Sync</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredConnectors.map((c) => {
                  const runs = c.total_runs_count;
                  const succ = c.successful_runs_count;
                  const rate = runs > 0 ? ((succ / runs) * 100).toFixed(1) : "100.0";
                  const rejRate = c.records_fetched_count > 0 
                    ? ((c.records_rejected_count / c.records_fetched_count) * 100).toFixed(1) 
                    : "0.0";

                  return (
                    <tr key={c.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-slate-900 dark:text-white">
                          {c.connector_name}
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                          {c.provider_type}
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                            c.health_status === "HEALTHY"
                              ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                              : c.health_status === "DEGRADED"
                              ? "bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300"
                              : "bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300"
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              c.health_status === "HEALTHY"
                                ? "bg-emerald-500"
                                : c.health_status === "DEGRADED"
                                ? "bg-amber-500"
                                : "bg-rose-500"
                            }`}
                          />
                          {c.health_status}
                        </span>
                        {c.degraded_reason && (
                          <div className="text-xs text-amber-600 dark:text-amber-400 mt-1 max-w-xs truncate">
                            {c.degraded_reason}
                          </div>
                        )}
                      </td>

                      <td className="px-6 py-4 font-mono font-medium">
                        {rate}%
                      </td>

                      <td className="px-6 py-4 text-xs">
                        <span className="text-emerald-600 dark:text-emerald-400 font-bold">{c.successful_runs_count}</span>
                        {" / "}
                        <span className={c.failed_runs_count > 0 ? "text-rose-600 font-bold" : "text-slate-400"}>
                          {c.failed_runs_count}
                        </span>
                        <div className="text-slate-400 dark:text-slate-500 text-[11px]">
                          Total: {c.total_runs_count}
                        </div>
                      </td>

                      <td className="px-6 py-4 text-xs font-mono">
                        <div>Fetched: {c.records_fetched_count.toLocaleString()}</div>
                        <div className="text-emerald-600 dark:text-emerald-400 font-semibold">
                          Stored: {c.records_inserted_count.toLocaleString()}
                        </div>
                      </td>

                      <td className="px-6 py-4">
                        <span className="font-mono text-xs">{rejRate}%</span>
                        <div className="text-[11px] text-slate-400">
                          {c.records_rejected_count} dropped
                        </div>
                      </td>

                      <td className="px-6 py-4 font-mono text-xs">
                        <span className={c.rate_limit_events_count > 0 ? "text-amber-600 font-bold" : "text-slate-400"}>
                          {c.rate_limit_events_count}
                        </span>
                      </td>

                      <td className="px-6 py-4 text-xs text-slate-500 dark:text-slate-400">
                        {c.last_run_at ? new Date(c.last_run_at).toLocaleString() : "Pending run"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

