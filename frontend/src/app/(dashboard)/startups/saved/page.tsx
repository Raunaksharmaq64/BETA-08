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
    <div className="space-y-6 max-w-5xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Saved Startup Opportunities
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Bookmarked pain points and technical signals for follow-up and custom proposals.
          </p>
        </div>
        <Link
          href="/startups"
          className="px-4 py-2 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 shadow-sm"
        >
          &larr; Discover More Startups
        </Link>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-500">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
          Loading bookmarks...
        </div>
      ) : error ? (
        <div className="p-6 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm">
          {error}
        </div>
      ) : savedItems.length === 0 ? (
        <div className="p-12 bg-white rounded-xl border border-slate-200 text-center">
          <p className="text-base font-semibold text-slate-700">No saved opportunities yet</p>
          <p className="text-xs text-slate-500 mt-1">
            Browse the Startup Intelligence directory and click &quot;Bookmark&quot; on relevant pain points.
          </p>
          <Link
            href="/startups"
            className="mt-4 inline-block px-4 py-2 text-xs font-semibold text-indigo-600 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100"
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
                className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700">
                      {opp.category}
                    </span>
                    <span className="text-xs font-bold text-rose-600">
                      Urgency {opp.urgency_score}/10
                    </span>
                    <span className="text-xs text-slate-400">Source: {opp.primary_source}</span>
                  </div>
                  <h3 className="font-bold text-slate-900 text-base">{opp.startup_name}</h3>
                  <p className="text-xs text-slate-700 line-clamp-2">{opp.detected_signal}</p>
                  {item.notes && (
                    <p className="text-xs text-indigo-600 italic mt-1">
                      Note: &ldquo;{item.notes}&rdquo;
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    href={`/startups/${opp.id}`}
                    className="px-3 py-2 text-xs font-semibold text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200"
                  >
                    View Details
                  </Link>
                  <Link
                    href={`/startups/${opp.id}/pitch`}
                    className="px-3 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
                  >
                    Draft Pitch
                  </Link>
                  <button
                    onClick={() => handleUnsave(opp.id)}
                    className="px-3 py-2 text-xs font-semibold text-rose-600 bg-rose-50 border border-rose-200 rounded-lg hover:bg-rose-100"
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

