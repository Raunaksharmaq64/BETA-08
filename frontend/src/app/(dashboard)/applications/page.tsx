"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { fastCache } from "@/services/fastCache";
import { useAuth } from "@/context/AuthContext";

interface ApplicationSummary {
  id: string;
  user_id: string;
  opportunity_id?: string;
  company_name: string;
  job_title: string;
  company_display?: string;
  title_display?: string;
  application_url?: string;
  status: string;
  applied_at?: string;
  apply_link_opened_at?: string;
  is_submission_confirmed?: boolean;
  current_stage?: string;
  salary_offered?: number;
  salary_currency?: string;
  contact_name?: string;
  contact_email?: string;
  next_action_due_at?: string;
  next_interview_at?: string;
  created_at: string;
  updated_at: string;
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

const KANBAN_STAGES = [
  {
    key: "SAVED_OR_PLANNING",
    label: "Planning / Saved",
    icon: "📌",
    statuses: ["SAVED", "PLANNING_TO_APPLY"],
    color: "border-amber-700/60 bg-amber-950/20 text-amber-300",
    targetStatus: "PLANNING_TO_APPLY",
  },
  {
    key: "APPLIED",
    label: "Applied & Pending",
    icon: "📨",
    statuses: ["APPLIED"],
    color: "border-blue-700/60 bg-blue-950/20 text-blue-300",
    targetStatus: "APPLIED",
  },
  {
    key: "ASSESSMENT",
    label: "Assessments",
    icon: "📝",
    statuses: ["ASSESSMENT"],
    color: "border-purple-700/60 bg-purple-950/20 text-purple-300",
    targetStatus: "ASSESSMENT",
  },
  {
    key: "INTERVIEW",
    label: "Interview Rounds",
    icon: "🎯",
    statuses: ["INTERVIEW"],
    color: "border-indigo-700/60 bg-indigo-950/20 text-indigo-300",
    targetStatus: "INTERVIEW",
  },
  {
    key: "OFFER",
    label: "Offers Received",
    icon: "🎉",
    statuses: ["OFFER"],
    color: "border-emerald-700/60 bg-emerald-950/20 text-emerald-300",
    targetStatus: "OFFER",
  },
  {
    key: "ARCHIVED",
    label: "Closed / Archived",
    icon: "📁",
    statuses: ["REJECTED", "WITHDRAWN", "GHOSTED", "CLOSED"],
    color: "border-slate-800 bg-slate-900/40 text-slate-400",
    targetStatus: "CLOSED",
  },
];

export default function ApplicationsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [applications, setApplications] = useState<ApplicationSummary[]>(() => {
    return fastCache.get<ApplicationSummary[]>("crm_applications") || [];
  });
  const [metrics, setMetrics] = useState<ApplicationMetrics | null>(() => {
    return fastCache.get<ApplicationMetrics>("crm_metrics") || null;
  });
  const [loading, setLoading] = useState(() => {
    return (fastCache.get<ApplicationSummary[]>("crm_applications") || []).length === 0;
  });
  const [isSyncing, setIsSyncing] = useState(false);
  const [autoSync, setAutoSync] = useState(true);
  const [lastSyncTime, setLastSyncTime] = useState<string>("Just now");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStatusTab, setSelectedStatusTab] = useState<string>("ALL");
  const [viewMode, setViewMode] = useState<"board" | "list">("board");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Kanban Drag-and-Drop state
  const [draggedAppId, setDraggedAppId] = useState<string | null>(null);
  const [dragOverColKey, setDragOverColKey] = useState<string | null>(null);

  // Transition state
  const [transitioningId, setTransitioningId] = useState<string | null>(null);
  const [confirmAppItem, setConfirmAppItem] = useState<ApplicationSummary | null>(null);
  const [confirmTargetStatus, setConfirmTargetStatus] = useState<string>("APPLIED");
  const [confirmReason, setConfirmReason] = useState<string>("");

  // Create Application Modal state
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [companyName, setCompanyName] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [appUrl, setAppUrl] = useState("");
  const [initialStatus, setInitialStatus] = useState("PLANNING_TO_APPLY");
  const [initialNotes, setInitialNotes] = useState("");
  const [contactName, setContactName] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [salaryOffered, setSalaryOffered] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const fetchData = async (isBackground = false) => {
    if (!isBackground && applications.length === 0) setLoading(true);
    else setIsSyncing(true);
    try {
      const [appsRes, metricsRes] = await Promise.all([
        apiClient<ApplicationSummary[]>("/applications?limit=100"),
        apiClient<ApplicationMetrics>("/applications/stats"),
      ]);
      const fetchedApps = appsRes.data || [];
      const fetchedMetrics = metricsRes.data || null;
      setApplications(fetchedApps);
      setMetrics(fetchedMetrics);
      fastCache.set("crm_applications", fetchedApps, 120000);
      if (fetchedMetrics) fastCache.set("crm_metrics", fetchedMetrics, 120000);
      setLastSyncTime(new Date().toLocaleTimeString());
    } catch (err: any) {
      console.error("Failed to load applications CRM data:", err);
    } finally {
      setLoading(false);
      setIsSyncing(false);
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
  }, [user, authLoading]);

  // Live Auto-Sync Poller (every 20 seconds when autoSync is enabled)
  useEffect(() => {
    if (!autoSync || !user) return;
    const interval = setInterval(() => {
      fetchData(true);
    }, 20000);
    return () => clearInterval(interval);
  }, [autoSync, user]);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

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
          company_name: companyName.trim(),
          job_title: jobTitle.trim(),
          custom_company_name: companyName.trim(),
          custom_job_title: jobTitle.trim(),
          application_url: appUrl.trim() || undefined,
          status: initialStatus,
          initial_notes: initialNotes.trim() || undefined,
          contact_name: contactName.trim() || undefined,
          contact_email: contactEmail.trim() || undefined,
          salary_offered: salaryOffered ? parseFloat(salaryOffered) : undefined,
        }),
      });
      setIsCreateModalOpen(false);
      setCompanyName("");
      setJobTitle("");
      setAppUrl("");
      setInitialNotes("");
      setContactName("");
      setContactEmail("");
      setSalaryOffered("");
      setInitialStatus("PLANNING_TO_APPLY");
      showToast("Application added to your application tracker!");
      fetchData();
    } catch (err: any) {
      setFormError(err.message || "Failed to create application.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleQuickTransition = async (
    app: ApplicationSummary,
    targetStatus: string,
    reason?: string,
    confirmSubmission = true
  ) => {
    if (app.status === targetStatus) return;

    setTransitioningId(app.id);

    // Save snapshot for atomic rollback on failure
    const previousApplications = [...applications];

    // 1. Instant Optimistic UI Update for zero perceived latency
    setApplications((prev) =>
      prev.map((item) =>
        item.id === app.id
          ? {
              ...item,
              status: targetStatus,
              applied_at:
                targetStatus === "APPLIED"
                  ? (item.applied_at || new Date().toISOString())
                  : item.applied_at,
            }
          : item
      )
    );

    try {
      // Auto-step if needed for state machine compliance
      if (app.status === "SAVED" && ["INTERVIEW", "OFFER", "ASSESSMENT"].includes(targetStatus)) {
        await apiClient(`/applications/${app.id}/transition`, {
          method: "POST",
          body: JSON.stringify({
            to_status: "PLANNING_TO_APPLY",
            reason: "Auto-transitioned before stage promotion",
            confirm_submission: false,
          }),
        });
      } else if (app.status === "GHOSTED" && ["OFFER", "ASSESSMENT", "SAVED", "PLANNING_TO_APPLY"].includes(targetStatus)) {
        await apiClient(`/applications/${app.id}/transition`, {
          method: "POST",
          body: JSON.stringify({
            to_status: "INTERVIEW",
            reason: "Resumed active communication",
            confirm_submission: false,
          }),
        });
      } else if ((app.status === "REJECTED" || app.status === "CLOSED" || app.status === "WITHDRAWN") && targetStatus === "OFFER") {
        await apiClient(`/applications/${app.id}/transition`, {
          method: "POST",
          body: JSON.stringify({
            to_status: "INTERVIEW",
            reason: "Reopened for final offer stage",
            confirm_submission: false,
          }),
        });
      }

      await apiClient(`/applications/${app.id}/transition`, {
        method: "POST",
        body: JSON.stringify({
          to_status: targetStatus,
          reason: reason || `Updated via Application Tracker`,
          confirm_submission: targetStatus === "APPLIED" ? true : confirmSubmission,
        }),
      });

      const title = app.title_display || app.job_title || "Application";
      const comp = app.company_display || app.company_name || "";
      showToast(`✓ Shifted "${title}" at ${comp} → ${targetStatus.replace(/_/g, " ")}!`);
      setConfirmAppItem(null);

      // Reconcile KPIs and server state in background
      fetchData(true);
    } catch (err: any) {
      // Rollback to prior state if backend rejected transition
      setApplications(previousApplications);
      showToast(`⚠️ Failed to update stage: ${err.message || "Invalid state transition"}`);
    } finally {
      setTransitioningId(null);
    }
  };

  const handleDropOnStage = async (appId: string, targetStatus: string, colStatuses: string[]) => {
    const cleanId = appId.includes("/") ? appId.split("/").filter(Boolean).pop()! : appId;
    const app = applications.find((a) => a.id === cleanId);
    if (!app) return;
    if (colStatuses.includes(app.status)) return;
    await handleQuickTransition(app, targetStatus, `Shifted stage via Kanban drag & drop`, true);
  };

  const handleDeleteApplication = async (app: ApplicationSummary) => {
    const title = app.title_display || app.job_title;
    if (!confirm(`Are you sure you want to remove "${title}" from your application tracking?`)) return;
    try {
      await apiClient(`/applications/${app.id}`, { method: "DELETE" });
      setApplications((prev) => prev.filter((a) => a.id !== app.id));
      showToast(`Removed "${title}" from tracking.`);
      fetchData(true);
    } catch (err: any) {
      alert(err.message || "Failed to delete application.");
    }
  };

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

  const filteredApps = applications.filter((app) => {
    const comp = (app.company_display || app.company_name || "").toLowerCase();
    const title = (app.title_display || app.job_title || "").toLowerCase();
    const city = (app.city || "").toLowerCase();

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      if (!comp.includes(q) && !title.includes(q) && !city.includes(q)) return false;
    }

    if (selectedStatusTab !== "ALL") {
      if (app.status !== selectedStatusTab) return false;
    }

    return true;
  });

  const kanbanApps = applications.filter((app) => {
    const comp = (app.company_display || app.company_name || "").toLowerCase();
    const title = (app.title_display || app.job_title || "").toLowerCase();
    const city = (app.city || "").toLowerCase();

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      if (!comp.includes(q) && !title.includes(q) && !city.includes(q)) return false;
    }

    return true;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              Job Application Tracker
            </h1>
            <span className="text-xs neo-inset text-emerald-900 font-mono font-bold px-3 py-1 rounded-xl flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Live Audit CRM v2.0
            </span>
          </div>
          <p className="text-slate-700 font-semibold text-sm mt-1">
            Real-time auditable tracking with state machines, stage timestamps, interview prep intelligence, and zero fake data.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <Link
            href="/calendar"
            className="neo-pill px-4 py-2 text-xs font-bold rounded-xl text-slate-800 hover:text-indigo-600 transition-all"
          >
            📅 Calendar
          </Link>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="neo-btn-primary px-4 py-2 text-xs font-bold rounded-xl shadow-md transition-all"
          >
            + Add Application
          </button>
        </div>
      </div>

      {/* Real-time Sync & Live Polling Bar */}
      <div className="neo-box flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl text-xs font-bold text-slate-800 border border-white/90">
        <div className="flex items-center gap-3 flex-wrap">
          <button
            onClick={() => setAutoSync(!autoSync)}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg font-semibold transition-colors border ${
              autoSync
                ? "bg-emerald-950/60 border-emerald-800 text-emerald-400"
                : "bg-slate-800 border-slate-700 text-slate-400"
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${autoSync ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
            Auto-Sync: {autoSync ? "LIVE (20s)" : "PAUSED"}
          </button>

          <span className="text-slate-700 font-bold">

            Last synced: <span className="text-slate-900 font-mono font-extrabold">{lastSyncTime}</span>
          </span>

          <span className="hidden lg:inline-flex items-center gap-1.5 text-slate-700 font-bold neo-inset px-3 py-1 rounded-xl">
            <span>✋</span> Drag & drop cards across Kanban stages to shift roles
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchData(false)}
            disabled={isSyncing}
            className="neo-pill inline-flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-slate-800 hover:text-indigo-600 font-bold transition-all disabled:opacity-50"
          >
            <span className={isSyncing ? "animate-spin" : ""}>⟳</span>
            {isSyncing ? "Syncing..." : "Sync Applications"}
          </button>
        </div>
      </div>

      {/* Real-time Toast Banner */}
      {toastMessage && (
        <div className="p-3.5 rounded-xl bg-emerald-950/90 border border-emerald-700 text-emerald-200 text-xs flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2 font-medium">
            <span>✨</span>
            <span>{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-emerald-400 hover:text-white">
            ✕
          </button>
        </div>
      )}

      {/* Live Pipeline Funnel KPIs */}
      {metrics && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Total</span>
            <div className="text-2xl font-black text-slate-900 mt-0.5">{metrics.total_applications}</div>
            <span className="text-[11px] text-slate-500">Tracked roles</span>
          </div>

          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-blue-400 uppercase tracking-wider">Active Applications</span>
            <div className="text-2xl font-black text-blue-800 mt-0.5">{metrics.active_pipeline}</div>
            <span className="text-[11px] text-blue-400/80">In-flight stages</span>
          </div>

          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">Interviews</span>
            <div className="text-2xl font-black text-indigo-800 mt-0.5">{metrics.interviews_scheduled}</div>
            <span className="text-[11px] text-indigo-400/80">Active rounds</span>
          </div>

          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Offers</span>
            <div className="text-2xl font-black text-emerald-800 mt-0.5">{metrics.offers_received}</div>
            <span className="text-[11px] text-emerald-400/80">Received</span>
          </div>

          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-orange-400 uppercase tracking-wider">Silent / Ghosted</span>
            <div className="text-2xl font-black text-orange-800 mt-0.5">{metrics.stalled_or_ghosted}</div>
            <span className="text-[11px] text-orange-400/80">&gt; 14 days silent</span>
          </div>

          <div className="neo-card neo-box-hover rounded-2xl p-4 border border-white/90">
            <span className="text-[11px] font-semibold text-rose-400 uppercase tracking-wider">Rejections</span>
            <div className="text-2xl font-black text-rose-800 mt-0.5">{metrics.rejections_received}</div>
            <span className="text-[11px] text-rose-400/80">Archive completed</span>
          </div>
        </div>
      )}

      {/* Filter and View Toggle Controls */}
      <div className="neo-box flex flex-col md:flex-row justify-between items-center gap-4 p-4 rounded-2xl border border-white/90">
        <div className="w-full md:w-80">
          <input
            type="text"
            placeholder="Search company, job role, or location..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full neo-inset rounded-xl px-4 py-2.5 text-xs font-bold text-slate-900 placeholder:text-slate-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center space-x-2 w-full md:w-auto justify-between md:justify-end">
          <div className="flex neo-inset p-1 rounded-xl text-xs font-bold">
            <button
              onClick={() => setViewMode("board")}
              className={`px-3 py-1.5 rounded-md font-semibold transition ${
                viewMode === "board" ? "neo-pill text-indigo-700 font-black shadow-sm" : "text-slate-700 hover:text-slate-950 font-bold"
              }`}
            >
              Kanban Board
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-1.5 rounded-md font-semibold transition ${
                viewMode === "list" ? "neo-pill text-indigo-700 font-black shadow-sm" : "text-slate-700 hover:text-slate-950 font-bold"
              }`}
            >
              Table View
            </button>
          </div>
        </div>
      </div>

      {/* Status Filter Chips */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2 scrollbar-thin">
        {[
          { key: "ALL", label: "All Applications", count: metrics?.total_applications || applications.length },
          { key: "SAVED", label: "Saved", count: metrics?.by_status?.SAVED || 0 },
          { key: "PLANNING_TO_APPLY", label: "Planning to Apply", count: metrics?.by_status?.PLANNING_TO_APPLY || 0 },
          { key: "APPLIED", label: "Applied", count: metrics?.by_status?.APPLIED || 0 },
          { key: "ASSESSMENT", label: "Assessment", count: metrics?.by_status?.ASSESSMENT || 0 },
          { key: "INTERVIEW", label: "Interview", count: metrics?.by_status?.INTERVIEW || 0 },
          { key: "OFFER", label: "Offer", count: metrics?.by_status?.OFFER || 0 },
          { key: "REJECTED", label: "Rejected", count: metrics?.by_status?.REJECTED || 0 },
        ].map((col) => {
          const isSelected = selectedStatusTab === col.key;
          return (
            <button
              key={col.key}
              onClick={() => setSelectedStatusTab(col.key)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all duration-150 ${
                isSelected

                  ? "neo-inset text-indigo-700 font-black shadow-inner border border-indigo-300"

                  : "neo-pill text-slate-800 hover:text-indigo-600 font-bold"
              }`}
            >
              {col.label} ({col.count})
            </button>
          );
        })}
      </div>

      {/* Top Background Revalidation Glow Bar */}
      {isSyncing && (
        <div className="fixed top-0 left-0 right-0 h-[2.5px] bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 animate-pulse z-50 shadow-sm" />
      )}

      {/* Main Content Area */}
      {loading && applications.length === 0 ? (
        <div className="py-20 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent mb-3" />
          <p className="text-sm">Loading application tracker...</p>
        </div>
      ) : filteredApps.length === 0 ? (
        <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-12 text-center">
          <h3 className="text-lg font-semibold text-slate-300">No applications in this view</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
            {searchQuery
              ? "No applications matched your search. Clear search or select All."
              : "Track job openings from the Opportunities feed or click Add Application."}
          </p>
          <div className="mt-4 flex items-center justify-center gap-3">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow"
            >
              + Add Application
            </button>
            <Link
              href="/opportunities"
              className="neo-btn-primary px-4 py-2 text-xs font-bold rounded-xl transition-all shadow-md"
            >
              Browse Opportunities →
            </Link>
          </div>
        </div>
      ) : viewMode === "board" ? (
        /* True Drag-and-Drop Kanban Columns Pipeline View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 items-start">
          {KANBAN_STAGES.map((col) => {
            const colApps = kanbanApps.filter((a) => col.statuses.includes(a.status));
            const isDropActive = dragOverColKey === col.key;

            return (
              <div
                key={col.key}
                onDragEnter={(e) => {
                  e.preventDefault();
                  if (dragOverColKey !== col.key) setDragOverColKey(col.key);
                }}
                onDragOver={(e) => {
                  e.preventDefault();
                  e.dataTransfer.dropEffect = "move";
                  if (dragOverColKey !== col.key) setDragOverColKey(col.key);
                }}
                onDragLeave={(e) => {
                  if (!e.currentTarget.contains(e.relatedTarget as Node)) {
                    if (dragOverColKey === col.key) setDragOverColKey(null);
                  }
                }}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragOverColKey(null);
                  const customData = e.dataTransfer.getData("application/x-rightfit-id");
                  const plainData = e.dataTransfer.getData("text/plain");
                  const droppedId = draggedAppId || customData || plainData;
                  if (droppedId) {
                    const cleanId = droppedId.includes("/") ? droppedId.split("/").filter(Boolean).pop()! : droppedId;
                    handleDropOnStage(cleanId, col.targetStatus, col.statuses);
                  }
                  setDraggedAppId(null);
                }}
                className={`border rounded-xl p-3 flex flex-col min-h-[520px] transition-colors duration-150 ${
                  isDropActive
                    ? "bg-slate-900 ring-2 ring-indigo-500 border-indigo-500 shadow-xl shadow-indigo-500/10"
                    : "neo-box border border-white/90 hover:border-slate-300/80"
                }`}
              >
                {/* Column Header */}
                <div className={`p-2.5 rounded-lg border flex items-center justify-between mb-3 ${col.color}`}>
                  <span className="text-xs font-bold flex items-center gap-1.5">
                    <span>{col.icon}</span>
                    <span>{col.label}</span>
                  </span>
                  <span className="text-xs font-mono font-bold px-1.5 py-0.2 rounded bg-black/30">
                    {colApps.length}
                  </span>
                </div>

                {/* Drop Zone Visual Indicator */}
                {isDropActive && (
                  <div className="pointer-events-none mb-3 p-3 rounded-xl border-2 border-dashed border-indigo-400 bg-indigo-950/60 text-indigo-200 text-center text-xs font-bold flex items-center justify-center gap-2 animate-pulse shadow-inner select-none">
                    <span>⬇️</span> Drop to move into {col.label}
                  </div>
                )}

                {/* Cards Container */}
                <div className="space-y-3 flex-1">
                  {colApps.length === 0 ? (
                    <div className="py-8 text-center text-[11px] text-slate-600 border border-dashed border-slate-800/80 rounded-lg">
                      {isDropActive ? "Release to drop card here" : "No roles here"}
                    </div>
                  ) : (
                    colApps.map((app) => {
                      const comp = app.company_display || app.company_name || "Company";
                      const title = app.title_display || app.job_title || "Job Title";
                      const isDragging = draggedAppId === app.id;
                      const isTransitioning = transitioningId === app.id;

                      return (
                        <div
                          key={app.id}
                          draggable={true}
                          onDragStart={(e) => {
                            e.dataTransfer.setData("text/plain", app.id);
                            e.dataTransfer.setData("application/x-rightfit-id", app.id);
                            e.dataTransfer.effectAllowed = "move";
                            setDraggedAppId(app.id);
                          }}
                          onDragEnd={() => {
                            setDraggedAppId(null);
                            setDragOverColKey(null);
                          }}
                          className={`neo-card neo-box-hover p-4 rounded-2xl border border-white/90 space-y-2.5 cursor-grab active:cursor-grabbing select-none ${
                            isDragging ? "opacity-40 border-dashed border-indigo-400 ring-2 ring-indigo-500/50" : ""
                          }`}
                        >
                          <div className="flex justify-between items-center gap-1">
                            {/* Interactive Stage Toggle Dropdown */}
                            <select
                              value={app.status}
                              onChange={(e) => {
                                e.stopPropagation();
                                handleQuickTransition(app, e.target.value, `Shifted stage to ${e.target.value}`, true);
                              }}
                              disabled={isTransitioning}
                              aria-label="Change status"
                              className={`px-2 py-0.5 text-[10px] font-bold rounded border cursor-pointer focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-slate-950 ${getStatusColor(app.status)}`}
                              draggable={false}
                            >
                              <option value="SAVED">Saved</option>
                              <option value="PLANNING_TO_APPLY">Planning</option>
                              <option value="APPLIED">Applied</option>
                              <option value="ASSESSMENT">Assessment</option>
                              <option value="INTERVIEW">Interview</option>
                              <option value="OFFER">Offer</option>
                              <option value="REJECTED">Rejected</option>
                              <option value="GHOSTED">Ghosted</option>
                              <option value="CLOSED">Closed</option>
                            </select>

                            <div className="flex items-center gap-1.5 text-slate-500">
                              {app.notes_count > 0 && (
                                <span className="text-[10px] text-slate-400 font-mono flex items-center gap-0.5">
                                  📝 {app.notes_count}
                                </span>
                              )}
                              <span className="text-sm text-slate-400 hover:text-slate-200 cursor-grab active:cursor-grabbing p-0.5 select-none" title="Drag card to move across stages">
                                ⋮⋮
                              </span>
                            </div>
                          </div>

                          <Link
                            href={`/applications/${app.id}`}
                            draggable={false}
                            className="block hover:text-indigo-300 transition"
                          >
                            <h4 className="font-black text-slate-900 text-sm line-clamp-2 leading-snug hover:text-indigo-600 transition-colors">
                              {title}
                            </h4>
                            <p className="text-xs text-indigo-700 font-bold mt-0.5">
                              {comp}
                            </p>
                          </Link>

                          {app.applied_at && (
                            <div className="text-[11px] text-slate-700 font-mono font-bold">
                              📅 Applied: {new Date(app.applied_at).toLocaleDateString()}
                            </div>
                          )}

                          {app.next_interview_at && (
                            <div className="text-[11px] text-indigo-800 font-bold flex items-center gap-1">
                              <span>🎯 Round:</span>
                              <span>{new Date(app.next_interview_at).toLocaleDateString()}</span>
                            </div>
                          )}

                          {/* Quick 1-Click State Transition Buttons */}
                          <div className="pt-2 border-t border-slate-800/80 space-y-1.5">
                            <div className="flex items-center gap-1 flex-wrap">
                              {app.status === "SAVED" && (
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleQuickTransition(app, "PLANNING_TO_APPLY"); }} draggable={false}
                                  disabled={isTransitioning}
                                  className="neo-pill text-[10px] font-bold px-2.5 py-0.5 text-amber-800 hover:text-amber-950 transition disabled:opacity-50"
                                >
                                  ⚡ Prepare
                                </button>
                              )}

                              {(app.status === "SAVED" || app.status === "PLANNING_TO_APPLY") && (
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleQuickTransition(app, "APPLIED", "Applied via company portal", true); }} draggable={false}
                                  disabled={isTransitioning}
                                  className="neo-pill text-[10px] font-bold px-2.5 py-0.5 text-blue-800 hover:text-blue-950 transition disabled:opacity-50"
                                >
                                  ✓ Applied
                                </button>
                              )}

                              {(app.status === "SAVED" || app.status === "PLANNING_TO_APPLY" || app.status === "APPLIED" || app.status === "ASSESSMENT") && (
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleQuickTransition(app, "INTERVIEW", "Interview invite received", true); }} draggable={false}
                                  disabled={isTransitioning}
                                  className="neo-pill text-[10px] font-bold px-2.5 py-0.5 text-indigo-800 hover:text-indigo-950 transition disabled:opacity-50"
                                >
                                  🎯 Interview
                                </button>
                              )}

                              {app.status !== "OFFER" && app.status !== "CLOSED" && (
                                <button
                                  onClick={(e) => { e.stopPropagation(); handleQuickTransition(app, "OFFER", "Formal offer extended", true); }} draggable={false}
                                  disabled={isTransitioning}
                                  className="neo-pill text-[10px] font-bold px-2.5 py-0.5 text-emerald-800 hover:text-emerald-950 transition disabled:opacity-50"
                                >
                                  🎉 Offer
                                </button>
                              )}

                              {app.status === "INTERVIEW" && (
                                <Link
                                  href={`/interview-prep/48-hour?role=${encodeURIComponent(title)}&company=${encodeURIComponent(comp)}`}

                                  draggable={false}
                                  className="text-[10px] font-semibold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800 hover:bg-purple-900 transition"
                                >
                                  🚀 Prep
                                </Link>
                              )}
                            </div>

                            <div className="flex items-center justify-between text-[11px] pt-1">
                              <Link

                                href={`/applications/${app.id}`}

                                draggable={false}

                                className="text-indigo-700 hover:text-indigo-900 font-bold"

                              >
                                Manage →
                              </Link>
                              <button
                                onClick={(e) => { e.stopPropagation(); handleDeleteApplication(app); }} draggable={false}
                                className="text-slate-500 hover:text-rose-400 text-xs"
                                title="Remove from tracking"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Dense Table View */
        <div className="overflow-x-auto bg-slate-900/80 border border-slate-800 rounded-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="neo-box uppercase text-[10px] text-slate-900 font-black border-b border-slate-300/80">
              <tr>
                <th className="px-4 py-3">Role & Employer</th>
                <th className="px-4 py-3">Current Status</th>
                <th className="px-4 py-3">Applied Date</th>
                <th className="px-4 py-3">Quick Stage Shift</th>
                <th className="px-4 py-3">Notes</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredApps.map((app) => {
                const comp = app.company_display || app.company_name || "Company";
                const title = app.title_display || app.job_title || "Job Title";
                const isTransitioning = transitioningId === app.id;

                return (
                  <tr key={app.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-4 py-3">
                      <Link href={`/applications/${app.id}`} className="font-bold text-white hover:text-indigo-300 block">
                        {title}
                      </Link>
                      <span className="text-[11px] text-indigo-400">{comp}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${getStatusColor(app.status)}`}>
                        {app.status.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono">
                      {app.applied_at ? new Date(app.applied_at).toLocaleDateString() : "—"}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {/* Plan/Prepare button */}
                        {app.status === "SAVED" && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleQuickTransition(app, "PLANNING_TO_APPLY"); }} draggable={false}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-amber-950/70 text-amber-300 border border-amber-800/80 hover:bg-amber-900 transition disabled:opacity-50"
                            title="Move to Planning to Apply"
                          >
                            ⚡ Plan
                          </button>
                        )}

                        {/* Applied button */}
                        {app.status !== "APPLIED" && (
                          <button
                            onClick={() => handleQuickTransition(app, "APPLIED", "Marked as applied", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-blue-950/70 text-blue-300 border border-blue-800/80 hover:bg-blue-900 transition disabled:opacity-50"
                            title="Mark as Applied"
                          >
                            {isTransitioning ? "⏳" : "✓ Applied"}
                          </button>
                        )}

                        {/* Assessment button */}
                        {app.status !== "ASSESSMENT" && app.status !== "OFFER" && app.status !== "CLOSED" && (
                          <button
                            onClick={() => handleQuickTransition(app, "ASSESSMENT", "Assessment scheduled", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-purple-950/70 text-purple-300 border border-purple-800/80 hover:bg-purple-900 transition disabled:opacity-50"
                            title="Move to Assessment"
                          >
                            📝 Assessment
                          </button>
                        )}

                        {/* Interview button */}
                        {app.status !== "INTERVIEW" && app.status !== "OFFER" && app.status !== "CLOSED" && (
                          <button
                            onClick={() => handleQuickTransition(app, "INTERVIEW", "Invited to interview", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-indigo-950/70 text-indigo-300 border border-indigo-800/80 hover:bg-indigo-900 transition disabled:opacity-50"
                            title="Move to Interview"
                          >
                            🎯 Interview
                          </button>
                        )}

                        {/* Offer button */}
                        {app.status !== "OFFER" && (
                          <button
                            onClick={() => handleQuickTransition(app, "OFFER", "Offer received", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-emerald-950/70 text-emerald-300 border border-emerald-800/80 hover:bg-emerald-900 transition disabled:opacity-50"
                            title="Move to Offer"
                          >
                            🎉 Offer
                          </button>
                        )}

                        {/* Reject button */}
                        {!["REJECTED", "CLOSED", "WITHDRAWN"].includes(app.status) && (
                          <button
                            onClick={() => handleQuickTransition(app, "REJECTED", "Rejected by company", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-rose-950/50 text-rose-300 border border-rose-800/60 hover:bg-rose-900/60 transition disabled:opacity-50"
                            title="Mark as Rejected"
                          >
                            ✕ Reject
                          </button>
                        )}

                        {/* Re-open button if closed/rejected */}
                        {["REJECTED", "CLOSED", "WITHDRAWN"].includes(app.status) && (
                          <button
                            onClick={() => handleQuickTransition(app, "PLANNING_TO_APPLY", "Re-opened application", true)}
                            disabled={isTransitioning}
                            className="text-[10px] font-medium px-2 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 transition disabled:opacity-50"
                            title="Re-open into Planning"
                          >
                            ↺ Re-open
                          </button>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-400 font-mono">
                      {app.notes_count > 0 ? `${app.notes_count} note(s)` : "None"}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/applications/${app.id}`}
                          className="text-xs text-indigo-900 hover:text-indigo-600 font-bold px-3 py-1.5 rounded-xl neo-pill border border-indigo-200 inline-block transition-all"
                        >
                          Manage →
                        </Link>
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDeleteApplication(app); }} draggable={false}
                          className="text-slate-500 hover:text-rose-400 p-1 text-xs"
                          title="Delete Application"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Confirmation Modal for Confirm Submission (Anti-Fake Auditing) */}
      {confirmAppItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>✓</span> Confirm Official Application Submission
              </h3>
              <button onClick={() => setConfirmAppItem(null)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              To guarantee 100% audit integrity, RightFit verifies that you have officially submitted your resume/application for{" "}
              <strong className="text-white">
                {confirmAppItem.title_display || confirmAppItem.job_title} at {confirmAppItem.company_display || confirmAppItem.company_name}
              </strong>.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">
                Audit Transition Note (Optional)
              </label>
              <input
                type="text"
                value={confirmReason}
                onChange={(e) => setConfirmReason(e.target.value)}
                placeholder="e.g. Submitted via Greenhouse official portal"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setConfirmAppItem(null)}
                className="px-3.5 py-1.5 text-xs font-semibold text-slate-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleQuickTransition(confirmAppItem, confirmTargetStatus, confirmReason, true)}
                className="px-4 py-2 text-xs font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white shadow"
              >
                Yes, Submission Confirmed
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Add Application Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-base font-bold text-white">Add Application to Tracker</h3>
              <button onClick={() => setIsCreateModalOpen(false)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            {formError && (
              <div className="p-3 bg-rose-950/60 border border-rose-800 text-rose-300 text-xs rounded-lg">
                {formError}
              </div>
            )}

            <form onSubmit={handleCreateApplication} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Company / Organization *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Stripe, Acme Corp, or Local Business"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Job Role / Position *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Growth Marketing Lead or Senior Engineer"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Application URL (Optional)</label>
                <input
                  type="url"
                  placeholder="https://..."
                  value={appUrl}
                  onChange={(e) => setAppUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Initial Status</label>
                  <select
                    value={initialStatus}
                    onChange={(e) => setInitialStatus(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="SAVED">Saved / Researching</option>
                    <option value="PLANNING_TO_APPLY">Planning to Apply</option>
                    <option value="APPLIED">Applied (Submitted)</option>
                    <option value="INTERVIEW">Interview Scheduled</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Target Salary ($)</label>
                  <input
                    type="number"
                    placeholder="120000"
                    value={salaryOffered}
                    onChange={(e) => setSalaryOffered(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Recruiter / Contact Name</label>
                <input
                  type="text"
                  placeholder="e.g. Sarah Jenkins"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Private Notes</label>
                <textarea
                  rows={2}
                  placeholder="Custom intro pitch notes or referral contact..."
                  value={initialNotes}
                  onChange={(e) => setInitialNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-3.5 py-1.5 text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Add Application"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
