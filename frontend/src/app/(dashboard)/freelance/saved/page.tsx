"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient, API_BASE_URL } from "@/services/apiClient";

export default function SavedFreelancePage() {
  const [savedItems, setSavedItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successNotice, setSuccessNotice] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // Note editing state
  const [editingId, setEditingId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  const fetchSaved = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<any>("/freelance/saved/all");
      setSavedItems(res.data || []);
    } catch (err: any) {
      setError(err?.message || "Failed to load saved freelance leads.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSaved();
  }, []);

  const handleUnsave = async (opportunityId: string) => {
    setError(null);
    try {
      await apiClient.delete(`/freelance/${opportunityId}/save`);
      setSavedItems((prev) => prev.filter((item) => item.opportunity_id !== opportunityId));
      setSuccessNotice("Opportunity removed from saved bookmarks.");
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to remove bookmark.");
    }
  };

  const handleStartEditNote = (item: any) => {
    setEditingId(item.opportunity_id);
    setNoteDraft(item.notes || "");
  };

  const handleSaveNote = async (opportunityId: string) => {
    setSavingNote(true);
    setError(null);
    try {
      await apiClient.post(`/freelance/${opportunityId}/save`, { notes: noteDraft });
      setSavedItems((prev) =>
        prev.map((item) =>
          item.opportunity_id === opportunityId ? { ...item, notes: noteDraft } : item
        )
      );
      setEditingId(null);
      setSuccessNotice("✓ Note updated successfully.");
      setTimeout(() => setSuccessNotice(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to update note.");
    } finally {
      setSavingNote(false);
    }
  };

  const handleExportSavedExcel = async () => {
    setExporting(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE_URL}/freelance/export/excel`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ saved_only: true }),
      });
      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        throw new Error(errJson?.detail || "Excel export failed.");
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `saved_freelance_leads_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      setSuccessNotice("✓ Saved leads exported to Excel (.xlsx) successfully!");
      setTimeout(() => setSuccessNotice(null), 4000);
    } catch (err: any) {
      setError(err?.message || "Failed to export saved leads.");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <Link href="/freelance" className="text-xs font-semibold text-indigo-400 hover:underline">
              ← Back to Opportunities Dashboard
            </Link>
            <h1 className="text-2xl font-bold text-white mt-2">Saved Freelance Leads</h1>
            <p className="text-xs text-slate-400 mt-1">
              Bookmarked prospective clients curated for follow-up, custom notes, and outreach.
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleExportSavedExcel}
              disabled={exporting || savedItems.length === 0}
              className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition shadow flex items-center space-x-1"
            >
              <span>📊</span>
              <span>{exporting ? "Exporting..." : "Export Excel (.xlsx)"}</span>
            </button>
            <span className="text-xs text-slate-400 font-medium">
              {savedItems.length} bookmarked
            </span>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-600 rounded-xl text-rose-200 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
          </div>
        )}
        {successNotice && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm flex items-center justify-between">
            <span>{successNotice}</span>
            <button onClick={() => setSuccessNotice(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
          </div>
        )}

        {loading ? (
          <div className="py-16 text-center text-slate-400">Loading saved leads...</div>
        ) : savedItems.length === 0 ? (
          <div className="py-16 text-center bg-slate-900/40 rounded-xl border border-dashed border-slate-800 text-slate-400">
            No saved freelance opportunities yet. Visit the{" "}
            <Link href="/freelance" className="text-indigo-400 underline">
              Opportunities Catalog
            </Link>{" "}
            to bookmark leads!
          </div>
        ) : (
          <div className="space-y-4">
            {savedItems.map((item) => (
              <div
                key={item.id}
                className="bg-slate-900 border border-slate-800 p-5 rounded-xl flex flex-col sm:flex-row sm:items-start justify-between gap-4 shadow-sm"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-base font-bold text-white">
                      {item.opportunity?.business_name || "Lead Record"}
                    </h3>
                    <span className="text-xs px-2 py-0.5 bg-slate-800 text-indigo-300 rounded font-semibold">
                      {item.opportunity?.service_category || "General"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {item.opportunity?.city || "Remote"} • {item.opportunity?.opportunity_title}
                  </p>

                  {/* Notes Editor Section */}
                  {editingId === item.opportunity_id ? (
                    <div className="mt-3 flex items-center gap-2">
                      <input
                        type="text"
                        value={noteDraft}
                        onChange={(e) => setNoteDraft(e.target.value)}
                        placeholder="Add candidate notes (e.g. called owner, follow up Tuesday)"
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        onClick={() => handleSaveNote(item.opportunity_id)}
                        disabled={savingNote}
                        className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg"
                      >
                        {savingNote ? "Saving..." : "Save"}
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <div className="mt-3 flex items-center gap-2">
                      <span className="text-xs text-indigo-300 bg-slate-950 px-2.5 py-1 rounded border border-slate-800/80">
                        {item.notes ? `Note: ${item.notes}` : "No notes attached"}
                      </span>
                      <button
                        onClick={() => handleStartEditNote(item)}
                        className="text-[11px] text-slate-400 hover:text-white underline"
                      >
                        {item.notes ? "Edit" : "+ Add Note"}
                      </button>
                    </div>
                  )}

                  <p className="text-[11px] text-slate-500 mt-2">
                    Saved on: {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>

                <div className="flex sm:flex-col items-center sm:items-end gap-2">
                  <Link
                    href={`/freelance/${item.opportunity_id}`}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition"
                  >
                    View Details →
                  </Link>
                  <button
                    onClick={() => handleUnsave(item.opportunity_id)}
                    className="px-3 py-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-950/40 border border-rose-800/40 rounded-lg text-xs transition"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
