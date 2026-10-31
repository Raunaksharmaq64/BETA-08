"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface JobSource {
  id: string;
  source_key: string;
  display_name: string;
  source_type: string;
  provider: string;
  base_url: string;
  enabled: boolean;
  policy_status: string;
  rate_limit_per_minute: number;
  timeout_seconds: number;
  retry_max_attempts: number;
  circuit_breaker_state: string;
  consecutive_failures: number;
  last_success_at: string | null;
  last_failure_at: string | null;
  cooldown_until: string | null;
  created_at: string;
}

interface RunLog {
  id: string;
  trigger_type: string;
  status: string;
  records_fetched: number;
  records_normalized: number;
  records_inserted: number;
  records_updated: number;
  duplicates_skipped: number;
  error_category: string | null;
  safe_error_summary: string | null;
  started_at: string;
  duration_seconds: number | null;
}

interface Observation {
  id: string;
  external_job_id: string;
  listing_url: string;
  observed_at: string;
  normalization_status: string;
  payload_hash_sha256: string;
  first_seen_at: string;
  last_seen_at: string;
}

export default function SourceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const sourceId = params.sourceId as string;

  const [source, setSource] = useState<JobSource | null>(null);
  const [runs, setRuns] = useState<RunLog[]>([]);
  const [observations, setObservations] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Policy Form
  const [targetPolicy, setTargetPolicy] = useState("ACTIVE");
  const [reviewNotes, setReviewNotes] = useState("Verified public documentation and rate limits.");
  const [policySubmitting, setPolicySubmitting] = useState(false);

  // Ingestion Form
  const [ingestMax, setIngestMax] = useState(50);
  const [ingestForce, setIngestForce] = useState(false);
  const [ingesting, setIngesting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [srcRes, runsRes, obsRes] = await Promise.all([
        apiClient<JobSource>(`/sources/${sourceId}`),
        apiClient<RunLog[]>(`/sources/${sourceId}/runs`),
        apiClient<Observation[]>(`/sources/${sourceId}/observations`),
      ]);
      setSource(srcRes.data);
      setRuns(runsRes.data);
      setObservations(obsRes.data);
      setTargetPolicy(srcRes.data.policy_status);
    } catch (err: any) {
      setError(err?.message || "Failed to load source details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sourceId) {
      loadData();
    }
  }, [sourceId]);

  const handleUpdatePolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setPolicySubmitting(true);
      setError(null);
      setSuccessMsg(null);
      await apiClient(`/sources/${sourceId}/policy`, {
        method: "PATCH",
        body: JSON.stringify({
          policy_status: targetPolicy,
          review_notes: reviewNotes,
        }),
      });
      setSuccessMsg(`Policy gate successfully transitioned to ${targetPolicy}.`);
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to update policy status.");
    } finally {
      setPolicySubmitting(false);
    }
  };

  const handleTriggerIngest = async () => {
    try {
      setIngesting(true);
      setError(null);
      setSuccessMsg(null);
      const res = await apiClient<any>(`/sources/${sourceId}/ingest`, {
        method: "POST",
        body: JSON.stringify({
          max_records: Number(ingestMax),
          force: Boolean(ingestForce),
        }),
      });
      const d = res.data;
      setSuccessMsg(
        `Ingestion run complete: ${d.records_fetched} fetched, ${d.records_inserted} inserted, ${d.records_updated} updated in ${d.duration_seconds}s.`
      );
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Ingestion run failed.");
    } finally {
      setIngesting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-slate-400">
        Loading source configuration & logs...
      </div>
    );
  }

  if (!source) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-12 text-center text-rose-400">
        Source not found. <Link href="/sources" className="underline">Back to Sources</Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Breadcrumb & Header */}
      <div>
        <Link href="/sources" className="text-xs text-indigo-400 hover:underline">&larr; Back to Sources Registry</Link>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
          <div>
            <h1 className="text-3xl font-bold text-white">{source.display_name}</h1>
            <p className="text-sm font-mono text-slate-400">{source.source_key}</p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700 capitalize">
              {source.provider}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-950 text-indigo-400 border border-indigo-800">
              Policy: {source.policy_status}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
              Circuit: {source.circuit_breaker_state}
            </span>
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="p-4 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 text-sm">
          {successMsg}
        </div>
      )}

      {error && (
        <div className="p-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Grid: Config & Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Source Metadata Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">Configuration</h2>
          <div className="space-y-3 text-sm">
            <div>
              <span className="text-slate-400 block text-xs">Endpoint URL</span>
              <span className="text-slate-200 font-mono text-xs break-all">{source.base_url}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Integration / Auth</span>
              <span className="text-slate-200">{source.source_type} &bull; Public</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Rate Limit Quota</span>
              <span className="text-slate-200 font-mono">{source.rate_limit_per_minute} req/min</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">HTTP Timeout & Max Retries</span>
              <span className="text-slate-200">{source.timeout_seconds}s timeout &bull; {source.retry_max_attempts} retries (with jitter)</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Consecutive Failures</span>
              <span className={source.consecutive_failures > 0 ? "text-rose-400 font-bold" : "text-emerald-400"}>
                {source.consecutive_failures}
              </span>
            </div>
          </div>
        </div>

        {/* Policy Gate Review Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">Governance Policy Gate</h2>
          <form onSubmit={handleUpdatePolicy} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Target Status</label>
              <select
                value={targetPolicy}
                onChange={(e) => setTargetPolicy(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none"
              >
                <option value="DRAFT">DRAFT</option>
                <option value="PENDING_REVIEW">PENDING_REVIEW</option>
                <option value="APPROVED">APPROVED</option>
                <option value="ACTIVE">ACTIVE (Permitted to ingest)</option>
                <option value="PAUSED">PAUSED</option>
                <option value="BLOCKED">BLOCKED</option>
                <option value="RETIRED">RETIRED</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Audit Rationale</label>
              <textarea
                required
                rows={2}
                value={reviewNotes}
                onChange={(e) => setReviewNotes(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={policySubmitting}
              className="w-full py-2 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
            >
              {policySubmitting ? "Updating..." : "Update Policy Decision"}
            </button>
          </form>
        </div>

        {/* Ingestion Trigger Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold text-white border-b border-slate-800 pb-2">Trigger Ingestion</h2>
          <p className="text-xs text-slate-400">
            Executes connector with sliding-window quota, 3-state circuit breaker check, and canonical normalization.
          </p>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Max Listings to Ingest</label>
              <input
                type="number"
                min="1"
                max="500"
                value={ingestMax}
                onChange={(e) => setIngestMax(Number(e.target.value))}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="forceBox"
                checked={ingestForce}
                onChange={(e) => setIngestForce(e.target.checked)}
                className="rounded bg-slate-950 border-slate-800 text-indigo-600"
              />
              <label htmlFor="forceBox" className="text-xs text-slate-300">
                Force execution (trial bypass if circuit is OPEN)
              </label>
            </div>
            <button
              type="button"
              onClick={handleTriggerIngest}
              disabled={ingesting || source.policy_status !== "ACTIVE"}
              className="w-full py-2 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50"
            >
              {ingesting ? "Ingesting Feed..." : "Run Ingestion Now"}
            </button>
            {source.policy_status !== "ACTIVE" && (
              <p className="text-[11px] text-amber-400 text-center">
                Ingestion blocked by Policy Gate. Source must be in ACTIVE status.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Execution Run Logs Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white">Ingestion Run History & Metrics</h2>
        </div>
        {runs.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">No ingestion runs logged yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">Started</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Fetched</th>
                  <th className="px-6 py-3">Inserted</th>
                  <th className="px-6 py-3">Updated</th>
                  <th className="px-6 py-3">Duplicates</th>
                  <th className="px-6 py-3">Duration</th>
                  <th className="px-6 py-3">Errors</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {runs.map((r) => (
                  <tr key={r.id}>
                    <td className="px-6 py-3 font-mono">{new Date(r.started_at).toLocaleString()}</td>
                    <td className="px-6 py-3">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        r.status === "SUCCESS" ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 font-mono">{r.records_fetched}</td>
                    <td className="px-6 py-3 font-mono text-emerald-400">+{r.records_inserted}</td>
                    <td className="px-6 py-3 font-mono text-blue-400">{r.records_updated}</td>
                    <td className="px-6 py-3 font-mono text-slate-400">{r.duplicates_skipped}</td>
                    <td className="px-6 py-3 font-mono">{r.duration_seconds ? `${r.duration_seconds}s` : "-"}</td>
                    <td className="px-6 py-3 max-w-xs truncate text-rose-300" title={r.safe_error_summary || ""}>
                      {r.safe_error_summary || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Observations Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white">Raw Source Observations (Provenance)</h2>
        </div>
        {observations.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-sm">No raw observations recorded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-3">External ID</th>
                  <th className="px-6 py-3">Listing URL</th>
                  <th className="px-6 py-3">Payload SHA-256</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Last Seen</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {observations.map((obs) => (
                  <tr key={obs.id}>
                    <td className="px-6 py-3 font-mono font-semibold text-white">{obs.external_job_id}</td>
                    <td className="px-6 py-3 max-w-sm truncate">
                      <a href={obs.listing_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">
                        {obs.listing_url}
                      </a>
                    </td>
                    <td className="px-6 py-3 font-mono text-slate-400">{obs.payload_hash_sha256.slice(0, 12)}...</td>
                    <td className="px-6 py-3">
                      <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800 text-slate-300">
                        {obs.normalization_status}
                      </span>
                    </td>
                    <td className="px-6 py-3 font-mono">{new Date(obs.last_seen_at).toLocaleString()}</td>
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
