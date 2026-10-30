"use client";

import React, { useEffect, useState } from "react";
import Navbar from "../../../components/layout/Navbar";
import { apiClient } from "../../../services/apiClient";

interface Preferences {
  preferred_roles: string[];
  preferred_skills: string[];
  preferred_industries: string[];
  preferred_locations: string[];
  remote_preference: "REMOTE" | "HYBRID" | "ON_SITE" | "ANY";
  min_salary?: number;
  max_salary?: number;
  currency: string;
  employment_types: string[];
  job_notification_frequency: string;
}

export default function PreferencesPage() {
  const [roles, setRoles] = useState("");
  const [skills, setSkills] = useState("");
  const [remotePref, setRemotePref] = useState<"REMOTE" | "HYBRID" | "ON_SITE" | "ANY">("ANY");
  const [minSalary, setMinSalary] = useState<number | "">("");
  const [currency, setCurrency] = useState("USD");
  const [notificationFreq, setNotificationFreq] = useState("DAILY");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function loadPreferences() {
      try {
        const resp = await apiClient<Preferences>("/candidate/preferences");
        const data = resp.data;
        setRoles(data.preferred_roles.join(", "));
        setSkills(data.preferred_skills.join(", "));
        setRemotePref(data.remote_preference);
        setMinSalary(data.min_salary || "");
        setCurrency(data.currency || "USD");
        setNotificationFreq(data.job_notification_frequency || "DAILY");
      } catch (err) {
        console.error("Failed to load preferences:", err);
      } finally {
        setLoading(false);
      }
    }
    loadPreferences();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      await apiClient("/candidate/preferences", {
        method: "PUT",
        body: JSON.stringify({
          preferred_roles: roles.split(",").map((r) => r.trim()).filter(Boolean),
          preferred_skills: skills.split(",").map((s) => s.trim()).filter(Boolean),
          preferred_industries: [],
          preferred_locations: [],
          remote_preference: remotePref,
          min_salary: minSalary === "" ? null : Number(minSalary),
          currency,
          employment_types: ["Full-time"],
          job_notification_frequency: notificationFreq,
        }),
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert("Failed to save preferences.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <Navbar />
        <div className="max-w-4xl mx-auto py-12 px-4 text-center">Loading preferences...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />

      <main className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-lg">
          <div className="mb-6 border-b border-slate-800 pb-4">
            <h1 className="text-xl font-bold text-white">Career & Opportunity Preferences</h1>
            <p className="text-sm text-slate-400 mt-1">
              Customize your match criteria across Core ATS jobs, Freelance leads, and Startup bottlenecks.
            </p>
          </div>

          {savedSuccess && (
            <div className="mb-6 p-4 bg-emerald-950/80 border border-emerald-500/50 rounded-lg text-sm text-emerald-200">
              Preferences successfully updated and synchronized!
            </div>
          )}

          <form onSubmit={handleSave} className="space-y-6">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                Preferred Job Roles (Comma-separated)
              </label>
              <input
                type="text"
                value={roles}
                onChange={(e) => setRoles(e.target.value)}
                placeholder="Staff Backend Engineer, Python Architect"
                className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                Preferred Skills to Target (Comma-separated)
              </label>
              <input
                type="text"
                value={skills}
                onChange={(e) => setSkills(e.target.value)}
                placeholder="FastAPI, PostgreSQL, Redis, Kubernetes"
                className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Work Arrangement
                </label>
                <select
                  value={remotePref}
                  onChange={(e) => setRemotePref(e.target.value as any)}
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="REMOTE">Remote Only</option>
                  <option value="HYBRID">Hybrid</option>
                  <option value="ON_SITE">On-Site</option>
                  <option value="ANY">Any Arrangement</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Opportunity Alerts Frequency
                </label>
                <select
                  value={notificationFreq}
                  onChange={(e) => setNotificationFreq(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="IMMEDIATE">Immediate Alert</option>
                  <option value="DAILY">Daily Digest</option>
                  <option value="WEEKLY">Weekly Summary</option>
                  <option value="NEVER">Do Not Send Alerts</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Minimum Expected Compensation
                </label>
                <input
                  type="number"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value === "" ? "" : Number(e.target.value))}
                  placeholder="e.g. 150000"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-2">
                  Currency (ISO 4217)
                </label>
                <input
                  type="text"
                  maxLength={3}
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value.toUpperCase())}
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-slate-800 flex justify-end">
              <button
                type="submit"
                disabled={saving}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-lg text-sm transition-colors"
              >
                {saving ? "Saving..." : "Save Preferences"}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

