"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface GovernedSource {
  source_id: string;
  provider_name: string;
  compliance_status: string;
  robots_txt_status: string;
  rate_limit_policy: string;
  retirement_stage: string;
  license_terms: string;
}

interface GovernanceData {
  governed_sources: GovernedSource[];
  governance_principles: {
    no_stealth_crawling: string;
    strict_attribution: string;
    rate_limiting: string;
    graceful_retirement: string;
  };
}

export default function SourceGovernancePage() {
  const [data, setData] = useState<GovernanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadGovernance() {
      try {
        setLoading(true);
        const res = await apiClient<GovernanceData>("/beta/sources/governance");
        if (res && res.data) {
          setData(res.data);
        }
      } catch (err: any) {
        console.error("Failed to load source governance", err);
      } finally {
        setLoading(false);
      }
    }
    loadGovernance();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 mb-2">
            Source Ethics & Regulatory Compliance
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Source Governance & Retirement Framework
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Tracking terms of service adherence, respectful robots.txt crawling, publisher attribution, and source lifecycle policies.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Link
            href="/quality/connectors"
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200"
          >
            Connector Metrics
          </Link>
          <Link
            href="/beta/release-notes"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Release Notes
          </Link>
        </div>
      </div>

      {/* Governance Principles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Principle 1
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white">
            No Stealth Crawling
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {data?.governance_principles?.no_stealth_crawling || "Only official APIs, verified job board RSS feeds, and publicly consented endpoints are queried."}
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Principle 2
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white">
            Strict Source Attribution
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {data?.governance_principles?.strict_attribution || "Every opportunity clearly attributes the original publisher and preserves deep application URLs."}
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Principle 3
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white">
            Exponential Backoff
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {data?.governance_principles?.rate_limiting || "Polite crawling respecting Retry-After headers, sliding window quotas, and token bucket limiters."}
          </p>
        </div>

        <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
            Principle 4
          </div>
          <div className="text-sm font-semibold text-slate-900 dark:text-white">
            Auditable Retirement
          </div>
          <p className="text-xs text-slate-600 dark:text-slate-400">
            {data?.governance_principles?.graceful_retirement || "Sources experiencing persistent API degradation are transitioned through Probation before decommission."}
          </p>
        </div>
      </div>

      {/* Governed Sources Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Governed Source Compliance Catalog
          </h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading source governance records...</div>
        ) : !data || data.governed_sources.length === 0 ? (
          <div className="p-8 text-center text-slate-500">No source records available.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-700 dark:text-slate-300">
              <thead className="bg-slate-50 dark:bg-slate-800/60 text-xs uppercase font-semibold text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="px-6 py-4">Source Provider</th>
                  <th className="px-6 py-4">Terms Compliance</th>
                  <th className="px-6 py-4">Robots.txt Adherence</th>
                  <th className="px-6 py-4">Rate Limiting Rule</th>
                  <th className="px-6 py-4">Lifecycle State</th>
                  <th className="px-6 py-4">License / Terms</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.governed_sources.map((src) => (
                  <tr key={src.source_id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white">
                      {src.provider_name}
                      <div className="text-xs text-slate-400 font-mono font-normal">
                        {src.source_id}
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                        {src.compliance_status}
                      </span>
                    </td>

                    <td className="px-6 py-4 font-mono text-xs">
                      {src.robots_txt_status}
                    </td>

                    <td className="px-6 py-4 text-xs font-mono">
                      {src.rate_limit_policy}
                    </td>

                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-800 dark:bg-indigo-950/60 dark:text-indigo-300">
                        {src.retirement_stage}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-xs text-slate-500 max-w-xs">
                      {src.license_terms}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

