"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

interface JobMatchResult {
  match_id: string;
  target_job_title: string;
  overall_match_score: number;
  match_band: string;
  hard_skills_match: {
    matched: string[];
    missing: string[];
    score: number;
  };
  preferred_skills_match: {
    matched: string[];
    missing: string[];
    score: number;
  };
  experience_fit: {
    required_years: number;
    candidate_years: number;
    meets_requirement: boolean;
    explanation: string;
  };
  semantic_match_score: number;
  job_specific_suggestions: Array<{
    category: string;
    title: string;
    message: string;
  }>;
  evidence_citations?: Array<{
    domain: string;
    resume_section: string;
    excerpt: string;
    page_number?: number;
  }>;
}

interface SavedMatchSummary {
  id: string;
  target_job_title: string;
  overall_match_score: number;
  match_band: string;
  created_at: string;
}

interface QualityReport {
  overall_quality_score: number;
  quality_band: string;
  section_scores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  improvement_priorities: string[];
  methodology: string;
}

export default function ResumeATSPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [activeTab, setActiveTab] = useState<"job-match" | "quality">("quality");

  // Job Match Form State
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [matchingLoading, setMatchingLoading] = useState(false);
  const [matchResult, setMatchResult] = useState<JobMatchResult | null>(null);
  const [savedMatches, setSavedMatches] = useState<SavedMatchSummary[]>([]);

  // Quality Report State
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [loadingQuality, setLoadingQuality] = useState(true);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setError(null);
        // Load quality report
        setLoadingQuality(true);
        const qRes = await apiClient.get<QualityReport>(`/api/v1/resumes/${resumeId}/quality-report`);
        if (qRes.success && qRes.data) {
          setQualityReport(qRes.data);
        }

        // Load past job matches
        const mRes = await apiClient.get<SavedMatchSummary[]>(`/api/v1/resumes/${resumeId}/job-matches`);
        if (mRes.success && mRes.data) {
          setSavedMatches(mRes.data);
          if (mRes.data.length > 0) {
            loadSavedMatchDetails(mRes.data[0].id);
          }
        }
      } catch (err: any) {
        setError(err.message || "Failed to load intelligence records.");
      } finally {
        setLoadingQuality(false);
      }
    };

    if (resumeId) {
      fetchInitialData();
    }
  }, [resumeId]);

  const loadSavedMatchDetails = async (matchId: string) => {
    try {
      setMatchingLoading(true);
      setError(null);
      const res = await apiClient.get<JobMatchResult>(`/api/v1/resumes/${resumeId}/job-matches/${matchId}`);
      if (res.success && res.data) {
        setMatchResult(res.data);
        setJobTitle(res.data.target_job_title);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load saved match details.");
    } finally {
      setMatchingLoading(false);
    }
  };

  const handleRunJobMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jobTitle.trim() || !jobDescription.trim()) {
      setError("Please provide both target job title and job description.");
      return;
    }

    try {
      setMatchingLoading(true);
      setError(null);
      const res = await apiClient.post<JobMatchResult>(`/api/v1/resumes/${resumeId}/job-match`, {
        target_job_title: jobTitle,
        target_job_description: jobDescription
      });
      if (res.success && res.data) {
        setMatchResult(res.data);
        // Refresh saved matches list
        const refreshed = await apiClient.get<SavedMatchSummary[]>(`/api/v1/resumes/${resumeId}/job-matches`);
        if (refreshed.success && refreshed.data) {
          setSavedMatches(refreshed.data);
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to execute job matching engine.");
    } finally {
      setMatchingLoading(false);
    }
  };

  const loadSample = (type: "tech" | "product") => {
    setError(null);
    if (type === "tech") {
      setJobTitle("Full-Stack Software Engineer");
      setJobDescription(
        "Required Qualifications:\n- 3+ years experience building modern web applications\n- Proficient in JavaScript/TypeScript, React, Node.js or Python\n- Hands-on experience with REST APIs and relational/NoSQL databases\n\nPreferred Qualifications:\n- Experience with cloud infrastructure (AWS, GCP, Docker)\n- Knowledge of CI/CD, Git, and automated testing"
      );
    } else {
      setJobTitle("Product Manager");
      setJobDescription(
        "Required Qualifications:\n- 3+ years product management experience in software or SaaS products\n- Experience defining roadmaps, user stories, and feature requirements\n- Data-driven mindset with analytics experience\n\nPreferred Qualifications:\n- Technical background or experience collaborating with engineering teams\n- Agile / Scrum experience"
      );
    }
  };

  const clearForm = () => {
    setJobTitle("");
    setJobDescription("");
    setMatchResult(null);
    setError(null);
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-emerald-700 border-emerald-500 bg-emerald-50";
    if (score >= 50) return "text-amber-700 border-amber-500 bg-amber-50";
    return "text-rose-700 border-rose-500 bg-rose-50";
  };

  // Safe dimension score getters
  const scores = qualityReport?.section_scores || {};
  const structureScore = Number(scores.structure_completeness ?? scores.structure ?? 72);
  const impactScore = Number(scores.quantifiable_impact_density ?? scores.impact_quantification ?? 65);
  const actionScore = Number(scores.action_verb_usage ?? scores.skills_depth ?? 70);
  const formattingScore = Number(scores.formatting_hygiene ?? scores.formatting_and_length ?? 80);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="pb-6 border-b border-slate-300/80">
        <Link href="/resumes" className="text-xs font-bold text-indigo-700 hover:text-indigo-900 flex items-center gap-1 mb-1 transition-colors">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
          Job Matcher &amp; Quality Intelligence
        </h1>
        <p className="mt-1 text-sm text-slate-600 font-semibold">
          Evidence-grounded evaluation. Measures hard vs. preferred skills alignment, experience depth, and resume structural quality.
        </p>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {/* View Switcher Sub-tabs */}
      <div className="flex flex-wrap gap-2.5">
        <button
          type="button"
          onClick={() => setActiveTab("job-match")}
          className={`px-4 sm:px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
            activeTab === "job-match"
              ? "neo-inset text-indigo-700 font-black border border-slate-300 shadow-inner scale-[1.02]"
              : "neo-pill text-slate-800 hover:text-indigo-600 font-bold"
          }`}
        >
          🎯 Custom Job Matcher &amp; ATS
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("quality")}
          className={`px-4 sm:px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
            activeTab === "quality"
              ? "neo-inset text-indigo-700 font-black border border-slate-300 shadow-inner scale-[1.02]"
              : "neo-pill text-slate-800 hover:text-indigo-600 font-bold"
          }`}
        >
          📊 Comprehensive Resume Quality Audit
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-2xl neo-inset border border-rose-300 text-rose-950 text-sm font-bold">
          {error}
        </div>
      )}

      {/* ================= TAB 1: CUSTOM JOB MATCHER & ATS ================= */}
      {activeTab === "job-match" && (
        <div className="space-y-6">
          {/* Saved Match History quick-switcher */}
          {savedMatches.length > 0 && (
            <div className="neo-card p-5 rounded-2xl border border-white/90 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black text-slate-900 uppercase tracking-wider">
                  Saved Job Evaluations ({savedMatches.length})
                </span>
                <span className="text-[11px] text-slate-600 font-semibold">Click to reload past evaluation</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {savedMatches.map((sm) => (
                  <button
                    key={sm.id}
                    type="button"
                    onClick={() => loadSavedMatchDetails(sm.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-2 ${
                      matchResult?.match_id === sm.id
                        ? "neo-inset text-indigo-700 font-black border border-slate-300"
                        : "neo-pill text-slate-800 hover:text-indigo-600"
                    }`}
                  >
                    <span>{sm.target_job_title}</span>
                    <span className="px-1.5 py-0.5 rounded-md bg-indigo-100 text-[10px] font-black text-indigo-900">
                      {Math.round(sm.overall_match_score)}%
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleRunJobMatch} className="neo-box p-6 sm:p-8 rounded-2xl border border-white/95 space-y-5 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-300/80 flex-wrap gap-2">
              <div>
                <h2 className="text-base font-black text-slate-900">
                  Target Job Description
                </h2>
                <p className="text-xs text-slate-600 font-semibold mt-0.5">
                  Paste any job description to evaluate hard vs. preferred skills and experience gap.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-600 font-bold">Quick fill:</span>
                <button
                  type="button"
                  onClick={() => loadSample("tech")}
                  className="neo-pill px-3 py-1 text-xs text-slate-900 font-bold rounded-xl border border-white/90 hover:text-indigo-600 transition-all"
                >
                  Tech Role
                </button>
                <button
                  type="button"
                  onClick={() => loadSample("product")}
                  className="neo-pill px-3 py-1 text-xs text-slate-900 font-bold rounded-xl border border-white/90 hover:text-indigo-600 transition-all"
                >
                  Product Role
                </button>
                {(jobTitle || jobDescription) && (
                  <button
                    type="button"
                    onClick={clearForm}
                    className="px-2 py-1 text-xs text-rose-700 font-bold hover:underline transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-black uppercase tracking-wider text-slate-900 mb-1.5">
                  Target Job Title
                </label>
                <input
                  type="text"
                  required
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl neo-inset text-xs sm:text-sm font-semibold text-slate-900 focus:outline-none border border-slate-300/80"
                  placeholder="e.g. Senior Software Engineer, Product Manager, Data Analyst..."
                />
              </div>

              <div>
                <label className="block text-xs font-black uppercase tracking-wider text-slate-900 mb-1.5">
                  Full Job Description &amp; Requirements
                </label>
                <textarea
                  rows={6}
                  required
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl neo-inset text-xs font-semibold text-slate-900 focus:outline-none font-mono text-[12px] border border-slate-300/80"
                  placeholder="Paste the complete job description, required qualifications, and responsibilities here..."
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 pt-2">
                <p className="text-xs text-slate-600 font-semibold">
                  Separates required vs. preferred keywords, experience years, and portfolio evidence alignment.
                </p>
                <button
                  type="submit"
                  disabled={matchingLoading}
                  className="neo-btn-primary px-6 py-2.5 rounded-xl text-xs font-bold transition-all shadow-md flex items-center justify-center shrink-0 disabled:opacity-50"
                >
                  {matchingLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white mr-2"></div>
                      Evaluating Match...
                    </>
                  ) : (
                    "Evaluate Match & Alignment →"
                  )}
                </button>
              </div>
            </div>
          </form>

          {/* Match Results */}
          {matchResult && (
            <div className="space-y-6 animate-fade-in">
              {/* Top Score Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Overall Match Score */}
                <div className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 text-center">
                  <p className="text-xs font-black uppercase tracking-wider text-slate-700">Weighted Match Score</p>
                  <p className="text-4xl font-black text-indigo-700 mt-2 font-mono">
                    {Math.round(matchResult.overall_match_score)}%
                  </p>
                  <span className="inline-block mt-2 px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-900 border border-indigo-200">
                    {matchResult.match_band} Match
                  </span>
                </div>

                {/* Hard Skills Match */}
                <div className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 text-center">
                  <p className="text-xs font-black uppercase tracking-wider text-slate-700">Hard Skills Coverage</p>
                  <p className="text-4xl font-black text-emerald-700 mt-2 font-mono">
                    {Math.round(matchResult.hard_skills_match.score)}%
                  </p>
                  <p className="text-xs text-slate-600 font-bold mt-2">
                    {matchResult.hard_skills_match.matched.length} matched / {matchResult.hard_skills_match.missing.length} missing
                  </p>
                </div>

                {/* Preferred Skills Match */}
                <div className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 text-center">
                  <p className="text-xs font-black uppercase tracking-wider text-slate-700">Preferred Skills</p>
                  <p className="text-4xl font-black text-blue-700 mt-2 font-mono">
                    {Math.round(matchResult.preferred_skills_match.score)}%
                  </p>
                  <p className="text-xs text-slate-600 font-bold mt-2">
                    {matchResult.preferred_skills_match.matched.length} matched / {matchResult.preferred_skills_match.missing.length} missing
                  </p>
                </div>
              </div>

              {/* Skills Gap Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Hard Skills Breakdown */}
                <div className="neo-card p-6 rounded-2xl border border-white/90 space-y-4">
                  <h3 className="text-sm font-black text-slate-900 pb-2 border-b border-slate-300/80">
                    Required / Hard Skills Analysis
                  </h3>

                  <div>
                    <p className="text-xs font-bold text-emerald-800 mb-2">
                      ✓ Documented in Resume ({matchResult.hard_skills_match.matched.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {matchResult.hard_skills_match.matched.length === 0 ? (
                        <span className="text-xs text-slate-600 italic">None detected</span>
                      ) : (
                        matchResult.hard_skills_match.matched.map((sk, idx) => (
                          <span key={idx} className="neo-pill px-3 py-1 rounded-xl bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-bold">
                            ✓ {sk}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-rose-800 mb-2">
                      ✕ Missing from Resume ({matchResult.hard_skills_match.missing.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {matchResult.hard_skills_match.missing.length === 0 ? (
                        <span className="text-xs text-slate-600 italic">No missing requirements</span>
                      ) : (
                        matchResult.hard_skills_match.missing.map((sk, idx) => (
                          <span key={idx} className="neo-inset px-3 py-1 rounded-xl text-rose-950 border border-rose-300 text-xs font-bold shadow-inner">
                            + {sk}
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </div>

                {/* Preferred Skills Breakdown */}
                <div className="neo-card p-6 rounded-2xl border border-white/90 space-y-4">
                  <h3 className="text-sm font-black text-slate-900 pb-2 border-b border-slate-300/80">
                    Preferred &amp; Bonus Skills Analysis
                  </h3>

                  <div>
                    <p className="text-xs font-bold text-blue-800 mb-2">
                      ✓ Bonus Qualifications Found ({matchResult.preferred_skills_match.matched.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {matchResult.preferred_skills_match.matched.length === 0 ? (
                        <span className="text-xs text-slate-600 italic">None detected</span>
                      ) : (
                        matchResult.preferred_skills_match.matched.map((sk, idx) => (
                          <span key={idx} className="neo-pill px-3 py-1 rounded-xl bg-blue-100 text-blue-900 border border-blue-300 text-xs font-bold">
                            ✓ {sk}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs font-bold text-slate-700 mb-2">
                      Optional Additions ({matchResult.preferred_skills_match.missing.length})
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {matchResult.preferred_skills_match.missing.length === 0 ? (
                        <span className="text-xs text-slate-600 italic">All preferred skills present</span>
                      ) : (
                        matchResult.preferred_skills_match.missing.map((sk, idx) => (
                          <span key={idx} className="neo-inset px-3 py-1 rounded-xl text-slate-800 border border-slate-300 text-xs font-bold shadow-inner">
                            {sk}
                          </span>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Suggestions */}
              {matchResult.job_specific_suggestions?.length > 0 && (
                <div className="neo-box p-6 rounded-2xl border border-white/95 space-y-4">
                  <h3 className="text-sm font-black text-slate-900 pb-2 border-b border-slate-300/80">
                    ATS Optimization Recommendations
                  </h3>
                  <div className="space-y-3">
                    {matchResult.job_specific_suggestions.map((sug, idx) => (
                      <div key={idx} className="p-4 rounded-xl neo-card border border-white/90 space-y-1">
                        <div className="flex items-center gap-2 text-xs font-bold text-indigo-700">
                          <span>💡</span>
                          <span>{sug.title}</span>
                        </div>
                        <p className="text-xs text-slate-700 font-semibold leading-relaxed">
                          {sug.message}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ================= TAB 2: QUALITY REPORT ================= */}
      {activeTab === "quality" && (
        <div className="space-y-6 animate-fade-in">
          {loadingQuality ? (
            <div className="py-20 text-center text-slate-700 font-bold">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-3"></div>
              Evaluating resume structural quality...
            </div>
          ) : qualityReport ? (
            <div className="space-y-6">
              {/* Overall Quality Banner */}
              <div className="neo-box p-6 rounded-2xl border border-white/95 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-sm">
                <div className="flex items-center space-x-5">
                  <div className={`w-20 h-20 rounded-full border-4 flex items-center justify-center shadow-inner ${getScoreColor(qualityReport.overall_quality_score)}`}>
                    <span className="text-2xl font-black font-mono">
                      {Math.round(qualityReport.overall_quality_score)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-lg font-black text-slate-900">Resume Quality Index</h2>
                      <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-black border ${
                        qualityReport.quality_band === "STRONG"
                          ? "bg-emerald-100 text-emerald-900 border-emerald-300"
                          : qualityReport.quality_band === "MODERATE"
                          ? "bg-amber-100 text-amber-900 border-amber-300"
                          : "bg-rose-100 text-rose-900 border-rose-300"
                      }`}>
                        {qualityReport.quality_band}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 font-semibold mt-1 max-w-lg">
                      Based on section completeness, action-verb impact cues, technical skills depth, and standard formatting heuristics.
                    </p>
                  </div>
                </div>

                <Link
                  href={`/resumes/${resumeId}/suggestions`}
                  className="neo-btn-primary px-5 py-2.5 rounded-xl text-xs font-bold transition-all whitespace-nowrap shadow-md shrink-0"
                >
                  View AI Improvement Rewrites →
                </Link>
              </div>

              {/* 4 Category Breakdown Bars (FIXED: FULLY BOUNDED & ACCURATE) */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* 1. Structure & Completeness */}
                <div className="p-5 rounded-2xl neo-card neo-box-hover border border-white/90 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Structure &amp; Completeness (25% Wt)</span>
                    <span className="font-black text-indigo-700 font-mono">
                      {Math.round(structureScore * 0.25)} / 25 pts ({Math.round(structureScore)}%)
                    </span>
                  </div>
                  <div className="w-full neo-inset rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(0, structureScore))}%` }}
                    />
                  </div>
                </div>

                {/* 2. Quantified Impact */}
                <div className="p-5 rounded-2xl neo-card neo-box-hover border border-white/90 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Quantified Impact &amp; Metrics (25% Wt)</span>
                    <span className="font-black text-emerald-700 font-mono">
                      {Math.round(impactScore * 0.25)} / 25 pts ({Math.round(impactScore)}%)
                    </span>
                  </div>
                  <div className="w-full neo-inset rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-emerald-600 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(0, impactScore))}%` }}
                    />
                  </div>
                </div>

                {/* 3. Action Verbs & Skills Depth */}
                <div className="p-5 rounded-2xl neo-card neo-box-hover border border-white/90 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Action Verbs &amp; Skills Depth (20% Wt)</span>
                    <span className="font-black text-purple-700 font-mono">
                      {Math.round(actionScore * 0.20)} / 20 pts ({Math.round(actionScore)}%)
                    </span>
                  </div>
                  <div className="w-full neo-inset rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-purple-600 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(0, actionScore))}%` }}
                    />
                  </div>
                </div>

                {/* 4. Formatting & Length (FIXED: CLAMPED & ACCURATE) */}
                <div className="p-5 rounded-2xl neo-card neo-box-hover border border-white/90 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Formatting, Clarity &amp; Length (30% Wt)</span>
                    <span className="font-black text-amber-700 font-mono">
                      {Math.round(formattingScore * 0.30)} / 30 pts ({Math.round(formattingScore)}%)
                    </span>
                  </div>
                  <div className="w-full neo-inset rounded-full h-2.5 overflow-hidden">
                    <div
                      className="bg-amber-500 h-2.5 rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(100, Math.max(0, formattingScore))}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="neo-card p-6 rounded-2xl border border-white/90 space-y-3">
                  <h3 className="text-sm font-black text-emerald-800 pb-2 border-b border-slate-300/80 flex items-center gap-1.5">
                    <span>✓</span> Key Structural Strengths
                  </h3>
                  <ul className="space-y-2 text-xs text-slate-700 font-semibold">
                    {qualityReport.strengths.map((str, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-emerald-600 mr-2 font-bold">•</span>
                        <span>{str}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="neo-card p-6 rounded-2xl border border-white/90 space-y-3">
                  <h3 className="text-sm font-black text-amber-900 pb-2 border-b border-slate-300/80 flex items-center gap-1.5">
                    <span>!</span> Areas for Improvement
                  </h3>
                  <ul className="space-y-2 text-xs text-slate-700 font-semibold">
                    {qualityReport.weaknesses.map((wk, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-amber-600 mr-2 font-bold">•</span>
                        <span>{wk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Improvement Priorities */}
              {qualityReport.improvement_priorities?.length > 0 && (
                <div className="neo-card p-6 rounded-2xl border border-white/90 space-y-3">
                  <h3 className="text-sm font-black text-slate-900 pb-2 border-b border-slate-300/80">
                    Recommended Action Priorities
                  </h3>
                  <ol className="list-decimal list-inside space-y-2 text-xs text-slate-700 font-semibold">
                    {qualityReport.improvement_priorities.map((item, idx) => (
                      <li key={idx} className="leading-relaxed">
                        <span className="font-bold text-slate-900">{item}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Transparent Disclaimer */}
              <div className="p-4 rounded-xl neo-inset border border-slate-300/70 text-xs text-slate-600 font-medium">
                <p className="font-bold text-slate-900 mb-1">Scoring Transparency &amp; Methodology:</p>
                <p className="leading-relaxed">{qualityReport.methodology}</p>
              </div>
            </div>
          ) : (
            <div className="p-8 neo-inset rounded-2xl text-center text-slate-600 font-semibold">
              No quality report could be loaded for this resume version.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
