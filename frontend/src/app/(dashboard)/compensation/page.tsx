"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface CompensationBenchmark {
  role_title?: string;
  role_category?: string;
  geography?: string;
  experience_level?: string;
  compensation_type: string;
  currency: string;
  sample_size: number;
  has_statistically_justified_median: boolean;
  median?: number | null;
  min?: number | null;
  max?: number | null;
  p25?: number | null;
  p75?: number | null;
  missing_compensation_rate: number;
  data_freshness: string;
  observations: Array<{
    id: string;
    role_title: string;
    employer_name?: string;
    base_salary_min?: number;
    base_salary_max?: number;
    total_compensation_min?: number;
    total_compensation_max?: number;
    currency: string;
    geography?: string;
    experience_level?: string;
    compensation_type: string;
    source_name?: string;
  }>;
  disclosure: {
    methodology: string;
    disclaimer: string;
    min_sample_rule: string;
  };
}

export default function CompensationExplorerPage() {
  const [data, setData] = useState<CompensationBenchmark | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [compensationType, setCompensationType] = useState("BASE_SALARY");
  const [roleCategory, setRoleCategory] = useState("ALL");
  const [currency, setCurrency] = useState("USD");
  const [experienceLevel, setExperienceLevel] = useState("ALL");
  const [geography, setGeography] = useState("ALL");

  const fetchCompensation = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      params.append("compensation_type", compensationType);
      params.append("currency", currency);
      if (roleCategory !== "ALL") params.append("role_category", roleCategory);
      if (experienceLevel !== "ALL") params.append("experience_level", experienceLevel);
      if (geography !== "ALL") params.append("geography", geography);

      const res: any = await apiClient.get(`/market/compensation?${params.toString()}`);
      setData(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load compensation benchmarks.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompensation();
  }, [compensationType, roleCategory, currency, experienceLevel, geography]);

  const formatCurrency = (val: number | null | undefined, curr: string) => {
    if (val === null || val === undefined) return "—";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: curr,
      maximumFractionDigits: 0,
    }).format(val);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Compensation Explorer
            </h1>
            <span className="text-xs bg-emerald-950 text-emerald-400 font-mono px-2 py-0.5 rounded border border-emerald-800">
              Sample Disclosed
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Empirical compensation intelligence strictly isolated by pay structure, currency, and role level. No fabricated projections.
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
            href="/market-intelligence/sources"
            className="px-3 py-2 bg-slate-800/60 hover:bg-slate-800 text-slate-400 rounded-lg text-xs font-medium border border-slate-800 transition-colors"
          >
            Methodology & Sources
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Pay Type:
            </span>
            <div className="inline-flex rounded-lg bg-slate-950 p-1 border border-slate-800">
              {[
                { id: "BASE_SALARY", label: "Base Salary" },
                { id: "TOTAL_COMPENSATION", label: "Total Comp" },
                { id: "CONTRACT_HOURLY", label: "Hourly / Contract" },
                { id: "EQUITY_GRANT", label: "Equity" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setCompensationType(tab.id)}
                  className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    compensationType === tab.id
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Currency Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Currency:
            </span>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="INR">INR (₹)</option>
            </select>
          </div>
        </div>

        {/* Secondary Filters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-slate-800/80">
          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Role Track</label>
            <select
              value={roleCategory}
              onChange={(e) => setRoleCategory(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Role Tracks</option>
              <option value="ENGINEERING">Software Engineering</option>
              <option value="DATA_AI">Data & Artificial Intelligence</option>
              <option value="PRODUCT">Product Management</option>
              <option value="DESIGN">Design & UX</option>
              <option value="DEVOPS_CLOUD">Cloud & Infrastructure</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Experience Level</label>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">All Levels</option>
              <option value="ENTRY">Entry / Junior (0-2y)</option>
              <option value="MID">Mid-Level (3-5y)</option>
              <option value="SENIOR">Senior (6-9y)</option>
              <option value="LEAD_STAFF">Lead / Staff (10y+)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-slate-400 mb-1">Geography</label>
            <select
              value={geography}
              onChange={(e) => setGeography(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            >
              <option value="ALL">Global / Remote & Local</option>
              <option value="US_REMOTE">US Remote</option>
              <option value="US_HYBRID">US Onsite / Hybrid</option>
              <option value="EU_REMOTE">EU Remote</option>
              <option value="INDIA">India (Domestic)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Content */}
      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-4"></div>
          <p>Compiling audited compensation benchmarks...</p>
        </div>
      ) : error ? (
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-6 text-center text-sm text-red-300">
          {error}
        </div>
      ) : data ? (
        <div className="space-y-8">
          {/* Top Metrics Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Median Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Audited Median
              </div>
              <div className="mt-2 text-3xl font-extrabold text-white">
                {data.has_statistically_justified_median
                  ? formatCurrency(data.median, data.currency)
                  : "N/A"}
              </div>
              <p className="mt-2 text-xs text-slate-400">
                {data.has_statistically_justified_median
                  ? `Computed over N=${data.sample_size} validated points`
                  : `Sample N=${data.sample_size} (< 5 threshold)`}
              </p>
            </div>

            {/* Observed Range Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Observed Range
              </div>
              <div className="mt-2 text-xl font-bold text-slate-200">
                {data.min !== null && data.max !== null
                  ? `${formatCurrency(data.min, data.currency)} – ${formatCurrency(data.max, data.currency)}`
                  : "No range data"}
              </div>
              <p className="mt-2 text-xs text-slate-400">
                25th–75th Percentiles:{" "}
                {data.p25 && data.p75
                  ? `${formatCurrency(data.p25, data.currency)} – ${formatCurrency(data.p75, data.currency)}`
                  : "N/A (< 5 points)"}
              </p>
            </div>

            {/* Sample Size Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Audited Sample Size
              </div>
              <div className="mt-2 text-3xl font-extrabold text-indigo-400">
                {data.sample_size} <span className="text-sm font-normal text-slate-400">observations</span>
              </div>
              <div className="mt-2 text-xs text-slate-400">
                Confidence Rule:{" "}
                <span
                  className={
                    data.sample_size >= 5
                      ? "text-emerald-400 font-semibold"
                      : "text-amber-400 font-semibold"
                  }
                >
                  {data.sample_size >= 5 ? "Sample Confirmed" : "Low Sample Warning"}
                </span>
              </div>
            </div>

            {/* Transparency / Non-Disclosure Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Unstated Salary Rate
              </div>
              <div className="mt-2 text-3xl font-extrabold text-amber-400">
                {Math.round(data.missing_compensation_rate * 100)}%
              </div>
              <p className="mt-2 text-xs text-slate-400">
                Postings in this segment omitting explicit salary disclosures
              </p>
            </div>
          </div>

          {/* Low Sample Warning Banner */}
          {!data.has_statistically_justified_median && (
            <div className="bg-amber-950/40 border border-amber-800/80 rounded-xl p-4 flex items-start gap-3">
              <span className="text-amber-400 font-bold text-lg">⚠️</span>
              <div>
                <h4 className="text-sm font-bold text-amber-200">
                  Statistical Disclosure Boundary Active
                </h4>
                <p className="text-xs text-amber-300/90 mt-1">
                  Sample size for this combination is N={data.sample_size} (&lt; 5). RIGHT FIT adheres to scientific reporting standards and deliberately suppresses composite medians on micro-samples to prevent false precision. Individual observations remain visible below for qualitative inspection.
                </p>
              </div>
            </div>
          )}

          {/* Observations Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-white">Underlying Observation Records</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Verified salary disclosures collected from employer postings and audited source feeds.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                Currency: {data.currency}
              </span>
            </div>

            {data.observations && data.observations.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 uppercase font-semibold border-b border-slate-800">
                    <tr>
                      <th className="px-6 py-3">Role Title</th>
                      <th className="px-6 py-3">Employer</th>
                      <th className="px-6 py-3">Type</th>
                      <th className="px-6 py-3">Reported Range</th>
                      <th className="px-6 py-3">Level</th>
                      <th className="px-6 py-3">Location</th>
                      <th className="px-6 py-3">Source</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {data.observations.map((obs) => {
                      const minVal =
                        data.compensation_type === "BASE_SALARY"
                          ? obs.base_salary_min
                          : obs.total_compensation_min || obs.base_salary_min;
                      const maxVal =
                        data.compensation_type === "BASE_SALARY"
                          ? obs.base_salary_max
                          : obs.total_compensation_max || obs.base_salary_max;

                      return (
                        <tr key={obs.id} className="hover:bg-slate-800/40 transition-colors">
                          <td className="px-6 py-3.5 font-medium text-white">{obs.role_title}</td>
                          <td className="px-6 py-3.5 text-slate-300">{obs.employer_name || "Confidential"}</td>
                          <td className="px-6 py-3.5">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-indigo-400 border border-slate-700">
                              {obs.compensation_type}
                            </span>
                          </td>
                          <td className="px-6 py-3.5 font-semibold text-emerald-400">
                            {formatCurrency(minVal, obs.currency)} – {formatCurrency(maxVal, obs.currency)}
                          </td>
                          <td className="px-6 py-3.5 text-slate-400">{obs.experience_level || "Not specified"}</td>
                          <td className="px-6 py-3.5 text-slate-400">{obs.geography || "Remote"}</td>
                          <td className="px-6 py-3.5 text-slate-500 font-mono text-[11px]">{obs.source_name || "Audited Feed"}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400">
                No observations matching this specific filter combination in current audited snapshot.
              </div>
            )}
          </div>

          {/* Methodology & Boundary Disclosures */}
          <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-3">
            <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Statistical Methodology & Integrity Rules
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400 leading-relaxed">
              <div>
                <span className="font-semibold text-slate-200">Independent Pay Isolation:</span> Base salaries, total cash compensation, equity percentages, and contract hourly rates are never blended into a single artificial composite score.
              </div>
              <div>
                <span className="font-semibold text-slate-200">Currency Integrity:</span> Figures are reported strictly in their original currency of record. No arbitrary cross-currency conversions are performed without disclosure.
              </div>
              <div>
                <span className="font-semibold text-slate-200">Sample Boundary (N &ge; 5):</span> {data.disclosure?.min_sample_rule || "Medians and percentiles require N >= 5 distinct observations."}
              </div>
              <div>
                <span className="font-semibold text-slate-200">Transparency:</span> Unstated salary rates disclose employer non-disclosure rates so candidates understand market coverage.
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

