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
    contact_email?: string;
    twitter_url?: string;
    linkedin_url?: string;
    github_url?: string;
    contact_page_url?: string;
    problem_explanation?: string;
    how_to_solve_strategy?: string;
    contact_info?: {
      email?: string;
      twitter?: string;
      linkedin?: string;
      github?: string;
      contact_page?: string;
    };
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
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisMessage, setAnalysisMessage] = useState<string | null>(null);
  const [copiedPitch, setCopiedPitch] = useState(false);

  const handleGenerateGeminiAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisMessage(null);
    try {
      const res: any = await apiClient.post(`/startups/${oppId}/analyze`, {});
      if (res?.data) {
        setData(prev => {
          if (!prev) return prev;
          return {
            ...prev,
            opportunity: {
              ...prev.opportunity,
              problem_explanation: res.data.problem_explanation,
              how_to_solve_strategy: res.data.how_to_solve_strategy,
              contact_email: res.data.contact_email || prev.opportunity.contact_email,
              twitter_url: res.data.twitter_url || prev.opportunity.twitter_url,
              linkedin_url: res.data.linkedin_url || prev.opportunity.linkedin_url,
              github_url: res.data.github_url || prev.opportunity.github_url,
              contact_page_url: res.data.contact_page_url || prev.opportunity.contact_page_url,
            },
            ai_summary: {
              ...prev.ai_summary,
              model: res.data.ai_model || "gemini-2.5-flash-lite",
              generated_at: res.data.ai_generated_at,
              insight: res.data.ai_insight || prev.ai_summary.insight,
              opportunity: res.data.ai_opportunity || prev.ai_summary.opportunity,
              pitch_idea: res.data.ai_pitch_idea || prev.ai_summary.pitch_idea,
              problem_explanation: res.data.problem_explanation,
              how_to_solve_strategy: res.data.how_to_solve_strategy,
            }
          };
        });
        setAnalysisMessage("✨ Gemini AI Blueprint successfully generated and saved!");
        setActiveTab("ai");
      }
    } catch (err: any) {
      alert("Gemini analysis error: " + (err?.message || "Error"));
    } finally {
      setAnalyzing(false);
    }
  };

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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <Link href="/startups" className="text-sm font-semibold text-indigo-400 hover:text-indigo-300 transition-colors">
          &larr; Back to Startup Directory
        </Link>
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleBookmark}
            className="px-4 py-2 text-xs font-semibold text-slate-200 bg-slate-800 border border-slate-700 rounded-lg hover:bg-slate-700 shadow-sm transition-colors"
          >
            ★ Bookmark
          </button>
          <button
            onClick={handleGenerateGeminiAnalysis}
            disabled={analyzing}
            className="px-4 py-2 text-xs font-bold text-white bg-gradient-to-r from-purple-600 via-indigo-600 to-emerald-600 rounded-lg hover:from-purple-500 hover:to-emerald-500 shadow-md flex items-center gap-1.5 transition-all disabled:opacity-50"
            title="Generate deep problem breakdown and step-by-step resolution strategy using Gemini LLM"
          >
            {analyzing ? (
              <>
                <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Running Gemini AI...</span>
              </>
            ) : (
              <>
                <span>✨</span>
                <span>Analyze with Gemini AI</span>
              </>
            )}
          </button>
          <Link
            href={`/startups/${oppId}/workspace`}
            className="px-4 py-2 text-xs font-semibold text-white bg-purple-600 rounded-lg hover:bg-purple-500 shadow-sm flex items-center gap-1 transition-colors"
          >
            🚀 Opportunity Workspace
          </Link>
          <Link
            href={`/startups/${oppId}/pitch`}
            className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 shadow-sm transition-colors"
          >
            Draft Outreach Pitch &rarr;
          </Link>
        </div>
      </div>

      {/* Header Profile Card */}
      <div className="p-6 bg-slate-900/90 rounded-xl border border-slate-800 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-900/50 text-purple-300 border border-purple-700/60">
                {opportunity.category}
              </span>
              <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                Source: {opportunity.primary_source}
              </span>
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                  opportunity.has_conflicting_evidence
                    ? "bg-amber-950/60 text-amber-300 border-amber-800/60"
                    : opportunity.corroboration_count >= 3
                    ? "bg-emerald-950/60 text-emerald-300 border-emerald-800/60"
                    : opportunity.corroboration_count >= 2
                    ? "bg-blue-950/60 text-blue-300 border-blue-800/60"
                    : "bg-slate-800 text-slate-300 border-slate-700"
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
            <h1 className="text-2xl font-bold text-white">{opportunity.startup_name}</h1>
            {opportunity.domain && (
              <p className="text-sm text-indigo-400 font-mono mt-0.5">
                <a
                  href={opportunity.website_url || `https://${opportunity.domain}`}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:underline"
                >
                  {opportunity.domain} ↗
                </a>
              </p>
            )}
          </div>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-center">
              <div className="text-xs font-semibold text-slate-400 uppercase">Urgency Score</div>
              <div
                className={`text-xl font-bold mt-0.5 ${
                  opportunity.urgency_score >= 8
                    ? "text-rose-400"
                    : opportunity.urgency_score >= 6
                    ? "text-amber-400"
                    : "text-slate-200"
                }`}
              >
                {opportunity.urgency_score} / 10
              </div>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-center">
              <div className="text-xs font-semibold text-slate-400 uppercase">Corroboration</div>
              <div className="text-xl font-bold text-slate-200 mt-0.5">
                {opportunity.corroboration_count} Source{opportunity.corroboration_count > 1 ? "s" : ""}
              </div>
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-800">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
            Detected Problem Statement
          </div>
          <p className="text-sm text-slate-200 font-medium leading-relaxed">
            {opportunity.detected_signal}
          </p>
        </div>

        {/* Founder & Company Social Accounts Row */}
        {(() => {
          const email = opportunity.contact_email || opportunity.contact_info?.email;
          const twitter = opportunity.twitter_url || opportunity.contact_info?.twitter;
          const linkedin = opportunity.linkedin_url || opportunity.contact_info?.linkedin;
          const github = opportunity.github_url || opportunity.contact_info?.github;
          const contactPage = opportunity.contact_page_url || opportunity.contact_info?.contact_page;
          const hasSocial = email || twitter || linkedin || github || contactPage;

          if (!hasSocial) return null;
          return (
            <div className="pt-3 border-t border-slate-800 space-y-2">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <span>🌐</span>
                <span>Founder &amp; Company Social Channels</span>
              </div>
              <div className="flex flex-wrap items-center gap-2.5">
                {linkedin && (
                  <a
                    href={linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-950 text-blue-300 border border-blue-800/80 hover:bg-blue-900 transition-colors shadow-sm"
                  >
                    <span>💼</span> LinkedIn Profile / Company ↗
                  </a>
                )}
                {twitter && (
                  <a
                    href={twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-950 text-sky-300 border border-sky-800/80 hover:bg-slate-800 transition-colors shadow-sm"
                  >
                    <span>𝕏</span> Twitter / X ↗
                  </a>
                )}
                {github && (
                  <a
                    href={github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-950 text-slate-200 border border-slate-700 hover:bg-slate-800 transition-colors shadow-sm"
                  >
                    <span>🐙</span> GitHub Repo / Org ↗
                  </a>
                )}
                {email && (
                  <a
                    href={`mailto:${email}`}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-800/80 hover:bg-emerald-900 transition-colors shadow-sm"
                  >
                    <span>✉️</span> Email ({email}) ↗
                  </a>
                )}
                {contactPage && (
                  <a
                    href={contactPage}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-950 text-purple-300 border border-purple-800/80 hover:bg-purple-900 transition-colors shadow-sm"
                  >
                    <span>🔗</span> Official Contact Page ↗
                  </a>
                )}
              </div>
            </div>
          );
        })()}

        {/* Deep Problem Breakdown & Step-by-Step Resolution Strategy Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 border-t border-slate-800">
          {/* Problem Breakdown Card */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-rose-900/40 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-rose-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🚨</span> Problem Root Cause &amp; Operational Impact
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/60 font-mono">
                Verified Signal
              </span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              {opportunity.problem_explanation || ai_summary.problem_explanation || opportunity.pain_point_description || opportunity.detected_signal}
            </p>
          </div>

          {/* How to Solve / Action Plan Card */}
          <div className="p-4 rounded-xl bg-slate-950/80 border border-emerald-900/40 space-y-2 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                <span>🛠️</span> How to Solve (Developer Action Plan)
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/60 font-mono">
                Actionable Blueprint
              </span>
            </div>
            <div className="text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-line bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
              {opportunity.how_to_solve_strategy || ai_summary.how_to_solve_strategy || "Click 'Analyze with Gemini AI' above to generate a customized technical roadmap."}
            </div>
          </div>
        </div>

        {/* Success Alert Banner */}
        {analysisMessage && (
          <div className="p-3 bg-emerald-950/80 border border-emerald-700 rounded-xl text-emerald-200 text-xs font-semibold flex items-center gap-2">
            <span>✓</span> {analysisMessage}
          </div>
        )}

        {/* Resume Synergy & Founder Pitch Alignment */}
        <div className="pt-3 border-t border-slate-800 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
              <span>🎯</span>
              <span>Resume Alignment &amp; Solution Strategy</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
              Founder Bottleneck Fit
            </span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            Your verified background and past project competencies position you to resolve this startup&apos;s operational friction. Highlight these direct metrics when initiating founder outreach:
          </p>
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 space-y-1">
            <span className="text-amber-400 text-[11px] font-semibold">Recommended Pitch Bullet:</span>
            <p className="italic">
              &quot;Architected and shipped scalable solutions addressing {opportunity.category} bottlenecks, reducing system friction and accelerating team execution.&quot;
            </p>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="flex flex-wrap border-b border-slate-800 gap-x-6 gap-y-2 text-sm font-semibold">
        <button
          onClick={() => setActiveTab("observation")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "observation"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          1. Observation Ledger ({evidence_ledger.length})
        </button>
        <button
          onClick={() => setActiveTab("ai")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "ai"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          2. AI Summary & Strategy
        </button>
        <button
          onClick={() => setActiveTab("tech")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "tech"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          3. Technographics ({technology_findings.length})
        </button>
        <button
          onClick={() => setActiveTab("corroboration")}
          className={`pb-3 border-b-2 transition-colors ${
            activeTab === "corroboration"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          4. Corroboration & Audit ({corroboration_ledger.length})
        </button>
      </div>

      {/* Tab 1: Observation Ledger */}
      {activeTab === "observation" && (
        <div className="space-y-4">
          <div className="p-4 bg-blue-950/40 border border-blue-800/60 rounded-xl text-blue-300 text-xs">
            <strong>Provenance Policy:</strong> These observations represent unaltered data obtained directly from public feeds or website audits. AI interpretation is strictly excluded from this tab.
          </div>

          {evidence_ledger.map((ev) => (
            <div key={ev.id} className="p-5 bg-slate-900/80 rounded-xl border border-slate-800 shadow-sm space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold text-slate-200">{ev.publisher}</span>
                <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono">{ev.source_type}</span>
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{ev.source_title}</h4>
                <blockquote className="mt-2 p-3 bg-slate-950 rounded-lg border-l-4 border-indigo-500 text-xs text-slate-300 italic leading-relaxed">
                  &ldquo;{ev.observation_excerpt}&rdquo;
                </blockquote>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-2 border-t border-slate-800 text-xs text-slate-400">
                <div>Published: {ev.published_at}</div>
                <div>Retrieved: {ev.retrieved_at ? new Date(ev.retrieved_at).toLocaleDateString() : "N/A"}</div>
                <div>Method: {ev.collection_method}</div>
                <div>
                  {ev.source_url ? (
                    <a href={ev.source_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">
                      View Original URL ↗
                    </a>
                  ) : (
                    "URL Unavailable"
                  )}
                </div>
              </div>
              {ev.source_limitations && (
                <div className="text-xs text-slate-500 mt-1">
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
          <div className="p-4 bg-purple-950/40 border border-purple-800/60 rounded-xl text-purple-300 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <span className="font-bold">Machine-Generated Synthesis:</span> Model: {ai_summary.model}
            </div>
            <div className="text-purple-400 font-mono">
              Generated: {ai_summary.generated_at ? new Date(ai_summary.generated_at).toLocaleString() : "Cached"}
            </div>
          </div>

          <div className="p-6 bg-slate-900/80 rounded-xl border border-slate-800 shadow-sm space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Root Cause &amp; Technical Bottleneck
              </h3>
              <p className="text-sm text-slate-300 mt-1 leading-relaxed">
                {ai_summary.insight || ai_summary.problem_explanation || "No deep insight generated yet."}
              </p>
            </div>

            <div className="pt-4 border-t border-slate-800">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Recommended Solution Direction
              </h3>
              <p className="text-sm text-slate-300 mt-1 leading-relaxed">
                {ai_summary.opportunity || "Solution direction pending candidate formulation."}
              </p>
            </div>

            {ai_summary.how_to_solve_strategy && (
              <div className="pt-4 border-t border-slate-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <span>🛠️</span> Strategic Execution Roadmap
                </h3>
                <div className="mt-2 p-4 bg-slate-950 rounded-lg text-xs text-emerald-200 font-mono whitespace-pre-line border border-slate-800 leading-relaxed">
                  {ai_summary.how_to_solve_strategy}
                </div>
              </div>
            )}

            {ai_summary.pitch_idea && (
              <div className="pt-4 border-t border-slate-800 space-y-2">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                    <span>✉️</span> Founder Outreach Pitch (Gemini Crafted)
                  </h3>
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(ai_summary.pitch_idea || "");
                      setCopiedPitch(true);
                      setTimeout(() => setCopiedPitch(false), 2500);
                    }}
                    className="px-2.5 py-1 rounded bg-indigo-600/40 hover:bg-indigo-600 text-indigo-200 text-xs font-semibold border border-indigo-500/50 transition-colors"
                  >
                    {copiedPitch ? "✓ Copied Pitch!" : "📋 Copy Outreach Pitch"}
                  </button>
                </div>
                <div className="p-4 bg-slate-950 rounded-lg text-xs text-slate-200 font-mono whitespace-pre-line border border-slate-800 leading-relaxed">
                  {ai_summary.pitch_idea}
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-slate-800 p-3 bg-slate-950 rounded-lg text-xs text-slate-400 italic border border-slate-800">
              <strong>Governance Notice:</strong> {ai_summary.disclaimer}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Technographics */}
      {activeTab === "tech" && (
        <div className="space-y-4">
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-400">
            <strong>Evidence-Based Findings:</strong> Only technologies with public code tags, website audit proofs, or explicit mention in founder issues are presented. General industry speculation is strictly blocked.
          </div>

          {technology_findings.length === 0 ? (
            <div className="p-8 bg-slate-900/60 rounded-xl border border-slate-800 text-center text-slate-400 text-sm">
              No specific technology stack signals detected in current public observations.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {technology_findings.map((tf) => (
                <div key={tf.id} className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 shadow-sm space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{tf.technology_name}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-semibold border border-indigo-800">
                      {tf.finding_type}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    Category: <span className="font-medium text-slate-200">{tf.category}</span> | Confidence:{" "}
                    <span className="font-semibold text-emerald-400">{Math.round(tf.confidence_score * 100)}%</span>
                  </div>
                  <div className="text-xs text-slate-500 italic pt-1 border-t border-slate-800">
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
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl text-xs text-slate-400">
            <strong>Corroboration Protocol:</strong> Distinguishes independent verification from repeated syndications. Multiple independent sources increase trust rating.
          </div>

          {corroboration_ledger.map((cr) => (
            <div key={cr.id} className="p-4 bg-slate-900/80 rounded-xl border border-slate-800 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h4 className="text-sm font-bold text-white">{cr.source_name}</h4>
                <p className="text-xs text-slate-500 font-mono mt-0.5">ID: {cr.source_identifier}</p>
                {cr.notes && <p className="text-xs text-slate-400 mt-1">{cr.notes}</p>}
              </div>
              <div>
                <span
                  className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                    cr.is_independent ? "bg-emerald-950/60 text-emerald-300 border-emerald-800/60" : "bg-slate-800 text-slate-300 border-slate-700"
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

