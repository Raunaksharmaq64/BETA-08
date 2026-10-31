"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface NotificationPreferences {
  in_app_enabled: boolean;
  email_enabled: boolean;
  interview_reminders: boolean;
  application_follow_ups: boolean;
  assessment_deadlines: boolean;
  prep_milestones: boolean;
  frequency: string; // INSTANT, DAILY_DIGEST, WEEKLY_DIGEST
  quiet_hours_start: string;
  quiet_hours_end: string;
  timezone: string;
  job_alerts_enabled: boolean;
  digest_email_enabled: boolean;
  market_intelligence_alerts: boolean;
}

export default function NotificationPreferencesPage() {
  const { user } = useAuth();

  const [prefs, setPrefs] = useState<NotificationPreferences>({
    in_app_enabled: true,
    email_enabled: false,
    interview_reminders: true,
    application_follow_ups: true,
    assessment_deadlines: true,
    prep_milestones: true,
    frequency: "DAILY_DIGEST",
    quiet_hours_start: "22:00",
    quiet_hours_end: "08:00",
    timezone: "UTC",
    job_alerts_enabled: true,
    digest_email_enabled: false,
    market_intelligence_alerts: true,
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
        method: "PATCH",
        body: JSON.stringify(prefs),
      });
      setSuccessMsg("Notification preferences and quiet hours saved successfully.");
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
        <h1 className="text-2xl font-bold text-white">Smart Notification Settings</h1>
        <p className="text-xs text-slate-400 mt-1">
          Control notification frequencies, quiet hours, delivery channels, and opportunity alerts.
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
          {/* Notification Frequency & Schedule */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Delivery Frequency & Quiet Hours
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                {
                  id: "INSTANT",
                  label: "Instant Alerts",
                  desc: "Immediate push for high-confidence jobs and interview milestones",
                },
                {
                  id: "DAILY_DIGEST",
                  label: "Daily Digest (Recommended)",
                  desc: "Single consolidated briefing delivered once every morning",
                },
                {
                  id: "WEEKLY_DIGEST",
                  label: "Weekly Summary",
                  desc: "Weekend recap of verified market movements and applications",
                },
              ].map((f) => (
                <div
                  key={f.id}
                  onClick={() => setPrefs({ ...prefs, frequency: f.id })}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    prefs.frequency === f.id
                      ? "bg-indigo-950/50 border-indigo-500 text-white"
                      : "bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-300"
                  }`}
                >
                  <div className="font-semibold text-xs mb-1">{f.label}</div>
                  <div className="text-[11px] text-slate-400">{f.desc}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Quiet Hours Start</label>
                <input
                  type="time"
                  value={prefs.quiet_hours_start || "22:00"}
                  onChange={(e) => setPrefs({ ...prefs, quiet_hours_start: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Quiet Hours End</label>
                <input
                  type="time"
                  value={prefs.quiet_hours_end || "08:00"}
                  onChange={(e) => setPrefs({ ...prefs, quiet_hours_end: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Timezone</label>
                <select
                  value={prefs.timezone || "UTC"}
                  onChange={(e) => setPrefs({ ...prefs, timezone: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white"
                >
                  <option value="UTC">UTC</option>
                  <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                  <option value="America/New_York">America/New_York (EST)</option>
                  <option value="America/Los_Angeles">America/Los_Angeles (PST)</option>
                  <option value="Europe/London">Europe/London (GMT)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Alert Categories */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Notification Categories
            </h2>

            <div className="space-y-3">
              {[
                {
                  key: "job_alerts_enabled" as const,
                  title: "Smart Opportunity & Job Match Alerts",
                  desc: "New verified opportunities matching your skill evidence and calibrated preferences.",
                },
                {
                  key: "market_intelligence_alerts" as const,
                  title: "Market Intelligence & Salary Shifts",
                  desc: "Significant compensation changes and trending skills in your target role categories.",
                },
                {
                  key: "interview_reminders" as const,
                  title: "Interview Rounds & 48-Hour Sprint",
                  desc: "Sprint milestones, round checklists, and interview time reminders.",
                },
                {
                  key: "application_follow_ups" as const,
                  title: "Application Updates & Follow-ups",
                  desc: "Status transitions, submission confirmations, and recommended follow-up dates.",
                },
                {
                  key: "assessment_deadlines" as const,
                  title: "Assessment & Take-Home Deadlines",
                  desc: "Countdown alerts for pending technical assignments and coding challenges.",
                },
                {
                  key: "prep_milestones" as const,
                  title: "Career Learning Milestones",
                  desc: "Skill gap progression and weekly skill roadmap achievements.",
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
                    checked={Boolean(prefs[item.key])}
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
                  <div className="text-xs text-slate-400">Bell badge & notification inbox</div>
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
                  <div className="text-sm font-semibold text-white">Email Digest</div>
                  <div className="text-xs text-slate-400">Consolidated updates to your verified email</div>
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
