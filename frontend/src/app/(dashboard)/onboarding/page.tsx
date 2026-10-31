"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "../../../components/layout/Navbar";
import { apiClient } from "../../../services/apiClient";

interface SkillItem {
  name: string;
  category: string;
  proficiency: "Beginner" | "Intermediate" | "Expert";
}

interface ProjectItem {
  title: string;
  role: string;
  description: string;
  link: string;
}

const POPULAR_SKILLS = [
  { name: "Python", category: "Backend" },
  { name: "TypeScript", category: "Frontend" },
  { name: "React", category: "Frontend" },
  { name: "Next.js", category: "Frontend" },
  { name: "FastAPI", category: "Backend" },
  { name: "Node.js", category: "Backend" },
  { name: "PostgreSQL", category: "Database" },
  { name: "Docker", category: "DevOps" },
  { name: "AWS", category: "DevOps" },
  { name: "TailwindCSS", category: "Frontend" },
  { name: "Git", category: "Tools" },
  { name: "Machine Learning", category: "AI/ML" },
];

const POPULAR_ROLES = [
  "Backend Engineer",
  "Full Stack Engineer",
  "Frontend Engineer",
  "DevOps Engineer",
  "Software Engineer Intern",
  "Data Engineer",
  "AI Engineer",
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Step 1: Personal & Education (Crucial for cold start)
  const [headline, setHeadline] = useState("");
  const [summary, setSummary] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("India");
  const [institution, setInstitution] = useState("");
  const [degree, setDegree] = useState("");
  const [fieldOfStudy, setFieldOfStudy] = useState("");
  const [gradYear, setGradYear] = useState("");

  // Step 2: Categorized Skills
  const [skillsList, setSkillsList] = useState<SkillItem[]>([
    { name: "Python", category: "Backend", proficiency: "Intermediate" },
    { name: "FastAPI", category: "Backend", proficiency: "Intermediate" },
  ]);
  const [newSkillName, setNewSkillName] = useState("");
  const [newSkillCategory, setNewSkillCategory] = useState("Backend");
  const [newSkillProficiency, setNewSkillProficiency] = useState<"Beginner" | "Intermediate" | "Expert">("Intermediate");

  // Step 3: Projects & Portfolio
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [projTitle, setProjTitle] = useState("");
  const [projRole, setProjRole] = useState("");
  const [projDesc, setProjDesc] = useState("");
  const [projLink, setProjLink] = useState("");
  const [isFresher, setIsFresher] = useState(false);

  // Step 4: Career Preferences
  const [targetRoles, setTargetRoles] = useState<string[]>(["Backend Engineer"]);
  const [customRole, setCustomRole] = useState("");
  const [remotePref, setRemotePref] = useState("REMOTE");
  const [minSalary, setMinSalary] = useState("80000");
  const [currency, setCurrency] = useState("USD");
  const [preferredLocations, setPreferredLocations] = useState("Bangalore, Remote");

  // Dynamic calculated completeness
  const calculateEstimatedCompleteness = () => {
    let score = 0;
    if (headline && city) score += 20;
    if (institution && degree) score += 15;
    if (skillsList.length >= 2) score += 30;
    else if (skillsList.length === 1) score += 15;
    if (projects.length > 0 || isFresher) score += 15;
    if (targetRoles.length > 0) score += 20;
    return Math.min(100, score);
  };

  const handleAddSkill = (name: string, category = "Backend", prof: "Beginner" | "Intermediate" | "Expert" = "Intermediate") => {
    const trimmed = name.trim();
    if (!trimmed) return;
    if (skillsList.some((s) => s.name.toLowerCase() === trimmed.toLowerCase())) return;
    setSkillsList([...skillsList, { name: trimmed, category, proficiency: prof }]);
    setNewSkillName("");
  };

  const handleRemoveSkill = (name: string) => {
    setSkillsList(skillsList.filter((s) => s.name !== name));
  };

  const handleToggleRole = (role: string) => {
    if (targetRoles.includes(role)) {
      setTargetRoles(targetRoles.filter((r) => r !== role));
    } else {
      setTargetRoles([...targetRoles, role]);
    }
  };

  const handleAddProject = () => {
    if (!projTitle.trim()) return;
    setProjects([
      ...projects,
      {
        title: projTitle.trim(),
        role: projRole.trim() || "Lead Contributor",
        description: projDesc.trim(),
        link: projLink.trim(),
      },
    ]);
    setProjTitle("");
    setProjRole("");
    setProjDesc("");
    setProjLink("");
  };

  const handleRemoveProject = (index: number) => {
    setProjects(projects.filter((_, idx) => idx !== index));
  };

  const handleFinalSubmit = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      // 1. Save Profile Info
      await apiClient("/candidate/profile", {
        method: "PUT",
        body: JSON.stringify({
          headline: headline || "Software Engineer",
          summary: summary || "Driven software developer specializing in modern scalable applications.",
          city: city || "Remote",
          country: country || "India",
        }),
      });

      // 2. Save Education if provided
      if (institution.trim() && degree.trim()) {
        try {
          await apiClient("/candidate/education", {
            method: "POST",
            body: JSON.stringify({
              institution: institution.trim(),
              degree: degree.trim(),
              field_of_study: fieldOfStudy.trim() || "Computer Science",
              end_date: gradYear.trim() || "2025",
              is_current: false,
            }),
          });
        } catch (eduErr) {
          console.warn("Education save notice:", eduErr);
        }
      }

      // 3. Save Skills with proficiency
      for (const sk of skillsList) {
        try {
          await apiClient("/candidate/skills", {
            method: "POST",
            body: JSON.stringify({
              skill_name: sk.name,
              category: sk.category,
              proficiency: sk.proficiency,
            }),
          });
        } catch (skErr) {
          console.warn("Skill save notice:", skErr);
        }
      }

      // 4. Save Projects as Experiences
      for (const pr of projects) {
        try {
          await apiClient("/candidate/experience", {
            method: "POST",
            body: JSON.stringify({
              company: pr.title,
              role: pr.role,
              employment_type: "Project / Portfolio",
              description: `${pr.description} ${pr.link ? `(Link: ${pr.link})` : ""}`,
              skills: skillsList.map((s) => s.name).slice(0, 5),
            }),
          });
        } catch (prErr) {
          console.warn("Project save notice:", prErr);
        }
      }

      // 5. Save Preferences
      const locList = preferredLocations
        .split(",")
        .map((l) => l.trim())
        .filter(Boolean);

      await apiClient("/candidate/preferences", {
        method: "PUT",
        body: JSON.stringify({
          preferred_roles: targetRoles.length > 0 ? targetRoles : ["Software Engineer"],
          preferred_locations: locList.length > 0 ? locList : ["Remote"],
          remote_preference: remotePref,
          min_salary: parseFloat(minSalary) || 0,
          currency: currency,
          job_notification_frequency: "DAILY",
        }),
      });

      router.push("/opportunities");
    } catch (err: any) {
      console.error("Onboarding submission failed:", err);
      setErrorMsg(err.message || "Failed to complete onboarding. Please review your entries.");
    } finally {
      setLoading(false);
    }
  };

  const estimatedScore = calculateEstimatedCompleteness();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 pb-16">
      <Navbar />

      <main className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
        {/* Header and Progress Bar */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-400">
                Phase 3-14 Enhanced • Step {step} of 4
              </span>
              <h1 className="text-2xl font-bold text-white mt-1">
                {step === 1 && "Personal & Academic Foundation"}
                {step === 2 && "Core Technical & Domain Skills"}
                {step === 3 && "Projects, Portfolio & Experience"}
                {step === 4 && "Career Preferences & Match Calibration"}
              </h1>
            </div>

            {/* Profile completeness unlock pill */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 px-4 min-w-[220px]">
              <div className="flex justify-between items-center text-xs mb-1.5">
                <span className="text-slate-400 font-medium">Profile Completeness</span>
                <span className="font-bold text-indigo-400">{estimatedScore}%</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-emerald-400 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${estimatedScore}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-400 mt-1.5">
                {estimatedScore < 40 && "⚠️ Cold-start mode active"}
                {estimatedScore >= 40 && estimatedScore < 75 && "⚡ Unlocking semantic matching"}
                {estimatedScore >= 75 && "🎯 High-precision evidence matching ready"}
              </div>
            </div>
          </div>

          {/* Stepper tabs */}
          <div className="grid grid-cols-4 gap-2 mt-6">
            {[
              { id: 1, label: "1. Basics & Education" },
              { id: 2, label: "2. Skills & Mastery" },
              { id: 3, label: "3. Projects & Work" },
              { id: 4, label: "4. Preferences" },
            ].map((s) => (
              <button
                key={s.id}
                type="button"
                onClick={() => setStep(s.id)}
                className={`py-2 text-xs font-medium rounded-lg border text-center transition-all ${
                  step === s.id
                    ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 font-semibold"
                    : step > s.id
                    ? "bg-slate-900 border-emerald-500/40 text-emerald-400"
                    : "bg-slate-900/60 border-slate-800 text-slate-400"
                }`}
              >
                {step > s.id ? "✓ " : ""}
                {s.label}
              </button>
            ))}
          </div>
        </div>

        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
            {errorMsg}
          </div>
        )}

        <div className="bg-slate-900 border border-slate-800 p-6 sm:p-8 rounded-2xl shadow-xl">
          {/* STEP 1: Personal & Education */}
          {step === 1 && (
            <div className="space-y-6">
              <div className="bg-indigo-950/40 border border-indigo-800/40 rounded-xl p-4 text-xs text-indigo-200">
                💡 <span className="font-semibold text-indigo-100">Cold-Start Intelligence:</span> Providing your degree
                and field of study enables RIGHT FIT to match fresher-friendly, internship, and entry-level positions
                even before full job history is added.
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Professional Headline *
                  </label>
                  <input
                    type="text"
                    value={headline}
                    onChange={(e) => setHeadline(e.target.value)}
                    placeholder="e.g. Senior Backend Engineer | Distributed Systems & Cloud"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Executive Summary / Technical Bio
                  </label>
                  <textarea
                    value={summary}
                    onChange={(e) => setSummary(e.target.value)}
                    rows={3}
                    placeholder="Briefly describe your core expertise, key achievements, and current career trajectory..."
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Current City *</label>
                  <input
                    type="text"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="e.g. Bengaluru, Berlin, San Francisco"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Country</label>
                  <input
                    type="text"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                    placeholder="e.g. India, United States"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                  />
                </div>
              </div>

              {/* Education Sub-Section */}
              <div className="pt-6 border-t border-slate-800">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-3">
                  Academic Credentials (Education)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      College / University Name
                    </label>
                    <input
                      type="text"
                      value={institution}
                      onChange={(e) => setInstitution(e.target.value)}
                      placeholder="e.g. MANIT Bhopal, IIT Delhi, Stanford University"
                      className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Degree</label>
                    <input
                      type="text"
                      value={degree}
                      onChange={(e) => setDegree(e.target.value)}
                      placeholder="e.g. B.Tech, M.S., B.S."
                      className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Field of Study</label>
                    <input
                      type="text"
                      value={fieldOfStudy}
                      onChange={(e) => setFieldOfStudy(e.target.value)}
                      placeholder="e.g. Computer Science & Engineering"
                      className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                      Graduation Year
                    </label>
                    <input
                      type="text"
                      value={gradYear}
                      onChange={(e) => setGradYear(e.target.value)}
                      placeholder="e.g. 2025"
                      className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 focus:outline-none focus:border-indigo-500 text-sm"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* STEP 2: Categorized Skills */}
          {step === 2 && (
            <div className="space-y-6">
              <div className="bg-indigo-950/40 border border-indigo-800/40 rounded-xl p-4 text-xs text-indigo-200">
                🎯 <span className="font-semibold text-indigo-100">Evidence Matching Engine:</span> Add your verified
                skills along with self-assessed proficiency. The recommendation system uses this to calculate exact skill
                overlap, semantic similarity, and skill gaps.
              </div>

              {/* Quick suggestions */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Quick Add Popular Competencies
                </label>
                <div className="flex flex-wrap gap-2">
                  {POPULAR_SKILLS.map((sk) => {
                    const isAdded = skillsList.some((s) => s.name.toLowerCase() === sk.name.toLowerCase());
                    return (
                      <button
                        key={sk.name}
                        type="button"
                        onClick={() => !isAdded && handleAddSkill(sk.name, sk.category)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                          isAdded
                            ? "bg-indigo-600/30 border-indigo-500/50 text-indigo-300 opacity-60 cursor-default"
                            : "bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300"
                        }`}
                      >
                        {isAdded ? "✓ " : "+ "}
                        {sk.name}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Custom Add Form */}
              <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-800">
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-3">
                  Add Custom Skill & Proficiency
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 items-end">
                  <div className="sm:col-span-5">
                    <span className="block text-[11px] text-slate-400 mb-1">Skill Name</span>
                    <input
                      type="text"
                      value={newSkillName}
                      onChange={(e) => setNewSkillName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          e.preventDefault();
                          handleAddSkill(newSkillName, newSkillCategory, newSkillProficiency);
                        }
                      }}
                      placeholder="e.g. Kafka, GraphQL, PyTorch"
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    />
                  </div>

                  <div className="sm:col-span-3">
                    <span className="block text-[11px] text-slate-400 mb-1">Category</span>
                    <select
                      value={newSkillCategory}
                      onChange={(e) => setNewSkillCategory(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    >
                      <option value="Backend">Backend</option>
                      <option value="Frontend">Frontend</option>
                      <option value="Database">Database</option>
                      <option value="DevOps">Cloud / DevOps</option>
                      <option value="AI/ML">AI / ML</option>
                      <option value="Tools">Tools / Soft Skills</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <span className="block text-[11px] text-slate-400 mb-1">Proficiency</span>
                    <select
                      value={newSkillProficiency}
                      onChange={(e) => setNewSkillProficiency(e.target.value as any)}
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    >
                      <option value="Beginner">Beginner</option>
                      <option value="Intermediate">Intermediate</option>
                      <option value="Expert">Expert</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <button
                      type="button"
                      onClick={() => handleAddSkill(newSkillName, newSkillCategory, newSkillProficiency)}
                      className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium text-xs transition-colors"
                    >
                      Add Skill
                    </button>
                  </div>
                </div>
              </div>

              {/* Added Skills List */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase">
                    Your Configured Skills ({skillsList.length})
                  </label>
                  <span className="text-[11px] text-slate-400">At least 2 required for high-precision match</span>
                </div>

                {skillsList.length === 0 ? (
                  <p className="text-xs text-slate-500 italic p-3 bg-slate-800/30 rounded-lg">
                    No skills added yet. Select from the quick tags above or enter your own.
                  </p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {skillsList.map((sk) => (
                      <span
                        key={sk.name}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs bg-slate-800 border border-slate-700 text-slate-200"
                      >
                        <span className="font-semibold text-white">{sk.name}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">
                          {sk.category}
                        </span>
                        <span
                          className={`text-[10px] px-1.5 py-0.5 rounded ${
                            sk.proficiency === "Expert"
                              ? "bg-purple-900/60 text-purple-300"
                              : sk.proficiency === "Intermediate"
                              ? "bg-blue-900/60 text-blue-300"
                              : "bg-slate-700 text-slate-400"
                          }`}
                        >
                          {sk.proficiency}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSkill(sk.name)}
                          className="ml-1 text-slate-400 hover:text-rose-400 font-bold"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* STEP 3: Projects & Portfolio */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="bg-indigo-950/40 border border-indigo-800/40 rounded-xl p-4 text-xs text-indigo-200">
                🚀 <span className="font-semibold text-indigo-100">Practical Demonstration:</span> Add your notable
                software projects, hackathons, or previous internships. Demonstrated projects significantly boost
                recommendation confidence.
              </div>

              <div className="flex items-center gap-2 p-3 bg-slate-800/50 rounded-xl border border-slate-800">
                <input
                  type="checkbox"
                  id="fresherCheck"
                  checked={isFresher}
                  onChange={(e) => setIsFresher(e.target.checked)}
                  className="rounded border-slate-700 text-indigo-600 focus:ring-indigo-500"
                />
                <label htmlFor="fresherCheck" className="text-xs text-slate-300 cursor-pointer">
                  I am a fresh graduate or current student with no commercial work experience yet.
                </label>
              </div>

              {/* Add Project Form */}
              <div className="p-4 bg-slate-800/60 rounded-xl border border-slate-800 space-y-3">
                <h4 className="text-xs font-semibold text-slate-300 uppercase">Add Project or Internship</h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <span className="block text-[11px] text-slate-400 mb-1">Project Name / Company</span>
                    <input
                      type="text"
                      value={projTitle}
                      onChange={(e) => setProjTitle(e.target.value)}
                      placeholder="e.g. Distributed Task Queue or Acme Corp"
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    />
                  </div>
                  <div>
                    <span className="block text-[11px] text-slate-400 mb-1">Role / Position</span>
                    <input
                      type="text"
                      value={projRole}
                      onChange={(e) => setProjRole(e.target.value)}
                      placeholder="e.g. Backend Lead or SDE Intern"
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <span className="block text-[11px] text-slate-400 mb-1">Impact & Technologies Used</span>
                    <textarea
                      value={projDesc}
                      onChange={(e) => setProjDesc(e.target.value)}
                      rows={2}
                      placeholder="Built asynchronous processing engine handling 10k req/sec using Redis and FastAPI..."
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    />
                  </div>
                  <div className="sm:col-span-2">
                    <span className="block text-[11px] text-slate-400 mb-1">GitHub / Demo URL (Optional)</span>
                    <input
                      type="url"
                      value={projLink}
                      onChange={(e) => setProjLink(e.target.value)}
                      placeholder="https://github.com/username/project"
                      className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                    />
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    type="button"
                    onClick={handleAddProject}
                    disabled={!projTitle.trim()}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white rounded-lg text-xs font-medium"
                  >
                    + Add to Profile
                  </button>
                </div>
              </div>

              {/* Projects List */}
              {projects.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-semibold text-slate-300 uppercase">Added Projects ({projects.length})</h4>
                  {projects.map((p, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-800 rounded-xl border border-slate-700 flex justify-between items-start"
                    >
                      <div>
                        <div className="font-semibold text-sm text-white">
                          {p.title} <span className="text-xs text-indigo-400 font-normal">({p.role})</span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1">{p.description}</p>
                        {p.link && (
                          <a
                            href={p.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-indigo-400 hover:underline mt-1 inline-block"
                          >
                            🔗 {p.link}
                          </a>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => handleRemoveProject(idx)}
                        className="text-xs text-slate-400 hover:text-rose-400 ml-4"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* STEP 4: Career Preferences & Calibration */}
          {step === 4 && (
            <div className="space-y-6">
              <div className="bg-indigo-950/40 border border-indigo-800/40 rounded-xl p-4 text-xs text-indigo-200">
                ⚙️ <span className="font-semibold text-indigo-100">Personalized Matching Calibration:</span> Tell the
                engine your target roles and workplace preferences. The cold-start ranking algorithm will use these to
                surface relevant jobs immediately.
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                  Target Job Titles (Select all that apply)
                </label>
                <div className="flex flex-wrap gap-2 mb-3">
                  {POPULAR_ROLES.map((role) => {
                    const active = targetRoles.includes(role);
                    return (
                      <button
                        key={role}
                        type="button"
                        onClick={() => handleToggleRole(role)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                          active
                            ? "bg-indigo-600 border-indigo-500 text-white font-semibold"
                            : "bg-slate-800 hover:bg-slate-700 border-slate-700 text-slate-300"
                        }`}
                      >
                        {active ? "✓ " : "+ "}
                        {role}
                      </button>
                    );
                  })}
                </div>

                <div className="flex gap-2">
                  <input
                    type="text"
                    value={customRole}
                    onChange={(e) => setCustomRole(e.target.value)}
                    placeholder="Add custom role (e.g. Distributed Systems Engineer)"
                    className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      if (customRole.trim() && !targetRoles.includes(customRole.trim())) {
                        setTargetRoles([...targetRoles, customRole.trim()]);
                        setCustomRole("");
                      }
                    }}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-medium"
                  >
                    Add
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Workplace Arrangement
                  </label>
                  <select
                    value={remotePref}
                    onChange={(e) => setRemotePref(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                  >
                    <option value="REMOTE">Remote Only</option>
                    <option value="HYBRID">Hybrid (Flexible)</option>
                    <option value="ON_SITE">On-Site Only</option>
                    <option value="ANY">Any Arrangement</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Preferred Locations (Comma-separated)
                  </label>
                  <input
                    type="text"
                    value={preferredLocations}
                    onChange={(e) => setPreferredLocations(e.target.value)}
                    placeholder="e.g. Bengaluru, Remote, San Francisco"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">
                    Minimum Target Compensation
                  </label>
                  <input
                    type="number"
                    value={minSalary}
                    onChange={(e) => setMinSalary(e.target.value)}
                    placeholder="e.g. 80000"
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Currency</label>
                  <select
                    value={currency}
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 text-sm"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="INR">INR (₹)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Stepper Navigation Actions */}
          <div className="flex justify-between items-center mt-8 pt-5 border-t border-slate-800">
            {step > 1 ? (
              <button
                type="button"
                onClick={() => setStep(step - 1)}
                className="px-5 py-2.5 rounded-lg border border-slate-700 text-sm text-slate-300 hover:text-white hover:bg-slate-800 transition-colors"
              >
                ← Back
              </button>
            ) : (
              <div />
            )}

            {step < 4 ? (
              <button
                type="button"
                onClick={() => setStep(step + 1)}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-semibold text-sm transition-colors shadow-lg shadow-indigo-600/20"
              >
                Continue to Step {step + 1} →
              </button>
            ) : (
              <button
                type="button"
                onClick={handleFinalSubmit}
                disabled={loading}
                className="px-8 py-2.5 bg-gradient-to-r from-indigo-600 to-emerald-600 hover:from-indigo-500 hover:to-emerald-500 rounded-lg text-white font-bold text-sm transition-all shadow-lg shadow-emerald-600/20 disabled:opacity-50"
              >
                {loading ? "Calibrating Career Profile..." : "Complete & Discover Opportunities 🚀"}
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
