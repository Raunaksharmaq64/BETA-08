"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

interface QualityReport {
  resume_id: string;
  version_id: string;
  overall_quality_score: number;
  quality_band: string;
  section_scores: {
    structure_and_completeness: number;
    quantified_impact_and_bullets: number;
    skills_depth_and_relevance: number;
    formatting_and_length: number;
  };
  strengths: string[];
  weaknesses: string[];
  critical_issues: string[];
  improvement_priorities: string[];
  methodology: string;
}

interface JobMatchResult {
  match_id?: string;
  resume_id: string;
  version_id: string;
  target_job_title: string;
  overall_match_score: number;
  keyword_coverage_score: number;
  required_skills_match: {
    target_count: number;
    matched_count: number;
    match_percentage: number;
    matched: string[];
    missing: string[];
  };
  preferred_skills_match: {
    target_count: number;
    matched_count: number;
    match_percentage: number;
    matched: string[];
    missing: string[];
  };
  experience_level_match: {
    required_years: number | null;
    detected_years: number;
    estimated_candidate_years?: number;
    assessment: string;
    score: number;
  };
  project_theme_alignments: Array<{
    theme?: string;
    jd_theme?: string;
    bullet_excerpt?: string;
    matched_bullets?: string[];
    score?: number;
    match_score?: number;
  }>;
  unverified_matches: string[];
  job_specific_suggestions?: Array<{
    category?: string;
    type?: string;
    title: string;
    message: string;
    keywords?: string[];
  }>;
  created_at?: string;
}

interface SavedMatchSummary {
  id: string;
  target_job_title: string;
  overall_match_score: number;
  keyword_coverage_score: number;
  created_at: string;
}

export default function ResumeATSAnalysisPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  // Active view tab: "job-match" | "quality"
  const [activeTab, setActiveTab] = useState<"job-match" | "quality">("job-match");

  // Quality Report state
  const [qualityReport, setQualityReport] = useState<QualityReport | null>(null);
  const [loadingQuality, setLoadingQuality] = useState(false);

  // Saved job matches list
  const [savedMatches, setSavedMatches] = useState<SavedMatchSummary[]>([]);
  const [loadingSavedMatches, setLoadingSavedMatches] = useState(false);

  // Job Matcher state
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [matchResult, setMatchResult] = useState<JobMatchResult | null>(null);
  const [matchingLoading, setMatchingLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch quality report and saved matches on initial mount
  useEffect(() => {
    const fetchQuality = async () => {
      try {
        setLoadingQuality(true);
        const res = await apiClient.get<QualityReport>(`/api/v1/resumes/${resumeId}/quality`);
        if (res.success && res.data) {
          setQualityReport(res.data);
        }
      } catch (err: any) {
        // Silently capture quality load issue
      } finally {
        setLoadingQuality(false);
      }
    };

    const fetchSavedMatches = async () => {
      try {
        setLoadingSavedMatches(true);
        const res = await apiClient.get<SavedMatchSummary[]>(`/api/v1/resumes/${resumeId}/job-matches`);
        if (res.success && res.data) {
          setSavedMatches(res.data);
        }
      } catch (err: any) {
        // Silently capture saved matches load issue
      } finally {
        setLoadingSavedMatches(false);
      }
    };

    if (resumeId) {
      fetchQuality();
      fetchSavedMatches();
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
    if (score >= 75) return "text-emerald-400 border-emerald-500/40";
    if (score >= 50) return "text-amber-400 border-amber-500/40";
    return "text-rose-400 border-rose-500/40";
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="mb-6 pb-6 border-b border-slate-800">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl font-bold text-slate-100">Job Matcher & Quality Intelligence</h1>
        <p className="mt-1 text-sm text-slate-400">
          Evidence-grounded evaluation. Measures hard vs. preferred skills alignment, experience depth, and resume structural quality.
        </p>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {/* View Switcher Sub-tabs: Only 2 focused options */}
      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setActiveTab("job-match")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === "job-match"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          🎯 Custom Job Matcher & ATS
        </button>
        <button
          onClick={() => setActiveTab("quality")}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-colors ${
            activeTab === "quality"
              ? "bg-indigo-600 text-white shadow-sm"
              : "bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          📊 Comprehensive Resume Quality Audit
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* ================= TAB 1: CUSTOM JOB MATCHER & ATS ================= */}
      {activeTab === "job-match" && (
        <div className="space-y-8">
          {/* Saved Match History quick-switcher */}
          {savedMatches.length > 0 && (
            <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                  Saved Job Evaluations ({savedMatches.length})
                </span>
                <span className="text-[11px] text-slate-500">Click to reload past evaluation</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {savedMatches.map((sm) => (
                  <button
                    key={sm.id}
                    type="button"
                    onClick={() => loadSavedMatchDetails(sm.id)}
                    className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors flex items-center space-x-2 ${
                      matchResult?.match_id === sm.id
                        ? "bg-indigo-950/80 border-indigo-600 text-indigo-200"
                        : "bg-slate-800/80 border-slate-700 text-slate-300 hover:bg-slate-700"
                    }`}
                  >
                    <span>{sm.target_job_title}</span>
                    <span className="px-1.5 py-0.5 rounded bg-slate-900 text-[10px] font-bold text-indigo-400">
                      {Math.round(sm.overall_match_score)}%
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleRunJobMatch} className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
              <h2 className="text-base font-semibold text-slate-200">
                Target Job Description
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400">Quick fill:</span>
                <button
                  type="button"
                  onClick={() => loadSample("tech")}
                  className="px-2 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition-colors"
                >
                  Tech Role
                </button>
                <button
                  type="button"
                  onClick={() => loadSample("product")}
                  className="px-2 py-1 text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition-colors"
                >
                  Product Role
                </button>
                {(jobTitle || jobDescription) && (
                  <button
                    type="button"
                    onClick={clearForm}
                    className="px-2 py-1 text-[11px] text-slate-400 hover:text-rose-400 transition-colors"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Job Title</label>
                <input
                  type="text"
                  required
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 placeholder-slate-500"
                  placeholder="e.g. Senior Software Engineer, Product Manager, Data Analyst..."
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Full Job Description & Requirements</label>
                <textarea
                  rows={6}
                  required
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-mono text-[12px] placeholder-slate-500"
                  placeholder="Paste the complete job description, required qualifications, and responsibilities here..."
                />
              </div>

              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 pt-2">
                <p className="text-[11px] text-slate-400">
                  Separates required vs. preferred keywords, experience years, and portfolio evidence alignment.
                </p>
                <button
                  type="submit"
                  disabled={matchingLoading}
                  className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white rounded-lg text-xs font-semibold transition-colors flex items-center justify-center shrink-0"
                >
                  {matchingLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-3.5 w-3.5 border-b-2 border-white mr-2"></div>
                      Evaluating Match...
                    </>
                  ) : (
                    "Evaluate Match & Alignment"
                  )}
                </button>
              </div>
            </div>
          </form>

          {/* Match Results */}
          {matchResult && (
            <div className="space-y-8 animate-fadeIn">
              {/* Top Score Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                {/* Overall Match Score */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Weighted Match Score</p>
                  <div className="mt-4 flex items-center justify-center">
                    <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center ${getScoreColor(matchResult.overall_match_score)}`}>
                      <span className="text-2xl font-bold">
                        {Math.round(matchResult.overall_match_score)}%
                      </span>
                    </div>
                  </div>
                  <p className="mt-3 text-xs text-slate-400">
                    Required (45%), Preferred (20%), Experience (20%), Project Evidence (15%)
                  </p>
                </div>

                {/* Required Skills Match */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Required Skills</p>
                  <div className="mt-4 flex items-center justify-center">
                    <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center ${getScoreColor(matchResult.required_skills_match.match_percentage)}`}>
                      <span className="text-2xl font-bold">
                        {Math.round(matchResult.required_skills_match.match_percentage)}%
                      </span>
                    </div>
                  </div>
                  <p className="mt-3 text-xs text-slate-400">
                    {matchResult.required_skills_match.matched_count} of {matchResult.required_skills_match.target_count} core requirements verified.
                  </p>
                </div>

                {/* Experience Fit */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Experience Alignment</p>
                  <div className="mt-4 flex flex-col items-center justify-center h-24">
                    <span className="text-xl font-bold text-slate-100">
                      {matchResult.experience_level_match.detected_years} yrs detected
                    </span>
                    <span className="text-xs text-slate-400 mt-1">
                      {matchResult.experience_level_match.required_years ? `Target: ${matchResult.experience_level_match.required_years}+ yrs` : "No strict minimum"}
                    </span>
                  </div>
                  <span className={`inline-block px-2.5 py-1 rounded text-xs font-semibold ${
                    matchResult.experience_level_match.assessment === "MEETS_REQUIREMENT"
                      ? "bg-emerald-950/60 text-emerald-300 border border-emerald-800"
                      : "bg-amber-950/60 text-amber-300 border border-amber-800"
                  }`}>
                    {matchResult.experience_level_match.assessment.replace(/_/g, " ")}
                  </span>
                </div>
              </div>

              {/* Required & Preferred Skills Breakdowns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Required Skills Card */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-slate-200 mb-3 pb-2 border-b border-slate-800 flex items-center justify-between">
                    <span>Core Required Skills</span>
                    <span className="text-xs text-emerald-400 font-semibold">{matchResult.required_skills_match.matched_count}/{matchResult.required_skills_match.target_count} Matched</span>
                  </h3>

                  <div className="space-y-4">
                    <div>
                      <p className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider mb-2">✓ Verified in Resume</p>
                      <div className="flex flex-wrap gap-2">
                        {matchResult.required_skills_match.matched.length === 0 ? (
                          <span className="text-xs text-slate-500 italic">No exact requirement matches.</span>
                        ) : (
                          matchResult.required_skills_match.matched.map((sk, idx) => (
                            <span key={idx} className="px-2.5 py-1 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-800/80 text-xs font-medium">
                              {sk}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider mb-2">✕ Missing Requirements</p>
                      <div className="flex flex-wrap gap-2">
                        {matchResult.required_skills_match.missing.length === 0 ? (
                          <span className="text-xs text-emerald-400 font-medium">All core requirements met!</span>
                        ) : (
                          matchResult.required_skills_match.missing.map((sk, idx) => (
                            <span key={idx} className="px-2.5 py-1 rounded bg-rose-950/20 text-rose-300 border border-rose-900/60 text-xs font-medium">
                              {sk}
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Preferred Skills Card */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-slate-200 mb-3 pb-2 border-b border-slate-800 flex items-center justify-between">
                    <span>Preferred / Nice-to-Have Skills</span>
                    <span className="text-xs text-indigo-400 font-semibold">{matchResult.preferred_skills_match.matched_count}/{matchResult.preferred_skills_match.target_count} Matched</span>
                  </h3>

                  <div className="space-y-4">
                    <div>
                      <p className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider mb-2">✓ Demonstrated in Resume</p>
                      <div className="flex flex-wrap gap-2">
                        {matchResult.preferred_skills_match.matched.length === 0 ? (
                          <span className="text-xs text-slate-500 italic">No preferred matches detected.</span>
                        ) : (
                          matchResult.preferred_skills_match.matched.map((sk, idx) => (
                            <span key={idx} className="px-2.5 py-1 rounded bg-indigo-950/40 text-indigo-300 border border-indigo-800/80 text-xs font-medium">
                              {sk}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">Missing Preferred</p>
                      <div className="flex flex-wrap gap-2">
                        {matchResult.preferred_skills_match.missing.length === 0 ? (
                          <span className="text-xs text-indigo-400 font-medium">All preferred skills present!</span>
                        ) : (
                          matchResult.preferred_skills_match.missing.map((sk, idx) => (
                            <span key={idx} className="px-2.5 py-1 rounded bg-slate-800 text-slate-400 border border-slate-700 text-xs font-medium">
                              {sk}
                            </span>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Unverified / Inferred Skills Notice */}
              {matchResult.unverified_matches.length > 0 && (
                <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-800/70 text-xs">
                  <p className="font-semibold text-amber-200 flex items-center">
                    <span className="mr-2">💡</span> Skills Inferred from Experience Context
                  </p>
                  <p className="text-slate-300 mt-1">
                    The following matched skills were detected in your experience narratives or project descriptions:
                  </p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {matchResult.unverified_matches.map((sk, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded bg-amber-900/40 text-amber-300 border border-amber-700 font-mono text-[11px]">
                        {sk}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Project & Portfolio Evidence Alignment */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                <h3 className="text-sm font-bold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                  Portfolio & Project Evidence Alignment
                </h3>
                <p className="text-xs text-slate-400 mb-4">
                  Evidence citations showing where your documented projects and experience align directly with the target job's key domains:
                </p>

                {matchResult.project_theme_alignments.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No specific project bullet alignments found for target JD themes.</p>
                ) : (
                  <div className="space-y-3">
                    {matchResult.project_theme_alignments.map((align, idx) => {
                      const themeName = align.theme || align.jd_theme || "Project Alignment";
                      const bullets = align.matched_bullets && align.matched_bullets.length > 0
                        ? align.matched_bullets
                        : align.bullet_excerpt
                        ? [align.bullet_excerpt]
                        : [];
                      return (
                        <div key={idx} className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800">
                          <div className="flex flex-wrap justify-between items-center gap-2 mb-2">
                            <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                              Theme: {themeName}
                            </span>
                            <span className="text-[11px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800 font-medium">
                              Verified Evidence
                            </span>
                          </div>
                          {bullets.length > 0 ? (
                            <ul className="list-disc list-inside space-y-1 text-xs text-slate-300">
                              {bullets.map((b, bIdx) => (
                                <li key={bIdx} className="italic">&ldquo;{b}&rdquo;</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-xs text-slate-500 italic">Direct experience evidence mapped to this competency.</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Actionable Recommendations */}
              {matchResult.job_specific_suggestions && matchResult.job_specific_suggestions.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                    ATS Optimization Recommendations
                  </h3>
                  <div className="space-y-3">
                    {matchResult.job_specific_suggestions.map((sug, idx) => (
                      <div key={idx} className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800/80">
                        <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300 mb-1">
                          <span>💡</span>
                          <span>{sug.title}</span>
                        </div>
                        <p className="text-xs text-slate-400 leading-relaxed">
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
        <div className="space-y-8 animate-fadeIn">
          {loadingQuality ? (
            <div className="py-20 text-center text-slate-400">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
              Evaluating resume structural quality...
            </div>
          ) : qualityReport ? (
            <div className="space-y-8">
              {/* Overall Quality Banner */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 flex flex-col sm:flex-row items-center justify-between gap-6">
                <div className="flex items-center space-x-5">
                  <div className={`w-20 h-20 rounded-full border-4 flex items-center justify-center ${getScoreColor(qualityReport.overall_quality_score)}`}>
                    <span className="text-2xl font-bold">
                      {Math.round(qualityReport.overall_quality_score)}
                    </span>
                  </div>
                  <div>
                    <div className="flex items-center space-x-2">
                      <h2 className="text-lg font-bold text-slate-100">Resume Quality Index</h2>
                      <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                        qualityReport.quality_band === "STRONG"
                          ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800"
                          : qualityReport.quality_band === "MODERATE"
                          ? "bg-amber-950/80 text-amber-300 border border-amber-800"
                          : "bg-rose-950/80 text-rose-300 border border-rose-800"
                      }`}>
                        {qualityReport.quality_band}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-1 max-w-lg">
                      Based on section completeness, action-verb impact cues, technical skills depth, and standard formatting heuristics.
                    </p>
                  </div>
                </div>

                <Link
                  href={`/resumes/${resumeId}/suggestions`}
                  className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors whitespace-nowrap shadow-sm"
                >
                  View AI Improvement Rewrites →
                </Link>
              </div>

              {/* 4 Category Breakdown Bars */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex justify-between items-center text-xs mb-1.5">
                    <span className="font-semibold text-slate-300">Structure & Completeness (25%)</span>
                    <span className="font-bold text-slate-100">{qualityReport.section_scores.structure_and_completeness}/25</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-indigo-500 h-2 rounded-full"
                      style={{ width: `${(qualityReport.section_scores.structure_and_completeness / 25) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex justify-between items-center text-xs mb-1.5">
                    <span className="font-semibold text-slate-300">Quantified Impact & Action Verbs (35%)</span>
                    <span className="font-bold text-slate-100">{qualityReport.section_scores.quantified_impact_and_bullets}/35</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-emerald-500 h-2 rounded-full"
                      style={{ width: `${(qualityReport.section_scores.quantified_impact_and_bullets / 35) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex justify-between items-center text-xs mb-1.5">
                    <span className="font-semibold text-slate-300">Skills Depth & Organization (20%)</span>
                    <span className="font-bold text-slate-100">{qualityReport.section_scores.skills_depth_and_relevance}/20</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full"
                      style={{ width: `${(qualityReport.section_scores.skills_depth_and_relevance / 20) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div className="flex justify-between items-center text-xs mb-1.5">
                    <span className="font-semibold text-slate-300">Formatting, Clarity & Length (20%)</span>
                    <span className="font-bold text-slate-100">{qualityReport.section_scores.formatting_and_length}/20</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2">
                    <div
                      className="bg-amber-500 h-2 rounded-full"
                      style={{ width: `${(qualityReport.section_scores.formatting_and_length / 20) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-emerald-400 mb-3 pb-2 border-b border-slate-800">
                    ✓ Key Structural Strengths
                  </h3>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {qualityReport.strengths.map((str, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-emerald-500 mr-2">•</span>
                        <span>{str}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-amber-400 mb-3 pb-2 border-b border-slate-800">
                    ! Areas for Improvement
                  </h3>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {qualityReport.weaknesses.map((wk, idx) => (
                      <li key={idx} className="flex items-start">
                        <span className="text-amber-500 mr-2">•</span>
                        <span>{wk}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Improvement Priorities */}
              {qualityReport.improvement_priorities.length > 0 && (
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
                  <h3 className="text-sm font-bold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                    Recommended Action Priorities
                  </h3>
                  <ol className="list-decimal list-inside space-y-2 text-xs text-slate-300">
                    {qualityReport.improvement_priorities.map((item, idx) => (
                      <li key={idx} className="leading-relaxed">
                        <span className="font-medium text-slate-200">{item}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {/* Transparent Disclaimer */}
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs text-slate-400">
                <p className="font-semibold text-slate-300 mb-1">Scoring Transparency & Methodology:</p>
                <p className="leading-relaxed">{qualityReport.methodology}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-400 italic">No quality report could be loaded for this resume version.</p>
          )}
        </div>
      )}
    </div>
  );
}
