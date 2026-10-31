"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface ApplicationSummary {
  id: string;
  user_id: string;
  opportunity_id?: string;
  custom_company_name?: string;
  custom_job_title?: string;
  application_url?: string;
  status: string;
  applied_at?: string;
  next_action_due_at?: string;
  next_interview_at?: string;
  created_at: string;
  updated_at: string;
  company_display: string;
  title_display: string;
  workplace_type?: string;
  city?: string;
  notes_count: number;
}

interface ApplicationMetrics {
  total_applications: number;
  by_status: Record<string, number>;
  active_pipeline: number;
  interviews_scheduled: number;
  offers_received: number;
  rejections_received: number;
  stalled_or_ghosted: number;
}

const STATUS_COLUMNS = [
  { key: "ALL", label: "All Applications" },
  { key: "SAVED", label: "Saved" },
  { key: "PLANNING_TO_APPLY", label: "Planning to Apply" },
  { key: "APPLIED", label: "Applied" },
  { key: "ASSESSMENT", label: "Assessment" },
  { key: "INTERVIEW", label: "Interview" },
  { key: "OFFER", label: "Offer" },
  { key: "REJECTED", label: "Rejected" },
  { key: "WITHDRAWN", label: "Withdrawn" },
  { key: "GHOSTED", label: "Ghosted" },
  { key: "CLOSED", label: "Closed" },
];

export default function ApplicationsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [applications, setApplications] = useState<ApplicationSummary[]>([]);
  const [metrics, setMetrics] = useState<ApplicationMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"list" | "board">("board");

  // Create Application Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [appUrl, setAppUrl] = useState("");
  const [initialStatus, setInitialStatus] = useState("SAVED");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [appsRes, metricsRes] = await Promise.all([
        apiClient<ApplicationSummary[]>(
          selectedStatus === "ALL"
            ? `/applications?limit=100`
            : `/applications?status=${selectedStatus}&limit=100`
        ),
        apiClient<ApplicationMetrics>("/applications/metrics"),
      ]);
      setApplications(appsRes.data || []);
      setMetrics(metricsRes.data || null);
    } catch (err: any) {
      console.error("Failed to load applications data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
      return;
    }
    if (user) {
      fetchData();
    }
  }, [user, authLoading, selectedStatus]);

  const handleCreateApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    if (!companyName.trim() || !jobTitle.trim()) {
      setFormError("Company name and job title are required.");
      return;
    }

    setSubmitting(true);
    try {
      await apiClient("/applications", {
        method: "POST",
        body: JSON.stringify({
          custom_company_name: companyName.trim(),
          custom_job_title: jobTitle.trim(),
          application_url: appUrl.trim() || undefined,
          status: initialStatus,
        }),
      });
      setIsCreateModalOpen(false);
      setCompanyName("");
      setJobTitle("");
      setAppUrl("");
      setInitialStatus("SAVED");
      fetchData();
    } catch (err: any) {
      setFormError(err.message || "Failed to create application.");
    } finally {
      setSubmitting(false);
    }
  };

  const filteredApps = applications.filter((app) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      app.company_display.toLowerCase().includes(q) ||
      app.title_display.toLowerCase().includes(q) ||
      (app.city && app.city.toLowerCase().includes(q))
    );
  });

  const getStatusColor = (st: string) => {
    switch (st) {
      case "SAVED":
        return "bg-slate-800 text-slate-300 border-slate-700";
      case "PLANNING_TO_APPLY":
        return "bg-amber-950/60 text-amber-300 border-amber-800/60";
      case "APPLIED":
        return "bg-blue-950/60 text-blue-300 border-blue-800/60";
      case "ASSESSMENT":
        return "bg-purple-950/60 text-purple-300 border-purple-800/60";
      case "INTERVIEW":
        return "bg-indigo-950/60 text-indigo-300 border-indigo-800/60";
      case "OFFER":
        return "bg-emerald-950/60 text-emerald-300 border-emerald-800/60";
      case "REJECTED":
        return "bg-rose-950/60 text-rose-300 border-rose-800/60";
      case "WITHDRAWN":
        return "bg-slate-800/50 text-slate-400 border-slate-700/50";
      case "GHOSTED":
        return "bg-orange-950/60 text-orange-300 border-orange-800/60";
      case "CLOSED":
        return "bg-zinc-800 text-zinc-400 border-zinc-700";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Application CRM</h1>
          <p className="text-slate-400 text-sm mt-1">
            Track career opportunities through auditable state transitions, notes, and milestones.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/calendar"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            📅 View Calendar
          </Link>
          <Link
            href="/interview-prep"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-950/80 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-700/60 transition"
          >
            🎯 Interview Prep
          </Link>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow transition"
          >
            + Add Application
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total</span>
            <div className="text-2xl font-bold text-white mt-1">{metrics.total_applications}</div>
            <span className="text-xs text-slate-500">Tracked roles</span>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-blue-400 uppercase tracking-wider">Active Pipeline</span>
            <div className="text-2xl font-bold text-blue-300 mt-1">{metrics.active_pipeline}</div>
            <span className="text-xs text-blue-500/80">In-progress</span>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-indigo-400 uppercase tracking-wider">Interviews</span>
            <div className="text-2xl font-bold text-indigo-300 mt-1">{metrics.interviews_scheduled}</div>
            <span className="text-xs text-indigo-500/80">Active rounds</span>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Offers</span>
            <div className="text-2xl font-bold text-emerald-300 mt-1">{metrics.offers_received}</div>
            <span className="text-xs text-emerald-500/80">Received</span>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-orange-400 uppercase tracking-wider">Ghosted / Stalled</span>
            <div className="text-2xl font-bold text-orange-300 mt-1">{metrics.stalled_or_ghosted}</div>
            <span className="text-xs text-orange-500/80">&gt; 14 days silent</span>
          </div>
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
            <span className="text-xs font-medium text-rose-400 uppercase tracking-wider">Rejections</span>
            <div className="text-2xl font-bold text-rose-300 mt-1">{metrics.rejections_received}</div>
            <span className="text-xs text-rose-500/80">Completed</span>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-900/60 p-4 rounded-xl border border-slate-800">
        <div className="w-full md:w-80">
          <input
            type="text"
            placeholder="Search company, title, or city..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* View mode toggle */}
        <div className="flex items-center space-x-2 w-full md:w-auto justify-between md:justify-end">
          <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
            <button
              onClick={() => setViewMode("board")}
              className={`px-3 py-1.5 rounded-md font-medium transition ${
                viewMode === "board"
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Kanban Board
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-1.5 rounded-md font-medium transition ${
                viewMode === "list"
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Table View
            </button>
          </div>
        </div>
      </div>

      {/* Status pills selector */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin">
        {STATUS_COLUMNS.map((col) => {
          const isSelected = selectedStatus === col.key;
          const count =
            col.key === "ALL"
              ? metrics?.total_applications || 0
              : metrics?.by_status[col.key] || 0;
          return (
            <button
              key={col.key}
              onClick={() => setSelectedStatus(col.key)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap border transition ${
                isSelected
                  ? "bg-indigo-600 text-white border-indigo-500 shadow"
                  : "bg-slate-900/80 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
              }`}
            >
              {col.label} ({count})
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      {loading ? (
        <div className="py-20 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
          <p className="text-sm">Loading applications...</p>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
          <h3 className="text-lg font-semibold text-slate-300">No applications found</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
            {searchQuery
              ? "No applications matched your search query. Try clearing the filter."
              : "Track your job hunt pipeline by adding your first application or saving jobs from Search."}
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="mt-4 px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow transition"
          >
            + Add First Application
          </button>
        </div>
      ) : viewMode === "board" ? (
        /* Kanban View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {filteredApps.map((app) => (
            <div
              key={app.id}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl p-4 flex flex-col justify-between transition group shadow-sm hover:shadow-indigo-500/5"
            >
              <div>
                <div className="flex justify-between items-start gap-2">
                  <span
                    className={`px-2 py-0.5 text-[11px] font-semibold rounded-md border ${getStatusColor(
                      app.status
                    )}`}
                  >
                    {app.status.replace(/_/g, " ")}
                  </span>
                  {app.notes_count > 0 && (
                    <span className="text-[11px] text-slate-500 flex items-center gap-1">
                      📝 {app.notes_count}
                    </span>
                  )}
                </div>

                <Link
                  href={`/applications/${app.id}`}
                  className="block mt-3 group-hover:text-indigo-400 transition"
                >
                  <h3 className="font-semibold text-white text-base leading-snug line-clamp-1">
                    {app.title_display}
                  </h3>
                  <p className="text-slate-400 text-xs mt-0.5 font-medium">
                    {app.company_display}
                  </p>
                </Link>

                <div className="text-xs text-slate-500 mt-3 space-y-1">
                  {app.city && <div>📍 {app.city}</div>}
                  {app.applied_at && (
                    <div>
                      📅 Applied: {new Date(app.applied_at).toLocaleDateString()}
                    </div>
                  )}
                  {app.next_interview_at && (
                    <div className="text-indigo-400 font-medium">
                      🎯 Interview: {new Date(app.next_interview_at).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex justify-between items-center text-xs">
                <Link
                  href={`/applications/${app.id}`}
                  className="text-indigo-400 hover:text-indigo-300 font-medium"
                >
                  View Details &rarr;
                </Link>
                {app.application_url && (
                  <a
                    href={app.application_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-400 hover:text-slate-200"
                    title="External job link"
                  >
                    🔗 Portal
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Table View */
        <div className="overflow-x-auto bg-slate-900/80 border border-slate-800 rounded-xl">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Role & Company</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Applied Date</th>
                <th className="px-4 py-3">Next Action</th>
                <th className="px-4 py-3">Notes</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredApps.map((app) => (
                <tr key={app.id} className="hover:bg-slate-800/30 transition">
                  <td className="px-4 py-3">
                    <Link
                      href={`/applications/${app.id}`}
                      className="font-medium text-white hover:text-indigo-400 block"
                    >
                      {app.title_display}
                    </Link>
                    <span className="text-xs text-slate-400">{app.company_display}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 text-xs font-medium rounded-md border ${getStatusColor(
                        app.status
                      )}`}
                    >
                      {app.status.replace(/_/g, " ")}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="px-4 py-3 text-xs text-indigo-400 font-medium">
                    {app.next_interview_at
                      ? `Interview: ${new Date(app.next_interview_at).toLocaleDateString()}`
                      : app.next_action_due_at
                      ? `Due: ${new Date(app.next_action_due_at).toLocaleDateString()}`
                      : "—"}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">
                    {app.notes_count > 0 ? `${app.notes_count} note(s)` : "None"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/applications/${app.id}`}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-medium px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 border border-slate-700"
                    >
                      Manage
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Add Application</h3>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {formError && (
              <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-lg">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateApplication} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Acme Cloud Corp"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Job Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Senior Backend Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Application / Career Portal URL
                </label>
                <input
                  type="url"
                  placeholder="https://..."
                  value={appUrl}
                  onChange={(e) => setAppUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Initial Status
                </label>
                <select
                  value={initialStatus}
                  onChange={(e) => setInitialStatus(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="SAVED">SAVED (Researching)</option>
                  <option value="PLANNING_TO_APPLY">PLANNING TO APPLY (Preparing)</option>
                  <option value="APPLIED">APPLIED (Confirmed submission)</option>
                  <option value="ASSESSMENT">ASSESSMENT (Take-home / OA)</option>
                  <option value="INTERVIEW">INTERVIEW (In rounds)</option>
                </select>
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Create Application"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

