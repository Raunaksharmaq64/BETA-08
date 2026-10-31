"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";

interface OpportunityDetail {
  opportunity: {
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
    published_at: string;
    first_seen_at?: string;
    last_checked_at?: string;
    corroboration_count: number;
    has_conflicting_evidence: boolean;
  };
  ai_summary: {
    is_ai_generated: boolean;
    model: string;
    generated_at?: string;
    insight?: string;
    opportunity?: string;
    pitch_idea?: string;
    problem_explanation?: string;
    how_to_solve_strategy?: string;
    disclaimer: string;
  };
  evidence_ledger: Array<{
    id: string;
    source_title: string;
    source_url?: string;
    publisher: string;
    source_type: string;
    observation_excerpt: string;
    collection_method: string;
    source_limitations?: string;
    published_at: string;
    retrieved_at?: string;
    is_corroborating: boolean;
  }>;
  technology_findings: Array<{
    id: string;
    technology_name: string;
    category: string;
    finding_type: string;
    confidence_score: number;
    traceable_evidence: string;
  }>;
  corroboration_ledger: Array<{
    id: string;
    source_identifier: string;
    source_name: string;
    is_independent: boolean;
    conflicts_with_primary: boolean;
    notes?: string;
  }>;
}

export default function StartupOpportunityDetailPage() {
  const params = useParams();
  const oppId = params.opportunityId as string;

  const [data, setData] = useState<OpportunityDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"observation" | "ai" | "tech" | "corroboration">("observation");

  useEffect(() => {
    if (!oppId) return;
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<any>(`/startups/${oppId}`);
        setData(res.data);
      } catch (err: any) {
        setError(err?.message || "Failed to load startup details.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [oppId]);

  const handleBookmark = async () => {
    try {
      await apiClient.post(`/startups/${oppId}/save`, { notes: "Bookmarked from detail view" });
      alert("Opportunity bookmarked successfully!");
    } catch (err: any) {
      alert("Failed to bookmark: " + (err?.message || "Error"));
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Loading deep opportunity intelligence...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="space-y-4">
        <Link href="/startups" className="text-sm font-semibold text-indigo-600 hover:underline">
          &larr; Back to Directory
        </Link>
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm">
          {error || "Startup opportunity not found."}
        </div>
      </div>
    );
  }

  const { opportunity, ai_summary, evidence_ledger, technology_findings, corroboration_ledger } = data;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <Link href="/startups" className="text-sm font-semibold text-indigo-600 hover:underline">
          &larr; Back to Startup Directory
        </Link>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleBookmark}
            className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 shadow-sm"
          >
            Bookmark
          </button>
          <Link
            href={`/startups/${oppId}/workspace`}
            className="px-4 py-2 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-700 shadow-sm flex items-center gap-1"
          >
            🚀 Opportunity Workspace
          </Link>
          <Link
            href={`/startups/${oppId}/pitch`}
            className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-sm"
          >
            Draft Outreach Pitch &rarr;
          </Link>
        </div>
      </div>

      {/* Header Profile Card */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                {opportunity.category}
              </span>
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                Source: {opportunity.primary_source}
              </span>
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                  opportunity.has_conflicting_evidence
                    ? "bg-amber-50 text-amber-800 border-amber-300"
                    : opportunity.corroboration_count >= 3
                    ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                    : opportunity.corroboration_count >= 2
                    ? "bg-blue-50 text-blue-800 border-blue-300"
                    : "bg-slate-100 text-slate-700 border-slate-300"
                }`}
              >
                {opportunity.has_conflicting_evidence
                  ? "⚠️ Customer Validation Required"
                  : opportunity.corroboration_count >= 3
                  ? "✓ Independently Corroborated"
                  : opportunity.corroboration_count >= 2
                  ? "⚡ Repeated Observations"
                  : "○ Observed Problem"}
              </span>
            </div>
            <h1 className="text-2xl font-bold text-slate-900">{opportunity.startup_name}</h1>
            {opportunity.domain && (
              <p className="text-sm text-slate-500 font-mono mt-0.5">
                <a
                  href={opportunity.website_url || `https://${opportunity.domain}`}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:underline text-indigo-600"
                >
                  {opportunity.domain} ↗
                </a>
              </p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center flex-1 sm:flex-none min-w-[120px]">
              <div className="text-xs font-semibold text-slate-500 uppercase">Urgency Score</div>
              <div
                className={`text-xl font-bold mt-0.5 ${
                  opportunity.urgency_score >= 8
                    ? "text-rose-600"
                    : opportunity.urgency_score >= 6
                    ? "text-amber-600"
                    : "text-slate-800"
                }`}
              >
                {opportunity.urgency_score} / 10
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-center flex-1 sm:flex-none min-w-[120px]">
              <div className="text-xs font-semibold text-slate-500 uppercase">Corroboration</div>
              <div className="text-xl font-bold text-slate-800 mt-0.5">
                {opportunity.corroboration_count} Source{opportunity.corroboration_count > 1 ? "s" : ""}
              </div>
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100">
          <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">
            Detected Problem Statement
          </div>
          <p className="text-sm text-slate-800 font-medium leading-relaxed">
            {opportunity.detected_signal}
          </p>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex border-b border-slate-200 space-x-6 text-sm font-semibold overflow-x-auto scrollbar-none whitespace-nowrap">
        <button
          onClick={() => setActiveTab("observation")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "observation"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          1. Observation Ledger ({evidence_ledger.length})
        </button>
        <button
          onClick={() => setActiveTab("ai")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "ai"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          2. AI Summary & Strategy
        </button>
        <button
          onClick={() => setActiveTab("tech")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "tech"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          3. Technographics ({technology_findings.length})
        </button>
        <button
          onClick={() => setActiveTab("corroboration")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "corroboration"
              ? "border-indigo-600 text-indigo-600"
              : "border-transparent text-slate-500 hover:text-slate-800"
          }`}
        >
          4. Corroboration & Audit ({corroboration_ledger.length})
        </button>
      </div>

      {/* Tab 1: Observation Ledger */}
      {activeTab === "observation" && (
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-blue-900 text-xs">
            <strong>Provenance Policy:</strong> These observations represent unaltered data obtained directly from public feeds or website audits. AI interpretation is strictly excluded from this tab.
          </div>

          {evidence_ledger.map((ev) => (
            <div key={ev.id} className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-500">
                <span className="font-semibold text-slate-800">{ev.publisher}</span>
                <span className="px-2 py-0.5 rounded bg-slate-100 font-mono">{ev.source_type}</span>
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">{ev.source_title}</h4>
                <blockquote className="mt-2 p-3 bg-slate-50 rounded-lg border-l-4 border-indigo-400 text-xs text-slate-700 italic leading-relaxed">
                  &ldquo;{ev.observation_excerpt}&rdquo;
                </blockquote>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-xs text-slate-500">
                <div>Published: {ev.published_at}</div>
                <div>Retrieved: {ev.retrieved_at ? new Date(ev.retrieved_at).toLocaleDateString() : "N/A"}</div>
                <div>Method: {ev.collection_method}</div>
                <div>
                  {ev.source_url ? (
                    <a href={ev.source_url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">
                      View Original URL ↗
                    </a>
                  ) : (
                    "URL Unavailable"
                  )}
                </div>
              </div>
              {ev.source_limitations && (
                <div className="text-xs text-slate-400 mt-1">
                  <strong>Limitation Notes:</strong> {ev.source_limitations}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Tab 2: AI Summary & Strategy */}
      {activeTab === "ai" && (
        <div className="space-y-5">
          {/* AI Banner */}
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl text-purple-900 text-xs flex items-center justify-between">
            <div>
              <span className="font-bold">Machine-Generated Synthesis:</span> Model: {ai_summary.model}
            </div>
            <div className="text-purple-700 font-mono">
              Generated: {ai_summary.generated_at ? new Date(ai_summary.generated_at).toLocaleString() : "Cached"}
            </div>
          </div>

          <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Root Cause &amp; Technical Bottleneck
              </h3>
              <p className="text-sm text-slate-700 mt-1 leading-relaxed">
                {ai_summary.insight || ai_summary.problem_explanation || "No deep insight generated yet."}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Recommended Solution Direction
              </h3>
              <p className="text-sm text-slate-700 mt-1 leading-relaxed">
                {ai_summary.opportunity || "Solution direction pending candidate formulation."}
              </p>
            </div>

            {ai_summary.how_to_solve_strategy && (
              <div className="pt-4 border-t border-slate-100">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Strategic Execution Roadmap
                </h3>
                <div className="mt-2 p-3 bg-slate-50 rounded-lg text-xs text-slate-800 font-mono whitespace-pre-wrap">
                  {ai_summary.how_to_solve_strategy}
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-100 p-3 bg-slate-50 rounded-lg text-xs text-slate-500 italic">
              <strong>Governance Notice:</strong> {ai_summary.disclaimer}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Technographics */}
      {activeTab === "tech" && (
        <div className="space-y-4">
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
            <strong>Evidence-Based Findings:</strong> Only technologies with public code tags, website audit proofs, or explicit mention in founder issues are presented. General industry speculation is strictly blocked.
          </div>

          {technology_findings.length === 0 ? (
            <div className="p-8 bg-white rounded-xl border border-slate-200 text-center text-slate-500 text-sm">
              No specific technology stack signals detected in current public observations.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {technology_findings.map((tf) => (
                <div key={tf.id} className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-slate-900">{tf.technology_name}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 font-semibold">
                      {tf.finding_type}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500">
                    Category: <span className="font-medium text-slate-700">{tf.category}</span> | Confidence:{" "}
                    <span className="font-semibold text-emerald-700">{Math.round(tf.confidence_score * 100)}%</span>
                  </div>
                  <div className="text-xs text-slate-400 italic pt-1 border-t border-slate-100">
                    Traceability: {tf.traceable_evidence}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Corroboration & Audit */}
      {activeTab === "corroboration" && (
        <div className="space-y-4">
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
            <strong>Corroboration Protocol:</strong> Distinguishes independent verification from repeated syndications. Multiple independent sources increase trust rating.
          </div>

          {corroboration_ledger.map((cr) => (
            <div key={cr.id} className="p-4 bg-white rounded-xl border border-slate-200 shadow-sm flex items-center justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-900">{cr.source_name}</h4>
                <p className="text-xs text-slate-500 font-mono mt-0.5">ID: {cr.source_identifier}</p>
                {cr.notes && <p className="text-xs text-slate-600 mt-1">{cr.notes}</p>}
              </div>
              <div>
                <span
                  className={`text-xs px-2.5 py-1 rounded-full font-semibold ${
                    cr.is_independent ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-700"
                  }`}
                >
                  {cr.is_independent ? "Independent Source" : "Syndicated Duplicate"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

