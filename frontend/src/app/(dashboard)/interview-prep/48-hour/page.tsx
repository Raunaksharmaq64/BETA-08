"use client";

import React, { useEffect, useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface SprintBlock {
  block_name: string;
  timeframe: string;
  focus: string;
  tasks: string[];
}

interface SprintPreparation {
  plan_id: string;
  target_company: string;
  target_role: string;
  hours_remaining: number;
  blocks: SprintBlock[];
}

interface PlanOption {
  id: string;
  target_company: string;
  target_role: string;
}

function Sprint48HourContent() {
  const searchParams = useSearchParams();
  const planIdParam = searchParams.get("planId");
  const { user, loading: authLoading } = useAuth();

  const [plans, setPlans] = useState<PlanOption[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<string>(planIdParam || "");
  const [sprintData, setSprintData] = useState<SprintPreparation | null>(null);
  const [loading, setLoading] = useState(false);
  const [checkedTasks, setCheckedTasks] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Load available plans to let candidate select
    const loadPlans = async () => {
      try {
        const res = await apiClient<PlanOption[]>("/interview-prep/plans");
        const loaded = res.data || [];
        setPlans(loaded);
        if (!selectedPlanId && loaded.length > 0) {
          setSelectedPlanId(loaded[0].id);
        }
      } catch (err) {
        console.error("Failed to load plans for 48h sprint:", err);
      }
    };
    if (user) loadPlans();
  }, [user]);

  const fetchSprint = async (planId: string) => {
    if (!planId) return;
    setLoading(true);
    try {
      const res = await apiClient<SprintPreparation>(
        `/interview-prep/plans/${planId}/48h-sprint`
      );
      setSprintData(res.data);
    } catch (err: any) {
      console.error("Failed to load sprint data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedPlanId) {
      fetchSprint(selectedPlanId);
    }
  }, [selectedPlanId]);

  const toggleTask = (taskKey: string) => {
    setCheckedTasks((prev) => ({
      ...prev,
      [taskKey]: !prev[taskKey],
    }));
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
            <span>⚡ 48-Hour Sprint Preparation Mode</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Prioritized high-impact sprint blocks designed for the final 48 hours before your
            interview.
          </p>
        </div>

        {/* Plan Selector */}
        {plans.length > 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-2 flex items-center space-x-2 text-xs">
            <span className="text-slate-400 font-medium">Target Plan:</span>
            <select
              value={selectedPlanId}
              onChange={(e) => setSelectedPlanId(e.target.value)}
              className="bg-transparent text-indigo-400 font-bold focus:outline-none"
            >
              {plans.map((p) => (
                <option key={p.id} value={p.id} className="bg-slate-900 text-slate-200">
                  {p.target_company} — {p.target_role}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
          <p className="text-sm">Synthesizing 48-Hour sprint checklist...</p>
        </div>
      ) : !sprintData ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
          <p>Please select an interview plan above to view your personalized 48-hour sprint.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Sprint Banner */}
          <div className="bg-gradient-to-r from-amber-950/40 via-slate-900 to-indigo-950/40 border border-amber-800/40 rounded-2xl p-6 shadow-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <span className="text-xs uppercase font-bold text-amber-400 tracking-wider">
                Interview Sprint in Progress
              </span>
              <h2 className="text-2xl font-bold text-white mt-1">
                {sprintData.target_role} @ {sprintData.target_company}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Zero cramming. Focus on high-signal evidence, crisp communication, and mental
                clarity.
              </p>
            </div>

            <div className="bg-slate-950/80 border border-amber-800/60 rounded-xl px-5 py-3 text-center">
              <span className="text-[11px] text-slate-400 uppercase font-semibold">
                Countdown Window
              </span>
              <div className="text-2xl font-extrabold text-amber-300">
                ~{sprintData.hours_remaining} Hours
              </div>
            </div>
          </div>

          {/* Quick Action Navigation */}
          <div className="flex flex-wrap gap-3">
            <Link
              href="/interview-prep/star"
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-800/80 transition"
            >
              ⭐ Review Evidence-Grounded STAR Stories &rarr;
            </Link>
            <Link
              href="/interview-prep/mock"
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/80 transition"
            >
              🎙️ Run Mock Interview Rubric Session &rarr;
            </Link>
          </div>

          {/* 4 Time-Boxed Blocks */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {sprintData.blocks.map((block, idx) => {
              const blockColors = [
                {
                  badge: "bg-blue-950 text-blue-300 border-blue-800",
                  card: "border-blue-900/40",
                },
                {
                  badge: "bg-purple-950 text-purple-300 border-purple-800",
                  card: "border-purple-900/40",
                },
                {
                  badge: "bg-amber-950 text-amber-300 border-amber-800",
                  card: "border-amber-900/40",
                },
                {
                  badge: "bg-emerald-950 text-emerald-300 border-emerald-800",
                  card: "border-emerald-900/40",
                },
              ];
              const style = blockColors[idx % blockColors.length];

              return (
                <div
                  key={block.block_name}
                  className={`bg-slate-900 border ${style.card} rounded-2xl p-6 shadow-md flex flex-col justify-between space-y-4`}
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span
                        className={`text-[11px] font-bold px-2.5 py-0.5 rounded uppercase tracking-wider border ${style.badge}`}
                      >
                        {block.timeframe}
                      </span>
                      <span className="text-xs font-mono text-slate-500">Block {idx + 1}/4</span>
                    </div>

                    <h3 className="text-lg font-bold text-white pt-1">{block.block_name}</h3>
                    <p className="text-xs text-slate-400 font-medium italic">{block.focus}</p>

                    <div className="space-y-2 pt-3 border-t border-slate-800/60">
                      {block.tasks.map((task, tIdx) => {
                        const taskKey = `${idx}-${tIdx}`;
                        const isDone = !!checkedTasks[taskKey];
                        return (
                          <label
                            key={taskKey}
                            className={`flex items-start space-x-3 p-2.5 rounded-lg border text-xs cursor-pointer transition ${
                              isDone
                                ? "bg-slate-950/40 border-slate-800/40 opacity-60 text-slate-500 line-through"
                                : "bg-slate-950 border-slate-800 text-slate-200 hover:border-slate-700"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isDone}
                              onChange={() => toggleTask(taskKey)}
                              className="mt-0.5 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                            />
                            <span className="leading-relaxed">{task}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Sprint48HourPage() {
  return (
    <Suspense
      fallback={
        <div className="py-20 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
          <p className="text-sm">Loading 48-Hour sprint...</p>
        </div>
      }
    >
      <Sprint48HourContent />
    </Suspense>
  );
}
