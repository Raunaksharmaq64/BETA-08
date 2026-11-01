"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface StatusHistoryItem {
  id: string;
  from_status?: string;
  to_status: string;
  changed_at: string;
  reason?: string;
  changed_by: string;
}

interface NoteItem {
  id: string;
  content: string;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

interface ApplicationDetail {
  id: string;
  user_id: string;
  opportunity_id?: string;
  custom_company_name?: string;
  custom_job_title?: string;
  application_url?: string;
  status: string;
  applied_at?: string;
  apply_link_opened_at?: string;
  submission_confirmed: boolean;
  next_action_due_at?: string;
  next_interview_at?: string;
  rejection_reason?: string;
  offer_amount?: number;
  offer_currency?: string;
  offer_deadline?: string;
  created_at: string;
  updated_at: string;
  company_display: string;
  title_display: string;
  workplace_type?: string;
  city?: string;
  status_history?: StatusHistoryItem[];
  notes?: NoteItem[];
  recent_notes?: NoteItem[];
}

const VALID_STATUSES = [
  "SAVED",
  "PLANNING_TO_APPLY",
  "APPLIED",
  "ASSESSMENT",
  "INTERVIEW",
  "OFFER",
  "REJECTED",
  "WITHDRAWN",
  "GHOSTED",
  "CLOSED",
];

export default function ApplicationDetailPage() {
  const router = useRouter();
  const params = useParams();
  const applicationId = params?.applicationId as string;
  const { user, loading: authLoading } = useAuth();

  const [application, setApplication] = useState<ApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  // Transition state
  const [targetStatus, setTargetStatus] = useState("");
  const [transitionReason, setTransitionReason] = useState("");
  const [isConfirmApplyModalOpen, setIsConfirmApplyModalOpen] = useState(false);
  const [transitioning, setTransitioning] = useState(false);

  // Add Note state
  const [noteContent, setNoteContent] = useState("");
  const [isPinned, setIsPinned] = useState(false);
  const [addingNote, setAddingNote] = useState(false);

  const normalizeApp = (raw: any): ApplicationDetail => {
    if (!raw) return raw;
    const rawNotes = raw.notes || raw.recent_notes || [];
    const rawHistory = raw.status_history || [];
    return {
      ...raw,
      company_display: raw.company_display || raw.company_name || raw.custom_company_name || "Company",
      title_display: raw.title_display || raw.job_title || raw.custom_job_title || "Job Application",
      notes: Array.isArray(rawNotes) ? rawNotes : [],
      status_history: Array.isArray(rawHistory) ? rawHistory : [],
    };
  };

  const fetchApplication = async () => {
    if (!applicationId) return;
    setLoading(true);
    try {
      const res = await apiClient<any>(`/applications/${applicationId}`);
      if (res.data) {
        const norm = normalizeApp(res.data);
        setApplication(norm);
        setTargetStatus(norm.status);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to load application details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user && applicationId) {
      fetchApplication();
    }
  }, [user, authLoading, applicationId]);

  const handleOpenApplyLink = async () => {
    if (!application?.application_url) return;
    const comp = application.company_display || application.custom_company_name || "Company";

    const title = application.title_display || application.custom_job_title || "Job";

    const safeUrl = application.application_url.toLowerCase().includes("jooble.org")

      ? `https://www.google.com/search?q=${encodeURIComponent(`${comp} ${title} job apply`)}`

      : application.application_url;
    try {
      // Notify backend to track opening timestamp
      const res = await apiClient<ApplicationDetail>(
        `/applications/${applicationId}/open-apply-link`,
        { method: "POST" }
      );
      setApplication(normalizeApp(res.data));
      // Open link in new tab
      window.open(safeUrl, "_blank", "noopener,noreferrer");
    } catch (err) {
      console.error("Failed to track apply link opening:", err);
      window.open(safeUrl, "_blank", "noopener,noreferrer");
    }
  };

  const handleExecuteTransition = async (confirmSubmission: boolean = false) => {
    if (!targetStatus || targetStatus === application?.status) return;
    setTransitioning(true);
    try {
      const res = await apiClient<ApplicationDetail>(
        `/applications/${applicationId}/status`,
        {
          method: "PATCH",
          body: JSON.stringify({
            status: targetStatus,
            reason: transitionReason || undefined,
            confirm_submission: confirmSubmission,
          }),
        }
      );
      setApplication(normalizeApp(res.data));
      setIsConfirmApplyModalOpen(false);
      setTransitionReason("");
    } catch (err: any) {
      alert(err.message || "Invalid state transition.");
      if (application) setTargetStatus(application.status);
    } finally {
      setTransitioning(false);
    }
  };

  const onStatusSelectChange = (newStatus: string) => {
    setTargetStatus(newStatus);
    if (newStatus === "APPLIED") {
      setIsConfirmApplyModalOpen(true);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteContent.trim()) return;
    setAddingNote(true);
    try {
      await apiClient(`/applications/${applicationId}/notes`, {
        method: "POST",
        body: JSON.stringify({
          content: noteContent.trim(),
          is_pinned: isPinned,
        }),
      });
      setNoteContent("");
      setIsPinned(false);
      fetchApplication();
    } catch (err: any) {
      alert(err.message || "Failed to add note.");
    } finally {
      setAddingNote(false);
    }
  };

  const handleDeleteNote = async (noteId: string) => {
    if (!confirm("Are you sure you want to delete this note?")) return;
    try {
      await apiClient(`/applications/${applicationId}/notes/${noteId}`, {
        method: "DELETE",
      });
      fetchApplication();
    } catch (err: any) {
      alert(err.message || "Failed to delete note.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center text-slate-400">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
        <p>Loading application...</p>
      </div>
    );
  }

  if (errorMsg || !application) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <div className="bg-rose-950/60 border border-rose-800 text-rose-300 p-6 rounded-2xl">
          <h2 className="text-xl font-bold">Application Not Found</h2>
          <p className="text-sm mt-2">{errorMsg || "The requested application does not exist."}</p>
          <Link
            href="/applications"
            className="inline-block mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm"
          >
            &larr; Back to Applications
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back button & Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/applications"
          className="text-sm font-medium text-slate-400 hover:text-white flex items-center gap-1 transition"
        >
          &larr; Back to Applications
        </Link>
        <div className="flex items-center space-x-2">
          <Link
            href={`/interview-prep?appId=${application.id}`}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-950/80 hover:bg-indigo-900 text-indigo-300 border border-indigo-700/60 transition"
          >
            🎯 Interview Prep for this role
          </Link>
        </div>
      </div>

      {/* Hero Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-indigo-950 border border-indigo-800 text-indigo-300 uppercase tracking-wide">
                {application.status.replace(/_/g, " ")}
              </span>
              {application.workplace_type && (
                <span className="text-xs text-slate-400">
                  {application.workplace_type} {application.city ? `• ${application.city}` : ""}
                </span>
              )}
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-2">
              {application.title_display}
            </h1>
            <p className="text-slate-400 text-base font-medium">{application.company_display}</p>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap items-center gap-3">
            {application.application_url && (
              <button
                onClick={handleOpenApplyLink}
                className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow transition flex items-center gap-2"
                title="Opens apply portal and tracks click in audit trail"
              >
                <span>🔗 Open Application Link</span>
              </button>
            )}
          </div>
        </div>

        {/* Timestamps and State Indicators */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-slate-800 text-xs">
          <div>
            <span className="text-slate-500">Tracked Since:</span>
            <div className="text-slate-300 font-medium">
              {new Date(application.created_at).toLocaleDateString()}
            </div>
          </div>
          <div>
            <span className="text-slate-500">Apply Link Opened:</span>
            <div className="text-slate-300 font-medium">
              {application.apply_link_opened_at
                ? new Date(application.apply_link_opened_at).toLocaleString()
                : "Not opened yet"}
            </div>
          </div>
          <div>
            <span className="text-slate-500">Submission Confirmed:</span>
            <div
              className={`font-semibold ${
                application.submission_confirmed ? "text-emerald-400" : "text-amber-400"
              }`}
            >
              {application.submission_confirmed ? "Confirmed Yes" : "No (Manual confirm required)"}
            </div>
          </div>
          <div>
            <span className="text-slate-500">Applied At:</span>
            <div className="text-slate-300 font-medium">
              {application.applied_at
                ? new Date(application.applied_at).toLocaleDateString()
                : "Not submitted"}
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Status Transition & Audit Trail (Left 7) + Notes (Right 5) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-7 space-y-6">
          {/* Transition Box */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>⚡ Update Status Machine</span>
            </h2>
            <p className="text-xs text-slate-400">
              State transitions are governed by auditable rules. Every transition requires reason or
              confirmation.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Change To Status:
                </label>
                <select
                  value={targetStatus}
                  onChange={(e) => onStatusSelectChange(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {VALID_STATUSES.map((st) => (
                    <option key={st} value={st}>
                      {st.replace(/_/g, " ")} {st === application.status ? "(Current)" : ""}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">
                  Reason / Context (Optional):
                </label>
                <input
                  type="text"
                  placeholder="e.g. Recruiter scheduled round 1"
                  value={transitionReason}
                  onChange={(e) => setTransitionReason(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {targetStatus !== application.status && targetStatus !== "APPLIED" && (
              <div className="flex justify-end pt-2">
                <button
                  onClick={() => handleExecuteTransition(false)}
                  disabled={transitioning}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
                >
                  {transitioning ? "Updating..." : `Confirm Transition to ${targetStatus}`}
                </button>
              </div>
            )}
          </div>

          {/* Status History Audit Trail */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white">Auditable State History</h2>
            <div className="relative border-l border-slate-800 pl-4 space-y-4 ml-2">
              {(application.status_history || []).length === 0 ? (
                <div className="text-xs text-slate-500 py-2">No status history recorded yet.</div>
              ) : (
                (application.status_history || []).map((hist) => (
                <div key={hist.id} className="relative">
                  <div className="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-indigo-500 ring-4 ring-slate-900" />
                  <div className="text-xs">
                    <div className="font-semibold text-slate-200">
                      {hist.from_status ? `${hist.from_status} → ` : ""}
                      <span className="text-indigo-400">{hist.to_status}</span>
                    </div>
                    <div className="text-slate-500 mt-0.5">
                      {new Date(hist.changed_at).toLocaleString()} • by {hist.changed_by}
                    </div>
                    {hist.reason && (
                      <p className="text-slate-400 mt-1 italic bg-slate-950/60 p-2 rounded border border-slate-800/80">
                        &quot;{hist.reason}&quot;
                      </p>
                    )}
                  </div>
                </div>
              )))
              }
            </div>
          </div>
        </div>

        {/* Right Column: Private Notes */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center justify-between">
              <span>Candidate Private Notes</span>
              <span className="text-xs text-slate-500 font-normal">Encrypted & Candidate-Only</span>
            </h2>

            {/* Add note form */}
            <form onSubmit={handleAddNote} className="space-y-3">
              <textarea
                rows={3}
                required
                placeholder="Log recruiter names, salary expectations, interview takeaways..."
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />
              <div className="flex justify-between items-center">
                <label className="flex items-center space-x-2 text-xs text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={isPinned}
                    onChange={(e) => setIsPinned(e.target.checked)}
                    className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0"
                  />
                  <span>Pin to top</span>
                </label>
                <button
                  type="submit"
                  disabled={addingNote || !noteContent.trim()}
                  className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
                >
                  {addingNote ? "Saving..." : "Add Note"}
                </button>
              </div>
            </form>

            {/* Notes List */}
            <div className="space-y-3 pt-2">
              {(application.notes || []).length === 0 ? (
                <div className="text-center py-6 text-xs text-slate-500">
                  No notes recorded yet. Keep personal reminders and research here.
                </div>
              ) : (
                (application.notes || [])
                  .slice()
                  .sort((a, b) => (b.is_pinned ? 1 : 0) - (a.is_pinned ? 1 : 0))
                  .map((note) => (
                    <div
                      key={note.id}
                      className={`p-3 rounded-lg border text-xs space-y-2 transition ${
                        note.is_pinned
                          ? "bg-indigo-950/20 border-indigo-800/60"
                          : "bg-slate-950/80 border-slate-800"
                      }`}
                    >
                      <div className="flex justify-between items-start text-slate-400">
                        <span className="text-[10px]">
                          {note.is_pinned && <span className="text-indigo-400 mr-1">📌 PINNED</span>}
                          {new Date(note.created_at).toLocaleString()}
                        </span>
                        <button
                          onClick={() => handleDeleteNote(note.id)}
                          className="text-slate-500 hover:text-rose-400 text-xs"
                          title="Delete note"
                        >
                          ✕
                        </button>
                      </div>
                      <p className="text-slate-200 whitespace-pre-wrap">{note.content}</p>
                    </div>
                  ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for APPLIED state */}
      {isConfirmApplyModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white">Confirm Application Submission</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Right Fit strictly distinguishes between browsing or opening an external apply link
              and <strong>actual candidate submission</strong>.
            </p>
            <div className="p-3 bg-indigo-950/40 border border-indigo-800/60 rounded-xl text-xs text-indigo-300">
              Did you complete and submit your application on the employer&apos;s portal?
            </div>
            <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => {
                  setIsConfirmApplyModalOpen(false);
                  setTargetStatus(application.status);
                }}
                className="px-4 py-2 text-xs text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleExecuteTransition(true)}
                disabled={transitioning}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow"
              >
                {transitioning ? "Saving..." : "Yes, I Confirmed My Submission"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

