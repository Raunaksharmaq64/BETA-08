"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../../services/apiClient";

interface Education {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  achievements?: string;
  provenance: string;
}

interface Experience {
  id: string;
  company: string;
  role: string;
  employment_type: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  skills: string[];
  provenance: string;
}

interface Skill {
  id: string;
  skill_name: string;
  category: string;
  proficiency: string;
  years_experience?: number;
  provenance: string;
}

interface Profile {
  id: string;
  user_id: string;
  headline?: string;
  summary?: string;
  phone?: string;
  city?: string;
  state?: string;
  country?: string;
  timezone?: string;
  education: Education[];
  experience: Experience[];
  skills: Skill[];
}

interface CompletenessSectionImpact {
  section_key: string;
  section_name: string;
  is_completed: boolean;
  weight_percentage: number;
  why_it_matters: string;
  unlocks: string;
  is_required: boolean;
}

interface Completeness {
  score_percentage: number;
  has_basic_info: boolean;
  has_education: boolean;
  has_experience: boolean;
  has_skills: boolean;
  has_preferences: boolean;
  missing_sections: string[];
  section_breakdown?: CompletenessSectionImpact[];
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [completeness, setCompleteness] = useState<Completeness | null>(null);
  const [loading, setLoading] = useState(true);
  const [editingBasic, setEditingBasic] = useState(false);

  // Edit form state
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");

  // Modal forms
  const [showEduModal, setShowEduModal] = useState(false);
  const [eduInst, setEduInst] = useState("");
  const [eduDegree, setEduDegree] = useState("");
  const [eduField, setEduField] = useState("");

  const [showSkillModal, setShowSkillModal] = useState(false);
  const [skillName, setSkillName] = useState("");
  const [skillProf, setSkillProf] = useState("Intermediate");

  const loadData = async () => {
    try {
      const [pResp, cResp] = await Promise.all([
        apiClient<Profile>("/candidate/profile"),
        apiClient<Completeness>("/candidate/profile/completeness"),
      ]);
      setProfile(pResp.data);
      setCompleteness(cResp.data);
      setHeadline(pResp.data.headline || "");
      setSummary(pResp.data.summary || "");
      setCity(pResp.data.city || "");
      setCountry(pResp.data.country || "");
    } catch (err) {
      console.error("Failed to load profile:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSaveBasic = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const resp = await apiClient<Profile>("/candidate/profile", {
        method: "PUT",
        body: JSON.stringify({ headline, summary, city, country }),
      });
      setProfile(resp.data);
      setEditingBasic(false);
      loadData();
    } catch (err) {
      alert("Failed to update profile.");
    }
  };

  const handleAddEdu = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient("/candidate/education", {
        method: "POST",
        body: JSON.stringify({
          institution: eduInst,
          degree: eduDegree,
          field_of_study: eduField,
          provenance: "USER_PROVIDED",
        }),
      });
      setShowEduModal(false);
      setEduInst("");
      setEduDegree("");
      setEduField("");
      loadData();
    } catch (err) {
      alert("Failed to add education.");
    }
  };

  const handleDeleteEdu = async (id: string) => {
    if (!confirm("Delete this education entry?")) return;
    try {
      await apiClient(`/candidate/education/${id}`, { method: "DELETE" });
      loadData();
    } catch (err) {
      alert("Failed to delete entry.");
    }
  };

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient("/candidate/skills", {
        method: "POST",
        body: JSON.stringify({
          skill_name: skillName,
          proficiency: skillProf,
          provenance: "USER_PROVIDED",
        }),
      });
      setShowSkillModal(false);
      setSkillName("");
      loadData();
    } catch (err) {
      alert("Failed to add skill.");
    }
  };

  const handleDeleteSkill = async (id: string) => {
    try {
      await apiClient(`/candidate/skills/${id}`, { method: "DELETE" });
      loadData();
    } catch (err) {
      alert("Failed to delete skill.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-12 px-4 text-center text-slate-400">Loading profile...</div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Completeness Banner & Section Impact Unlocks */}
        {completeness && (
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <span className="text-sm font-semibold tracking-wide text-indigo-400 uppercase">
                  Profile Completeness & Matching Power
                </span>
                <p className="text-xs text-slate-400 mt-0.5">
                  Complete each section to activate high-precision semantic matching and compensation calibration.
                </p>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold text-white">{completeness.score_percentage}%</span>
              </div>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${completeness.score_percentage}%` }}
              />
            </div>

            {completeness.section_breakdown && completeness.section_breakdown.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
                {completeness.section_breakdown.map((sec) => (
                  <div
                    key={sec.section_key}
                    className={`p-3 rounded-xl border text-xs transition-all ${
                      sec.is_completed
                        ? "bg-slate-950/60 border-emerald-500/30 text-slate-300"
                        : "bg-slate-950/40 border-amber-500/30 text-slate-400"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-semibold text-white flex items-center gap-1.5">
                        {sec.is_completed ? (
                          <span className="text-emerald-400 font-bold">✓</span>
                        ) : (
                          <span className="text-amber-400 font-bold">○</span>
                        )}
                        {sec.section_name}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                        {sec.weight_percentage}% wt
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-300">
                      <span className="text-indigo-400 font-medium">Unlocks: </span>
                      {sec.unlocks}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {completeness.missing_sections.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2 items-center text-xs text-slate-400">
                <span>Next steps to unlock:</span>
                {completeness.missing_sections.map((sec) => (
                  <span key={sec} className="px-2.5 py-1 bg-amber-500/10 text-amber-300 rounded border border-amber-500/20">
                    + {sec}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Basic Personal Information */}
        <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-white">Basic Information</h2>
            <button
              onClick={() => setEditingBasic(!editingBasic)}
              className="text-xs font-semibold px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-indigo-400 border border-slate-700"
            >
              {editingBasic ? "Cancel" : "Edit Profile"}
            </button>
          </div>

          {editingBasic ? (
            <form onSubmit={handleSaveBasic} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Headline</label>
                <input
                  type="text"
                  value={headline}
                  onChange={(e) => setHeadline(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Summary</label>
                <textarea
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  rows={3}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">City</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 uppercase mb-1">Country</label>
                  <input
                    type="text"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                  />
                </div>
              </div>
              <button type="submit" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded text-sm font-medium">
                Save Changes
              </button>
            </form>
          ) : (
            <div className="space-y-2">
              <div className="text-xl font-bold text-white">{profile?.headline || "No headline configured"}</div>
              <p className="text-sm text-slate-300">{profile?.summary || "Add a career summary to highlight your strengths."}</p>
              <div className="text-xs text-slate-400 mt-2">
                Location: {profile?.city || "Remote"}, {profile?.country || "Global"}
              </div>
            </div>
          )}
        </section>

        {/* Education Credentials */}
        <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-white">Education Credentials</h2>
            <button
              onClick={() => setShowEduModal(true)}
              className="text-xs font-semibold px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              + Add Education
            </button>
          </div>

          <div className="space-y-3">
            {profile?.education && profile.education.length > 0 ? (
              profile.education.map((edu) => (
                <div key={edu.id} className="p-4 bg-slate-800/60 border border-slate-800 rounded-lg flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-white">{edu.institution}</h3>
                    <p className="text-sm text-indigo-300">{edu.degree} in {edu.field_of_study}</p>
                    <span className="inline-block mt-2 px-2 py-0.5 text-[10px] uppercase font-bold rounded bg-slate-800 text-slate-400 border border-slate-700">
                      Provenance: {edu.provenance}
                    </span>
                  </div>
                  <button
                    onClick={() => handleDeleteEdu(edu.id)}
                    className="text-xs text-red-400 hover:text-red-300"
                  >
                    Delete
                  </button>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400">No education credentials added yet.</p>
            )}
          </div>
        </section>

        {/* Skills Section */}
        <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-sm">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-bold text-white">Skills & Competencies</h2>
            <button
              onClick={() => setShowSkillModal(true)}
              className="text-xs font-semibold px-3 py-1.5 rounded bg-indigo-600 hover:bg-indigo-500 text-white"
            >
              + Add Skill
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {profile?.skills && profile.skills.length > 0 ? (
              profile.skills.map((skill) => (
                <span
                  key={skill.id}
                  className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-200 flex items-center space-x-2"
                >
                  <span className="font-medium">{skill.skill_name}</span>
                  <span className="text-xs text-indigo-400">({skill.proficiency})</span>
                  <button
                    onClick={() => handleDeleteSkill(skill.id)}
                    className="text-slate-400 hover:text-red-400 font-bold ml-1"
                  >
                    ×
                  </button>
                </span>
              ))
            ) : (
              <p className="text-sm text-slate-400">No skills listed yet.</p>
            )}
          </div>
        </section>

      {/* Add Education Modal */}
      {showEduModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 max-w-md w-full p-6 rounded-xl shadow-xl">
            <h3 className="text-lg font-bold text-white mb-4">Add Education Credential</h3>
            <form onSubmit={handleAddEdu} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Institution</label>
                <input
                  type="text"
                  required
                  value={eduInst}
                  onChange={(e) => setEduInst(e.target.value)}
                  placeholder="e.g. Stanford University"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Degree</label>
                <input
                  type="text"
                  required
                  value={eduDegree}
                  onChange={(e) => setEduDegree(e.target.value)}
                  placeholder="e.g. B.S."
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Field of Study</label>
                <input
                  type="text"
                  required
                  value={eduField}
                  onChange={(e) => setEduField(e.target.value)}
                  placeholder="e.g. Computer Science"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowEduModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium"
                >
                  Save Credential
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Skill Modal */}
      {showSkillModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-700 max-w-sm w-full p-6 rounded-xl shadow-xl">
            <h3 className="text-lg font-bold text-white mb-4">Add Skill</h3>
            <form onSubmit={handleAddSkill} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Skill Name</label>
                <input
                  type="text"
                  required
                  value={skillName}
                  onChange={(e) => setSkillName(e.target.value)}
                  placeholder="e.g. TypeScript"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Proficiency</label>
                <select
                  value={skillProf}
                  onChange={(e) => setSkillProf(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Expert">Expert</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowSkillModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium"
                >
                  Add Skill
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

