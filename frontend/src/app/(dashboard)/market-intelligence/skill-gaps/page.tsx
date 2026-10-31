"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SkillGapRecommendation {
  id: string;
  canonical_skill_name: string;
  skill_slug: string;
  category: string;
  gap_status: "INTERESTED" | "ALREADY_LEARNING" | "NOT_RELEVANT" | "COMPLETED";
  role_demand_frequency_pct: number;
  distinct_job_count: number;
  notes?: string;
  created_at: string;
}

interface SkillGapResponse {
  target_role: string;
  time_window: string;
  candidate_confirmed_skills: string[];
  candidate_confirmed_skills_count: number;
  recommendations: SkillGapRecommendation[];
  disclaimer: string;
}

export default function CandidateSkillGapPage() {
  const [data, setData] = useState<SkillGapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [timeWindow, setTimeWindow] = useState("30d");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [viewMode, setViewMode] = useState<"roadmap" | "grid">("roadmap");
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchSkillGaps = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append("target_role", targetRole);
      params.append("time_window", timeWindow);

      const res: any = await apiClient.get(`/market/skill-gaps?${params.toString()}`);
      setData(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load skill-gap diagnostics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSkillGaps();
  }, [targetRole, timeWindow]);

  const handleUpdateStatus = async (
    recommendationId: string,
    newStatus: "INTERESTED" | "ALREADY_LEARNING" | "NOT_RELEVANT" | "COMPLETED"
  ) => {
    setUpdatingId(recommendationId);
    try {
      await apiClient.post(`/market/skill-gaps/${recommendationId}/status`, {
        status: newStatus,
      });

      // Update state locally for instant snappy feedback
      if (data) {
        setData({
          ...data,
          recommendations: data.recommendations.map((rec) =>
            rec.id === recommendationId ? { ...rec, gap_status: newStatus } : rec
          ),
        });
      }
    } catch (err: any) {
      alert("Failed to update status: " + (err?.message || "Unknown error"));
    } finally {
      setUpdatingId(null);
    }
  };

  const filteredRecs = data?.recommendations?.filter((rec) => {
    if (statusFilter === "ALL") return true;
    return rec.gap_status === statusFilter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Candidate Skill-Gap Diagnostics
            </h1>
            <span className="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800">
              Personalized & Non-Mutating
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Compare your verified resume skills against observed technology demand in active job postings.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/market-intelligence"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-semibold border border-slate-700 transition-colors"
          >
            ← Market Demand
          </Link>
          <Link
            href="/profile"
            className="px-3 py-2 bg-indigo-950/60 hover:bg-indigo-900/60 text-indigo-300 rounded-lg text-xs font-medium border border-indigo-800 transition-colors"
          >
            Manage Confirmed Skills
          </Link>
        </div>
      </div>

      {/* Control Bar: Target Role & Time Window */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 flex-1 max-w-xl">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-400 whitespace-nowrap">
              Target Role:
            </label>
            <input
              type="text"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              placeholder="e.g. Software Engineer, Backend Engineer, Frontend Developer"
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3.5 py-2 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Demand Window:
            </span>
            <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              {["7d", "30d", "90d"].map((w) => (
                <button
                  key={w}
                  onClick={() => setTimeWindow(w)}
                  className={`px-3 py-1 rounded-md text-xs font-medium uppercase transition-colors ${
                    timeWindow === w
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {w}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Filter by Gap Status & View Mode */}
        <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 flex-wrap gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mr-1">
              Status Filter:
            </span>
            {[
              { id: "ALL", label: "All Items" },
              { id: "INTERESTED", label: "Interested" },
              { id: "ALREADY_LEARNING", label: "Already Learning" },
              { id: "COMPLETED", label: "Completed" },
              { id: "NOT_RELEVANT", label: "Not Relevant" },
            ].map((statusTab) => (
              <button
                key={statusTab.id}
                onClick={() => setStatusFilter(statusTab.id)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                  statusFilter === statusTab.id
                    ? "bg-slate-800 text-indigo-400 border border-slate-700 font-semibold"
                    : "text-slate-400 hover:text-slate-200 bg-slate-950 border border-transparent"
                }`}
              >
                {statusTab.label}
              </button>
            ))}
          </div>

          {/* View Mode Toggle (Module L) */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              type="button"
              onClick={() => setViewMode("roadmap")}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                viewMode === "roadmap"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              🛣️ Visual Roadmap
            </button>
            <button
              type="button"
              onClick={() => setViewMode("grid")}
              className={`px-3 py-1 rounded-md text-xs font-semibold transition ${
                viewMode === "grid"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              ⊞ Grid Cards
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-4"></div>
          <p>Auditing verified candidate skills against live market postings...</p>
        </div>
      ) : error ? (
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-6 text-center text-sm text-red-300">
          {error}
        </div>
      ) : data ? (
        <div className="space-y-8">
          {/* Confirmed Skills Summary Banner */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-white">
                Your Confirmed Evidence-Backed Skills ({data.candidate_confirmed_skills_count})
              </h3>
              <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
                <span>✓</span> Verified against uploaded resume & profile
              </span>
            </div>

            {data.candidate_confirmed_skills && data.candidate_confirmed_skills.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {data.candidate_confirmed_skills.map((skill, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-950/60 text-emerald-300 border border-emerald-800/80"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">
                No verified skills detected. Upload your resume or add confirmed skills in your profile to run personalized diagnostics.
              </p>
            )}
          </div>

          {/* Missing Skills / Market Recommendations Grid */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-white">
                  Identified Skill Gaps for &ldquo;{data.target_role}&rdquo;
                </h3>
                <p className="text-xs text-slate-400">
                  Skills frequently demanded in recent vacancies that are not currently in your confirmed profile.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400 bg-slate-900 px-3 py-1 rounded-md border border-slate-800">
                {filteredRecs?.length || 0} recommendations
              </span>
            </div>

            {filteredRecs && filteredRecs.length > 0 ? (
              viewMode === "roadmap" ? (
                /* Sequential Career Growth Roadmap View (Module L) */
                <div className="space-y-8">
                  {[
                    {
                      phase: 1,
                      title: "Milestone 1: High-Yield Core Mandates",
                      badge: "Demand > 40%",
                      badgeColor: "bg-rose-950 text-rose-300 border-rose-800",
                      description: "Foundational requirements appearing across the majority of active job vacancies. Learning these unlocks immediate maximum job match rate.",
                      items: filteredRecs.filter((r) => r.role_demand_frequency_pct >= 40),
                      estTime: "2-4 Weeks",
                    },
                    {
                      phase: 2,
                      title: "Milestone 2: Stack Deepening & Mid-Level Fluency",
                      badge: "Demand 20% - 40%",
                      badgeColor: "bg-indigo-950 text-indigo-300 border-indigo-800",
                      description: "Key architectural and tooling competencies that distinguish qualified candidates from entry applicants.",
                      items: filteredRecs.filter((r) => r.role_demand_frequency_pct >= 20 && r.role_demand_frequency_pct < 40),
                      estTime: "3-5 Weeks",
                    },
                    {
                      phase: 3,
                      title: "Milestone 3: Competitive Edge & Specialized Frameworks",
                      badge: "Demand < 20%",
                      badgeColor: "bg-emerald-950 text-emerald-300 border-emerald-800",
                      description: "Emerging libraries and niche specializations that give you a distinctive competitive edge in technical interview rounds.",
                      items: filteredRecs.filter((r) => r.role_demand_frequency_pct < 20),
                      estTime: "2-3 Weeks",
                    },
                  ].map((stage) => (
                    stage.items.length > 0 && (
                      <div key={stage.phase} className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
                          <div className="flex items-center gap-2">
                            <span className="w-6 h-6 rounded-full bg-indigo-600 text-white font-bold text-xs flex items-center justify-center">
                              {stage.phase}
                            </span>
                            <h4 className="text-base font-bold text-white">{stage.title}</h4>
                            <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${stage.badgeColor}`}>
                              {stage.badge}
                            </span>
                          </div>
                          <span className="text-xs text-slate-400 font-medium">Est. Sprint: {stage.estTime}</span>
                        </div>
                        <p className="text-xs text-slate-400">{stage.description}</p>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                          {stage.items.map((rec) => (
                            <div
                              key={rec.id}
                              className="bg-slate-950 p-4 rounded-xl border border-slate-800/80 hover:border-slate-700 transition flex flex-col justify-between space-y-3"
                            >
                              <div className="space-y-2">
                                <div className="flex items-start justify-between gap-2">
                                  <div>
                                    <div className="font-bold text-sm text-white">{rec.canonical_skill_name}</div>
                                    <div className="text-[10px] text-indigo-400 font-mono uppercase">{rec.category}</div>
                                  </div>
                                  <span
                                    className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase ${
                                      rec.gap_status === "INTERESTED"
                                        ? "bg-indigo-950 text-indigo-400 border-indigo-800"
                                        : rec.gap_status === "ALREADY_LEARNING"
                                        ? "bg-amber-950 text-amber-400 border-amber-800"
                                        : rec.gap_status === "COMPLETED"
                                        ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                        : "bg-slate-800 text-slate-400 border-slate-700"
                                    }`}
                                  >
                                    {rec.gap_status.replace("_", " ")}
                                  </span>
                                </div>

                                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
                                  <span className="text-purple-400 font-semibold block text-[11px] mb-0.5">
                                    💡 Practical Portfolio Milestone:
                                  </span>
                                  Build a proof-of-concept project demonstrating practical usage of {rec.canonical_skill_name} with verified test coverage.
                                </div>

                                <div className="flex justify-between text-xs text-slate-400">
                                  <span>Market Demand:</span>
                                  <span className="font-semibold text-white">{rec.role_demand_frequency_pct}% of vacancies</span>
                                </div>
                              </div>

                              <div className="flex items-center justify-between gap-2 pt-2 border-t border-slate-800/60">
                                <button
                                  type="button"
                                  onClick={() => handleUpdateStatus(rec.id, rec.gap_status === "ALREADY_LEARNING" ? "COMPLETED" : "ALREADY_LEARNING")}
                                  className="text-xs px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200"
                                >
                                  {rec.gap_status === "ALREADY_LEARNING" ? "✓ Mark Completed" : "⚡ Start Learning"}
                                </button>
                                <Link
                                  href="/profile"
                                  className="text-xs text-indigo-400 hover:underline"
                                >
                                  Add to Profile &rarr;
                                </Link>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )
                  ))}
                </div>
              ) : (
                /* Traditional Grid Cards View */
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredRecs.map((rec) => (
                    <div
                      key={rec.id}
                      className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 flex flex-col justify-between space-y-4 transition-colors"
                    >
                      <div className="space-y-3">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <Link
                              href={`/market-intelligence/skills/${rec.skill_slug}`}
                              className="text-base font-bold text-white hover:text-indigo-400 transition"
                            >
                              {rec.canonical_skill_name}
                            </Link>
                            <div className="text-[10px] font-mono uppercase text-indigo-400 mt-0.5">
                              {rec.category}
                            </div>
                          </div>

                          {/* Status Badge */}
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase font-mono ${
                              rec.gap_status === "INTERESTED"
                                ? "bg-indigo-950 text-indigo-400 border-indigo-800"
                                : rec.gap_status === "ALREADY_LEARNING"
                                ? "bg-amber-950 text-amber-400 border-amber-800"
                                : rec.gap_status === "COMPLETED"
                                ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                                : "bg-slate-800 text-slate-400 border-slate-700"
                            }`}
                          >
                            {rec.gap_status.replace("_", " ")}
                          </span>
                        </div>

                        <div className="space-y-1">
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Demand Frequency:</span>
                            <span className="font-semibold text-white">
                              {rec.role_demand_frequency_pct}% of postings
                            </span>
                          </div>
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Observed Vacancies:</span>
                            <span className="font-semibold text-slate-200">
                              {rec.distinct_job_count} distinct roles
                            </span>
                          </div>
                        </div>

                        {rec.notes && (
                          <p className="text-xs text-slate-400 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80">
                            {rec.notes}
                          </p>
                        )}
                      </div>

                      {/* Interactive Action Controls */}
                      <div className="border-t border-slate-800 pt-3">
                        <div className="text-[11px] font-medium text-slate-400 mb-2">Update Status:</div>
                        <div className="grid grid-cols-2 gap-1.5">
                          <button
                            disabled={updatingId === rec.id || rec.gap_status === "INTERESTED"}
                            onClick={() => handleUpdateStatus(rec.id, "INTERESTED")}
                            className={`px-2 py-1.5 rounded text-[11px] font-medium transition text-center ${
                              rec.gap_status === "INTERESTED"
                                ? "bg-indigo-600 text-white font-bold"
                                : "bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800"
                            }`}
                          >
                            Interested
                          </button>
                          <button
                            disabled={updatingId === rec.id || rec.gap_status === "ALREADY_LEARNING"}
                            onClick={() => handleUpdateStatus(rec.id, "ALREADY_LEARNING")}
                            className={`px-2 py-1.5 rounded text-[11px] font-medium transition text-center ${
                              rec.gap_status === "ALREADY_LEARNING"
                                ? "bg-amber-600 text-white font-bold"
                                : "bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800"
                            }`}
                          >
                            Learning
                          </button>
                          <button
                            disabled={updatingId === rec.id || rec.gap_status === "COMPLETED"}
                            onClick={() => handleUpdateStatus(rec.id, "COMPLETED")}
                            className={`px-2 py-1.5 rounded text-[11px] font-medium transition text-center ${
                              rec.gap_status === "COMPLETED"
                                ? "bg-emerald-600 text-white font-bold"
                                : "bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800"
                            }`}
                          >
                            Completed
                          </button>
                          <button
                            disabled={updatingId === rec.id || rec.gap_status === "NOT_RELEVANT"}
                            onClick={() => handleUpdateStatus(rec.id, "NOT_RELEVANT")}
                            className={`px-2 py-1.5 rounded text-[11px] font-medium transition text-center ${
                              rec.gap_status === "NOT_RELEVANT"
                                ? "bg-slate-700 text-white font-bold"
                                : "bg-slate-950 hover:bg-slate-800 text-slate-400 border border-slate-800"
                            }`}
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-400 space-y-3">
                <div className="text-3xl">🎉</div>
                <h4 className="text-base font-bold text-white">No Unaddressed Gaps Found</h4>
                <p className="text-xs text-slate-400 max-w-md mx-auto">
                  Your verified skills comprehensively cover observed requirements for &ldquo;{data.target_role}&rdquo; in this window, or all suggestions match your current filter.
                </p>
              </div>
            )}
          </div>

          {/* Non-Mutation & Privacy Invariant Disclaimer */}
          <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-2">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Privacy & Non-Mutation Safeguard
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              {data.disclaimer ||
                "Skill gap diagnostics are purely informational. In accordance with RIGHT FIT integrity rules, the platform never invents candidate qualifications or silently adds skills to your resume. Profile changes require explicit candidate action."}
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
}

