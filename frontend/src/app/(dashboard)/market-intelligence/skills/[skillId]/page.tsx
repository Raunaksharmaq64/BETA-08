"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SkillAlias {
  id: string;
  alias: string;
  source_type: string;
}

interface SkillDetail {
  id: string;
  canonical_name: string;
  slug: string;
  category: string;
  technology_family?: string;
  description?: string;
  aliases: SkillAlias[];
  demand_snapshots: Array<{
    time_window: string;
    role_category: string;
    geography: string;
    distinct_job_count: number;
    sample_size: number;
    frequency_pct: number;
    trend_direction: string;
    snapshot_date: string;
  }>;
  methodology: string;
  limitations: string;
}

export default function SkillDetailPage() {
  const params = useParams();
  const router = useRouter();
  const skillId = params?.skillId as string;

  const [skill, setSkill] = useState<SkillDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!skillId) return;
    const fetchSkill = async () => {
      setLoading(true);
      setError(null);
      try {
        const res: any = await apiClient.get(`/market/skills/${encodeURIComponent(skillId)}`);
        setSkill(res.data);
      } catch (err: any) {
        setError(err?.message || "Failed to load skill details.");
      } finally {
        setLoading(false);
      }
    };
    fetchSkill();
  }, [skillId]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-12 text-center text-slate-400">
        <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-4"></div>
        <p>Loading canonical skill intelligence...</p>
      </div>
    );
  }

  if (error || !skill) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-6 text-center space-y-4">
          <h2 className="text-lg font-bold text-red-200">Skill Not Found or Error</h2>
          <p className="text-sm text-red-300">{error || "Could not retrieve skill profile."}</p>
          <Link
            href="/market-intelligence"
            className="inline-flex px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-semibold transition"
          >
            ← Return to Market Intelligence
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Breadcrumb */}
      <nav className="flex items-center space-x-2 text-xs text-slate-400">
        <Link href="/market-intelligence" className="hover:text-slate-200">
          Market Intelligence
        </Link>
        <span>/</span>
        <span className="text-slate-200 font-semibold">{skill.canonical_name}</span>
      </nav>

      {/* Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 shadow-sm">
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-3xl font-extrabold text-white tracking-tight">
                {skill.canonical_name}
              </h1>
              <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md border border-slate-700 font-mono">
                {skill.slug}
              </span>
              <span className="text-xs bg-indigo-950 text-indigo-400 px-2.5 py-1 rounded-md border border-indigo-800 font-semibold uppercase">
                {skill.category}
              </span>
              {skill.technology_family && (
                <span className="text-xs bg-cyan-950 text-cyan-400 px-2.5 py-1 rounded-md border border-cyan-800">
                  Family: {skill.technology_family}
                </span>
              )}
            </div>
            <p className="mt-3 text-slate-300 text-sm max-w-3xl leading-relaxed">
              {skill.description || "Canonical technology entity tracked across verified career opportunities."}
            </p>
          </div>

          <div className="flex gap-2">
            <Link
              href="/market-intelligence"
              className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium border border-slate-700 transition"
            >
              Browse All Skills
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Aliases & Taxonomy Details */}
        <div className="space-y-6 lg:col-span-1">
          {/* Canonical Aliases */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-3">
              Recognized Synonyms & Aliases
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              All raw query terms that deterministically resolve to this canonical entity without false merges.
            </p>
            {skill.aliases && skill.aliases.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {skill.aliases.map((alias) => (
                  <span
                    key={alias.id || alias.alias}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-mono bg-slate-800/80 text-slate-300 border border-slate-700"
                  >
                    {alias.alias}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No specific aliases registered. Matches exact canonical name.</p>
            )}
          </div>

          {/* Governance & Integrity */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-3">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              Governance & Integrity
            </h2>
            <div className="space-y-2 text-xs text-slate-400">
              <div className="flex justify-between">
                <span>Entity Type:</span>
                <span className="font-semibold text-slate-200">Canonical Skill Node</span>
              </div>
              <div className="flex justify-between">
                <span>Alias Resolution:</span>
                <span className="font-semibold text-emerald-400">Deterministic 1-to-1</span>
              </div>
              <div className="flex justify-between">
                <span>False-Precision Protection:</span>
                <span className="font-semibold text-indigo-400">Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Demand Snapshots & Market Evidence */}
        <div className="space-y-6 lg:col-span-2">
          {/* Demand Snapshots */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-base font-bold text-white mb-2">
              Observed Market Demand Snapshots
            </h2>
            <p className="text-xs text-slate-400 mb-6">
              Demand counts represent distinct verified job vacancies requiring this skill within each respective time window.
            </p>

            {skill.demand_snapshots && skill.demand_snapshots.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {skill.demand_snapshots.map((snap, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono text-indigo-400 uppercase">
                        Window: {snap.time_window}
                      </span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          snap.trend_direction === "RISING"
                            ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                            : snap.trend_direction === "FALLING"
                            ? "bg-amber-950 text-amber-400 border-amber-800"
                            : "bg-slate-800 text-slate-300 border-slate-700"
                        }`}
                      >
                        {snap.trend_direction}
                      </span>
                    </div>

                    <div className="text-2xl font-black text-white">
                      {snap.distinct_job_count}{" "}
                      <span className="text-xs font-normal text-slate-400">vacancies</span>
                    </div>

                    <div className="text-xs text-slate-400">
                      Market Share:{" "}
                      <span className="font-semibold text-white">{snap.frequency_pct}%</span>
                    </div>

                    <div className="text-[11px] text-slate-500 border-t border-slate-800 pt-2">
                      Sample: N={snap.sample_size} postings
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-slate-950/40 border border-slate-800 rounded-lg p-6 text-center text-xs text-slate-400">
                Demand snapshot gathering in progress for this canonical node.
              </div>
            )}
          </div>

          {/* Methodology & Boundary Disclosures */}
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Methodology & Boundary Disclosures
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              {skill.methodology ||
                "Aggregated exclusively over verified canonical opportunities. Each opportunity is counted at most once per skill regardless of repeated keyword occurrences in the JD."}
            </p>
            <div className="text-[11px] text-slate-500 italic">
              Limitations: {skill.limitations || "Subject to published posting volume; small sub-segments with N < 5 omit medians."}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

