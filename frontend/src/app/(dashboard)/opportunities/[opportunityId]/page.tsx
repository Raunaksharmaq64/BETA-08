"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";

interface VerificationEvidence {
  id: string;
  opportunity_id: string;
  source_id: string;
  check_id: string;
  check_timestamp: string;
  check_method: string;
  check_outcome: string;
  http_status: number | null;
  provider_status: string | null;
  evidence_category: string;
  evidence_reference: string | null;
  safe_response_metadata: Record<string, any>;
  verification_rule_version: string;
  confidence_category: string;
  error_category: string | null;
}

interface OpportunityVerificationDetail {
  opportunity_id: string;
  verification_status: string;
  freshness_state: string;
  user_friendly_status: string;
  user_explanation: string;
  published_at: string | null;
  source_updated_at: string | null;
  first_seen_at: string;
  last_seen_at: string;
  last_checked_at: string | null;
  last_successful_check_at: string | null;
  last_verified_at: string | null;
  status_changed_at: string | null;
  closed_at: string | null;
  expires_at: string | null;
  is_suppressed: boolean;
  evidence_history: VerificationEvidence[];
}

interface SourceMapping {
  id: string;
  source_key: string;
  external_job_id: string;
  original_url: string;
  first_seen_at: string;
  last_seen_at: string;
  mapping_status: string;
  match_tier: string;
  match_method: string;
  confidence_score: number;
}

interface OpportunityBasic {
  id: string;
  title: string;
  company_name: string;
  description_clean: string;
  employment_type: string;
  is_remote: boolean;
  city: string | null;
  country: string | null;
  min_salary: number | null;
  max_salary: number | null;
  currency: string | null;
  application_url: string;
}

export default function OpportunityVerificationPage() {
  const params = useParams();
  const opportunityId = params?.opportunityId as string;

  const [opp, setOpp] = useState<OpportunityBasic | null>(null);
  const [detail, setDetail] = useState<OpportunityVerificationDetail | null>(null);
  const [mappings, setMappings] = useState<SourceMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchData = async () => {
    if (!opportunityId) return;
    try {
      setLoading(true);
      setError(null);

      const [oppRes, verifRes, mapRes] = await Promise.all([
        apiClient<OpportunityBasic>(`/opportunities/${opportunityId}`),
        apiClient<OpportunityVerificationDetail>(`/opportunities/${opportunityId}/verification`),
        apiClient<SourceMapping[]>(`/opportunities/${opportunityId}/mappings`),
      ]);

      setOpp(oppRes.data);
      setDetail(verifRes.data);
      setMappings(mapRes.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load opportunity verification details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [opportunityId]);

  const handleVerifyNow = async () => {
    try {
      setVerifying(true);
      setError(null);
      setSuccessMsg(null);

      const res = await apiClient<OpportunityVerificationDetail>(`/opportunities/${opportunityId}/verify`, {
        method: "POST",
        body: JSON.stringify({ force: true, check_method: "DIRECT_API" }),
      });

      setDetail(res.data);
      setSuccessMsg("Verification completed! Evidence logged and timestamps refreshed.");
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Verification check failed.");
    } finally {
      setVerifying(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Not recorded";
    try {
      return new Date(dateStr).toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 text-center text-slate-400">
        Loading verification evidence and timestamps...
      </div>
    );
  }

  if (error && !detail) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-16 space-y-4">
        <div className="p-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-sm">
          {error}
        </div>
        <Link href="/opportunities" className="text-sm text-indigo-400 underline">
          &larr; Return to Opportunities
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Navigation & Header */}
      <div className="space-y-4">
        <Link href="/opportunities" className="inline-flex items-center text-xs text-slate-400 hover:text-white transition-colors">
          &larr; Back to Canonical Opportunities
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold tracking-tight text-white">{opp?.title}</h1>
              {opp?.is_remote && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                  REMOTE
                </span>
              )}
            </div>
            <p className="mt-1 text-sm text-indigo-400">
              {opp?.company_name} &bull; {[opp?.city, opp?.country].filter(Boolean).join(", ") || "Location unstated"}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={handleVerifyNow}
              disabled={verifying}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50 transition-colors shadow-lg shadow-indigo-950"
            >
              {verifying ? "Executing Verification..." : "Verify Status Now"}
            </button>
            {opp?.application_url && (
              <a
                href={opp.application_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
              >
                Open Source URL &rarr;
              </a>
            )}
          </div>
        </div>
      </div>

      {successMsg && (
        <div className="p-3 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 text-xs">
          {successMsg}
        </div>
      )}

      {error && (
        <div className="p-3 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-xs">
          {error}
        </div>
      )}

      {/* Verification Status & Explanation Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
              Candidate Freshness Assessment
            </span>
            <div className="text-lg font-bold text-white mt-1">
              {detail?.user_friendly_status}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <span className="px-3 py-1 rounded-full text-xs font-bold border bg-indigo-950 text-indigo-300 border-indigo-800">
              State: {detail?.verification_status}
            </span>
            <span className="px-3 py-1 rounded-full text-xs font-bold border bg-slate-800 text-slate-300 border-slate-700">
              Freshness: {detail?.freshness_state}
            </span>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/80 p-3 rounded-lg border border-slate-800/80">
          {detail?.user_explanation}
        </p>
      </div>

      {/* 10 Independent Timestamps Grid */}
      <div className="space-y-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">
          Independent Observation & Verification Timestamps
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Published At</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.published_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">First Seen</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.first_seen_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Last Seen</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.last_seen_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Last Checked</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.last_checked_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Last Verified</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.last_verified_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Last Successful Check</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.last_successful_check_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Status Changed At</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.status_changed_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Source Updated At</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.source_updated_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Closed At</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.closed_at || null)}</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[11px] text-slate-500 block">Expires At</span>
            <span className="text-xs font-semibold text-white block">{formatDate(detail?.expires_at || null)}</span>
          </div>
        </div>
      </div>

      {/* Source Provenance & Mappings */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-bold text-white">Source Provenance & Requisition Mappings</h2>
        <p className="text-xs text-slate-400">
          Auditable mapping between external ATS board records and this canonical opportunity.
        </p>

        {mappings.length === 0 ? (
          <div className="text-xs text-slate-500 italic p-3 bg-slate-950 rounded-lg">
            No external source mappings recorded.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">Source Key</th>
                  <th className="py-2.5 px-3">External Job ID</th>
                  <th className="py-2.5 px-3">Match Tier</th>
                  <th className="py-2.5 px-3">Method</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">First Seen</th>
                  <th className="py-2.5 px-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {mappings.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-850">
                    <td className="py-2.5 px-3 font-mono text-indigo-400">{m.source_key}</td>
                    <td className="py-2.5 px-3 font-mono">{m.external_job_id}</td>
                    <td className="py-2.5 px-3 font-semibold text-emerald-400">{m.match_tier}</td>
                    <td className="py-2.5 px-3 text-slate-400">{m.match_method}</td>
                    <td className="py-2.5 px-3">{(m.confidence_score * 100).toFixed(0)}%</td>
                    <td className="py-2.5 px-3">{formatDate(m.first_seen_at)}</td>
                    <td className="py-2.5 px-3">
                      <a
                        href={m.original_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-400 hover:underline"
                      >
                        Source Link &rarr;
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Immutable Verification Evidence Trail */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-base font-bold text-white">Immutable Verification Evidence Trail</h2>
        <p className="text-xs text-slate-400">
          Chronological evidence log recorded every time this listing is probed via direct provider API or bounded URL checker.
        </p>

        {detail?.evidence_history.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500 italic bg-slate-950 rounded-lg">
            No verification evidence events recorded yet. Click &quot;Verify Status Now&quot; above to run the first check.
          </div>
        ) : (
          <div className="space-y-3">
            {detail?.evidence_history.map((ev) => (
              <div
                key={ev.id}
                className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2 hover:border-slate-700 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-white">{ev.check_method}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.check_outcome === "OPEN"
                          ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                          : ev.check_outcome === "CLOSED" || ev.check_outcome === "NOT_FOUND"
                          ? "bg-rose-950 text-rose-400 border border-rose-800"
                          : "bg-amber-950 text-amber-400 border border-amber-800"
                      }`}
                    >
                      Outcome: {ev.check_outcome}
                    </span>
                    {ev.http_status && (
                      <span className="font-mono text-[11px] text-slate-400">HTTP {ev.http_status}</span>
                    )}
                  </div>
                  <span className="text-[11px] text-slate-500 font-mono">{formatDate(ev.check_timestamp)}</span>
                </div>

                <div className="text-xs text-slate-300 flex flex-wrap gap-x-4 gap-y-1">
                  <span>Category: <strong className="text-slate-200">{ev.evidence_category}</strong></span>
                  <span>Confidence: <strong className="text-slate-200">{ev.confidence_category}</strong></span>
                  {ev.evidence_reference && (
                    <span>Reference: <strong className="text-indigo-400 font-mono">{ev.evidence_reference}</strong></span>
                  )}
                  {ev.error_category && (
                    <span className="text-rose-400">Error: {ev.error_category}</span>
                  )}
                </div>

                {ev.safe_response_metadata && Object.keys(ev.safe_response_metadata).length > 0 && (
                  <pre className="text-[10px] font-mono bg-slate-900 p-2.5 rounded border border-slate-800/80 text-slate-400 overflow-x-auto">
                    {JSON.stringify(ev.safe_response_metadata, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

