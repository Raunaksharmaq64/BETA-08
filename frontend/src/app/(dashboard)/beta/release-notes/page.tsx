"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface VerifiedCapability {
  module: string;
  summary: string;
  status: string;
}

interface ReleaseNotesData {
  release_version: string;
  release_date: string;
  codename: string;
  verified_capabilities: VerifiedCapability[];
  known_limitations: string[];
  beta_environment_guardrails: string[];
  next_roadmap_milestones: string[];
}

export default function ReleaseNotesPage() {
  const [data, setData] = useState<ReleaseNotesData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadNotes() {
      try {
        setLoading(true);
        const res = await apiClient<ReleaseNotesData>("/beta/release-notes");
        if (res && res.data) {
          setData(res.data);
        }
      } catch (err: any) {
        console.error("Failed to load release notes", err);
      } finally {
        setLoading(false);
      }
    }
    loadNotes();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 mb-2">
            Release Candidate: {data?.release_version || "1.0.0-beta.14"}
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            RIGHT FIT Beta Release Notes
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Codename: <span className="font-semibold text-slate-900 dark:text-white">{data?.codename || "Production Gate Verified"}</span> — Full platform verification across all 14 engineering phases.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Link
            href="/beta/feedback"
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200"
          >
            Submit Feedback
          </Link>
          <Link
            href="/beta/support"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Support Playbook
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading verified release notes...</div>
      ) : !data ? (
        <div className="p-8 text-center text-slate-500">Release notes unavailable.</div>
      ) : (
        <div className="space-y-8">
          {/* Verified Capabilities Grid */}
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
              Verified Platform Capabilities (Phases 0–14)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.verified_capabilities.map((cap, idx) => (
                <div
                  key={idx}
                  className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900 dark:text-white text-sm">
                      {cap.module}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                      {cap.status}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    {cap.summary}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Guardrails and Known Limitations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Known Limitations */}
            <div className="p-6 bg-amber-50/50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 rounded-xl space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                  Known Limitations in Beta
                </h3>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Operating under strict candidate consent and privacy rules without unapproved automation:
              </p>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                {data.known_limitations.map((lim, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-amber-600 font-bold">•</span>
                    <span>{lim}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Beta Environment Guardrails */}
            <div className="p-6 bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-200 dark:border-indigo-900/60 rounded-xl space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                <h3 className="text-base font-semibold text-slate-900 dark:text-white">
                  Operational Safety Guardrails
                </h3>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400">
                Guarantees enforced in the beta test environment:
              </p>
              <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
                {data.beta_environment_guardrails.map((gd, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-indigo-600 font-bold">•</span>
                    <span>{gd}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Roadmap Milestones */}
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-4 shadow-sm">
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              Continuous Improvement Milestones
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.next_roadmap_milestones.map((m, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-lg border border-slate-100 dark:border-slate-800 text-xs text-slate-700 dark:text-slate-300 flex items-center gap-3"
                >
                  <span className="w-6 h-6 rounded-full bg-indigo-100 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 font-bold flex items-center justify-center shrink-0">
                    {idx + 1}
                  </span>
                  <span>{m}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

