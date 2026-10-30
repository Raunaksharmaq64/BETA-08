"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";

export default function ResumeAnalysisPage() {
  const params = useParams();
  const resumeId = params?.resumeId as string;

  const [extraction, setExtraction] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showEvidence, setShowEvidence] = useState(true);

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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 mb-8 border-b border-slate-800 gap-4">
        <div>
          <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
            ← Back to Resumes
          </Link>
          <h1 className="text-2xl font-bold text-slate-100">Resume Extraction & Evidence</h1>
          <p className="mt-1 text-sm text-slate-400">
            Structured candidate information with verifiable citations from your document.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowEvidence(!showEvidence)}
            className="px-3.5 py-1.5 rounded-lg border border-slate-700 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            {showEvidence ? "Hide Evidence Excerpts" : "Show Evidence Excerpts"}
          </button>
          <Link
            href={`/resumes/${resumeId}/review`}
            className="px-4 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-xs font-semibold text-white transition-colors"
          >
            Open Review Workbench
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
          <div className="mt-3">
            <Link href={`/resumes/${resumeId}/status`} className="underline font-semibold text-rose-200">
              Run parsing pipeline now →
            </Link>
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

          {/* 4. Education */}
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

          {/* 5. Categorized Skills */}
          <section className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-4 pb-2 border-b border-slate-800">
              Categorized Technical Skills
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
          </section>

          {/* 6. Projects & Certifications */}
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

