"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface MatchBreakdown {
  skill_fit: {
    fit_score: number;
    total_required_skills: number;
    matched_required_count: number;
    matched_required_skills: string[];
    missing_required_skills: string[];
    matched_preferred_skills: string[];
    missing_preferred_skills: string[];
    unconfirmed_skills: string[];
    skill_evidence: Array<{
      skill: string;
      source_type: string;
      evidence_excerpt?: string;
      years_experience?: number;
      is_confirmed: boolean;
    }>;
  };
  eligibility: {
    status: string;
    summary: string;
    has_missing_candidate_data: boolean;
    criteria: Array<{
      criterion_name: string;
      required_value: string;
      candidate_value?: string;
      status: string;
      explanation: string;
    }>;
  };
  verification_status: string;
  verification_explanation: string;
  freshness_state: string;
  freshness_explanation: string;
  preference_match: Record<string, any>;
  ranking_score: number;
}

interface JobDetail {
  id: string;
  external_job_id: string;
  title: string;
  company_name: string;
  department?: string;
  description_clean: string;
  city?: string;
  state?: string;
  country?: string;
  workplace_type: string;
  is_remote: boolean;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
  currency?: string;
  salary_period?: string;
  required_skills: string[];
  application_url: string;
  source_name: string;
  source_key: string;
  source_published_at?: string;
  first_seen_at: string;
  last_seen_at: string;
  last_verified_at?: string;
  verification_status: string;
  freshness_state: string;
  is_saved: boolean;
  saved_job_id?: string;
  match_breakdown?: MatchBreakdown;
  provenance_metadata: Record<string, any>;
}

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const jobId = params?.jobId as string;

  const [job, setJob] = useState<JobDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Note editing state
  const [notes, setNotes] = useState("");
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [noteSavedMsg, setNoteSavedMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const fetchDetail = async () => {
      setIsLoading(true);
      setErrorMsg(null);
      try {
        const res = await apiClient<JobDetail>(`/jobs/${jobId}`);
        if (res.data) {
          setJob(res.data);
          // Fetch existing note if saved
          if (res.data.is_saved && res.data.saved_job_id) {
            const savedRes = await apiClient<any[]>("/saved-jobs");
            const match = savedRes.data?.find((s) => s.opportunity_id === jobId);
            if (match?.notes) setNotes(match.notes);
          }
        }
      } catch (err: any) {
        setErrorMsg(err.message || "Failed to load job posting details.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDetail();
  }, [jobId]);

  const handleToggleSave = async () => {
    if (!user) {
      router.push("/login");
      return;
    }
    if (!job) return;

    try {
      if (job.is_saved) {
        await apiClient(`/saved-jobs/${job.id}`, { method: "DELETE" });
        setJob({ ...job, is_saved: false, saved_job_id: undefined });
      } else {
        const res = await apiClient<any>("/saved-jobs", {
          method: "POST",
          body: JSON.stringify({ opportunity_id: job.id, notes }),
        });
        setJob({ ...job, is_saved: true, saved_job_id: res.data.id });
      }
    } catch (err: any) {
      alert("Failed to update save status: " + err.message);
    }
  };

  const handleSaveNote = async () => {
    if (!job?.saved_job_id) return;
    setIsSavingNote(true);
    setNoteSavedMsg(null);
    try {
      await apiClient(`/saved-jobs/${job.saved_job_id}`, {
        method: "PATCH",
        body: JSON.stringify({ notes }),
      });
      setNoteSavedMsg("Personal note saved!");
      setTimeout(() => setNoteSavedMsg(null), 2500);
    } catch (err: any) {
      alert("Failed to save note: " + err.message);
    } finally {
      setIsSavingNote(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-slate-800 rounded w-1/3" />
          <div className="h-64 bg-slate-900 rounded-2xl border border-slate-800" />
          <div className="h-96 bg-slate-900 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  if (errorMsg || !job) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <div className="p-6 rounded-2xl bg-red-950/40 border border-red-800/50 text-red-300">
          <h2 className="text-lg font-bold">Opportunity Not Available</h2>
          <p className="text-sm mt-2">{errorMsg || "The requested job posting could not be located."}</p>
          <Link
            href="/search"
            className="inline-block mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold rounded-lg"
          >
            ← Return to Job Discovery
          </Link>
        </div>
      </div>
    );
  }

  const match = job.match_breakdown;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button */}
      <div>
        <Link
          href="/search"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          ← Back to Job Discovery
        </Link>
      </div>

      {/* Main Posting Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">{job.title}</h1>
              {job.is_remote && (
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                  Remote Eligible
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 text-slate-300 text-base flex-wrap">
              <span className="font-semibold text-white">{job.company_name}</span>
              <span>•</span>
              <span>{job.city ? `${job.city}, ${job.country || ""}` : job.country || "Worldwide"}</span>
              <span>•</span>
              <span className="text-slate-400">{job.employment_type.replace(/_/g, " ")}</span>
              {job.department && (
                <>
                  <span>•</span>
                  <span className="text-slate-400">{job.department}</span>
                </>
              )}
            </div>
          </div>

          {/* Action Buttons: Apply & Save */}
          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={handleToggleSave}
              className={`px-4 py-2.5 rounded-xl text-sm font-semibold border transition-colors flex items-center gap-2 ${
                job.is_saved
                  ? "bg-rose-950/60 border-rose-700/60 text-rose-300 hover:bg-rose-900/60"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700 hover:text-white"
              }`}
            >
              <svg className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z" />
              </svg>
              {job.is_saved ? "Saved" : "Save Job"}
            </button>

            <a
              href={job.application_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-2.5 rounded-xl text-sm font-bold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors shadow-lg shadow-indigo-600/30 inline-flex items-center gap-2"
            >
              Apply on Company Site ↗
            </a>
          </div>
        </div>

        {/* Compensation & Trust Stats Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800">
          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">Compensation</div>
            <div className="text-base font-bold text-slate-200 mt-1">
              {job.min_salary || job.max_salary ? (
                <>
                  {job.currency || "$"}
                  {job.min_salary?.toLocaleString()} - {job.max_salary?.toLocaleString()}
                </>
              ) : (
                "Undisclosed"
              )}
            </div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">Verification State</div>
            <div className="text-sm font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
              <span>{job.verification_status === "OPEN_CONFIRMED" ? "✓ Open Confirmed" : job.verification_status}</span>
            </div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">Freshness State</div>
            <div className="text-sm font-bold text-cyan-400 mt-1">{job.freshness_state}</div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
            <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">Source Origin</div>
            <div className="text-sm font-bold text-slate-300 mt-1 truncate">{job.source_name}</div>
          </div>
        </div>
      </div>

      {/* Candidate Personal Notes Card (if saved) */}
      {job.is_saved && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">Your Private Application Notes</h3>
            {noteSavedMsg && <span className="text-xs text-emerald-400 font-medium">{noteSavedMsg}</span>}
          </div>
          <textarea
            rows={2}
            placeholder="Add personal interview dates, contact notes, or application follow-up reminders..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full p-3 bg-slate-950 rounded-xl border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          />
          <div className="flex justify-end">
            <button
              onClick={handleSaveNote}
              disabled={isSavingNote}
              className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 text-xs font-semibold rounded-lg transition-colors"
            >
              {isSavingNote ? "Saving..." : "Save Note"}
            </button>
          </div>
        </div>
      )}

      {/* Match Explanation Breakdown */}
      {match ? (
        <div className="space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Evidence-Based Match Breakdown</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Transparent evaluation comparing your reviewed resume evidence with verified job requirements.
              </p>
            </div>
            <div className="px-4 py-2 rounded-xl bg-indigo-950/80 border border-indigo-700/60 text-right">
              <div className="text-xs text-indigo-300 font-medium">Composite Ranking Score</div>
              <div className="text-xl font-extrabold text-white">{match.ranking_score} / 100</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Skill Fit Engine Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Skill Fit Analysis</h3>
                  <p className="text-xs text-slate-400">Strictly evidence-backed without hallucinated skills.</p>
                </div>
                <span className="text-2xl font-black text-indigo-400">{match.skill_fit.fit_score}%</span>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800">
                <div
                  className="bg-indigo-500 h-2.5 rounded-full transition-all"
                  style={{ width: `${match.skill_fit.fit_score}%` }}
                />
              </div>

              {/* Matched Skills with Evidence */}
              <div className="space-y-3">
                <div className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                  Matched Required Skills ({match.skill_fit.matched_required_count} / {match.skill_fit.total_required_skills})
                </div>
                {match.skill_fit.skill_evidence.length > 0 ? (
                  <div className="space-y-2">
                    {match.skill_fit.skill_evidence.map((ev, idx) => (
                      <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800/80 space-y-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-emerald-300">✓ {ev.skill}</span>
                          <span className="text-slate-500 text-[10px]">Source: {ev.source_type}</span>
                        </div>
                        {ev.evidence_excerpt && (
                          <p className="text-xs italic text-slate-400 bg-slate-900/60 p-2 rounded border border-slate-800">
                            &quot;{ev.evidence_excerpt}&quot;
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic">No required skills matched yet.</p>
                )}
              </div>

              {/* Missing Skills */}
              {match.skill_fit.missing_required_skills.length > 0 && (
                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <div className="text-xs font-semibold uppercase tracking-wider text-amber-400">
                    Missing Required Skills ({match.skill_fit.missing_required_skills.length})
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {match.skill_fit.missing_required_skills.map((s, idx) => (
                      <span
                        key={idx}
                        className="px-2.5 py-1 rounded-lg bg-amber-950/40 text-amber-300 border border-amber-800/40 text-xs font-medium"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Unconfirmed Skills */}
              {match.skill_fit.unconfirmed_skills.length > 0 && (
                <div className="p-3 rounded-xl bg-slate-950 border border-amber-800/50 text-xs text-amber-300 space-y-1">
                  <span className="font-semibold">⚠️ Unconfirmed Skills:</span>
                  <p className="text-slate-400">
                    {match.skill_fit.unconfirmed_skills.join(", ")} were extracted from your resume but await your confirmation.
                  </p>
                </div>
              )}
            </div>

            {/* Mandatory Eligibility Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-5">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Mandatory Eligibility</h3>
                  <p className="text-xs text-slate-400">Evaluated independently from skill fit.</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-lg text-xs font-bold border ${
                    match.eligibility.status === "MEETS_REQUIREMENTS"
                      ? "bg-emerald-950/60 border-emerald-700 text-emerald-300"
                      : match.eligibility.status === "UNKNOWN"
                      ? "bg-slate-800 border-slate-700 text-slate-300"
                      : "bg-rose-950/60 border-rose-800 text-rose-300"
                  }`}
                >
                  {match.eligibility.status.replace(/_/g, " ")}
                </span>
              </div>

              <p className="text-xs text-slate-300">{match.eligibility.summary}</p>

              {/* Criteria List */}
              <div className="space-y-3">
                {match.eligibility.criteria.map((crit, idx) => (
                  <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-white">{crit.criterion_name}</span>
                      <span
                        className={`font-semibold ${
                          crit.status === "SATISFIED"
                            ? "text-emerald-400"
                            : crit.status === "UNKNOWN"
                            ? "text-slate-400"
                            : "text-rose-400"
                        }`}
                      >
                        {crit.status}
                      </span>
                    </div>
                    <div className="text-xs text-slate-400">Required: {crit.required_value}</div>
                    {crit.candidate_value && (
                      <div className="text-xs text-slate-400">Your profile: {crit.candidate_value}</div>
                    )}
                    <p className="text-xs text-slate-500 pt-0.5">{crit.explanation}</p>
                  </div>
                ))}
              </div>

              {/* Trust & Freshness Explanation */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-1 text-xs">
                <span className="font-semibold text-slate-200">Trust & Verification Basis:</span>
                <p className="text-slate-400">{match.verification_explanation}</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 text-center space-y-2">
          <h3 className="text-base font-bold text-white">Sign In to View Evidence-Based Candidate Matching</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Log in and review your resume to get instant evidence match scores, mandatory eligibility checks, and missing skill advice.
          </p>
          <div className="pt-2">
            <Link
              href="/login"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold inline-block"
            >
              Sign In to RIGHT FIT
            </Link>
          </div>
        </div>
      )}

      {/* Full Description Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6">
        <h2 className="text-xl font-bold text-white tracking-tight">Full Job Description</h2>
        <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
          {job.description_clean}
        </div>

        {/* Required Skills Badges */}
        {job.required_skills.length > 0 && (
          <div className="pt-6 border-t border-slate-800 space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Documented Required Skills</h3>
            <div className="flex flex-wrap gap-2">
              {job.required_skills.map((s, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-lg bg-slate-950 text-slate-200 border border-slate-800 text-xs font-medium"
                >
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Provenance Footer */}
        <div className="pt-6 border-t border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-4">
          <div>
            First indexed: {new Date(job.first_seen_at).toLocaleDateString()} • External ID: {job.external_job_id}
          </div>
          <div>Ingested via {job.source_name} adapter</div>
        </div>
      </div>
    </div>
  );
}

