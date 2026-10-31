"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface DebriefItem {
  id: string;
  user_id: string;
  application_id?: string;
  round_id?: string;
  self_rating: number;
  outcome_feeling: string;
  questions_asked: string[];
  what_went_well?: string;
  what_could_improve?: string;
  interviewer_promises?: string;
  action_items: string[];
  created_at: string;
}

export default function InterviewDebriefPage() {
  const { user } = useAuth();

  const [debriefs, setDebriefs] = useState<DebriefItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [selfRating, setSelfRating] = useState(4);
  const [outcomeFeeling, setOutcomeFeeling] = useState("POSITIVE");
  const [questionsInput, setQuestionsInput] = useState("");
  const [whatWentWell, setWhatWentWell] = useState("");
  const [whatCouldImprove, setWhatCouldImprove] = useState("");
  const [interviewerPromises, setInterviewerPromises] = useState("");
  const [actionItemsInput, setActionItemsInput] = useState("");
  const [saving, setSaving] = useState(false);

  const fetchDebriefs = async () => {
    setLoading(true);
    try {
      const res = await apiClient<DebriefItem[]>("/interview-prep/debriefs");
      setDebriefs(res.data || []);
    } catch (err: any) {
      console.error("Failed to load debriefs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchDebriefs();
    }
  }, [user]);

  const handleSubmitDebrief = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const questionsList = questionsInput
        .split("\n")
        .map((q) => q.trim())
        .filter(Boolean);
      const actionsList = actionItemsInput
        .split("\n")
        .map((a) => a.trim())
        .filter(Boolean);

      await apiClient("/interview-prep/debriefs", {
        method: "POST",
        body: JSON.stringify({
          self_rating: selfRating,
          outcome_feeling: outcomeFeeling,
          questions_asked: questionsList,
          what_went_well: whatWentWell.trim() || undefined,
          what_could_improve: whatCouldImprove.trim() || undefined,
          interviewer_promises: interviewerPromises.trim() || undefined,
          action_items: actionsList,
        }),
      });

      setQuestionsInput("");
      setWhatWentWell("");
      setWhatCouldImprove("");
      setInterviewerPromises("");
      setActionItemsInput("");
      fetchDebriefs();
    } catch (err: any) {
      alert(err.message || "Failed to save debrief.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <Link
              href="/interview-prep"
              className="text-xs font-semibold text-slate-400 hover:text-white"
            >
              &larr; Interview Prep Hub
            </Link>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1 flex items-center gap-2">
            <span>📝 Post-Interview Debrief & Promises</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Capture immediate impressions, questions asked, and recruiter promises right after each
            round.
          </p>
        </div>
      </div>

      {/* Main Grid: Form (Left 7) + History (Right 5) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Debrief Form */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <h2 className="text-lg font-bold text-white">Log Round Debrief</h2>

          <form onSubmit={handleSubmitDebrief} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Self-Rating (1-5)
                </label>
                <div className="flex items-center space-x-2">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      type="button"
                      key={star}
                      onClick={() => setSelfRating(star)}
                      className={`text-lg p-1 transition ${
                        star <= selfRating ? "text-amber-400" : "text-slate-600"
                      }`}
                    >
                      ★
                    </button>
                  ))}
                  <span className="text-xs text-slate-400 ml-2">({selfRating}/5)</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Overall Impression
                </label>
                <select
                  value={outcomeFeeling}
                  onChange={(e) => setOutcomeFeeling(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="POSITIVE">Positive (Strong connection & answers)</option>
                  <option value="NEUTRAL">Neutral (Solid, but uncertain)</option>
                  <option value="CONCERNED">Concerned (Fumbled or misaligned)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Questions Asked by Interviewers (One per line)
              </label>
              <textarea
                rows={3}
                placeholder="e.g. Design a distributed cache with TTL&#10;How did you resolve a disagreement with product manager?"
                value={questionsInput}
                onChange={(e) => setQuestionsInput(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  What Went Well
                </label>
                <textarea
                  rows={2}
                  placeholder="System design diagram was praised, good rapport..."
                  value={whatWentWell}
                  onChange={(e) => setWhatWentWell(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  What Could Improve
                </label>
                <textarea
                  rows={2}
                  placeholder="Hesitated on cache invalidation subtleties..."
                  value={whatCouldImprove}
                  onChange={(e) => setWhatCouldImprove(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Recruiter / Company Promises Logged
              </label>
              <input
                type="text"
                placeholder="e.g. Recruiter promised decision by Thursday 5pm, team works hybrid 2 days"
                value={interviewerPromises}
                onChange={(e) => setInterviewerPromises(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Immediate Action Items (One per line)
              </label>
              <textarea
                rows={2}
                placeholder="e.g. Send thank-you note by tomorrow morning&#10;Review consensus algorithms"
                value={actionItemsInput}
                onChange={(e) => setActionItemsInput(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-800">
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2.5 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
              >
                {saving ? "Saving Debrief..." : "Save Interview Debrief"}
              </button>
            </div>
          </form>
        </div>

        {/* History List */}
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center justify-between">
            <span>Debrief History ({debriefs.length})</span>
          </h2>

          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent mb-2" />
              <p className="text-xs">Loading debriefs...</p>
            </div>
          ) : debriefs.length === 0 ? (
            <div className="p-8 text-center bg-slate-900 border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
              No interview debriefs recorded yet. Complete one after your next round.
            </div>
          ) : (
            <div className="space-y-4">
              {debriefs.map((deb) => (
                <div
                  key={deb.id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-amber-400 font-bold text-sm">
                        {"★".repeat(deb.self_rating)}
                        {"☆".repeat(5 - deb.self_rating)}
                      </span>
                      <span className="ml-2 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wide bg-slate-800 text-slate-300">
                        {deb.outcome_feeling}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-500">
                      {new Date(deb.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {deb.questions_asked && deb.questions_asked.length > 0 && (
                    <div className="space-y-1 text-xs">
                      <span className="text-slate-400 font-semibold text-[11px]">
                        Questions Asked:
                      </span>
                      <ul className="list-disc list-inside text-slate-300 text-[11px] space-y-0.5">
                        {deb.questions_asked.map((q, qIdx) => (
                          <li key={qIdx}>{q}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {deb.interviewer_promises && (
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-[11px] text-indigo-300">
                      <strong>Promises:</strong> {deb.interviewer_promises}
                    </div>
                  )}

                  {deb.action_items && deb.action_items.length > 0 && (
                    <div className="text-[11px] text-slate-400">
                      <strong>Action Items:</strong> {deb.action_items.join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

