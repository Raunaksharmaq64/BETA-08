"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "../../../../../services/apiClient";

export default function ResumeReviewPage() {
  const params = useParams();
  const router = useRouter();
  const resumeId = params?.resumeId as string;

  const [review, setReview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [overwriteConflicts, setOverwriteConflicts] = useState(false);
  const [editingFieldId, setEditingFieldId] = useState<string | null>(null);
  const [correctedValue, setCorrectedValue] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const fetchReview = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get<any>(`/api/v1/resumes/${resumeId}/review`);
      if (res.success && res.data) {
        setReview(res.data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load review workbench.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (resumeId) {
      fetchReview();
    }
  }, [resumeId]);

  const handleFieldAction = async (fieldId: string, action: string, value?: any) => {
    try {
      setSubmitting(true);
      const res = await apiClient.patch<any>(`/api/v1/resumes/${resumeId}/review`, {
        field_id: fieldId,
        action,
        corrected_value: value
      });
      if (res.success && res.data) {
        setReview(res.data);
        setEditingFieldId(null);
      }
    } catch (err: any) {
      alert("Action failed: " + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSyncToProfile = async () => {
    try {
      setSyncing(true);
      setError(null);
      setSuccessMsg(null);
      const res = await apiClient.post<any>(`/api/v1/resumes/${resumeId}/confirm`, {
        overwrite_conflicts: overwriteConflicts
      });
      if (res.success && res.data) {
        setSuccessMsg(res.data.message || "Candidate profile synchronized successfully!");
        fetchReview();
      }
    } catch (err: any) {
      setError(err.message || "Failed to synchronize profile.");
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 mb-8 border-b border-slate-800 gap-4">
        <div>
          <Link href="/resumes" className="text-xs font-medium text-indigo-400 hover:text-indigo-300 flex items-center mb-1">
            ← Back to Resumes
          </Link>
          <h1 className="text-2xl font-bold text-slate-100">Review & Verification Workbench</h1>
          <p className="mt-1 text-sm text-slate-400">
            Inspect extracted candidate facts, correct errors, and explicitly synchronize verified data to your profile.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href={`/resumes/${resumeId}/analysis`}
            className="px-3.5 py-1.5 rounded-lg border border-slate-700 text-xs font-medium text-slate-300 hover:bg-slate-800 transition-colors"
          >
            View Structured Analysis
          </Link>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-rose-900/40 border border-rose-700 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="mb-6 p-4 rounded-lg bg-emerald-900/40 border border-emerald-700 text-emerald-300 text-sm">
          {successMsg}
          <div className="mt-2">
            <Link href="/profile" className="text-emerald-200 underline font-semibold">
              View Updated Candidate Profile →
            </Link>
          </div>
        </div>
      )}

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto mb-3"></div>
          Loading review workbench...
        </div>
      ) : review ? (
        <div className="space-y-8">
          {/* Metrics Card */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-xs text-slate-400 font-medium">Pending Review</p>
              <p className="text-2xl font-bold text-amber-400 mt-1">{review.pending_fields_count}</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-xs text-slate-400 font-medium">Confirmed</p>
              <p className="text-2xl font-bold text-emerald-400 mt-1">{review.confirmed_fields_count}</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-xs text-slate-400 font-medium">Rejected</p>
              <p className="text-2xl font-bold text-rose-400 mt-1">{review.rejected_fields_count}</p>
            </div>
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-xs text-slate-400 font-medium">Profile Conflicts</p>
              <p className="text-2xl font-bold text-indigo-400 mt-1">{review.conflicts_with_profile?.length || 0}</p>
            </div>
          </div>

          {/* Profile Conflicts Warning Card */}
          {review.conflicts_with_profile?.length > 0 && (
            <div className="bg-amber-950/30 border border-amber-800/80 rounded-xl p-6">
              <div className="flex items-start space-x-3">
                <span className="text-amber-400 text-lg">⚠️</span>
                <div>
                  <h2 className="text-sm font-semibold text-amber-200">
                    Existing Profile Differences Detected ({review.conflicts_with_profile.length})
                  </h2>
                  <p className="text-xs text-amber-300/80 mt-1">
                    Some information in your resume differs from facts already present on your profile.
                    To prevent accidental overwrites, existing profile facts are preserved unless you explicitly enable conflict overwrite.
                  </p>

                  <div className="mt-4 space-y-2">
                    {review.conflicts_with_profile.map((c: any, cIdx: number) => (
                      <div key={cIdx} className="p-3 bg-slate-900/80 rounded-lg text-xs grid grid-cols-1 sm:grid-cols-2 gap-2 border border-slate-800">
                        <div>
                          <span className="text-slate-400 font-medium uppercase tracking-wider text-[10px]">
                            {c.field_name} (Current Profile):
                          </span>
                          <p className="text-slate-200 mt-0.5">{c.current_profile_value}</p>
                        </div>
                        <div>
                          <span className="text-indigo-400 font-medium uppercase tracking-wider text-[10px]">
                            {c.field_name} (From Resume):
                          </span>
                          <p className="text-slate-200 mt-0.5">{c.extracted_value}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Evidence Items Review List */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-slate-200 mb-6 pb-2 border-b border-slate-800">
              Extracted Facts Awaiting Candidate Review
            </h2>

            <div className="space-y-4">
              {review.evidence_items?.map((ev: any) => {
                const isEditing = editingFieldId === ev.field_id;
                return (
                  <div
                    key={ev.field_id}
                    className={`p-4 rounded-xl border transition-colors ${
                      ev.review_status === "CONFIRMED"
                        ? "bg-emerald-950/10 border-emerald-900/60"
                        : ev.review_status === "REJECTED"
                        ? "bg-rose-950/10 border-rose-900/60 opacity-60"
                        : "bg-slate-800/40 border-slate-700/80"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-semibold text-indigo-400">{ev.field_name}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            ev.review_status === "CONFIRMED"
                              ? "bg-emerald-900 text-emerald-200"
                              : ev.review_status === "REJECTED"
                              ? "bg-rose-900 text-rose-200"
                              : "bg-amber-900 text-amber-200"
                          }`}>
                            {ev.review_status}
                          </span>
                        </div>

                        {isEditing ? (
                          <div className="mt-2 flex items-center space-x-2">
                            <input
                              type="text"
                              value={correctedValue}
                              onChange={(e) => setCorrectedValue(e.target.value)}
                              className="px-3 py-1.5 rounded bg-slate-900 border border-slate-700 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                              placeholder="Enter corrected value"
                            />
                            <button
                              onClick={() => handleFieldAction(ev.field_id, "EDIT_AND_CONFIRM", correctedValue)}
                              disabled={submitting}
                              className="px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white"
                            >
                              Save & Confirm
                            </button>
                            <button
                              onClick={() => setEditingFieldId(null)}
                              className="px-3 py-1.5 rounded border border-slate-700 text-xs text-slate-400 hover:text-slate-200"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <p className="text-sm font-semibold text-slate-100 mt-1">
                            {ev.user_correction ? (
                              <span>
                                {ev.user_correction}{" "}
                                <span className="text-xs text-slate-400 font-normal line-through">({String(ev.extracted_value)})</span>
                              </span>
                            ) : (
                              String(ev.extracted_value)
                            )}
                          </p>
                        )}

                        <p className="text-xs text-slate-400 mt-1">
                          Source: <span className="text-slate-300">{ev.source_section || "Document"}</span> (Page {ev.page_number || 1}) • &ldquo;{ev.excerpt}&rdquo;
                        </p>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleFieldAction(ev.field_id, "CONFIRM")}
                          disabled={submitting || ev.review_status === "CONFIRMED"}
                          className="px-3 py-1.5 rounded-lg bg-emerald-700/80 hover:bg-emerald-600 disabled:opacity-40 text-xs font-semibold text-white transition-colors"
                        >
                          Confirm
                        </button>
                        <button
                          onClick={() => {
                            setEditingFieldId(ev.field_id);
                            setCorrectedValue(String(ev.extracted_value));
                          }}
                          disabled={submitting}
                          className="px-3 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-xs font-medium text-slate-200 transition-colors"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleFieldAction(ev.field_id, "REJECT")}
                          disabled={submitting || ev.review_status === "REJECTED"}
                          className="px-3 py-1.5 rounded-lg border border-slate-700 hover:border-rose-700 text-xs font-medium text-slate-400 hover:text-rose-300 transition-colors"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sync Action Footer */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">Synchronize to Profile</h3>
            <p className="text-xs text-slate-400 mb-4">
              Synchronizing will publish your confirmed education, experience, and skills into your official candidate profile.
            </p>

            <div className="flex items-center space-x-3 mb-6">
              <input
                type="checkbox"
                id="overwriteConflictsCheck"
                checked={overwriteConflicts}
                onChange={(e) => setOverwriteConflicts(e.target.checked)}
                className="w-4 h-4 rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-indigo-500"
              />
              <label htmlFor="overwriteConflictsCheck" className="text-xs text-slate-300">
                Overwrite existing candidate profile facts if conflicts exist (explicit consent required)
              </label>
            </div>

            <button
              onClick={handleSyncToProfile}
              disabled={syncing}
              className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-sm font-semibold text-white transition-colors flex items-center"
            >
              {syncing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Synchronizing Profile...
                </>
              ) : (
                "Synchronize Confirmed Facts to Profile →"
              )}
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}

