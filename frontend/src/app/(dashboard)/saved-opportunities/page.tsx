"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SavedEnvelope {
  schema_version: string;
  opportunity_id: string;
  opportunity_type: "JOB" | "FREELANCE" | "STARTUP_PAIN_POINT";
  title: string;
  short_description: string;
  organization_name: string;
  source_service: string;
  source_name: string;
  source_url?: string;
  location?: string;
  saved_id?: string;
  saved_notes?: string;
  saved_at?: string;
  type_specific_payload: any;
}

export default function UnifiedSavedOpportunitiesPage() {
  const [savedItems, setSavedItems] = useState<SavedEnvelope[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("ALL");

  const fetchSaved = async () => {
    setLoading(true);
    setError(null);
    try {
      const res: any = await apiClient.get("/opportunities/saved/all");
      setSavedItems(res.data || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load saved opportunities.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (item: SavedEnvelope) => {
    setRemovingId(item.opportunity_id);
    try {
      await apiClient.delete(`/opportunities/${item.opportunity_type}/${item.opportunity_id}/save`);
      setSavedItems(savedItems.filter((i) => i.opportunity_id !== item.opportunity_id));
    } catch (err: any) {
      alert(err?.message || "Failed to remove bookmark.");
    } finally {
      setRemovingId(null);
    }
  };

  const filteredItems = savedItems.filter((i) => {
    if (filterType === "ALL") return true;
    return i.opportunity_type === filterType;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
            Saved Pipeline Bookmarks
          </h1>
          <p className="mt-2 text-sm text-slate-400">
            Unified candidate bookmarks across Full-Time Jobs, Freelance Opportunities, and Startup Signals.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-semibold text-slate-200 border border-slate-700 transition-colors"
          >
            ← Back to Dashboard
          </Link>
          <Link
            href="/opportunities"
            className="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            Explore More Opportunities →
          </Link>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { id: "ALL", label: "All Saved", count: savedItems.length },
          { id: "JOB", label: "Jobs", count: savedItems.filter((i) => i.opportunity_type === "JOB").length },
          { id: "FREELANCE", label: "Freelance", count: savedItems.filter((i) => i.opportunity_type === "FREELANCE").length },
          {
            id: "STARTUP_PAIN_POINT",
            label: "Startup Signals",
            count: savedItems.filter((i) => i.opportunity_type === "STARTUP_PAIN_POINT").length,
          },
        ].map((tab) => {
          const isActive = filterType === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
                isActive
                  ? "bg-indigo-600 text-white shadow"
                  : "bg-slate-900 text-slate-400 hover:bg-slate-800 border border-slate-800"
              }`}
            >
              <span>{tab.label}</span>
              <span className={`px-1.5 py-0.2 rounded-full text-[10px] ${isActive ? "bg-indigo-800 text-indigo-200" : "bg-slate-800"}`}>
                {tab.count}
              </span>
            </button>
          );
        })}
      </div>

      {error && (
        <div className="p-4 rounded-xl border border-rose-800/60 bg-rose-950/40 text-sm text-rose-300">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-48 rounded-xl bg-slate-900 border border-slate-800" />
          ))}
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="text-center py-16 rounded-xl bg-slate-900 border border-slate-800 text-slate-400">
          <p className="text-base font-medium text-slate-300">No saved bookmarks in this category.</p>
          <p className="text-xs text-slate-500 mt-1">Bookmark opportunities from the Unified Pipeline or Dashboard to review them later.</p>
          <div className="mt-4">
            <Link
              href="/opportunities"
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
            >
              Browse pipeline now →
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item) => {
            const isJob = item.opportunity_type === "JOB";
            const isFreelance = item.opportunity_type === "FREELANCE";

            const badgeColor = isJob
              ? "bg-blue-950 text-blue-300 border-blue-800"
              : isFreelance
              ? "bg-emerald-950 text-emerald-300 border-emerald-800"
              : "bg-purple-950 text-purple-300 border-purple-800";

            const badgeText = isJob ? "Full-Time Job" : isFreelance ? "Freelance Lead" : "Startup Signal";

            return (
              <div
                key={`${item.opportunity_type}-${item.opportunity_id}`}
                className="p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 flex flex-col justify-between transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeColor}`}>
                      {badgeText}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">
                      {item.source_name}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-white line-clamp-2">
                      {item.title}
                    </h3>
                    <div className="text-xs font-medium text-indigo-400 mt-0.5">
                      {item.organization_name}
                      {item.location && <span className="text-slate-400"> • {item.location}</span>}
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                    {item.short_description}
                  </p>

                  {item.saved_notes && (
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-xs text-amber-300/90 font-sans">
                      <span className="text-slate-500 font-semibold uppercase text-[10px] block mb-0.5">Note:</span>
                      {item.saved_notes}
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                  <button
                    onClick={() => handleUnsave(item)}
                    disabled={removingId === item.opportunity_id}
                    className="text-xs font-semibold px-2.5 py-1 rounded bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-800 transition-colors"
                  >
                    {removingId === item.opportunity_id ? "Removing..." : "Remove Bookmark"}
                  </button>

                  {item.source_url ? (
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
                    >
                      Visit / Apply →
                    </a>
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

