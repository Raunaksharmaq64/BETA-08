"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SkillDemandItem {
  canonical_name: string;
  slug: string;
  category: string;
  distinct_job_count: number;
  frequency_pct: number;
  trend_direction: string;
  confidence: string;
}

interface MarketDemandData {
  time_window: string;
  role_category: string;
  geography: string;
  sample_size: number;
  distinct_employers: number;
  status: string;
  skills: SkillDemandItem[];
  source_composition: Record<string, number>;
  collection_period: {
    start: string;
    end: string;
  };
  confidence_level: string;
  methodology: string;
  limitations: string;
}

export default function MarketIntelligenceDashboardPage() {
  const [demandData, setDemandData] = useState<MarketDemandData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [timeWindow, setTimeWindow] = useState("30d");
  const [roleCategory, setRoleCategory] = useState("ALL");
  const [geography, setGeography] = useState("ALL");

  const fetchDemand = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append("time_window", timeWindow);
      if (roleCategory !== "ALL") params.append("role_category", roleCategory);
      if (geography !== "ALL") params.append("geography", geography);

      const res: any = await apiClient.get(`/market/demand/skills?${params.toString()}`);
      setDemandData(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load market demand intelligence.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemand();
  }, [timeWindow, roleCategory, geography]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Market & Skill Intelligence
            </h1>
            <span className="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800">
              Audited Sample v1.0
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Observed technology demand, role requirements, and period-over-period market signals with transparent sample boundaries.
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <Link
            href="/market-intelligence/skill-gaps"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            My Skill-Gap Diagnostics →
          </Link>
          <Link
            href="/compensation"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            Compensation Explorer
          </Link>
          <Link
            href="/market-intelligence/sources"
            className="inline-flex items-center px-3 py-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-xs font-medium text-slate-400 border border-slate-800 transition-colors"
          >
            Sources & Methodology
          </Link>
        </div>
      </div>

      {/* Mandatory Sample Boundary Disclosure Alert */}
      <div className="rounded-xl border border-blue-900/60 bg-blue-950/30 p-4 text-xs text-blue-300 space-y-1">
        <div className="flex items-center gap-2 font-semibold text-white">
          <span className="h-2 w-2 rounded-full bg-blue-400" />
          <span>Observed Sample Disclosure</span>
        </div>
        <p className="text-slate-300 leading-relaxed">
          RIGHT FIT market intelligence is derived from an audited sample of verified active opportunities discovered across connected ATS connectors.
          It does not purport to represent a universal census of all global or informal employment. All statistics disclose exact sample sizes and timeframes.
        </p>
      </div>

      {/* Controls & Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-slate-900 border border-slate-800">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-lg border border-slate-800 overflow-x-auto max-w-full">
            <span className="text-xs text-slate-400 font-medium px-2">Window:</span>
            {["7d", "30d", "90d"].map((w) => (
              <button
                key={w}
                onClick={() => setTimeWindow(w)}
                className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                  timeWindow === w
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                Last {w.replace("d", " Days")}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400 font-medium">Role:</label>
            <select
              value={roleCategory}
              onChange={(e) => setRoleCategory(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">All Engineering Roles</option>
              <option value="Backend">Backend Engineer</option>
              <option value="Full-Stack">Full-Stack Engineer</option>
              <option value="Data">Data Engineer</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-400 font-medium">Geography:</label>
            <select
              value={geography}
              onChange={(e) => setGeography(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="ALL">Global / Remote</option>
              <option value="United States">United States</option>
              <option value="India">India</option>
              <option value="Europe">Europe</option>
            </select>
          </div>
        </div>

        {demandData && (
          <div className="text-xs text-slate-400 font-mono">
            Sample N = <strong className="text-white">{demandData.sample_size}</strong> vacancies | <strong className="text-white">{demandData.distinct_employers}</strong> employers
          </div>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/40 text-sm text-rose-300">
          {error}
        </div>
      )}

      {/* Main Grid: Observed Skill Demand */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-44 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : !demandData || demandData.skills.length === 0 ? (
        <div className="text-center py-16 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 space-y-2">
          <p className="text-base font-semibold text-slate-200">Insufficient Data in Selected Window</p>
          <p className="text-xs text-slate-500">
            Fewer than minimum threshold observations exist for the selected filter combination. Broaden the time window or geography to inspect market context.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {demandData.skills.map((skill) => {
              const isIncreasing = skill.trend_direction === "INCREASING_IN_SAMPLE";
              const isDecreasing = skill.trend_direction === "DECREASING_IN_SAMPLE";

              return (
                <Link
                  key={skill.slug}
                  href={`/market-intelligence/skills/${skill.slug}`}
                  className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-indigo-600/70 transition-all flex flex-col justify-between group"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                        {skill.category}
                      </span>
                      <span
                        className={`text-[10px] font-semibold px-2 py-0.5 rounded ${
                          isIncreasing
                            ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                            : isDecreasing
                            ? "bg-rose-950 text-rose-300 border border-rose-800"
                            : "bg-slate-800 text-slate-400 border border-slate-700"
                        }`}
                      >
                        {skill.trend_direction.replace("_IN_SAMPLE", "")}
                      </span>
                    </div>

                    <div>
                      <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                        {skill.canonical_name}
                      </h3>
                      <div className="text-xs text-slate-400 mt-0.5 font-mono">
                        Mentioned in {skill.distinct_job_count} / {demandData.sample_size} opportunities
                      </div>
                    </div>

                    {/* Progress Bar representing sample share */}
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-400">Sample Share</span>
                        <span className="text-white font-bold">{skill.frequency_pct}%</span>
                      </div>
                      <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full"
                          style={{ width: `${Math.min(100, skill.frequency_pct)}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="text-slate-500 text-[11px]">{skill.confidence}</span>
                    <span className="text-indigo-400 font-semibold group-hover:underline">Detail →</span>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Methodology & Limitations Footer Box */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs text-slate-400">
            <div>
              <strong className="text-slate-200">Methodology:</strong> {demandData.methodology}
            </div>
            <div>
              <strong className="text-slate-200">Limitations:</strong> {demandData.limitations}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

