"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

export default function ResumeAnalysisPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [extraction, setExtraction] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(true);
  const [suggestedJobs, setSuggestedJobs] = useState<any[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);

  useEffect(() => {
    const fetchSuggestedJobs = async () => {
      try {
        setLoadingJobs(true);
        const res: any = await apiClient.get(`/resumes/${resumeId}/suggested-jobs?limit=3`);
        if (res?.data) {
          setSuggestedJobs(res.data);
        }
      } catch (err) {
        console.error("Failed to load suggested jobs for resume:", err);
      } finally {
        setLoadingJobs(false);
      }
    };
    if (resumeId) {
      fetchSuggestedJobs();
    }
  }, [resumeId]);

  useEffect(() => {
    const fetchExtraction = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await apiClient.get<any>(`/api/v1/resumes/${resumeId}/extraction`);
        if (res.success && res.data) {
          setExtraction(res.data);
        }
      } catch (err: any) {
        setError(err.message || "Failed to load extraction details. Make sure the resume has been parsed.");
      } finally {
        setLoading(false);
      }
    };

    if (resumeId) {
      fetchExtraction();
    }
  }, [resumeId]);

  const getConfidenceBadge = (level: string) => {
    switch (level) {
      case "HIGH":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-950/60 text-emerald-300 border border-emerald-800">High Confidence</span>;
      case "MEDIUM":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-950/60 text-amber-300 border border-amber-800">Medium Confidence</span>;
      case "LOW":
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-950/60 text-rose-300 border border-rose-800">Low Confidence</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-400 border border-slate-700">Evidence Unavailable</span>;
    }
  };

  const getEvidenceForField = (fieldNamePrefix: string) => {
    if (!extraction?.evidence_items) return null;
    return extraction.evidence_items.find((ev: any) => ev.field_name.startsWith(fieldNamePrefix));
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Navigation & Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 mb-6 border-b border-slate-800 gap-4">
        <div>
          <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
            ← Back to Resumes
          </Link>
          <h1 className="text-2xl font-bold text-slate-100">Resume Profile & Extracted Skills</h1>
          <p className="mt-1 text-sm text-slate-400">
            Parsed professional background, verified skills, and calibrated career opportunities.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href={`/resumes/${resumeId}/ats`}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white transition-colors shadow-sm flex items-center gap-1.5"
          >
            <span>🎯</span>
            <span>ATS Optimizer & Matcher →</span>
          </Link>
        </div>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {/* Scanned PDF Warning Banner */}
      {extraction?.is_scanned_pdf && (
        <div className="mb-6 p-4 rounded-xl bg-amber-950/40 border border-amber-800 text-amber-200 text-xs leading-relaxed flex items-start space-x-3">
          <span className="text-base font-bold">⚠️</span>
          <div>
            <p className="font-semibold text-amber-100">Scanned Document or Low Embedded Text Detected</p>
            <p className="mt-0.5">
              This document contains very few parseable character glyphs and may be an image scan or flattened PDF.
              Please verify your extracted details below or upload a clean, text-searchable PDF.
            </p>
          </div>
        </div>
      )}

      {/* Extraction Warnings/Notes */}
      {extraction?.extraction_notes && extraction.extraction_notes.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-slate-900 border border-slate-800 text-xs text-slate-400">
          <p className="font-semibold text-slate-300 mb-1">Extraction Notes:</p>
          <ul className="list-disc list-inside space-y-1">
            {extraction.extraction_notes.map((note: string, idx: number) => (
              <li key={idx}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
          <div className="mt-3">
            <button
              onClick={async () => {
                setLoading(true);
                try {
                  await apiClient.post(`/api/v1/resumes/${resumeId}/parse`);
                  window.location.reload();
                } catch (e: any) {
                  setError(e.message);
                  setLoading(false);
                }
              }}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white"
            >
              Parse Resume Now →
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
          Loading document extractions...
        </div>
      ) : extraction ? (
        <div className="space-y-8">
          {/* Detected Domain & Career Archetypes Banner */}
          {(extraction.domain_info || extraction.sections?.domain_info) && (() => {
            const dom = extraction.domain_info || extraction.sections?.domain_info;
            return (
              <section className="p-6 rounded-xl bg-gradient-to-r from-indigo-950/90 via-slate-900 to-purple-950/70 border border-indigo-700/60 shadow-lg text-white">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-2xl">{dom.icon || "🎯"}</span>
                      <h2 className="text-lg font-bold text-white">
                        Detected Domain: {dom.display_name}
                      </h2>
                      <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/30 border border-indigo-400 text-indigo-200">
                        {Math.round((dom.confidence_score || 0.9) * 100)}% Confidence
                      </span>
                    </div>
                    <p className="text-xs text-indigo-200/80">
                      Opportunities, freelance contracts, and startup bottlenecks across RightFit are automatically tailored to this discipline.
                    </p>
                    {dom.target_archetypes && dom.target_archetypes.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 pt-1">
                        <span className="text-xs text-slate-400">Target Career Archetypes:</span>
                        {dom.target_archetypes.map((arch: string) => (
                          <span
                            key={arch}
                            className="text-xs px-2.5 py-0.5 rounded-md bg-indigo-900/60 border border-indigo-700 text-indigo-200 font-medium"
                          >
                            {arch}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div>
                    <Link
                      href="/opportunities"
                      className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white shadow transition-colors"
                    >
                      View Recommended Opportunities →
                    </Link>
                  </div>
                </div>
              </section>
            );
          })()}

          {/* Calibrated Real Opportunities for this Resume */}
          {suggestedJobs.length > 0 && (
            <section className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <span>🎯</span> Top Opportunities Calibrated for this Resume
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Live career opportunities scored against your verified resume skills and target domain.
                  </p>
                </div>
                <Link
                  href="/opportunities"
                  className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1 shrink-0"
                >
                  Explore Live Opportunities →
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {suggestedJobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700 flex flex-col justify-between space-y-3 transition-colors"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between gap-1">
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 font-mono">
                          {Math.round(job.match_score)}% Match
                        </span>
                        <span className="text-[11px] text-slate-400 truncate max-w-[120px]">
                          {job.company_name}
                        </span>
                      </div>

                      <h3 className="text-sm font-bold text-white line-clamp-1 hover:text-indigo-300">
                        {job.title}
                      </h3>

                      <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                        {job.description_snippet}
                      </p>

                      {job.matched_skills && job.matched_skills.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1 pt-1">
                          <span className="text-[10px] text-emerald-400 font-medium">Matched:</span>
                          {job.matched_skills.slice(0, 2).map((s: string) => (
                            <span
                              key={s}
                              className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-950/80 border border-emerald-800 text-emerald-300 font-mono"
                            >
                              ✓ {s}
                            </span>
                          ))}
                        </div>
                      )}

                      {job.missing_skills && job.missing_skills.length > 0 && (
                        <div className="flex flex-wrap items-center gap-1">
                          <span className="text-[10px] text-amber-400 font-medium">Add to Resume:</span>
                          {job.missing_skills.slice(0, 2).map((s: string) => (
                            <span
                              key={s}
                              className="text-[10px] px-1.5 py-0.2 rounded bg-amber-950/60 border border-amber-800 text-amber-300 font-mono"
                            >
                              + {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        {job.location} {job.is_remote && "• Remote"}
                      </span>
                      <Link
                        href={`/jobs/${job.job_id}`}
                        className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
                      >
                        View Fit Breakdown →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 1. Contact & Personal Info */}
          <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800 flex items-center justify-between">
              <span>Personal & Contact Information</span>
              {getEvidenceForField("personal_info") && getConfidenceBadge(getEvidenceForField("personal_info")?.confidence_level)}
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-slate-400">Full Name</p>
                <p className="text-sm font-medium text-slate-200 mt-0.5">{extraction.personal_info?.full_name || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Email Address</p>
                <p className="text-sm font-medium text-slate-200 mt-0.5">{extraction.personal_info?.email || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Phone</p>
                <p className="text-sm font-medium text-slate-200 mt-0.5">{extraction.personal_info?.phone || "—"}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">LinkedIn</p>
                <p className="text-sm font-medium text-indigo-400 mt-0.5 truncate">
                  {extraction.personal_info?.linkedin_url ? (
                    <a href={extraction.personal_info.linkedin_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.linkedin_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">GitHub</p>
                <p className="text-sm font-medium text-indigo-400 mt-0.5 truncate">
                  {extraction.personal_info?.github_url ? (
                    <a href={extraction.personal_info.github_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.github_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Portfolio</p>
                <p className="text-sm font-medium text-indigo-400 mt-0.5 truncate">
                  {extraction.personal_info?.portfolio_url ? (
                    <a href={extraction.personal_info.portfolio_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      {extraction.personal_info.portfolio_url}
                    </a>
                  ) : "—"}
                </p>
              </div>
            </div>
          </section>

          {/* 2. Professional Summary */}
          {extraction.summary && (
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-3 pb-2 border-b border-slate-800 flex items-center justify-between">
                <span>Professional Summary</span>
                {getEvidenceForField("summary") && getConfidenceBadge(getEvidenceForField("summary")?.confidence_level)}
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">{extraction.summary.text}</p>
            </section>
          )}

          {/* 3. Work Experience */}
          <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
              Work Experience ({extraction.experience?.length || 0})
            </h2>

            {extraction.experience?.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No work experience sections detected.</p>
            ) : (
              <div className="space-y-6">
                {extraction.experience?.map((exp: any, idx: number) => {
                  const ev = getEvidenceForField(`experience[${idx}]`);
                  return (
                    <div key={idx} className="pb-5 border-b border-slate-800/60 last:border-0 last:pb-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <h3 className="text-sm font-bold text-slate-100">{exp.title}</h3>
                          <p className="text-xs font-semibold text-indigo-400">{exp.company}</p>
                        </div>
                        <div className="mt-1 sm:mt-0 flex items-center space-x-2">
                          <span className="text-xs text-slate-400">{exp.start_date} – {exp.end_date}</span>
                          {ev && getConfidenceBadge(ev.confidence_level)}
                        </div>
                      </div>

                      {exp.responsibilities?.length > 0 && (
                        <ul className="mt-3 space-y-1.5 list-disc list-inside text-xs text-slate-300">
                          {exp.responsibilities.map((r: string, rIdx: number) => (
                            <li key={rIdx}>{r}</li>
                          ))}
                        </ul>
                      )}

                      {showEvidence && ev && (
                        <div className="mt-3 p-2.5 rounded bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-400">
                          <span className="font-semibold text-slate-300">Evidence Citation:</span> Page {ev.page_number || 1} • &ldquo;{ev.excerpt}&rdquo;
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* 4. Internships (if present) */}
          {extraction.internships && extraction.internships.length > 0 && (
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
                Internships & Apprenticeships ({extraction.internships.length})
              </h2>
              <div className="space-y-4">
                {extraction.internships.map((intern: any, idx: number) => (
                  <div key={idx} className="pb-4 border-b border-slate-800/60 last:border-0 last:pb-0">
                    <div className="flex justify-between items-center">
                      <h3 className="text-sm font-bold text-slate-100">{intern.title || "Intern"}</h3>
                      <span className="text-xs text-slate-400">{intern.duration || ""}</span>
                    </div>
                    <p className="text-xs font-semibold text-indigo-400">{intern.company || ""}</p>
                    {intern.responsibilities && (
                      <p className="text-xs text-slate-300 mt-1">{intern.responsibilities}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* 5. Education */}
          <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
              Education ({extraction.education?.length || 0})
            </h2>

            {extraction.education?.length === 0 ? (
              <p className="text-sm text-slate-400 italic">No academic degrees detected.</p>
            ) : (
              <div className="space-y-4">
                {extraction.education?.map((edu: any, idx: number) => {
                  const ev = getEvidenceForField(`education[${idx}]`);
                  return (
                    <div key={idx} className="pb-4 border-b border-slate-800/60 last:border-0 last:pb-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                        <div>
                          <h3 className="text-sm font-bold text-slate-100">{edu.degree || "Degree"}</h3>
                          <p className="text-xs text-slate-300 font-medium">{edu.institution}</p>
                        </div>
                        <div className="mt-1 sm:mt-0 flex items-center space-x-2">
                          {edu.start_date && (
                            <span className="text-xs text-slate-400">{edu.start_date} – {edu.end_date}</span>
                          )}
                          {ev && getConfidenceBadge(ev.confidence_level)}
                        </div>
                      </div>
                      {edu.grade && (
                        <p className="text-xs text-emerald-400 mt-1 font-medium">{edu.grade}</p>
                      )}

                      {showEvidence && ev && (
                        <div className="mt-2.5 p-2 rounded bg-slate-950/40 border border-slate-800/80 text-[11px] text-slate-400">
                          <span className="font-semibold text-slate-300">Evidence Citation:</span> Page {ev.page_number || 1} • &ldquo;{ev.excerpt}&rdquo;
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* 6. Skills: Explicit vs. Inferred */}
          <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
              Categorized Technical Skills (Explicitly Stated)
            </h2>

            <div className="space-y-4">
              {Object.entries(extraction.skills || {}).map(([category, skillList]: [string, any]) => {
                if (!skillList || skillList.length === 0) return null;
                return (
                  <div key={category}>
                    <p className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-2">
                      {category.replace("_", " ")}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {skillList.map((s: any, sIdx: number) => (
                        <span
                          key={sIdx}
                          className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-xs font-medium text-slate-200"
                        >
                          {s.name}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Inferred Skills Subsection */}
            {extraction.inferred_skills && extraction.inferred_skills.length > 0 && (
              <div className="mt-6 pt-5 border-t border-slate-800">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-400">Inferred Technical Skills</span>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800 text-amber-300 font-medium">
                    Unverified • Inferred from Context
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-3">
                  These technologies were detected inside experience descriptions or project context, but not in an explicit Skills section. Confirm them in the Review Workbench.
                </p>
                <div className="flex flex-wrap gap-2">
                  {extraction.inferred_skills.map((s: any, sIdx: number) => (
                    <span
                      key={sIdx}
                      className="px-2.5 py-1 rounded-md bg-amber-950/20 border border-amber-800/60 text-xs font-medium text-amber-200"
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* 7. Supplementary Entities: Publications, Awards, Languages */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Publications */}
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                Publications ({extraction.publications?.length || 0})
              </h2>
              {(!extraction.publications || extraction.publications.length === 0) ? (
                <p className="text-xs text-slate-400 italic">No publications detected.</p>
              ) : (
                <ul className="space-y-2 text-xs text-slate-300">
                  {extraction.publications.map((pub: any, idx: number) => (
                    <li key={idx} className="pb-2 border-b border-slate-800/50 last:border-0 font-medium">
                      {pub.title || JSON.stringify(pub)}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {/* Awards */}
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                Awards & Honors ({extraction.awards?.length || 0})
              </h2>
              {(!extraction.awards || extraction.awards.length === 0) ? (
                <p className="text-xs text-slate-400 italic">No awards detected.</p>
              ) : (
                <ul className="space-y-2 text-xs text-slate-300">
                  {extraction.awards.map((aw: any, idx: number) => (
                    <li key={idx} className="pb-2 border-b border-slate-800/50 last:border-0 font-medium">
                      {aw.title || JSON.stringify(aw)}
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {/* Languages */}
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-3 pb-2 border-b border-slate-800">
                Languages ({extraction.languages?.length || 0})
              </h2>
              {(!extraction.languages || extraction.languages.length === 0) ? (
                <p className="text-xs text-slate-400 italic">No languages detected.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {extraction.languages.map((lang: any, idx: number) => (
                    <span key={idx} className="px-2.5 py-1 rounded bg-slate-800 text-xs text-slate-200 border border-slate-700">
                      {lang.language || JSON.stringify(lang)}
                    </span>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* 8. Projects & Certifications */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
                Key Projects ({extraction.projects?.length || 0})
              </h2>
              {extraction.projects?.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No specific projects section detected.</p>
              ) : (
                <div className="space-y-3">
                  {extraction.projects?.map((proj: any, idx: number) => (
                    <div key={idx} className="pb-3 border-b border-slate-800/60 last:border-0">
                      <p className="text-sm font-semibold text-slate-200">{proj.name}</p>
                      <p className="text-xs text-slate-400 mt-1">{proj.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>

            <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
                Certifications ({extraction.certifications?.length || 0})
              </h2>
              {extraction.certifications?.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No certifications detected.</p>
              ) : (
                <div className="space-y-3">
                  {extraction.certifications?.map((cert: any, idx: number) => (
                    <div key={idx} className="pb-3 border-b border-slate-800/60 last:border-0">
                      <p className="text-sm font-semibold text-slate-200">{cert.name}</p>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      ) : null}
    </div>
  );
}
