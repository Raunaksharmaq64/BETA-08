"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";
import { ResumeSubNav } from "../../../../../features/resume/ResumeSubNav";

export default function ResumeStatusPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params?.resumeId as string;

  const [resume, setResume] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<any>(`/api/v1/resumes/${resumeId}`);
      if (res.success && res.data) {
        setResume(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load resume details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchStatus();
    }
  }, [resumeId]);

  const handleStartParsing = async () => {
    try {
      setParsing(true);
      setError(null);
      const res = await apiClient.post<any>(`/api/v1/resumes/${resumeId}/parse`);
      if (res.success) {
        // Refresh status
        await fetchStatus();
      }
    } catch (err: any) {
      setError(err.message || "Parsing pipeline encountered an error.");
      fetchStatus();
    } finally {
      setParsing(false);
    }
  };

  const ver = resume?.active_version;
  const status = ver?.parsing_status || "UPLOADED";

  const steps = [
    { name: "File Upload & Signature Verification", completed: true },
    {
      name: "Text Extraction & Section Segmentation",
      completed: ["REVIEW_REQUIRED", "COMPLETED", "PARSED"].includes(status),
      active: status === "PROCESSING" || parsing,
      failed: status === "FAILED"
    },
    {
      name: "Structured Fact & Evidence Extraction",
      completed: ["REVIEW_REQUIRED", "COMPLETED"].includes(status),
      active: status === "PROCESSING" || parsing,
      failed: status === "FAILED"
    },
    {
      name: "Candidate Review & Profile Sync",
      completed: status === "COMPLETED",
      active: status === "REVIEW_REQUIRED"
    }
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
      <div className="mb-8">
        <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-2">
          ← Back to Resumes
        </Link>
        <h1 className="text-2xl font-bold text-slate-100">Document Parsing Lifecycle</h1>
        <p className="mt-1 text-sm text-slate-400">
          Tracking private text parsing, section classification, and evidence extraction for{" "}
          <span className="text-slate-200 font-medium">{resume?.title || "your resume"}</span>.
        </p>
      </div>

      <ResumeSubNav resumeId={resumeId} />

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="py-16 text-center text-slate-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
          Checking status...
        </div>
      ) : (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-8 shadow-sm">
          {/* Metadata Card */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-slate-800 gap-4">
            <div>
              <p className="text-xs text-slate-400 uppercase tracking-wider">Active Version</p>
              <h2 className="text-lg font-semibold text-slate-100 mt-0.5">
                {ver?.version_label || "v1"} ({ver?.original_filename})
              </h2>
            </div>
            <div className="text-left sm:text-right">
              <p className="text-xs text-slate-400 uppercase tracking-wider">Status</p>
              <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-semibold ${
                status === "COMPLETED"
                  ? "bg-emerald-900/60 text-emerald-300 border border-emerald-700"
                  : status === "REVIEW_REQUIRED"
                  ? "bg-amber-900/60 text-amber-300 border border-amber-700"
                  : status === "FAILED"
                  ? "bg-rose-900/60 text-rose-300 border border-rose-700"
                  : "bg-blue-900/60 text-blue-300 border border-blue-700"
              }`}>
                {status}
              </span>
            </div>
          </div>

          {/* Stepper */}
          <div className="py-8">
            <h3 className="text-sm font-semibold text-slate-300 mb-6 uppercase tracking-wider">Pipeline Progress</h3>
            <div className="space-y-4">
              {steps.map((step, idx) => (
                <div key={idx} className="flex items-center space-x-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    step.completed
                      ? "bg-emerald-600 text-white"
                      : step.failed
                      ? "bg-rose-600 text-white"
                      : step.active
                      ? "bg-indigo-600 text-white animate-pulse"
                      : "bg-slate-800 text-slate-400 border border-slate-700"
                  }`}>
                    {step.completed ? "✓" : step.failed ? "✕" : idx + 1}
                  </div>
                  <div>
                    <p className={`text-sm font-medium ${step.completed || step.active ? "text-slate-100" : "text-slate-400"}`}>
                      {step.name}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Action Footer */}
          <div className="pt-6 border-t border-slate-800 flex flex-wrap justify-between items-center gap-4">
            <p className="text-xs text-slate-400">
              {status === "UPLOADED" && "Document is ready to be parsed."}
              {status === "PROCESSING" && "Document parser is reading sections and extracting facts..."}
              {status === "REVIEW_REQUIRED" && "Document parsed successfully! Review the extracted facts before syncing."}
              {status === "COMPLETED" && "All confirmed facts have been synchronized to your candidate profile."}
              {status === "FAILED" && (ver?.error_message || "An error occurred during extraction.")}
            </p>

            <div className="flex space-x-3">
              {status === "UPLOADED" && (
                <button
                  onClick={handleStartParsing}
                  disabled={parsing}
                  className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white text-sm font-medium transition-colors flex items-center"
                >
                  {parsing ? "Parsing Pipeline Active..." : "Run Document Parsing Pipeline"}
                </button>
              )}

              {status === "FAILED" && (
                <button
                  onClick={handleStartParsing}
                  disabled={parsing}
                  className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium transition-colors"
                >
                  Retry Parsing
                </button>
              )}

              {(status === "REVIEW_REQUIRED" || status === "COMPLETED") && (
                <Link
                  href={`/resumes/${resumeId}/review`}
                  className="px-5 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium transition-colors"
                >
                  Open Review Workbench →
                </Link>
              )}

              <Link
                href={`/resumes/${resumeId}/analysis`}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition-colors"
              >
                View Extraction
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

