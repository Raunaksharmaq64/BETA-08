"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";
import { useAuth } from "@/context/AuthContext";

interface JobItem {
  id: string;
  title: string;
  company_name: string;
  city?: string;
  state?: string;
  country?: string;
  workplace_type: string;
  is_remote: boolean;
  employment_type: string;
  min_salary?: number;
  max_salary?: number;
  currency?: string;
  salary_period?: string;
  required_skills: string[];
  application_url: string;
  verification_status: string;
  freshness_state: string;
  first_seen_at: string;
  last_verified_at?: string;
  source_name: string;
  is_saved: boolean;
  saved_job_id?: string;
  skill_fit_score?: number;
  eligibility_status?: string;
  relevance_score?: number;
  matched_skills_preview: string[];
  missing_skills_preview: string[];
}

interface SourceCoverage {
  total_configured_sources: number;
  healthy_sources_count: number;
  degraded_sources_count: number;
  is_partial_results: boolean;
  coverage_details: Array<{
    source_key: string;
    display_name: string;
    status: string;
    records_count: number;
    outage_reason?: string;
  }>;
}

const POPULAR_SKILLS = [
  "React",
  "Python",
  "TypeScript",
  "Node.js",
  "Next.js",
  "FastAPI",
  "SQL",
  "PostgreSQL",
  "AWS",
  "Docker",
  "Kubernetes",
  "Figma",
  "UI/UX",
  "B2B Sales",
  "Growth Marketing",
  "SEO",
  "Content Strategy",
  "Financial Modeling",
  "Commercial Contracts",
  "Customer Success",
];

const QUICK_SEARCH_PILLS = [
  { label: "⚡ React", value: "react" },
  { label: "🌐 WebDev", value: "webdev" },
  { label: "💻 Full Stack", value: "full stack" },
  { label: "🐍 Python", value: "python" },
  { label: "🎨 Figma", value: "figma" },
  { label: "☁️ DevOps", value: "devops" },
  { label: "📈 B2B Sales", value: "sales" },
  { label: "📢 Marketing", value: "marketing" },
];

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  // Search filter states
  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [role, setRole] = useState(searchParams.get("role") || "");
  const [company, setCompany] = useState(searchParams.get("company") || "");
  const [city, setCity] = useState(searchParams.get("city") || "");
  const [isRemoteOnly, setIsRemoteOnly] = useState(searchParams.get("remote") === "true");
  const [workplaceType, setWorkplaceType] = useState(searchParams.get("workplace") || "");
  const [employmentType, setEmploymentType] = useState(searchParams.get("employment") || "");
  const [experienceLevel, setExperienceLevel] = useState(searchParams.get("level") || "");
  const [selectedSkills, setSelectedSkills] = useState<string[]>(
    searchParams.get("skills") ? searchParams.get("skills")!.split(",").filter(Boolean) : []
  );
  const [minSalary, setMinSalary] = useState(Number(searchParams.get("min_salary") || 0));
  const [sortBy, setSortBy] = useState(searchParams.get("sort_by") || "BEST_FIT");
  const [verificationFilter, setVerificationFilter] = useState(searchParams.get("verification") || "");
  const [page, setPage] = useState(Number(searchParams.get("page") || 1));

  // Debounced input states for instant typing responsiveness
  const [debouncedQuery, setDebouncedQuery] = useState(query);
  const [debouncedRole, setDebouncedRole] = useState(role);
  const [debouncedCompany, setDebouncedCompany] = useState(company);
  const [debouncedCity, setDebouncedCity] = useState(city);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
      setDebouncedRole(role);
      setDebouncedCompany(company);
      setDebouncedCity(city);
    }, 350);
    return () => clearTimeout(timer);
  }, [query, role, company, city]);

  // Result states
  const [jobs, setJobs] = useState<JobItem[]>(() => {
    return fastCache.get<JobItem[]>("search_jobs_default") || [];
  });
  const [totalCount, setTotalCount] = useState<number>(() => {
    return fastCache.get<number>("search_total_default") || 0;
  });
  const [totalPages, setTotalPages] = useState<number>(() => {
    return fastCache.get<number>("search_pages_default") || 1;
  });
  const [coverage, setCoverage] = useState<SourceCoverage | null>(null);
  const [isLoading, setIsLoading] = useState(() => {
    return (fastCache.get<JobItem[]>("search_jobs_default") || []).length === 0;
  });
  const [isFiltering, setIsFiltering] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Save Search Modal state
  const [isSaveModalOpen, setIsSaveModalOpen] = useState(false);
  const [saveSearchName, setSaveSearchName] = useState("");
  const [alertFrequency, setAlertFrequency] = useState("DAILY");
  const [isSavingSearch, setIsSavingSearch] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  const fetchJobs = async (overrides?: {
    q?: string;
    role?: string;
    company?: string;
    city?: string;
    page?: number;
  }) => {
    const qTerm = (overrides?.q !== undefined ? overrides.q : debouncedQuery).trim();
    const roleTerm = (overrides?.role !== undefined ? overrides.role : debouncedRole).trim();
    const compTerm = (overrides?.company !== undefined ? overrides.company : debouncedCompany).trim();
    const cityTerm = (overrides?.city !== undefined ? overrides.city : debouncedCity).trim();
    const pageNum = overrides?.page !== undefined ? overrides.page : page;

    const cacheKey = `search_${qTerm}_${roleTerm}_${compTerm}_${cityTerm}_${isRemoteOnly}_${workplaceType}_${employmentType}_${experienceLevel}_${selectedSkills.join(",")}_${sortBy}_${pageNum}`;
    const cached = fastCache.get<any>(cacheKey);
    if (cached && cached.items) {
      setJobs(cached.items);
      setTotalCount(cached.total_count || 0);
      setTotalPages(cached.total_pages || 1);
      setIsLoading(false);
      setIsFiltering(false);
    } else if (jobs.length > 0) {
      setIsFiltering(true);
    } else {
      setIsLoading(true);
    }

    setErrorMsg(null);
    try {
      const params = new URLSearchParams();
      if (qTerm) params.set("q", qTerm);
      if (roleTerm) params.set("role", roleTerm);
      if (compTerm) params.set("company", compTerm);
      if (cityTerm) params.set("city", cityTerm);
      if (isRemoteOnly) params.set("is_remote", "true");
      if (workplaceType) params.append("workplace_types", workplaceType);
      if (employmentType) params.append("employment_types", employmentType);
      if (experienceLevel === "FRESHER") params.set("is_fresher_friendly", "true");
      if (experienceLevel === "INTERNSHIP") params.set("is_internship", "true");
      if (selectedSkills.length > 0) {
        selectedSkills.forEach((s) => params.append("skills", s));
      }
      if (minSalary > 0) params.set("min_salary", minSalary.toString());
      if (verificationFilter) params.append("verification_statuses", verificationFilter);
      params.set("sort_by", sortBy);
      params.set("page", pageNum.toString());
      params.set("page_size", "15");

      const res = await apiClient<any>(`/search/jobs?${params.toString()}`);
      if (res.data) {
        setJobs(res.data.items || []);
        setTotalCount(res.data.total_count || 0);
        setTotalPages(res.data.total_pages || 1);
        setCoverage(res.data.source_coverage || null);

        fastCache.set(cacheKey, res.data, 120000);
        if (!qTerm && !roleTerm && !compTerm && selectedSkills.length === 0 && page === 1) {
          fastCache.set("search_jobs_default", res.data.items || [], 120000);
          fastCache.set("search_total_default", res.data.total_count || 0, 120000);
          fastCache.set("search_pages_default", res.data.total_pages || 1, 120000);
        }
      }
    } catch (err: any) {
      if (jobs.length === 0) setErrorMsg(err.message || "Failed to load job listings.");
    } finally {
      setIsLoading(false);
      setIsFiltering(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [
    page,
    sortBy,
    debouncedQuery,
    debouncedRole,
    debouncedCompany,
    debouncedCity,
    selectedSkills,
    experienceLevel,
    workplaceType,
    employmentType,
    minSalary,
    isRemoteOnly,
    verificationFilter,
  ]);

  const toggleSkill = (skill: string) => {
    setSelectedSkills((prev) => {
      const exists = prev.some((s) => s.toLowerCase() === skill.toLowerCase());
      if (exists) {
        return prev.filter((s) => s.toLowerCase() !== skill.toLowerCase());
      } else {
        return [...prev, skill];
      }
    });
    setPage(1);
  };

  const handleQuickPill = (val: string) => {
    const nextVal = query.toLowerCase() === val.toLowerCase() ? "" : val;
    setQuery(nextVal);
    setDebouncedQuery(nextVal);
    setPage(1);
    fetchJobs({ q: nextVal, page: 1 });
  };

  const handleResetFilters = () => {
    setQuery("");
    setRole("");
    setCompany("");
    setCity("");
    setDebouncedQuery("");
    setDebouncedRole("");
    setDebouncedCompany("");
    setDebouncedCity("");
    setIsRemoteOnly(false);
    setWorkplaceType("");
    setEmploymentType("");
    setExperienceLevel("");
    setSelectedSkills([]);
    setMinSalary(0);
    setVerificationFilter("");
    setSortBy("BEST_FIT");
    setPage(1);
    fetchJobs({ q: "", role: "", company: "", city: "", page: 1 });
  };

  const handleSearchSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setDebouncedQuery(query);
    setDebouncedRole(role);
    setDebouncedCompany(company);
    setDebouncedCity(city);
    setPage(1);
    fetchJobs({ q: query, role, company, city, page: 1 });
  };

  const handleToggleSaveJob = async (job: JobItem) => {
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      if (job.is_saved) {
        await apiClient(`/saved-jobs/${job.id}`, { method: "DELETE" });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: false, saved_job_id: undefined } : j))
        );
      } else {
        const res = await apiClient<any>("/saved-jobs", {
          method: "POST",
          body: JSON.stringify({ opportunity_id: job.id }),
        });
        setJobs((prev) =>
          prev.map((j) => (j.id === job.id ? { ...j, is_saved: true, saved_job_id: res.data.id } : j))
        );
      }
    } catch (err: any) {
      alert("Failed to update saved job status: " + err.message);
    }
  };

  const handleSaveSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      router.push("/login");
      return;
    }
    if (!saveSearchName.trim()) return;

    setIsSavingSearch(true);
    setSaveSuccessMsg(null);
    try {
      await apiClient("/saved-searches", {
        method: "POST",
        body: JSON.stringify({
          name: saveSearchName,
          query: query || undefined,
          filters: {
            role: role || undefined,
            company: company || undefined,
            city: city || undefined,
            is_remote: isRemoteOnly || undefined,
            verification_status: verificationFilter || undefined,
          },
          alert_enabled: true,
          alert_frequency: alertFrequency,
        }),
      });
      setSaveSuccessMsg("Search and alert notifications saved successfully!");
      setTimeout(() => {
        setIsSaveModalOpen(false);
        setSaveSuccessMsg(null);
        setSaveSearchName("");
      }, 1500);
    } catch (err: any) {
      alert("Failed to save search: " + err.message);
    } finally {
      setIsSavingSearch(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
      {/* Header & Save Search Action */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tight">Job Discovery & Matching</h1>
          <p className="text-sm text-slate-700 font-semibold mt-1">
            Search verified career opportunities evaluated with transparent, evidence-based candidate matching.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsSaveModalOpen(true)}
            className="neo-pill inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-indigo-700 hover:text-indigo-900 transition-all"
          >
            <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            Save Search & Alerts
          </button>
        </div>
      </div>

      {/* Partial Coverage Transparency Banner */}
      {coverage && coverage.is_partial_results && (
        <div className="mt-4 p-4 rounded-xl bg-amber-950/40 border border-amber-600/40 text-amber-200 flex items-start gap-3">
          <svg className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div>
            <div className="font-semibold text-amber-300">Notice: Partial Upstream Source Coverage</div>
            <p className="text-xs text-amber-200/90 mt-0.5">
              One or more upstream source connectors ({coverage.degraded_sources_count} of {coverage.total_configured_sources})
              are currently degraded or in circuit breaker cooldown. Zero matches on certain queries may reflect upstream provider outages rather than a lack of market openings.
            </p>
          </div>
        </div>
      )}

      {/* Main Grid: Filters Sidebar + Results */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1 space-y-6 neo-box p-6 rounded-2xl border border-white/90 shadow-sm">
          <form onSubmit={handleSearchSubmit} className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold">
                  Smart Keywords Search
                </label>
                {query && (
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      setDebouncedQuery("");
                      setPage(1);
                      fetchJobs({ q: "", page: 1 });
                    }}
                    className="text-[10px] text-slate-700 font-bold hover:text-slate-200"
                  >
                    Clear
                  </button>
                )}
              </div>
              <input
                type="text"
                placeholder="e.g. React, WebDev, Python, AWS..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
              {/* Quick Suggestion Pills */}
              <div className="flex flex-wrap gap-1 mt-2">
                {QUICK_SEARCH_PILLS.map((pill) => {
                  const isActive = query.toLowerCase() === pill.value.toLowerCase();
                  return (
                    <button
                      key={pill.value}
                      type="button"
                      onClick={() => handleQuickPill(pill.value)}
                      className={`text-[11px] px-2 py-0.5 rounded-full border transition-all ${
                        isActive
                          ? "bg-indigo-950 border-indigo-500 text-indigo-300 font-semibold shadow-sm"
                          : "bg-slate-950/60 border-slate-800 text-slate-700 font-bold hover:text-slate-200 hover:border-slate-700"
                      }`}
                    >
                      {pill.label}
                    </button>
                  );
                })}
              </div>
              <p className="text-[11px] text-slate-500 mt-1.5">
                Dynamic smart search across job titles, required skills, and tech stacks.
              </p>
            </div>

            {/* Popular Skills Multi-Select Chips */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold">
                  Required Skills
                </label>
                {selectedSkills.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setSelectedSkills([])}
                    className="text-[10px] text-slate-700 font-bold hover:text-slate-200"
                  >
                    Clear ({selectedSkills.length})
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
                {POPULAR_SKILLS.map((sk) => {
                  const isSelected = selectedSkills.some((s) => s.toLowerCase() === sk.toLowerCase());
                  return (
                    <button
                      key={sk}
                      type="button"
                      onClick={() => toggleSkill(sk)}
                      className={`px-2.5 py-1 rounded-md text-xs font-medium border transition-all ${isSelected
                        ? "bg-emerald-950/80 border-emerald-600 text-emerald-300 shadow-sm"
                        : "bg-slate-950/70 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white"
                        }`}
                    >
                      {isSelected ? `✓ ${sk}` : `+ ${sk}`}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Career Stage / Fresher Filter */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Experience / Level
              </label>
              <select
                value={experienceLevel}
                onChange={(e) => setExperienceLevel(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              >
                <option value="">All Experience Levels</option>
                <option value="FRESHER">🎓 Freshers & Entry Level (0-1 yrs)</option>
                <option value="INTERNSHIP">💼 Internships Only</option>
              </select>
            </div>

            {/* Workplace Mode */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Workplace Mode
              </label>
              <select
                value={workplaceType}
                onChange={(e) => {
                  setWorkplaceType(e.target.value);
                  if (e.target.value === "REMOTE") setIsRemoteOnly(true);
                }}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              >
                <option value="">All Workplace Modes</option>
                <option value="REMOTE">🌐 Remote</option>
                <option value="HYBRID">🏢 Hybrid</option>
                <option value="ON_SITE">📍 On-Site</option>
              </select>
            </div>

            {/* Employment Type */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Employment Type
              </label>
              <select
                value={employmentType}
                onChange={(e) => setEmploymentType(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              >
                <option value="">All Employment Types</option>
                <option value="FULL_TIME">Full-Time</option>
                <option value="CONTRACT">Contract / Freelance</option>
                <option value="PART_TIME">Part-Time</option>
                <option value="INTERNSHIP">Internship</option>
              </select>
            </div>

            {/* Role / Title */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Role / Title
              </label>
              <input
                type="text"
                placeholder="e.g. Frontend Engineer"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Company */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Company
              </label>
              <input
                type="text"
                placeholder="e.g. Stripe, Google, Acme"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Location */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Location
              </label>
              <input
                type="text"
                placeholder="City, State, or Country"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              />
            </div>

            {/* Minimum Salary */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Minimum Compensation
              </label>
              <select
                value={minSalary}
                onChange={(e) => setMinSalary(Number(e.target.value))}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              >
                <option value={0}>Any Compensation</option>
                <option value={50000}>$50,000+ / year</option>
                <option value={80000}>$80,000+ / year</option>
                <option value={100000}>$100,000+ / year</option>
                <option value={120000}>$120,000+ / year</option>
                <option value={150000}>$150,000+ / year</option>
              </select>
            </div>

            {/* Verification Status */}
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 font-bold mb-1">
                Verification Status
              </label>
              <select
                value={verificationFilter}
                onChange={(e) => setVerificationFilter(e.target.value)}
                className="w-full neo-inset rounded-xl px-3.5 py-2 text-slate-900 font-bold text-xs focus:outline-none"
              >
                <option value="">All Listings</option>
                <option value="OPEN_CONFIRMED">✓ Open Confirmed (Active ATS)</option>
                <option value="UNVERIFIED">Unverified Only</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="pt-2 space-y-2">
              <button
                type="submit"
                className="w-full py-2.5 px-4 neo-btn-primary text-white rounded-xl font-bold text-sm shadow-md transition-all cursor-pointer"
              >
                Search & Apply Filters
              </button>
              <button
                type="button"
                onClick={handleResetFilters}
                className="w-full py-2.5 px-4 neo-pill text-slate-800 hover:text-indigo-600 rounded-xl text-xs font-bold transition-all cursor-pointer"
              >
                Reset All Filters
              </button>
            </div>
          </form>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-3 space-y-4">
          {/* Active Filter Chips Ribbon */}
          {(query || selectedSkills.length > 0 || isRemoteOnly || experienceLevel || workplaceType || employmentType || minSalary > 0 || role || company || city || verificationFilter) && (
            <div className="flex flex-wrap items-center gap-1.5 p-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
              <span className="text-slate-700 font-bold font-semibold mr-1">Active Filters:</span>
              {query && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 font-medium">
                  <span>Keyword: {query}</span>
                  <button type="button" onClick={() => { setQuery(""); setDebouncedQuery(""); setPage(1); fetchJobs({ q: "", page: 1 }); }} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {selectedSkills.map((sk) => (
                <span key={sk} className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 font-medium">
                  <span>Skill: {sk}</span>
                  <button type="button" onClick={() => toggleSkill(sk)} className="hover:text-white ml-0.5">✕</button>
                </span>
              ))}
              {experienceLevel && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-950/80 text-amber-300 border border-amber-700/60 font-medium">
                  <span>{experienceLevel === "FRESHER" ? "Freshers / Entry-Level" : "Internships"}</span>
                  <button type="button" onClick={() => setExperienceLevel("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {workplaceType && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-950/80 text-blue-300 border border-blue-700/60 font-medium">
                  <span>Mode: {workplaceType}</span>
                  <button type="button" onClick={() => setWorkplaceType("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {isRemoteOnly && !workplaceType && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-950/80 text-blue-300 border border-blue-700/60 font-medium">
                  <span>Remote Only</span>
                  <button type="button" onClick={() => setIsRemoteOnly(false)} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {employmentType && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-purple-950/80 text-purple-300 border border-purple-700/60 font-medium">
                  <span>Type: {employmentType}</span>
                  <button type="button" onClick={() => setEmploymentType("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {minSalary > 0 && (
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 font-medium">
                  <span>Min: ${minSalary.toLocaleString()}</span>
                  <button type="button" onClick={() => setMinSalary(0)} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {role && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Role: {role}</span>
                  <button type="button" onClick={() => setRole("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {company && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Company: {company}</span>
                  <button type="button" onClick={() => setCompany("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {city && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Location: {city}</span>
                  <button type="button" onClick={() => setCity("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              {verificationFilter && (
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full neo-pill text-slate-900 font-bold border border-white/90 shadow-sm">
                  <span>Status: {verificationFilter === "OPEN_CONFIRMED" ? "Open Confirmed" : verificationFilter}</span>
                  <button type="button" onClick={() => setVerificationFilter("")} className="hover:text-white ml-0.5">✕</button>
                </span>
              )}
              <button
                type="button"
                onClick={handleResetFilters}
                className="text-xs text-rose-400 hover:text-rose-300 underline font-semibold ml-auto"
              >
                Clear All
              </button>
            </div>
          )}

          {/* Controls Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/60 px-4 py-3 rounded-xl border border-slate-800">
            <div className="text-sm text-slate-700 font-bold">
              Showing <span className="font-semibold text-white">{jobs.length}</span> of{" "}
              <span className="font-semibold text-white">{totalCount}</span> opportunities
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-700 font-bold">
              <label>Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-2.5 py-1.5 bg-slate-950 rounded-lg border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-indigo-500"
              >
                <option value="BEST_FIT">Best Fit (Match & Verified)</option>
                <option value="RELEVANCE">🎯 Relevance / Smart Match</option>
                <option value="MOST_RECENT">Most Recent</option>
                <option value="HIGHEST_SALARY">Highest Compensation</option>
                <option value="SKILL_MATCH">Skill Match %</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-600/40 text-red-300 text-sm">
              {errorMsg}
            </div>
          )}

          {/* Top Background Revalidation Glow Bar */}
          {isFiltering && (
            <div className="fixed top-0 left-0 right-0 h-[2.5px] bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 animate-pulse z-50 shadow-sm" />
          )}

          {/* Loading Skeleton */}
          {isLoading && jobs.length === 0 ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse bg-slate-900/40 rounded-2xl p-6 border border-slate-800 h-44" />
              ))}
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-16 bg-slate-900/30 rounded-2xl border border-slate-800">
              <p className="text-base font-medium text-slate-300">No opportunities matching your criteria</p>
              <p className="text-xs text-slate-500 mt-1">Try broadening your keywords or removing location filters.</p>
            </div>
          ) : (
            /* Opportunity Cards */
            <div className={`space-y-4 transition-opacity duration-150 ${isFiltering ? "opacity-80" : "opacity-100"}`}>
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="bg-slate-900/80 hover:bg-slate-900 transition-colors rounded-2xl p-6 border border-slate-800 hover:border-slate-700 space-y-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <Link
                          href={`/jobs/${job.id}`}
                          className="text-lg font-bold text-white hover:text-indigo-400 transition-colors"
                        >
                          {job.title}
                        </Link>
                        {job.is_remote && (
                          <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/60">
                            Remote
                          </span>
                        )}
                        <span className="px-2.5 py-0.5 text-xs font-bold rounded-full neo-pill text-slate-900 border border-white/90">
                          {job.workplace_type}
                        </span>
                      </div>
                      <div className="text-sm text-slate-700 font-bold mt-1 flex items-center gap-3 flex-wrap">
                        <span className="font-medium text-slate-200">{job.company_name}</span>
                        <span>•</span>
                        <span>{job.city ? `${job.city}, ${job.country || ""}` : job.country || "Worldwide"}</span>
                        <span>•</span>
                        <span className="text-xs text-slate-500">Source: {job.source_name}</span>
                      </div>
                    </div>

                    {/* Save / Bookmark Button */}
                    <button
                      type="button"
                      onClick={() => handleToggleSaveJob(job)}
                      title={job.is_saved ? "Remove from saved jobs" : "Save this job"}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${job.is_saved
                        ? "bg-amber-950/60 border-amber-600/70 text-amber-300 hover:bg-amber-900/60 shadow-sm"
                        : "bg-slate-800/90 hover:bg-slate-750 text-slate-300 border-slate-700 hover:border-slate-600"
                        }`}
                    >
                      <svg
                        className={`w-3.5 h-3.5 ${job.is_saved ? "text-amber-400 fill-current" : "text-slate-700 font-bold"}`}
                        fill={job.is_saved ? "currentColor" : "none"}
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"
                        />
                      </svg>
                      <span>{job.is_saved ? "★ Saved" : "☆ Save Job"}</span>
                    </button>
                  </div>

                  {/* Badges: Verification, Freshness, Skill Fit & Eligibility */}
                  <div className="flex items-center gap-3 flex-wrap text-xs pt-1">
                    {/* Verification Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-medium border ${job.verification_status === "OPEN_CONFIRMED"
                        ? "bg-emerald-950/50 border-emerald-800/70 text-emerald-300"
                        : job.verification_status === "UNVERIFIED"
                          ? "bg-slate-800/80 border-slate-700 text-slate-700 font-bold"
                          : "bg-amber-950/50 border-amber-800/70 text-amber-300"
                        }`}
                    >
                      {job.verification_status === "OPEN_CONFIRMED" ? "✓ Open Confirmed" : job.verification_status}
                    </span>

                    {/* Freshness Badge */}
                    <span
                      className={`px-2.5 py-1 rounded-md font-medium border ${job.freshness_state === "FRESH"
                        ? "bg-blue-950/50 border-blue-800/70 text-blue-300"
                        : job.freshness_state === "RECENT"
                          ? "bg-cyan-950/50 border-cyan-800/70 text-cyan-300"
                          : "bg-slate-800 border-slate-700 text-slate-700 font-bold"
                        }`}
                    >
                      Freshness: {job.freshness_state}
                    </span>

                    {/* Smart Match Relevance Badge */}
                    {job.relevance_score !== undefined && job.relevance_score !== null && job.relevance_score > 0 && (
                      <span className="px-2.5 py-1 rounded-md font-semibold bg-emerald-950/60 border border-emerald-600/60 text-emerald-300 flex items-center gap-1">
                        🎯 Smart Match ({Math.round(job.relevance_score)})
                      </span>
                    )}

                    {/* Skill Fit Badge */}
                    {job.skill_fit_score !== undefined && job.skill_fit_score !== null && (
                      <span className="px-2.5 py-1 rounded-md font-semibold bg-indigo-950/60 border border-indigo-700/60 text-indigo-300">
                        ★ {job.skill_fit_score}% Skill Fit
                      </span>
                    )}

                    {/* Mandatory Eligibility Badge */}
                    {job.eligibility_status && (
                      <span
                        className={`px-2.5 py-1 rounded-md font-medium border ${job.eligibility_status === "MEETS_REQUIREMENTS"
                          ? "bg-emerald-950/40 border-emerald-700/60 text-emerald-400"
                          : job.eligibility_status === "UNKNOWN"
                            ? "bg-slate-800 border-slate-700 text-slate-700 font-bold"
                            : "bg-rose-950/40 border-rose-800/60 text-rose-400"
                          }`}
                      >
                        Eligibility: {job.eligibility_status.replace(/_/g, " ")}
                      </span>
                    )}
                  </div>

                  {/* Company Requirements & Skill Alignment */}
                  <div className="p-3.5 rounded-xl neo-inset space-y-2.5">
                    {/* Company Required Skills */}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                          <span>Company Required Skills</span>
                          <span className="text-[10px] text-slate-500 font-normal">
                            {job.required_skills.length} required
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                          {job.required_skills.map((skill, idx) => {
                            const skillLower = skill.toLowerCase();
                            const isMatched = job.matched_skills_preview?.some(
                              (m) => m.toLowerCase() === skillLower
                            );
                            const isSearchMatched =
                              debouncedQuery &&
                              (skillLower.includes(debouncedQuery.toLowerCase()) ||
                                debouncedQuery.toLowerCase().includes(skillLower));
                            const isSkillSelected = selectedSkills.some(
                              (s) => s.toLowerCase() === skillLower
                            );
                            const isHighlighted = isMatched || isSearchMatched || isSkillSelected;

                            return (
                              <span
                                key={idx}
                                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold border transition-all ${isHighlighted ? "bg-emerald-100 border-emerald-300 text-emerald-900 shadow-sm" : "neo-pill text-slate-800 border-slate-200"}`}
                                title={
                                  isMatched
                                    ? "Matched from candidate profile / resume"
                                    : isSearchMatched || isSkillSelected
                                      ? "Matches your active search filter"
                                      : "Required by employer"
                                }
                              >
                                {isHighlighted && <span className="text-emerald-400 font-bold">✓</span>}
                                <span>{skill}</span>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Candidate Matched & Missing Skills from Resume */}
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1 border-t border-slate-800/80 text-xs">
                      {job.matched_skills_preview && job.matched_skills_preview.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-[11px] font-semibold text-emerald-400">Matched in Resume:</span>
                          <div className="flex items-center gap-1 flex-wrap">
                            {job.matched_skills_preview.map((ms, idx) => (
                              <span
                                key={idx}
                                className="text-[10px] px-2 py-0.5 rounded-lg bg-emerald-100 text-emerald-900 border border-emerald-300 font-mono font-bold"
                              >
                                ✓ {ms}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      {job.missing_skills_preview && job.missing_skills_preview.length > 0 && (
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="text-[11px] font-semibold text-amber-400">Missing from Resume:</span>
                          <div className="flex items-center gap-1 flex-wrap">
                            {job.missing_skills_preview.map((mis, idx) => (
                              <span
                                key={idx}
                                className="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-700 font-bold border border-slate-700 font-mono"
                              >
                                {mis}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Card Footer: Salary & Actions */}
                  <div className="flex items-center justify-between pt-3 border-t border-slate-800 text-sm">
                    <div className="font-semibold text-slate-200">
                      {job.min_salary || job.max_salary ? (
                        <>
                          {job.currency || "$"}
                          {job.min_salary?.toLocaleString()} - {job.max_salary?.toLocaleString()}{" "}
                          <span className="text-xs text-slate-700 font-bold font-normal">/ {job.salary_period || "year"}</span>
                        </>
                      ) : (
                        <span className="text-xs text-slate-500 font-normal">Salary not disclosed</span>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <Link
                        href={`/jobs/${job.id}`}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold neo-pill text-indigo-900 hover:text-indigo-600 border border-indigo-200 transition-all"
                      >
                        View Details →
                      </Link>
                      <a
                        href={job.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-colors"
                      >
                        Direct Apply ↗
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-slate-800">
              <button
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-slate-900 hover:text-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                ← Previous
              </button>
              <span className="text-xs text-slate-700 font-bold">
                Page <span className="text-white font-semibold">{page}</span> of {totalPages}
              </span>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                className="px-4 py-2 rounded-xl neo-pill text-xs font-bold text-slate-900 hover:text-indigo-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Save Search & Alert Modal */}
      {isSaveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Save Search & Configure Alerts</h3>
            <p className="text-xs text-slate-700 font-bold mt-1">
              Receive automatic notifications when fresh opportunities matching your filters are ingested.
            </p>

            <form onSubmit={handleSaveSearch} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Search Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Remote Backend Python Roles"
                  value={saveSearchName}
                  onChange={(e) => setSaveSearchName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Notification Cadence</label>
                <select
                  value={alertFrequency}
                  onChange={(e) => setAlertFrequency(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 rounded-lg border border-slate-800 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="INSTANT">Instant (Real-Time Ingestion)</option>
                  <option value="DAILY">Daily Digest</option>
                  <option value="WEEKLY">Weekly Summary</option>
                </select>
              </div>

              {saveSuccessMsg && (
                <div className="p-3 rounded-lg bg-emerald-950/50 border border-emerald-800/60 text-emerald-300 text-xs">
                  {saveSuccessMsg}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsSaveModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingSearch}
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white disabled:opacity-50"
                >
                  {isSavingSearch ? "Saving..." : "Save Subscription"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}


    </div>
  );
}

export default function JobSearchPage() {
  return (
    <React.Suspense
      fallback={
        <div className="max-w-7xl mx-auto px-4 py-16 text-slate-700 font-bold text-sm">
          Loading Job Discovery & Matching...
        </div>
      }
    >
      <SearchContent />
    </React.Suspense>
  );
}
