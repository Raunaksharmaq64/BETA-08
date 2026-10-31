"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface NotificationPreferences {
  application_updates: boolean;
  reminders: boolean;
  interview_rounds: boolean;
  saved_searches: boolean;
  email_enabled: boolean;
  in_app_enabled: boolean;
  quiet_hours_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  timezone?: string;
}

export default function NotificationPreferencesPage() {
  const { user } = useAuth();

  const [prefs, setPrefs] = useState<NotificationPreferences>({
    application_updates: true,
    reminders: true,
    interview_rounds: true,
    saved_searches: true,
    email_enabled: true,
    in_app_enabled: true,
    quiet_hours_enabled: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState("");

  const fetchPrefs = async () => {
    setLoading(true);
    try {
      const res = await apiClient<NotificationPreferences>("/notifications/preferences");
      if (res.data) setPrefs(res.data);
    } catch (err: any) {
      console.error("Failed to load notification preferences:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchPrefs();
    }
  }, [user]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg("");
    try {
      await apiClient("/notifications/preferences", {
        method: "PUT",
        body: JSON.stringify(prefs),
      });
      setSuccessMsg("Notification preferences saved successfully.");
      setTimeout(() => setSuccessMsg(""), 3500);
    } catch (err: any) {
      alert(err.message || "Failed to update preferences.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-2 text-xs text-slate-400 mb-1">
          <Link href="/notifications" className="hover:text-white">
            &larr; Notifications Center
          </Link>
        </div>
        <h1 className="text-2xl font-bold text-white">Notification Preferences</h1>
        <p className="text-xs text-slate-400 mt-1">
          Control which categories of alerts you receive and manage channel deliveries.
        </p>
      </div>

      {successMsg && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs rounded-xl">
          ✓ {successMsg}
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-slate-400 text-xs">Loading preferences...</div>
      ) : (
        <form onSubmit={handleSave} className="space-y-6">
          {/* Categories */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Notification Categories
            </h2>

            <div className="space-y-3">
              {[
                {
                  key: "application_updates" as const,
                  title: "Application Updates",
                  desc: "Status transitions, submission confirmations, and recruiter updates.",
                },
                {
                  key: "reminders" as const,
                  title: "Task Reminders",
                  desc: "Due date alerts for application deadlines and scheduled tasks.",
                },
                {
                  key: "interview_rounds" as const,
                  title: "Interview Rounds & 48-Hour Sprint",
                  desc: "Upcoming interview alerts, sprint milestones, and prep checklists.",
                },
                {
                  key: "saved_searches" as const,
                  title: "Saved Search Matches",
                  desc: "Verified fresh job alerts matching your personal search criteria.",
                },
              ].map((item) => (
                <label
                  key={item.key}
                  className="flex items-start justify-between p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 cursor-pointer hover:border-slate-700 transition"
                >
                  <div className="pr-4">
                    <div className="text-sm font-semibold text-white">{item.title}</div>
                    <div className="text-xs text-slate-400 mt-0.5">{item.desc}</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={prefs[item.key]}
                    onChange={(e) =>
                      setPrefs((prev) => ({ ...prev, [item.key]: e.target.checked }))
                    }
                    className="mt-1 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                  />
                </label>
              ))}
            </div>
          </div>

          {/* Delivery Channels */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Delivery Channels
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 cursor-pointer">
                <div>
                  <div className="text-sm font-semibold text-white">In-App Notifications</div>
                  <div className="text-xs text-slate-400">Banner & bell badges</div>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.in_app_enabled}
                  onChange={(e) =>
                    setPrefs((prev) => ({ ...prev, in_app_enabled: e.target.checked }))
                  }
                  className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                />
              </label>

              <label className="flex items-center justify-between p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 cursor-pointer">
                <div>
                  <div className="text-sm font-semibold text-white">Email Notifications</div>
                  <div className="text-xs text-slate-400">Digest to verified address</div>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.email_enabled}
                  onChange={(e) =>
                    setPrefs((prev) => ({ ...prev, email_enabled: e.target.checked }))
                  }
                  className="rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                />
              </label>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2.5 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50 transition"
            >
              {saving ? "Saving Changes..." : "Save Preferences"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

