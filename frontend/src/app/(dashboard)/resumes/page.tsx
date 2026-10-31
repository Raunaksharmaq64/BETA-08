"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "../../../context/AuthContext";
import { apiClient } from "../../../services/apiClient";

interface ResumeSummary {
  id: string;
  title: string;
  active_version_id?: string;
  active_version?: {
    id: string;
    version_number: number;
    version_label: string;
    original_filename: string;
    file_type: string;
    file_size_bytes: number;
    parsing_status: string;
    error_message?: string;
    uploaded_at: string;
  };
  version_count: number;
  created_at: string;
  updated_at: string;
}

export default function ResumeDashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [resumes, setResumes] = useState<ResumeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<ResumeSummary[]>("/api/v1/resumes");
      if (res.success && res.data) {
        setResumes(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load resumes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    } else if (isAuthenticated) {
      fetchResumes();
    }
  }, [authLoading, isAuthenticated]);

  const handleDelete = async (id: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}" and all its versions?`)) return;
    try {
      await apiClient.delete(`/api/v1/resumes/${id}`);
      fetchResumes();
    } catch (err: any) {
      alert("Delete failed: " + err.message);
    }
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "COMPLETED":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-900/60 text-emerald-300 border border-emerald-700">Completed</span>;
      case "REVIEW_REQUIRED":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-900/60 text-amber-300 border border-amber-700">Review Required</span>;
      case "PROCESSING":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900/60 text-blue-300 border border-blue-700">Parsing...</span>;
      case "FAILED":
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-rose-900/60 text-rose-300 border border-rose-700">Failed</span>;
      case "UPLOADED":
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700">Uploaded</span>;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between border-b border-slate-800 pb-6 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Resume Intelligence</h1>
          <p className="mt-1 text-sm text-slate-400">
            Upload, parse, review evidence, and optimize your resume versions for applicant tracking systems.
          </p>
        </div>
        <div className="mt-4 md:mt-0">
          <Link
            href="/resumes/upload"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
          >
            + Upload New Resume
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/30 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-16 text-center text-slate-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
          Loading resumes...
        </div>
      ) : resumes.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/40 rounded-xl border border-slate-800 p-8">
          <div className="w-16 h-16 bg-slate-800/80 rounded-full flex items-center justify-center mx-auto mb-4 text-indigo-400">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-slate-200">No resumes uploaded yet</h3>
          <p className="mt-2 text-sm text-slate-400 max-w-sm mx-auto">
            Upload your PDF or DOCX resume to extract structured experience, verified skills, and run ATS analysis.
          </p>
          <div className="mt-6">
            <Link
              href="/resumes/upload"
              className="inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-500 transition-colors"
            >
              Upload First Resume
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {resumes.map((resume) => {
            const ver = resume.active_version;
            return (
              <div
                key={resume.id}
                className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 shadow-sm hover:border-slate-700 transition-colors"
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-800/80 gap-3">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-semibold text-slate-100">{resume.title}</h2>
                      {getStatusBadge(ver?.parsing_status)}
                    </div>
                    <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
                      <span>File: {ver?.original_filename || "N/A"}</span>
                      <span>•</span>
                      <span>Format: {ver?.file_type?.toUpperCase()}</span>
                      <span>•</span>
                      <span>Versions: {resume.version_count}</span>
                      <span>•</span>
                      <span>Updated: {new Date(resume.updated_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleDelete(resume.id, resume.title)}
                      className="px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-medium text-slate-400 hover:text-rose-400 hover:border-rose-800 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {ver?.error_message && (
                  <div className="mt-4 p-3 rounded-lg bg-rose-950/40 border border-rose-800 text-rose-300 text-xs">
                    {ver.error_message}
                  </div>
                )}

                <div className="mt-5 flex flex-wrap gap-2.5">
                  {ver?.parsing_status === "UPLOADED" && (
                    <Link
                      href={`/resumes/${resume.id}/status`}
                      className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-medium text-white transition-colors"
                    >
                      Start Parsing Pipeline
                    </Link>
                  )}

                  {ver?.parsing_status === "REVIEW_REQUIRED" && (
                    <Link
                      href={`/resumes/${resume.id}/review`}
                      className="px-3.5 py-1.5 rounded-lg bg-amber-600 hover:bg-amber-500 text-xs font-medium text-white transition-colors"
                    >
                      Review & Confirm Facts
                    </Link>
                  )}

                  <Link
                    href={`/resumes/${resume.id}/analysis`}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors"
                  >
                    View Extraction & Evidence
                  </Link>

                  <Link
                    href={`/resumes/${resume.id}/ats`}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors"
                  >
                    Job Match & Quality
                  </Link>

                  <Link
                    href={`/resumes/${resume.id}/suggestions`}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors"
                  >
                    AI Rewrites & Polish
                  </Link>

                  <Link
                    href={`/resumes/${resume.id}/versions`}
                    className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition-colors"
                  >
                    Manage Versions ({resume.version_count})
                  </Link>

                  {resume.version_count > 1 && (
                    <Link
                      href={`/resumes/${resume.id}/versions`}
                      className="px-3.5 py-1.5 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/60 text-xs font-semibold text-indigo-300 border border-indigo-700/70 transition-colors"
                    >
                      Compare Diff ⮂
                    </Link>
                  )}

                  <a
                    href={`/api/v1/resumes/${resume.id}/download`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 border border-slate-700 transition-colors"
                  >
                    Download Original
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

