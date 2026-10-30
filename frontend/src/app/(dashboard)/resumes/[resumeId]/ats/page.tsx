"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";

interface ATSAnalysis {
  analysis_id: string;
  target_job_title: string;
  coverage_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  bullet_impact_score: number;
  bullet_impact_analysis: {
    total_bullets: number;
    strong_bullets_count: number;
    weak_bullets_count: number;
    scored_bullets: Array<{
      bullet: string;
      score: number;
      is_strong: boolean;
      cues: string[];
    }>;
  };
  actionable_suggestions: Array<{
    category: string;
    title: string;
    message: string;
    is_advisory: boolean;
  }>;
  formatting_observations: string[];
  methodology_and_limitations: string;
  created_at: string;
}

export default function ResumeATSAnalysisPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [jobTitle, setJobTitle] = useState("Senior Backend Engineer");
  const [jobDescription, setJobDescription] = useState(
    "We are seeking an experienced Senior Backend Engineer with proficiency in Python, FastAPI, PostgreSQL, Redis, Docker, and Kubernetes. The ideal candidate will design scalable microservices and optimize database query performance."
  );
  const [analysis, setAnalysis] = useState<ATSAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle || !jobDescription) {
      setError("Please provide both target job title and job description.");
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.post<ATSAnalysis>(`/api/v1/resumes/${resumeId}/ats-analysis`, {
        target_job_title: jobTitle,
        target_job_description: jobDescription
      });
      if (res.success && res.data) {
        setAnalysis(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to execute ATS keyword analysis.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-8 pb-6 border-b border-slate-800">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl font-bold text-slate-100">ATS Keyword & Bullet Impact Analysis</h1>
        <p className="mt-1 text-sm text-slate-400">
          Compare your resume against specific job requirements. Evaluates keyword coverage and quantified impact cues without fabricating facts.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Target Job Input Card */}
      <form onSubmit={handleRunAnalysis} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 mb-8 shadow-sm">
        <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
          Target Job Requirements
        </h2>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Job Title</label>
            <input
              type="text"
              required
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="e.g. Staff Software Engineer"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Target Job Description & Requirements</label>
            <textarea
              rows={4}
              required
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              placeholder="Paste the complete job description here..."
            />
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white mr-2"></div>
                  Analyzing Keyword Coverage...
                </>
              ) : (
                "Run ATS Alignment Analysis"
              )}
            </button>
          </div>
        </div>
      </form>

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-8">
          {/* Top Score Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Keyword Coverage */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Keyword Alignment</p>
              <div className="mt-4 flex items-center justify-center">
                <div className="w-24 h-24 rounded-full border-4 border-indigo-500/40 flex items-center justify-center">
                  <span className="text-2xl font-bold text-indigo-400">
                    {Math.round(analysis.coverage_score * 100)}%
                  </span>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-400">
                {analysis.matched_keywords.length} of {analysis.matched_keywords.length + analysis.missing_keywords.length} high-signal JD keywords found.
              </p>
            </div>

            {/* Bullet Impact Score */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Quantified Bullet Impact</p>
              <div className="mt-4 flex items-center justify-center">
                <div className="w-24 h-24 rounded-full border-4 border-emerald-500/40 flex items-center justify-center">
                  <span className="text-2xl font-bold text-emerald-400">
                    {Math.round(analysis.bullet_impact_score)}%
                  </span>
                </div>
              </div>
              <p className="mt-3 text-xs text-slate-400">
                {analysis.bullet_impact_analysis.strong_bullets_count} of {analysis.bullet_impact_analysis.total_bullets} bullets contain metrics or strong action verbs.
              </p>
            </div>
          </div>

          {/* Keywords Breakdown */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
              Keyword Coverage Breakdown
            </h2>

            <div className="space-y-4">
              <div>
                <p className="text-xs font-semibold text-emerald-400 mb-2">
                  ✓ Matched Keywords ({analysis.matched_keywords.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysis.matched_keywords.map((kw, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-800/80 text-xs">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold text-amber-400 mb-2">
                  ! Missing High-Signal Keywords ({analysis.missing_keywords.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {analysis.missing_keywords.map((kw, idx) => (
                    <span key={idx} className="px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700 text-xs">
                      {kw}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Actionable Grounded Suggestions */}
          {analysis.actionable_suggestions.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
                Actionable Optimization Guidance (Advisory Only)
              </h2>

              <div className="space-y-4">
                {analysis.actionable_suggestions.map((sug, idx) => (
                  <div key={idx} className="p-4 rounded-lg bg-indigo-950/20 border border-indigo-900/50">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">{sug.category}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-900 text-indigo-200">Advisory</span>
                    </div>
                    <p className="text-sm font-semibold text-slate-200 mt-1">{sug.title}</p>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">{sug.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Formatting Observations */}
          {analysis.formatting_observations.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                Formatting Observations
              </h2>
              <ul className="space-y-1.5 list-disc list-inside text-xs text-slate-300">
                {analysis.formatting_observations.map((obs, idx) => (
                  <li key={idx}>{obs}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Methodology & Limitations Card */}
          <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs text-slate-400">
            <p className="font-semibold text-slate-300 mb-1">Scoring Methodology & Platform Limitations:</p>
            <p className="leading-relaxed">{analysis.methodology_and_limitations}</p>
          </div>
        </div>
      )}
    </div>
  );
}

