"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface SavedSearch {
  id: string;
  user_id: string;
  name: string;
  query_json: Record<string, any>;
  filters_json: Record<string, any>;
  alert_enabled: boolean;
  alert_frequency: string;
  last_notified_at?: string;
  created_at: string;
  updated_at: string;
}

export default function SavedSearchesPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [searches, setSearches] = useState<SavedSearch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [runningAlerts, setRunningAlerts] = useState(false);
  const [alertSuccessMsg, setAlertSuccessMsg] = useState<string | null>(null);

  const fetchSearches = async () => {
    setIsLoading(true);
    try {
      const res = await apiClient<SavedSearch[]>("/saved-searches");
      setSearches(res.data || []);
    } catch (err: any) {
      console.error("Failed to load saved searches:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      fetchSearches();
    }
  }, [user, authLoading]);

  const handleToggleAlert = async (search: SavedSearch) => {
    const nextState = !search.alert_enabled;
    try {
      await apiClient(`/saved-searches/${search.id}`, {
        method: "PATCH",
        body: JSON.stringify({ alert_enabled: nextState }),
      });
      setSearches((prev) =>
        prev.map((s) => (s.id === search.id ? { ...s, alert_enabled: nextState } : s))
      );
    } catch (err: any) {
      alert("Failed to toggle alert status: " + err.message);
    }
  };

  const handleChangeFrequency = async (searchId: string, newFrequency: string) => {
    try {
      await apiClient(`/saved-searches/${searchId}`, {
        method: "PATCH",
        body: JSON.stringify({ alert_frequency: newFrequency }),
      });
      setSearches((prev) =>
        prev.map((s) => (s.id === searchId ? { ...s, alert_frequency: newFrequency } : s))
      );
    } catch (err: any) {
      alert("Failed to update frequency: " + err.message);
    }
  };

  const handleDelete = async (searchId: string) => {
    if (!confirm("Delete this saved search and its alert notifications?")) return;
    try {
      await apiClient(`/saved-searches/${searchId}`, { method: "DELETE" });
      setSearches((prev) => prev.filter((s) => s.id !== searchId));
    } catch (err: any) {
      alert("Failed to delete saved search: " + err.message);
    }
  };

  const handleTestAlerts = async () => {
    setRunningAlerts(true);
    setAlertSuccessMsg(null);
    try {
      const res = await apiClient<any[]>("/saved-searches/run-alerts", { method: "POST" });
      const deliveredCount = res.data?.length || 0;
      setAlertSuccessMsg(
        deliveredCount > 0
          ? `Alert worker executed: delivered ${deliveredCount} notification(s).`
          : "Alert worker executed: no newly ingested listings since last check."
      );
      setTimeout(() => setAlertSuccessMsg(null), 4000);
      fetchSearches();
    } catch (err: any) {
      alert("Alert check failed: " + err.message);
    } finally {
      setRunningAlerts(false);
    }
  };

  const buildSearchLink = (search: SavedSearch) => {
    const params = new URLSearchParams();
    if (search.query_json?.query) params.set("q", search.query_json.query);
    const f = search.filters_json || {};
    if (f.role) params.set("role", f.role);
    if (f.company) params.set("company", f.company);
    if (f.city) params.set("city", f.city);
    if (f.is_remote) params.set("remote", "true");
    if (f.verification_status) params.set("verification", f.verification_status);
    return `/search?${params.toString()}`;
  };

  if (authLoading || isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-slate-800 rounded w-1/4" />
          <div className="h-28 bg-slate-900 rounded-2xl border border-slate-800" />
          <div className="h-28 bg-slate-900 rounded-2xl border border-slate-800" />
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Saved Searches & Alerts</h1>
          <p className="text-sm text-slate-400 mt-1">
            Configure automated notifications for tailored searches so you never miss a verified match.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleTestAlerts}
            disabled={runningAlerts}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-indigo-300 border border-slate-700 text-xs font-semibold transition-colors disabled:opacity-50"
          >
            {runningAlerts ? "Evaluating..." : "Check Alerts Now"}
          </button>
          <Link
            href="/search"
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold transition-colors"
          >
            Create Search →
          </Link>
        </div>
      </div>

      {alertSuccessMsg && (
        <div className="p-3.5 rounded-xl bg-emerald-950/60 border border-emerald-800/60 text-emerald-300 text-xs">
          {alertSuccessMsg}
        </div>
      )}

      {/* Searches List */}
      {searches.length === 0 ? (
        <div className="text-center py-16 bg-slate-900/40 rounded-2xl border border-slate-800 space-y-3">
          <div className="text-4xl">🔔</div>
          <h3 className="text-base font-semibold text-white">No saved searches yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Set up filters in Job Discovery and click &quot;Save Search & Alerts&quot; to receive scheduled notifications.
          </p>
          <div className="pt-2">
            <Link
              href="/search"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold inline-block"
            >
              Configure First Search
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {searches.map((search) => (
            <div
              key={search.id}
              className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4 hover:border-slate-700 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <h3 className="text-lg font-bold text-white">{search.name}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-400 flex-wrap">
                    {search.query_json?.query && (
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 font-medium">
                        Query: &quot;{search.query_json.query}&quot;
                      </span>
                    )}
                    {Object.entries(search.filters_json || {}).map(([k, v]) => (
                      <span key={k} className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                        {k}: {String(v)}
                      </span>
                    ))}
                    <span>•</span>
                    <span>Created: {new Date(search.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <Link
                    href={buildSearchLink(search)}
                    className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors"
                  >
                    Run Search →
                  </Link>
                  <button
                    onClick={() => handleDelete(search.id)}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-rose-950/40 text-slate-400 hover:text-rose-300 border border-slate-700 hover:border-rose-800/60 text-xs font-semibold rounded-lg transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>

              {/* Alert Subscription Controls */}
              <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4 text-xs">
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={search.alert_enabled}
                      onChange={() => handleToggleAlert(search)}
                      className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className={search.alert_enabled ? "text-emerald-300 font-medium" : "text-slate-400"}>
                      {search.alert_enabled ? "Alerts Active" : "Alerts Paused"}
                    </span>
                  </label>
                </div>

                <div className="flex items-center gap-2 text-slate-400">
                  <span>Frequency:</span>
                  <select
                    value={search.alert_frequency}
                    onChange={(e) => handleChangeFrequency(search.id, e.target.value)}
                    className="px-2 py-1 bg-slate-950 rounded border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
                  >
                    <option value="INSTANT">Instant Delivery</option>
                    <option value="DAILY">Daily Digest</option>
                    <option value="WEEKLY">Weekly Summary</option>
                  </select>
                </div>

                {search.last_notified_at && (
                  <div className="text-slate-500">
                    Last notification: {new Date(search.last_notified_at).toLocaleString()}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

