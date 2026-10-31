"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface ScheduleConfig {
  id: string;
  source_id: string;
  source_name: string;
  interval_seconds: number;
  is_paused: boolean;
  max_records_per_run: number;
  rate_limit_per_minute: number;
  last_run_at: string | null;
  next_run_at: string | null;
}

interface TaskExecution {
  id: string;
  task_name: string;
  task_type: string;
  source_id: string;
  status: string;
  records_fetched: number;
  records_inserted: number;
  records_updated: number;
  duration_ms: number | null;
  started_at: string | null;
  completed_at: string | null;
}

interface DiscoveryStatusData {
  engine_state: string;
  total_active_sources: number;
  total_sources_configured: number;
  total_opportunities_discovered: {
    jobs: number;
    startups: number;
    total: number;
  };
  schedules: ScheduleConfig[];
  recent_executions: TaskExecution[];
  server_time: string;
}

export default function DiscoveryOperationsPage() {
  const [statusData, setStatusData] = useState<DiscoveryStatusData | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [msg, setMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const res: any = await apiClient.get("/discovery/status");
      if (res && res.data) {
        setStatusData(res.data);
      }
    } catch (err: any) {
      console.error("Failed to fetch discovery status", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleManualTrigger = async (oppType: "ALL" | "JOBS" | "STARTUPS") => {
    try {
      setActionInProgress("refresh");
      setMsg(null);
      const res: any = await apiClient.post("/discovery/refresh", { opportunity_type: oppType });
      setMsg({ type: "success", text: `Manual discovery run (${oppType}) completed successfully.` });
      fetchStatus();
    } catch (err: any) {
      setMsg({ type: "error", text: err?.message || "Failed to trigger discovery run." });
    } finally {
      setActionInProgress(null);
    }
  };

  const handleToggleSourcePause = async (sourceId: string, currentlyPaused: boolean) => {
    try {
      setActionInProgress(sourceId);
      setMsg(null);
      const endpoint = currentlyPaused ? `/discovery/resume?source_id=${sourceId}` : `/discovery/pause?source_id=${sourceId}`;
      await apiClient.post(endpoint);
      setMsg({
        type: "success",
        text: `Source '${sourceId}' ${currentlyPaused ? "resumed" : "paused"} successfully.`,
      });
      fetchStatus();
    } catch (err: any) {
      setMsg({ type: "error", text: err?.message || "Failed to update source schedule." });
    } finally {
      setActionInProgress(null);
    }
  };

  const handleGlobalPauseToggle = async (isGlobalPaused: boolean) => {
    try {
      setActionInProgress("global");
      setMsg(null);
      const endpoint = isGlobalPaused ? "/discovery/resume" : "/discovery/pause";
      await apiClient.post(endpoint);
      setMsg({
        type: "success",
        text: `Discovery engine ${isGlobalPaused ? "resumed" : "paused"} globally.`,
      });
      fetchStatus();
    } catch (err: any) {
      setMsg({ type: "error", text: err?.message || "Failed to update global engine state." });
    } finally {
      setActionInProgress(null);
    }
  };

  const isGlobalPaused = statusData?.engine_state === "PAUSED";

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 mb-2">
            Continuous Ingestion Orchestrator
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Discovery Operations & Scheduler Dashboard
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Real-time management of background Celery Beat schedules, connector quotas, per-source rate limits, and task executions.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
          <button
            onClick={() => handleGlobalPauseToggle(isGlobalPaused)}
            disabled={actionInProgress === "global"}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition-colors shadow-sm ${
              isGlobalPaused
                ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                : "bg-rose-600 hover:bg-rose-700 text-white"
            }`}
          >
            {isGlobalPaused ? "▶ Resume Engine" : "⏸ Pause All Discovery"}
          </button>
          <button
            onClick={() => handleManualTrigger("ALL")}
            disabled={actionInProgress === "refresh"}
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm disabled:opacity-50 flex items-center gap-2"
          >
            <span className={actionInProgress === "refresh" ? "animate-spin" : ""}>⟳</span>
            {actionInProgress === "refresh" ? "Ingesting..." : "Trigger Full Refresh"}
          </button>
        </div>
      </div>

      {msg && (
        <div
          className={`p-4 rounded-xl border text-sm ${
            msg.type === "success"
              ? "bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300"
              : "bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-800 dark:text-rose-300"
          }`}
        >
          {msg.text}
        </div>
      )}

      {/* KPI Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Engine State
          </div>
          <div className="mt-2 text-2xl font-bold flex items-center gap-2">
            <span
              className={`w-3 h-3 rounded-full ${
                !isGlobalPaused ? "bg-emerald-500 animate-pulse" : "bg-rose-500"
              }`}
            />
            <span className="text-slate-900 dark:text-white">
              {statusData?.engine_state || "ACTIVE"}
            </span>
          </div>
          <div className="mt-1 text-xs text-slate-500">
            {statusData?.total_active_sources || 0} of {statusData?.total_sources_configured || 0} sources active
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Canonical Jobs Ingested
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {statusData?.total_opportunities_discovered.jobs.toLocaleString() || 0}
          </div>
          <div className="mt-1 text-xs text-emerald-600 font-medium">Verified Core Records</div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Startup Problem Signals
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {statusData?.total_opportunities_discovered.startups.toLocaleString() || 0}
          </div>
          <div className="mt-1 text-xs text-indigo-600 font-medium">Corroborated Observations</div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Total Discovered Pipeline
          </div>
          <div className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
            {statusData?.total_opportunities_discovered.total.toLocaleString() || 0}
          </div>
          <div className="mt-1 text-xs text-slate-500">Live Cross-Module Opportunities</div>
        </div>
      </div>

      {/* Configured Sources & Schedules */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Configured Refresh Schedules & Quotas
          </h2>
          <span className="text-xs text-slate-500">
            Server Time: {statusData?.server_time ? new Date(statusData.server_time).toLocaleTimeString() : "--"}
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading schedule configurations...</div>
        ) : !statusData?.schedules || statusData.schedules.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No schedules configured.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Source Identifier</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Cadence / Interval</th>
                  <th className="px-6 py-4">Max Records / Run</th>
                  <th className="px-6 py-4">Last Execution</th>
                  <th className="px-6 py-4">Next Run Due</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {statusData.schedules.map((sch) => (
                  <tr key={sch.source_id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                      {sch.source_name}
                      <div className="text-xs font-mono text-slate-400 font-normal">
                        {sch.source_id}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                          !sch.is_paused
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                            : "bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300"
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            !sch.is_paused ? "bg-emerald-500" : "bg-slate-400"
                          }`}
                        />
                        {!sch.is_paused ? "ACTIVE" : "PAUSED"}
                      </span>
                    </td>

                    <td className="px-6 py-4 font-mono text-xs">
                      {sch.interval_seconds >= 3600
                        ? `${sch.interval_seconds / 3600} hr`
                        : `${sch.interval_seconds / 60} min`}
                    </td>

                    <td className="px-6 py-4 font-mono text-xs">
                      {sch.max_records_per_run} records
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-500">
                      {sch.last_run_at ? new Date(sch.last_run_at).toLocaleString() : "Pending initial run"}
                    </td>

                    <td className="px-6 py-4 text-xs font-mono text-indigo-600 dark:text-indigo-400">
                      {sch.next_run_at ? new Date(sch.next_run_at).toLocaleTimeString() : "--"}
                    </td>

                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleToggleSourcePause(sch.source_id, sch.is_paused)}
                        disabled={actionInProgress === sch.source_id}
                        className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                          sch.is_paused
                            ? "bg-emerald-100 text-emerald-800 hover:bg-emerald-200 dark:bg-emerald-950 dark:text-emerald-300"
                            : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
                        }`}
                      >
                        {sch.is_paused ? "Resume" : "Pause"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recent Executions Audit */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Recent Task Execution Logs
          </h2>
        </div>

        {!statusData?.recent_executions || statusData.recent_executions.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No execution logs recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Task Name</th>
                  <th className="px-6 py-4">Source ID</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Records (Fetched / Stored)</th>
                  <th className="px-6 py-4">Execution Time</th>
                  <th className="px-6 py-4">Completed At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {statusData.recent_executions.map((ex) => (
                  <tr key={ex.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                      {ex.task_name}
                      <div className="text-xs text-slate-400 font-mono font-normal">{ex.task_type}</div>
                    </td>

                    <td className="px-6 py-4 text-xs font-mono text-slate-500">
                      {ex.source_id || "GLOBAL"}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          ex.status === "SUCCESS"
                            ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300"
                            : ex.status === "RUNNING"
                            ? "bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300"
                            : "bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300"
                        }`}
                      >
                        {ex.status}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-xs font-mono">
                      {ex.records_fetched} fetched /{" "}
                      <span className="text-emerald-600 font-bold">{ex.records_inserted} inserted</span>
                    </td>

                    <td className="px-6 py-4 text-xs font-mono text-slate-500">
                      {ex.duration_ms !== null ? `${ex.duration_ms} ms` : "--"}
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-500">
                      {ex.completed_at ? new Date(ex.completed_at).toLocaleTimeString() : "--"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

