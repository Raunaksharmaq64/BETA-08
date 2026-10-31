"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface CalendarEvent {
  event_id: string;
  event_type: "INTERVIEW_ROUND" | "REMINDER";
  title: string;
  start_time: string;
  end_time?: string;
  source_id: string;
  metadata: Record<string, any>;
  has_conflict?: boolean;
}

interface ReminderItem {
  id: string;
  title: string;
  description?: string;
  category: string;
  priority: string;
  due_at: string;
  is_completed: boolean;
  application_id?: string;
}

const COMMON_TIMEZONES = [
  { value: "Asia/Kolkata", label: "India Standard Time (Asia/Kolkata)" },
  { value: "UTC", label: "Coordinated Universal Time (UTC)" },
  { value: "America/New_York", label: "Eastern Time (America/New_York)" },
  { value: "America/Chicago", label: "Central Time (America/Chicago)" },
  { value: "America/Denver", label: "Mountain Time (America/Denver)" },
  { value: "America/Los_Angeles", label: "Pacific Time (America/Los_Angeles)" },
  { value: "Europe/London", label: "London (Europe/London)" },
  { value: "Europe/Berlin", label: "Central European (Europe/Berlin)" },
  { value: "Asia/Singapore", label: "Singapore / Hong Kong (Asia/Singapore)" },
  { value: "Asia/Tokyo", label: "Japan Standard Time (Asia/Tokyo)" },
];

export default function CalendarPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const [selectedTz, setSelectedTz] = useState("UTC");
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [reminders, setReminders] = useState<ReminderItem[]>([]);
  const [loading, setLoading] = useState(true);

  // New Reminder Modal
  const [isNewReminderOpen, setIsNewReminderOpen] = useState(false);
  const [remTitle, setRemTitle] = useState("");
  const [remDesc, setRemDesc] = useState("");
  const [remDueAt, setRemDueAt] = useState("");
  const [remCategory, setRemCategory] = useState("FOLLOW_UP");
  const [remPriority, setRemPriority] = useState("NORMAL");
  const [savingReminder, setSavingReminder] = useState(false);

  const getGoogleCalendarUrl = (title: string, start: string, end?: string) => {
    try {
      const s = new Date(start).toISOString().replace(/-|:|\.\d\d\d/g, "");
      const e = end ? new Date(end).toISOString().replace(/-|:|\.\d\d\d/g, "") : s;
      return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(
        title
      )}&dates=${s}/${e}&details=${encodeURIComponent("RIGHT FIT Scheduled Career Event")}`;
    } catch {
      return "#";
    }
  };

  useEffect(() => {
    // Detect candidate default browser timezone
    try {
      const detected = Intl.DateTimeFormat().resolvedOptions().timeZone;
      if (detected) setSelectedTz(detected);
    } catch (e) {
      // fallback to UTC
    }
  }, []);

  const fetchCalendar = async () => {
    setLoading(true);
    try {
      const now = new Date();
      const start = new Date(now.getFullYear(), now.getMonth() - 1, 1).toISOString();
      const end = new Date(now.getFullYear(), now.getMonth() + 2, 0).toISOString();

      const [calRes, remRes] = await Promise.all([
        apiClient<CalendarEvent[]>(
          `/reminders/calendar?timezone=${encodeURIComponent(
            selectedTz
          )}&start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`
        ),
        apiClient<ReminderItem[]>("/reminders"),
      ]);

      setEvents(calRes.data || []);
      setReminders(remRes.data || []);
    } catch (err: any) {
      console.error("Failed to load calendar events:", err);
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
      fetchCalendar();
    }
  }, [user, authLoading, selectedTz]);

  const handleCreateReminder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!remTitle.trim() || !remDueAt) return;
    setSavingReminder(true);
    try {
      // Convert selected date-time to ISO UTC string
      const isoDate = new Date(remDueAt).toISOString();
      await apiClient("/reminders", {
        method: "POST",
        body: JSON.stringify({
          title: remTitle.trim(),
          description: remDesc.trim() || undefined,
          due_at: isoDate,
          timezone: selectedTz,
          category: remCategory,
          priority: remPriority,
        }),
      });
      setIsNewReminderOpen(false);
      setRemTitle("");
      setRemDesc("");
      setRemDueAt("");
      fetchCalendar();
    } catch (err: any) {
      alert(err.message || "Failed to create reminder.");
    } finally {
      setSavingReminder(false);
    }
  };

  const handleToggleComplete = async (rem: ReminderItem) => {
    try {
      await apiClient(`/reminders/${rem.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          is_completed: !rem.is_completed,
        }),
      });
      fetchCalendar();
    } catch (err: any) {
      alert(err.message || "Failed to update reminder.");
    }
  };

  const handleDeleteReminder = async (remId: string) => {
    if (!confirm("Are you sure you want to delete this reminder?")) return;
    try {
      await apiClient(`/reminders/${remId}`, { method: "DELETE" });
      fetchCalendar();
    } catch (err: any) {
      alert(err.message || "Failed to delete reminder.");
    }
  };

  const hasConflicts = events.some((e) => e.has_conflict);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Calendar & Deadlines</h1>
          <p className="text-slate-400 text-sm mt-1">
            Aggregated candidate timeline: scheduled interview rounds, deadlines, and smart
            reminders.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Timezone picker */}
          <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg text-xs">
            <span className="text-slate-400 font-medium">🌐 Timezone:</span>
            <select
              value={selectedTz}
              onChange={(e) => setSelectedTz(e.target.value)}
              className="bg-transparent text-indigo-400 font-semibold focus:outline-none"
            >
              {COMMON_TIMEZONES.map((tz) => (
                <option key={tz.value} value={tz.value} className="bg-slate-900 text-slate-200">
                  {tz.label}
                </option>
              ))}
              {!COMMON_TIMEZONES.some((t) => t.value === selectedTz) && (
                <option value={selectedTz} className="bg-slate-900 text-slate-200">
                  {selectedTz}
                </option>
              )}
            </select>
          </div>

          <a
            href="/api/v1/calendar/export.ics"
            download="rightfit-schedule.ics"
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center space-x-1.5 shadow-sm"
            title="Download standard .ics file for Google Calendar, Apple Calendar, and Outlook"
          >
            <span>📅 Export (.ics)</span>
          </a>

          <button
            onClick={() => setIsNewReminderOpen(true)}
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow transition"
          >
            + Add Reminder
          </button>
        </div>
      </div>

      {/* Conflict Warning Alert */}
      {hasConflicts && (
        <div className="p-4 bg-amber-950/40 border border-amber-800/80 rounded-xl text-amber-200 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-base">⚠️</span>
            <span>
              <strong>Schedule Conflict Detected:</strong> Two or more scheduled events overlap in
              your selected timezone. Please review your interview slots.
            </span>
          </div>
        </div>
      )}

      {/* Agenda & Reminders Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Aggregated Calendar Timeline (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center justify-between">
              <span>📅 Aggregated Events ({events.length})</span>
              <span className="text-xs text-slate-400 font-normal">
                Timezone: {selectedTz}
              </span>
            </h2>

            {loading ? (
              <div className="py-12 text-center text-slate-400">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent mb-2" />
                <p className="text-xs">Loading schedule...</p>
              </div>
            ) : events.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-xs border border-dashed border-slate-800 rounded-lg">
                No events or interview rounds scheduled in this period.
              </div>
            ) : (
              <div className="space-y-3">
                {events.map((ev) => (
                  <div
                    key={ev.event_id}
                    className={`p-4 rounded-xl border transition ${
                      ev.has_conflict
                        ? "bg-amber-950/20 border-amber-800"
                        : ev.event_type === "INTERVIEW_ROUND"
                        ? "bg-indigo-950/30 border-indigo-800/60"
                        : "bg-slate-950/80 border-slate-800"
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider ${
                              ev.event_type === "INTERVIEW_ROUND"
                                ? "bg-indigo-900 text-indigo-300"
                                : "bg-slate-800 text-slate-400"
                            }`}
                          >
                            {ev.event_type === "INTERVIEW_ROUND" ? "🎯 Interview" : "⏰ Reminder"}
                          </span>
                          {ev.has_conflict && (
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-900 text-amber-200 uppercase">
                              Conflict
                            </span>
                          )}
                        </div>
                        <h3 className="font-semibold text-white text-sm mt-1">{ev.title}</h3>
                      </div>
                      <div className="text-right text-xs text-slate-400">
                        <div className="font-medium text-slate-200">
                          {new Date(ev.start_time).toLocaleDateString([], {
                            weekday: "short",
                            month: "short",
                            day: "numeric",
                          })}
                        </div>
                        <div>
                          {new Date(ev.start_time).toLocaleTimeString([], {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                          {ev.end_time &&
                            ` - ${new Date(ev.end_time).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}`}
                        </div>
                      </div>
                    </div>

                    {/* Metadata details */}
                    {ev.metadata && Object.keys(ev.metadata).length > 0 && (
                      <div className="mt-3 pt-2 border-t border-slate-800/60 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">
                        {ev.metadata.meeting_link && (
                          <a
                            href={ev.metadata.meeting_link}
                            target="_blank"
                            rel="noreferrer"
                            className="text-indigo-400 hover:text-indigo-300 underline font-medium"
                          >
                            Join Meeting Link ↗
                          </a>
                        )}
                        {ev.metadata.company_name && (
                          <span>Company: {ev.metadata.company_name}</span>
                        )}
                        {ev.metadata.category && <span>Category: {ev.metadata.category}</span>}
                        <a
                          href={getGoogleCalendarUrl(ev.title, ev.start_time, ev.end_time)}
                          target="_blank"
                          rel="noreferrer"
                          className="text-emerald-400 hover:text-emerald-300 underline font-medium ml-auto"
                        >
                          + Add to Google Cal ↗
                        </a>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Manage Reminders & Tasks (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h2 className="text-base font-bold text-white flex items-center justify-between">
              <span>Task Reminders ({reminders.length})</span>
            </h2>

            {reminders.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500">
                No active tasks. Add reminders for application deadlines or interview preparation.
              </div>
            ) : (
              <div className="space-y-3">
                {reminders.map((rem) => (
                  <div
                    key={rem.id}
                    className={`p-3.5 rounded-lg border text-xs flex items-start justify-between gap-3 transition ${
                      rem.is_completed
                        ? "bg-slate-950/40 border-slate-800/40 opacity-60"
                        : "bg-slate-950 border-slate-800"
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <input
                        type="checkbox"
                        checked={rem.is_completed}
                        onChange={() => handleToggleComplete(rem)}
                        className="mt-0.5 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-0"
                      />
                      <div>
                        <div
                          className={`font-semibold text-slate-200 ${
                            rem.is_completed ? "line-through text-slate-500" : ""
                          }`}
                        >
                          {rem.title}
                        </div>
                        {rem.description && (
                          <p className="text-slate-400 text-[11px] mt-0.5">{rem.description}</p>
                        )}
                        <div className="text-[11px] text-slate-500 mt-1 flex items-center gap-2">
                          <span>
                            Due: {new Date(rem.due_at).toLocaleDateString()}{" "}
                            {new Date(rem.due_at).toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </span>
                          <span>•</span>
                          <span className="uppercase text-[10px] font-bold text-indigo-400">
                            {rem.priority}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDeleteReminder(rem.id)}
                      className="text-slate-500 hover:text-rose-400 text-xs"
                      title="Delete reminder"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* New Reminder Modal */}
      {isNewReminderOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <h3 className="text-lg font-bold text-white">Create Reminder</h3>
              <button
                onClick={() => setIsNewReminderOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateReminder} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Send thank-you note to recruiter"
                  value={remTitle}
                  onChange={(e) => setRemTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Due Date & Time *
                </label>
                <input
                  type="datetime-local"
                  required
                  value={remDueAt}
                  onChange={(e) => setRemDueAt(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={remCategory}
                    onChange={(e) => setRemCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="FOLLOW_UP">Follow-Up</option>
                    <option value="DEADLINE">Application Deadline</option>
                    <option value="PREPARATION">Interview Prep</option>
                    <option value="GENERAL">General</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Priority
                  </label>
                  <select
                    value={remPriority}
                    onChange={(e) => setRemPriority(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="LOW">Low</option>
                    <option value="NORMAL">Normal</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Description / Context (Optional)
                </label>
                <textarea
                  rows={2}
                  placeholder="Notes or context for this reminder..."
                  value={remDesc}
                  onChange={(e) => setRemDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsNewReminderOpen(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingReminder}
                  className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
                >
                  {savingReminder ? "Saving..." : "Create Reminder"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

