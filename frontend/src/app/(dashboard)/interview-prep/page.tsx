"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface InterviewRound {
  id: string;
  round_number: number;
  round_name: string;
  round_type: string;
  scheduled_at?: string;
  interviewer_names?: string;
  meeting_link?: string;
  status: string;
}

interface InterviewPlan {
  id: string;
  user_id: string;
  application_id?: string;
  target_role: string;
  target_company: string;
  target_date?: string;
  current_phase: string;
  rounds: InterviewRound[];
  created_at: string;
}

function InterviewPrepHubContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const appIdParam = searchParams.get("appId");
  const { user, loading: authLoading } = useAuth();

  const [plans, setPlans] = useState<InterviewPlan[]>([]);
  const [loading, setLoading] = useState(true);

  // New Plan Modal
  const [isNewPlanOpen, setIsNewPlanOpen] = useState(false);
  const [targetCompany, setTargetCompany] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [targetDate, setTargetDate] = useState("");
  const [creatingPlan, setCreatingPlan] = useState(false);

  // New Round Modal
  const [selectedPlanForRound, setSelectedPlanForRound] = useState<InterviewPlan | null>(null);
  const [roundName, setRoundName] = useState("");
  const [roundType, setRoundType] = useState("TECHNICAL");
  const [roundScheduledAt, setRoundScheduledAt] = useState("");
  const [roundMeetingLink, setRoundMeetingLink] = useState("");
  const [addingRound, setAddingRound] = useState(false);

  const fetchPlans = async () => {
    setLoading(true);
    try {
      const res = await apiClient<InterviewPlan[]>("/interview-prep/plans");
      setPlans(res.data || []);
    } catch (err: any) {
      console.error("Failed to load interview plans:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      fetchPlans();
    }
  }, [user, authLoading]);

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetCompany.trim() || !targetRole.trim()) return;
    setCreatingPlan(true);
    try {
      await apiClient("/interview-prep/plans", {
        method: "POST",
        body: JSON.stringify({
          target_company: targetCompany.trim(),
          target_role: targetRole.trim(),
          target_date: targetDate ? new Date(targetDate).toISOString() : undefined,
          application_id: appIdParam || undefined,
        }),
      });
      setIsNewPlanOpen(false);
      setTargetCompany("");
      setTargetRole("");
      setTargetDate("");
      fetchPlans();
    } catch (err: any) {
      alert(err.message || "Failed to create plan.");
    } finally {
      setCreatingPlan(false);
    }
  };

  const handleAddRound = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPlanForRound || !roundName.trim()) return;
    setAddingRound(true);
    try {
      const roundNumber = selectedPlanForRound.rounds.length + 1;
      await apiClient(`/interview-prep/plans/${selectedPlanForRound.id}/rounds`, {
        method: "POST",
        body: JSON.stringify({
          round_number: roundNumber,
          round_name: roundName.trim(),
          round_type: roundType,
          scheduled_at: roundScheduledAt ? new Date(roundScheduledAt).toISOString() : undefined,
          meeting_link: roundMeetingLink.trim() || undefined,
        }),
      });
      setSelectedPlanForRound(null);
      setRoundName("");
      setRoundScheduledAt("");
      setRoundMeetingLink("");
      fetchPlans();
    } catch (err: any) {
      alert(err.message || "Failed to add interview round.");
    } finally {
      setAddingRound(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-slate-900">
            Interview Intelligence Hub
          </h1>
          <p className="text-slate-700 font-semibold text-sm mt-1">
            End-to-end interview lifecycle: 48-Hour sprint preparation, evidence-grounded STAR
            stories, interactive mock sessions, and debriefs.
          </p>
        </div>
        <button
          onClick={() => setIsNewPlanOpen(true)}
          className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow transition"
        >
          + New Interview Plan
        </button>
      </div>

      {/* Quick Access Tools Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link
          href="/interview-prep/48-hour"
          className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 group transition-all duration-200 shadow-sm"
        >
          <div className="text-2xl mb-2">⚡</div>
          <h3 className="font-black text-slate-900 group-hover:text-amber-700 transition text-base">
            48-Hour Sprint Mode
          </h3>
          <p className="text-slate-400 text-xs mt-1 leading-relaxed">
            Time-boxed 4-block revision plan leading directly up to your scheduled interview round.
          </p>
        </Link>

        <Link
          href="/interview-prep/star"
          className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 group transition-all duration-200 shadow-sm"
        >
          <div className="text-2xl mb-2">⭐</div>
          <h3 className="font-black text-slate-900 group-hover:text-indigo-700 transition text-base">
            STAR Story Builder
          </h3>
          <p className="text-slate-400 text-xs mt-1 leading-relaxed">
            Craft high-impact behavioral answers strictly grounded in confirmed resume evidence.
          </p>
        </Link>

        <Link
          href="/interview-prep/mock"
          className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 group transition-all duration-200 shadow-sm"
        >
          <div className="text-2xl mb-2">🎙️</div>
          <h3 className="font-black text-slate-900 group-hover:text-emerald-700 transition text-base">
            Mock Practice & Rubric
          </h3>
          <p className="text-slate-400 text-xs mt-1 leading-relaxed">
            Practice realistic questions and get evaluated against a 6-factor transparent rubric.
          </p>
        </Link>

        <Link
          href="/interview-prep/debrief"
          className="neo-card neo-box-hover p-6 rounded-2xl border border-white/90 group transition-all duration-200 shadow-sm"
        >
          <div className="text-2xl mb-2">📝</div>
          <h3 className="font-black text-slate-900 group-hover:text-purple-700 transition text-base">
            Post-Interview Debrief
          </h3>
          <p className="text-slate-400 text-xs mt-1 leading-relaxed">
            Log interviewer questions, self-reflections, and promised follow-up timelines.
          </p>
        </Link>
      </div>

      {/* Active Interview Plans */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-white flex items-center justify-between">
          <span>Active Multi-Round Plans ({plans.length})</span>
        </h2>

        {loading ? (
          <div className="py-16 text-center text-slate-400">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
            <p className="text-sm">Loading interview plans...</p>
          </div>
        ) : plans.length === 0 ? (
          <div className="bg-slate-900/60 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
            <h3 className="text-base font-semibold text-slate-300">No active interview plans</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
              Create an interview plan for an upcoming application to organize rounds, sprint
              schedules, and STAR stories.
            </p>
            <button
              onClick={() => setIsNewPlanOpen(true)}
              className="mt-4 px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow"
            >
              + Create First Plan
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className="neo-card neo-box-hover rounded-2xl p-6 border border-white/90 shadow-sm transition-all duration-200 space-y-4"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 uppercase tracking-wide border border-indigo-800/80">
                      Phase: {plan.current_phase}
                    </span>
                    <h3 className="text-lg font-black text-slate-900 mt-1.5">{plan.target_role}</h3>
                    <p className="text-sm text-slate-400 font-medium">{plan.target_company}</p>
                  </div>
                  <Link
                    href={`/interview-prep/48-hour?planId=${plan.id}`}
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-950/80 hover:bg-amber-900/80 text-amber-300 border border-amber-700/60 transition"
                  >
                    ⚡ Sprint 48h
                  </Link>
                </div>

                {/* Rounds listing */}
                <div className="space-y-2 pt-2 border-t border-slate-800/60">
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span className="font-semibold text-slate-300">
                      Rounds ({plan.rounds.length})
                    </span>
                    <button
                      onClick={() => setSelectedPlanForRound(plan)}
                      className="text-indigo-400 hover:text-indigo-300 font-medium"
                    >
                      + Add Round
                    </button>
                  </div>

                  {plan.rounds.length === 0 ? (
                    <div className="text-xs text-slate-500 italic py-2">
                      No rounds scheduled yet. Click &quot;+ Add Round&quot; to log round details.
                    </div>
                  ) : (
                    <div className="space-y-1.5">
                      {plan.rounds.map((round) => (
                        <div
                          key={round.id}
                          className="flex justify-between items-center p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs"
                        >
                          <div>
                            <span className="font-semibold text-slate-200">
                              R{round.round_number}: {round.round_name}
                            </span>
                            <span className="ml-2 text-slate-500 uppercase text-[10px]">
                              [{round.round_type}]
                            </span>
                          </div>
                          <div className="text-right text-[11px] text-slate-400">
                            {round.scheduled_at
                              ? new Date(round.scheduled_at).toLocaleDateString([], {
                                  month: "short",
                                  day: "numeric",
                                })
                              : "Unscheduled"}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Plan Modal */}
      {isNewPlanOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Create Interview Plan</h3>
              <button
                onClick={() => setIsNewPlanOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target Company *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Stripe, Google, Datadog"
                  value={targetCompany}
                  onChange={(e) => setTargetCompany(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target Role *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Distributed Systems Engineer"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target / First Interview Date (Optional)
                </label>
                <input
                  type="date"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsNewPlanOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creatingPlan}
                  className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow"
                >
                  {creatingPlan ? "Creating..." : "Create Plan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Round Modal */}
      {selectedPlanForRound && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">
                Add Round: {selectedPlanForRound.target_company}
              </h3>
              <button
                onClick={() => setSelectedPlanForRound(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAddRound} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Round Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. System Design & Concurrency"
                  value={roundName}
                  onChange={(e) => setRoundName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Round Type
                </label>
                <select
                  value={roundType}
                  onChange={(e) => setRoundType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="RECRUITER_SCREEN">Recruiter Screen</option>
                  <option value="TECHNICAL">Technical / Coding</option>
                  <option value="SYSTEM_DESIGN">System Design & Architecture</option>
                  <option value="BEHAVIORAL">Behavioral / Leadership (STAR)</option>
                  <option value="HIRING_MANAGER">Hiring Manager Discussion</option>
                  <option value="EXECUTIVE">Executive / Culture Fit</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Scheduled Date & Time (Optional)
                </label>
                <input
                  type="datetime-local"
                  value={roundScheduledAt}
                  onChange={(e) => setRoundScheduledAt(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Meeting Link (Google Meet / Zoom / Chime)
                </label>
                <input
                  type="url"
                  placeholder="https://meet.google.com/..."
                  value={roundMeetingLink}
                  onChange={(e) => setRoundMeetingLink(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedPlanForRound(null)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={addingRound}
                  className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow"
                >
                  {addingRound ? "Saving..." : "Add Round"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default function InterviewPrepHubPage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
          <p className="text-sm">Loading interview prep...</p>
        </div>
      }
    >
      <InterviewPrepHubContent />
    </Suspense>
  );
}
