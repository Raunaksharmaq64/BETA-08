"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface MarketSource {
  id: string;
  source_key: string;
  name: string;
  source_type: string;
  description?: string;
  website_url?: string;
  ingestion_frequency?: string;
  is_active: boolean;
  reliability_score?: number;
}

interface MethodologyDisclosure {
  phase: string;
  engine: string;
  guarantees: Array<{
    rule_id: string;
    title: string;
    description: string;
    audit_rule: string;
  }>;
  version: string;
}

export default function MarketSourcesAndMethodologyPage() {
  const [sources, setSources] = useState<MarketSource[]>([]);
  const [methodology, setMethodology] = useState<MethodologyDisclosure | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRegistry = async () => {
      setLoading(true);
      setError(null);
      try {
        const [sourcesRes, methRes]: any = await Promise.all([
          apiClient.get("/market/sources"),
          apiClient.get("/market/methodology"),
        ]);
        setSources(sourcesRes.data?.sources || []);
        setMethodology(methRes.data);
      } catch (err: any) {
        setError(err?.message || "Failed to load market source registry.");
      } finally {
        setLoading(false);
      }
    };
    fetchRegistry();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Market Sources & Methodology Registry
            </h1>
            <span className="text-xs bg-indigo-950 text-indigo-400 font-mono px-2 py-0.5 rounded border border-indigo-800">
              Audit Transparency
            </span>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Transparent registry of data sources, ingestion frequencies, and statistical governance rules powering RIGHT FIT Market Intelligence.
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
            href="/compensation"
            className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold border border-slate-700 transition-colors"
          >
            Compensation Explorer
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="animate-spin inline-block w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full mb-4"></div>
          <p>Loading audited source registry and integrity rules...</p>
        </div>
      ) : error ? (
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-6 text-center text-sm text-red-300">
          {error}
        </div>
      ) : (
        <div className="space-y-10">
          {/* Section 1: Methodology Guarantees */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-xl font-bold text-white">Statistical Integrity & Governance Invariants</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Non-negotiable data rules designed to eliminate false precision, opaque scoring, and fabricated metrics.
                </p>
              </div>
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded border border-emerald-800">
                Phase 12 Audited
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {methodology?.guarantees ? (
                methodology.guarantees.map((item, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 space-y-2 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-indigo-400 uppercase">
                        {item.rule_id}
                      </span>
                      <span className="text-[10px] bg-indigo-950 text-indigo-300 px-2 py-0.5 rounded font-mono">
                        Audited Rule
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-200">{item.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.description}</p>
                    <div className="text-[11px] font-mono text-emerald-400 bg-slate-900 px-2.5 py-1.5 rounded border border-slate-800 mt-2">
                      Constraint: {item.audit_rule}
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 text-xs text-slate-400">
                  Standard governance rules applied across all market intelligence aggregation pipelines.
                </div>
              )}
            </div>
          </div>

          {/* Section 2: Registered Market Data Sources */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 md:p-8 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-xl font-bold text-white">Registered Ingestion Sources</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Active pipelines feeding canonical opportunities and audited salary observations.
                </p>
              </div>
              <span className="text-xs font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                {sources.length} Registered Sources
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {sources.map((src) => (
                <div
                  key={src.id}
                  className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-sm font-bold text-white">{src.name}</h3>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase ${
                          src.is_active
                            ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                            : "bg-slate-800 text-slate-400 border-slate-700"
                        }`}
                      >
                        {src.is_active ? "Active" : "Paused"}
                      </span>
                    </div>

                    <div className="text-[11px] font-mono text-indigo-400 uppercase">
                      Type: {src.source_type}
                    </div>

                    <p className="text-xs text-slate-400 leading-relaxed">
                      {src.description || "Direct opportunity feeder for canonical ingestion."}
                    </p>
                  </div>

                  <div className="border-t border-slate-800 pt-3 space-y-1.5 text-xs text-slate-400">
                    <div className="flex justify-between">
                      <span>Ingestion Frequency:</span>
                      <span className="font-semibold text-slate-300">
                        {src.ingestion_frequency || "Daily Batch"}
                      </span>
                    </div>
                    {src.reliability_score !== undefined && src.reliability_score !== null && (
                      <div className="flex justify-between">
                        <span>Reliability Score:</span>
                        <span className="font-semibold text-emerald-400">
                          {Math.round(src.reliability_score * 100)}%
                        </span>
                      </div>
                    )}
                    {src.website_url && (
                      <div className="pt-1">
                        <a
                          href={src.website_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[11px] text-indigo-400 hover:underline flex items-center gap-1"
                        >
                          Source Documentation ↗
                        </a>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

