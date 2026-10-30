"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface DuplicateCandidate {
  id: string;
  primary_opportunity_id: string;
  primary_title: string;
  primary_company: string;
  primary_location: string | null;
  duplicate_opportunity_id: string;
  duplicate_title: string;
  duplicate_company: string;
  duplicate_location: string | null;
  match_tier: string;
  match_method: string;
  confidence_score: number;
  match_evidence: Record<string, any>;
  status: string;
  created_at: string;
}

export default function DuplicateReviewWorkbenchPage() {
  const [candidates, setCandidates] = useState<DuplicateCandidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("PROPOSED");

  // Merge Modal State
  const [activeMergeCandidate, setActiveMergeCandidate] = useState<DuplicateCandidate | null>(null);
  const [mergeReason, setMergeReason] = useState("Verified same position across sources");
  const [merging, setMerging] = useState(false);

  // Unmerge Modal State
  const [activeUnmergeDecisionId, setActiveUnmergeDecisionId] = useState<string | null>(null);
  const [unmergeReason, setUnmergeReason] = useState("Re-evaluating role uniqueness based on new candidate evidence");
  const [unmerging, setUnmerging] = useState(false);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient<DuplicateCandidate[]>(`/duplicates?status=${filterStatus}`);
      setCandidates(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load duplicate candidates.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [filterStatus]);

  const handleRunDetection = async () => {
    try {
      setDetecting(true);
      setError(null);
      setSuccessMsg(null);
      const res = await apiClient<{ detected_count: number; lookback_days: number }>("/duplicates/detect", {
        method: "POST",
      });
      setSuccessMsg(`Detection complete! Found ${res.data.detected_count} new candidate duplicate pair(s).`);
      await fetchCandidates();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Detection routine failed.");
    } finally {
      setDetecting(false);
    }
  };

  const handleConfirmMerge = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeMergeCandidate) return;
    try {
      setMerging(true);
      setError(null);
      await apiClient("/duplicates/merge", {
        method: "POST",
        body: JSON.stringify({
          primary_id: activeMergeCandidate.primary_opportunity_id,
          duplicate_ids: [activeMergeCandidate.duplicate_opportunity_id],
          reason: mergeReason.trim(),
        }),
      });
      setSuccessMsg("Successfully merged! Duplicate opportunity suppressed and source mappings reassigned.");
      setActiveMergeCandidate(null);
      await fetchCandidates();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to merge opportunities.");
    } finally {
      setMerging(false);
    }
  };

  const getTierBadge = (tier: string) => {
    if (tier === "TIER_1_EXACT") {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-purple-950 text-purple-300 border border-purple-800">
          Tier 1: Exact Match
        </span>
      );
    }
    if (tier === "TIER_2_STRONG") {
      return (
        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-950 text-blue-300 border border-blue-800">
          Tier 2: Strong Multi-Attribute
        </span>
      );
    }
    return (
      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-950 text-amber-300 border border-amber-800">
        Tier 3: Probable Similarity
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <Link href="/quality" className="text-xs text-slate-400 hover:text-white transition-colors">
          &larr; Back to Quality Dashboard
        </Link>
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Duplicate Review & Merge Workbench</h1>
            <p className="mt-2 text-sm text-slate-400 max-w-3xl">
              Inspect cross-source duplicate candidates, verify multi-attribute matching evidence,
              and execute auditable, reversible merges to protect candidate discovery from repost clutter.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRunDetection}
              disabled={detecting}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50 transition-colors shadow-lg shadow-indigo-950"
            >
              {detecting ? "Running Detection..." : "Run Duplicate Detection"}
            </button>
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

      {/* Filter Tabs */}
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setFilterStatus("PROPOSED")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            filterStatus === "PROPOSED"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-850"
          }`}
        >
          Proposed Candidates
        </button>
        <button
          onClick={() => setFilterStatus("CONFIRMED")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            filterStatus === "CONFIRMED"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-850"
          }`}
        >
          Confirmed Merges
        </button>
        <button
          onClick={() => setFilterStatus("ALL")}
          className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
            filterStatus === "ALL"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-850"
          }`}
        >
          All Records
        </button>
      </div>

      {/* Candidate List */}
      {loading ? (
        <div className="p-16 text-center text-slate-400">Loading duplicate candidates...</div>
      ) : candidates.length === 0 ? (
        <div className="p-12 text-center text-slate-400 bg-slate-900 border border-slate-800 rounded-xl space-y-3">
          <p className="text-sm text-slate-300">No duplicate candidates found in &quot;{filterStatus}&quot; state.</p>
          <p className="text-xs">
            Click &quot;Run Duplicate Detection&quot; above to scan recent opportunities across all sources.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {candidates.map((cand) => (
            <div
              key={cand.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl"
            >
              {/* Header Badge & Confidence */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-4 gap-3">
                <div className="flex items-center space-x-3">
                  {getTierBadge(cand.match_tier)}
                  <span className="text-xs font-semibold text-slate-300">
                    Confidence: {(cand.confidence_score * 100).toFixed(0)}%
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono">
                    Method: {cand.match_method}
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      cand.status === "CONFIRMED"
                        ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                        : cand.status === "UNMERGED"
                        ? "bg-amber-950 text-amber-400 border border-amber-800"
                        : "bg-blue-950 text-blue-300 border border-blue-800"
                    }`}
                  >
                    Status: {cand.status}
                  </span>

                  {cand.status === "PROPOSED" && (
                    <button
                      onClick={() => setActiveMergeCandidate(cand)}
                      className="px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
                    >
                      Merge into Primary &rarr;
                    </button>
                  )}
                </div>
              </div>

              {/* Side-by-Side Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Primary Listing */}
                <div className="bg-slate-950 p-4 rounded-xl border border-emerald-900/50 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                      Primary Canonical Opportunity
                    </span>
                    <Link
                      href={`/opportunities/${cand.primary_opportunity_id}`}
                      className="text-[11px] text-indigo-400 hover:underline"
                    >
                      View Details &rarr;
                    </Link>
                  </div>
                  <h3 className="text-base font-bold text-white">{cand.primary_title}</h3>
                  <div className="text-xs font-semibold text-indigo-300">
                    {cand.primary_company} &bull; {cand.primary_location || "Location not stated"}
                  </div>
                  <div className="text-[11px] font-mono text-slate-500">
                    ID: {cand.primary_opportunity_id}
                  </div>
                </div>

                {/* Duplicate Listing */}
                <div className="bg-slate-950 p-4 rounded-xl border border-rose-900/40 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-rose-400">
                      Duplicate Listing (To Suppress)
                    </span>
                    <Link
                      href={`/opportunities/${cand.duplicate_opportunity_id}`}
                      className="text-[11px] text-indigo-400 hover:underline"
                    >
                      View Details &rarr;
                    </Link>
                  </div>
                  <h3 className="text-base font-bold text-white">{cand.duplicate_title}</h3>
                  <div className="text-xs font-semibold text-indigo-300">
                    {cand.duplicate_company} &bull; {cand.duplicate_location || "Location not stated"}
                  </div>
                  <div className="text-[11px] font-mono text-slate-500">
                    ID: {cand.duplicate_opportunity_id}
                  </div>
                </div>
              </div>

              {/* Match Evidence Details */}
              {cand.match_evidence && Object.keys(cand.match_evidence).length > 0 && (
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs text-slate-400 space-y-1">
                  <span className="font-semibold text-slate-300 block">Match Evidence Criteria:</span>
                  <pre className="text-[10px] font-mono text-slate-400 overflow-x-auto">
                    {JSON.stringify(cand.match_evidence, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Merge Action Confirmation Modal */}
      {activeMergeCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Confirm Duplicate Opportunity Merge</h3>
              <button
                onClick={() => setActiveMergeCandidate(null)}
                className="text-slate-400 hover:text-white text-lg"
              >
                &times;
              </button>
            </div>

            <div className="text-xs text-slate-300 space-y-2">
              <p>
                You are merging <strong className="text-rose-400">{activeMergeCandidate.duplicate_title}</strong> at{" "}
                <strong className="text-white">{activeMergeCandidate.duplicate_company}</strong> into the primary listing.
              </p>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1 text-[11px]">
                <div>&bull; Duplicate opportunity will be marked <code className="text-rose-400">is_suppressed=true</code>.</div>
                <div>&bull; Source mappings will be reassigned to the primary canonical record.</div>
                <div>&bull; An auditable, reversible <code className="text-indigo-400">MergeDecisionRecord</code> will be logged.</div>
              </div>
            </div>

            <form onSubmit={handleConfirmMerge} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Auditable Justification Reason</label>
                <textarea
                  value={mergeReason}
                  onChange={(e) => setMergeReason(e.target.value)}
                  rows={3}
                  required
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveMergeCandidate(null)}
                  className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={merging}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {merging ? "Merging..." : "Confirm & Merge"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

