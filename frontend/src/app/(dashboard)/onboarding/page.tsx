"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Navbar from "../../../components/layout/Navbar";
import { apiClient } from "../../../services/apiClient";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);

  // Step 1: Basic
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [city, setCity] = useState("");

  // Step 2: Skills
  const [skills, setSkills] = useState("");

  // Step 3: Preferences
  const [roles, setRoles] = useState("");
  const [remotePref, setRemotePref] = useState("REMOTE");

  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Final submission
      setLoading(true);
      try {
        await apiClient("/candidate/profile", {
          method: "PUT",
          body: JSON.stringify({ headline, summary, city }),
        });
        const skillList = skills.split(",").map((s) => s.trim()).filter(Boolean);
        for (const s of skillList) {
          await apiClient("/candidate/skills", {
            method: "POST",
            body: JSON.stringify({ skill_name: s, proficiency: "Intermediate" }),
          });
        }
        const roleList = roles.split(",").map((r) => r.trim()).filter(Boolean);
        await apiClient("/candidate/preferences", {
          method: "PUT",
          body: JSON.stringify({
            preferred_roles: roleList,
            remote_preference: remotePref,
          }),
        });
        router.push("/profile");
      } catch (err) {
        alert("Failed to complete onboarding.");
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <Navbar />

      <main className="max-w-2xl mx-auto py-12 px-4 sm:px-6">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-xl shadow-lg">
          <div className="mb-6 flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Step {step} of 3</span>
              <h1 className="text-xl font-bold text-white mt-1">
                {step === 1 && "Personal & Professional Overview"}
                {step === 2 && "Core Technical Skills"}
                {step === 3 && "Career Preferences & Discovery"}
              </h1>
            </div>
          </div>

          {step === 1 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Professional Headline
                </label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  placeholder="e.g. Senior Backend Engineer"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Summary & Impact
                </label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={4}
                  placeholder="Describe your technical background..."
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">City</label>
                <input
                  type="text"
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="e.g. San Francisco"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Key Skills (Comma-separated)
                </label>
                <input
                  type="text"
                  value={skills}
                  onChange={(e) => setSkills(e.target.value)}
                  placeholder="Python, FastAPI, PostgreSQL, Docker"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                />
                <p className="text-xs text-slate-400 mt-2">
                  Enter your core competencies to train the matching intelligence engine.
                </p>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Target Job Titles (Comma-separated)
                </label>
                <input
                  type="text"
                  value={roles}
                  onChange={(e) => setRoles(e.target.value)}
                  placeholder="Backend Engineer, Systems Architect"
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Workplace Preference
                </label>
                <select
                  value={remotePref}
                  onChange={(e) => setRemotePref(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
                >
                  <option value="REMOTE">Remote Only</option>
                  <option value="HYBRID">Hybrid</option>
                  <option value="ON_SITE">On-Site</option>
                  <option value="ANY">Any Arrangement</option>
                </select>
              </div>
            </div>
          )}

          <div className="flex justify-between items-center mt-8 pt-4 border-t border-slate-800">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-white"
              >
                Back
              </button>
            ) : <div />}

            <button
              type="button"
              onClick={handleNext}
              disabled={loading}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium text-sm transition-colors"
            >
              {loading ? "Saving..." : step === 3 ? "Complete Onboarding" : "Continue"}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
