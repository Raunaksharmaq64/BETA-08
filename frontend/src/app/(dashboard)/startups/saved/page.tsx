"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SavedStartupItem {
  saved_id: string;
  notes?: string;
  saved_at: string;
  opportunity: {
    id: string;
    startup_name: string;
    domain?: string;
    website_url?: string;
    category: string;
    detected_signal: string;
    urgency_score: number;
    primary_source: string;
  };
}

export default function SavedStartupOpportunitiesPage() {
  const [savedItems, setSavedItems] = useState<SavedStartupItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSaved = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<any>("/startups/saved/all");
      setSavedItems(res.data || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load saved startup opportunities.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (oppId: string) => {
    try {
      await apiClient.delete(`/startups/${oppId}/save`);
      setSavedItems((prev) => prev.filter((item) => item.opportunity.id !== oppId));
    } catch (err: any) {
      alert("Failed to remove bookmark: " + (err?.message || "Error"));
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Saved Startup Opportunities
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Bookmarked pain points and technical signals for follow-up and custom proposals.
          </p>
        </div>
        <Link
          href="/startups"
          className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 shadow-sm transition shrink-0"
        >
          &larr; Discover More Startups
        </Link>
      </div>

      {loading ? (
        <div className="p-16 text-center text-slate-400">
          <div className="w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          Loading bookmarks...
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-sm">
          {error}
        </div>
      ) : savedItems.length === 0 ? (
        <div className="p-16 bg-slate-900 border border-slate-800 rounded-xl text-center">
          <p className="text-base font-semibold text-slate-300">No saved opportunities yet</p>
          <p className="text-xs text-slate-500 mt-1">
            Browse the Startup Intelligence directory and click &quot;Bookmark&quot; on relevant pain points.
          </p>
          <Link
            href="/startups"
            className="mt-4 inline-block px-4 py-2 text-xs font-semibold text-indigo-400 bg-indigo-950/60 border border-indigo-800 rounded-lg hover:bg-indigo-900/60 transition"
          >
            Explore Directory
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {savedItems.map((item) => {
            const opp = item.opportunity;
            return (
              <div
                key={item.saved_id}
                className="p-5 bg-slate-900 rounded-xl border border-slate-800 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition"
              >
                <div className="space-y-1.5 max-w-2xl">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-800">
                      {opp.category}
                    </span>
                    <span className="text-[10px] font-bold text-rose-400 px-2 py-0.5 rounded bg-rose-950/60 border border-rose-800/60">
                      Urgency {opp.urgency_score}/10
                    </span>
                    <span className="text-xs text-slate-400">Source: {opp.primary_source}</span>
                  </div>
                  <h3 className="font-bold text-white text-base">{opp.startup_name}</h3>
                  <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">{opp.detected_signal}</p>
                  {item.notes && (
                    <p className="text-xs text-indigo-400 italic mt-1">
                      Note: &ldquo;{item.notes}&rdquo;
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2 shrink-0 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800">
                  <Link
                    href={`/startups/${opp.id}`}
                    className="px-3 py-1.5 text-xs font-semibold text-slate-200 bg-slate-800 rounded-lg hover:bg-slate-700 border border-slate-700 transition"
                  >
                    View Details
                  </Link>
                  <Link
                    href={`/startups/${opp.id}/pitch`}
                    className="px-3 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition"
                  >
                    Draft Pitch
                  </Link>
                  <button
                    onClick={() => handleUnsave(opp.id)}
                    className="px-3 py-1.5 text-xs font-semibold text-rose-300 bg-rose-950/60 border border-rose-800/60 rounded-lg hover:bg-rose-900/60 transition"
                  >
                    Remove
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
