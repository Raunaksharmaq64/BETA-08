"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface SavedJob {
  id: string;
  user_id: string;
  opportunity_id: string;
  notes?: string;
  created_at: string;
  opportunity?: {
    id: string;
    title: string;
    company_name: string;
    city?: string;
    country?: string;
    workplace_type: string;
    is_remote: boolean;
    verification_status: string;
    freshness_state: string;
    application_url: string;
    min_salary?: number;
    max_salary?: number;
    currency?: string;
  };
}

export default function SavedJobsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingNotesId, setEditingNotesId] = useState<string | null>(null);
  const [tempNotes, setTempNotes] = useState("");

  const fetchSavedJobs = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient<SavedJob[]>("/saved-jobs");
      setSavedJobs(res.data || []);
    } catch (err: any) {
      console.error("Failed to load saved jobs:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      fetchSavedJobs();
    }
  }, [user, authLoading]);

  const handleUnsave = async (opportunityId: string) => {
    if (!confirm("Are you sure you want to remove this job from your saved list?")) return;
    try {
      await apiClient(`/saved-jobs/${opportunityId}`, { method: "DELETE" });
      setSavedJobs((prev) => prev.filter((s) => s.opportunity_id !== opportunityId));
    } catch (err: any) {
      alert("Failed to unsave job: " + err.message);
    }
  };

  const handleStartEditNote = (saved: SavedJob) => {
    setEditingNotesId(saved.id);
    setTempNotes(saved.notes || "");
  };

  const handleSaveNote = async (savedJobId: string) => {
    try {
      await apiClient(`/saved-jobs/${savedJobId}`, {
        method: "PATCH",
        body: JSON.stringify({ notes: tempNotes }),
      });
      setSavedJobs((prev) =>
        prev.map((s) => (s.id === savedJobId ? { ...s, notes: tempNotes } : s))
      );
      setEditingNotesId(null);
    } catch (err: any) {
      alert("Failed to update note: " + err.message);
    }
  };

  if (authLoading || isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-800 rounded w-1/4" />
          <div className="h-32 bg-slate-900 rounded-2xl border border-slate-800" />
          <div className="h-32 bg-slate-900 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Saved Jobs</h1>
          <p className="text-sm text-slate-400 mt-1">
            Track opportunities you have bookmarked, review status updates, and keep application notes.
          </p>
        </div>
        <Link
          href="/search"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-colors"
        >
          Find More Jobs →
        </Link>
      </div>

      {/* Saved Jobs List */}
      {savedJobs.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800 space-y-3">
          <div className="text-4xl">🔖</div>
          <h3 className="text-base font-semibold text-white">No saved jobs yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Browse verified job postings in Job Discovery and click the bookmark icon to save opportunities here.
          </p>
          <div className="pt-2">
            <Link
              href="/search"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold inline-block"
            >
              Start Searching Jobs
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {savedJobs.map((saved) => {
            const opp = saved.opportunity;
            const isEditing = editingNotesId === saved.id;

            return (
              <div
                key={saved.id}
                className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link
                        href={`/jobs/${saved.opportunity_id}`}
                        className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                      >
                        {opp ? opp.title : `Opportunity ${saved.opportunity_id.slice(0, 8)}`}
                      </Link>
                      {opp?.is_remote && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                          Remote
                        </span>
                      )}
                    </div>
                    {opp && (
                      <div className="text-xs text-slate-400 flex flex-wrap items-center gap-2">
                        <span className="font-semibold text-slate-300">{opp.company_name}</span>
                        <span>•</span>
                        <span>{opp.city ? `${opp.city}, ${opp.country || ""}` : opp.country || "Worldwide"}</span>
                        <span>•</span>
                        <span>Saved on {new Date(saved.created_at).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {opp?.application_url && (
                      <a
                        href={opp.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 rounded-lg transition-colors"
                      >
                        Apply ↗
                      </a>
                    )}
                    <button
                      onClick={() => handleUnsave(saved.opportunity_id)}
                      className="px-3 py-1.5 bg-rose-950/40 hover:bg-rose-900/40 text-xs font-semibold text-rose-300 border border-rose-800/60 rounded-lg transition-colors"
                    >
                      Remove
                    </button>
                  </div>
                </div>

                {/* Status Badges */}
                {opp && (
                  <div className="flex items-center gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 font-medium">
                      ✓ {opp.verification_status}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-800/60 text-cyan-300 font-medium">
                      Freshness: {opp.freshness_state}
                    </span>
                  </div>
                )}

                {/* Personal Notes Section */}
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between text-slate-400">
                    <span className="font-semibold text-slate-300">Application Notes:</span>
                    {!isEditing && (
                      <button
                        onClick={() => handleStartEditNote(saved)}
                        className="text-indigo-400 hover:text-indigo-300 font-medium underline"
                      >
                        {saved.notes ? "Edit Note" : "+ Add Note"}
                      </button>
                    )}
                  </div>

                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        rows={2}
                        value={tempNotes}
                        onChange={(e) => setTempNotes(e.target.value)}
                        placeholder="e.g. Applied on Oct 30, recruiter screening scheduled..."
                        className="w-full p-2.5 bg-slate-900 rounded-lg border border-slate-700 text-slate-200 focus:outline-none focus:border-indigo-500"
                      />
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => setEditingNotesId(null)}
                          className="px-2.5 py-1 bg-slate-800 text-slate-400 rounded hover:text-white"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleSaveNote(saved.id)}
                          className="px-3 py-1 bg-indigo-600 text-white rounded font-medium hover:bg-indigo-500"
                        >
                          Save
                        </button>
                      </div>
                    </div>
                  ) : (
                    <p className="text-slate-400 italic">
                      {saved.notes || "No notes added yet. Keep track of referral contacts or interview stages here."}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

