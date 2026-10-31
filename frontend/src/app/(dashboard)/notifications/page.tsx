"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface NotificationItem {
  id: string;
  user_id: string;
  category: string;
  title: string;
  message: string;
  link_url?: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export default function NotificationsPage() {
  const { user, loading: authLoading } = useAuth();

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const url = unreadOnly ? "/notifications?unread_only=true" : "/notifications";
      const res = await apiClient<NotificationItem[]>(url);
      setNotifications(res.data || []);
    } catch (err: any) {
      console.error("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user, unreadOnly]);

  const handleMarkAsRead = async (id: string) => {
    try {
      await apiClient(`/notifications/${id}/read`, { method: "PATCH" });
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n))
      );
    } catch (err) {
      console.error("Failed to mark notification as read:", err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await apiClient("/notifications/read-all", { method: "POST" });
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, is_read: true, read_at: new Date().toISOString() }))
      );
    } catch (err) {
      console.error("Failed to mark all as read:", err);
    }
  };

  const filtered = notifications.filter((n) => {
    if (selectedCategory === "ALL") return true;
    return n.category === selectedCategory;
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
            <span>🔔 Notifications</span>
            {unreadCount > 0 && (
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-indigo-600 text-white font-bold">
                {unreadCount} unread
              </span>
            )}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Application updates, reminder alerts, and scheduled interview rounds.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {unreadCount > 0 && (
            <button
              onClick={handleMarkAllAsRead}
              className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
            >
              ✓ Mark All as Read
            </button>
          )}
          <Link
            href="/settings/notifications"
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-indigo-400 border border-slate-800 transition"
          >
            ⚙️ Preferences
          </Link>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2">
          {["ALL", "REMINDER", "APPLICATION_UPDATE", "INTERVIEW_ROUND"].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                selectedCategory === cat
                  ? "bg-indigo-600 text-white"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {cat.replace(/_/g, " ")}
            </button>
          ))}
        </div>

        <label className="flex items-center space-x-2 text-xs text-slate-400 cursor-pointer">
          <input
            type="checkbox"
            checked={unreadOnly}
            onChange={(e) => setUnreadOnly(e.target.checked)}
            className="rounded bg-slate-950 border-slate-800 text-indigo-600 focus:ring-0"
          />
          <span>Unread only</span>
        </label>
      </div>

      {/* Notification List */}
      {loading ? (
        <div className="py-16 text-center text-slate-400">
          <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent mb-2" />
          <p className="text-xs">Loading notifications...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl text-slate-500 text-xs">
          No notifications found.
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className={`p-4 rounded-xl border transition flex items-start justify-between gap-4 ${
                !item.is_read
                  ? "bg-slate-900 border-indigo-900/80 shadow-sm shadow-indigo-500/5"
                  : "bg-slate-950/60 border-slate-800/80 opacity-75"
              }`}
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-400 uppercase">
                    {item.category.replace(/_/g, " ")}
                  </span>
                  {!item.is_read && (
                    <span className="w-2 h-2 rounded-full bg-indigo-500 ring-2 ring-indigo-400/20" />
                  )}
                  <span className="text-xs text-slate-500">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>

                <h3 className="font-semibold text-white text-sm">{item.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed">{item.message}</p>

                {item.link_url && (
                  <div className="pt-2">
                    <Link
                      href={item.link_url}
                      className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 inline-flex items-center gap-1"
                    >
                      View Details &rarr;
                    </Link>
                  </div>
                )}
              </div>

              {!item.is_read && (
                <button
                  onClick={() => handleMarkAsRead(item.id)}
                  className="px-2.5 py-1 text-[11px] font-medium text-slate-400 hover:text-white rounded bg-slate-800 hover:bg-slate-700 whitespace-nowrap transition"
                >
                  Mark read
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

