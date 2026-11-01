"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../../../services/apiClient";

interface PrivacySettings {
  profile_visibility: "PUBLIC" | "PRIVATE" | "ANONYMIZED";
  opportunity_alerts: boolean;
  email_notifications: boolean;
  ai_processing_enabled: boolean;
  data_usage_research: boolean;
}

interface ConsentRecord {
  id: string;
  purpose: string;
  granted: boolean;
  policy_version: string;
  created_at: string;
  withdrawn_at?: string;
}

export default function PrivacySettingsPage() {
  const [settings, setSettings] = useState<PrivacySettings | null>(null);
  const [consents, setConsents] = useState<ConsentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Export State
  const [exportUrl, setExportUrl] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // Deletion Modal State
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState("");
  const [deleteReason, setDeleteReason] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [deletionStatus, setDeletionStatus] = useState<string | null>(null);

  const loadPrivacyData = async () => {
    try {
      const [sResp, cResp] = await Promise.all([
        apiClient<PrivacySettings>("/candidate/privacy"),
        apiClient<ConsentRecord[]>("/candidate/consents"),
      ]);
      setSettings(sResp.data);
      setConsents(cResp.data);
    } catch (err) {
      console.error("Failed to load privacy settings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPrivacyData();
  }, []);

  const handleToggle = (key: keyof PrivacySettings) => {
    if (!settings) return;
    setSettings({ ...settings, [key]: !settings[key] });
  };

  const handleSaveSettings = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      await apiClient("/candidate/privacy", {
        method: "PUT",
        body: JSON.stringify(settings),
      });
      alert("Privacy settings updated.");
    } catch (err) {
      alert("Failed to save settings.");
    } finally {
      setSaving(false);
    }
  };

  const handleWithdrawConsent = async (consentId: string) => {
    try {
      await apiClient(`/candidate/consents/${consentId}`, { method: "DELETE" });
      loadPrivacyData();
    } catch (err) {
      alert("Failed to withdraw consent.");
    }
  };

  const handleRequestExport = async () => {
    setExporting(true);
    try {
      const resp = await apiClient<{ download_url: string }>("/candidate/data-export", {
        method: "POST",
      });
      setExportUrl(resp.data.download_url);
    } catch (err) {
      alert("Failed to generate data export.");
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    setDeleting(true);
    try {
      const resp = await apiClient<{ message: string; scheduled_deletion_at: string }>(
        "/candidate/account-deletion",
        {
          method: "POST",
          body: JSON.stringify({
            confirmation: deleteConfirmation,
            reason: deleteReason,
          }),
        }
      );
      setDeletionStatus(resp.data.message);
      setShowDeleteModal(false);
    } catch (err: any) {
      alert(err.message || "Failed to schedule account deletion.");
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4 text-center text-slate-400">Loading privacy preferences...</div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {deletionStatus && (
        <div className="p-4 bg-amber-950/80 border border-amber-500/50 rounded-xl text-amber-200 text-sm">
          {deletionStatus}
        </div>
      )}

      {/* Visibility & AI Processing Settings */}
      <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h2 className="text-lg font-bold text-white mb-2">Privacy & Discoverability</h2>
        <p className="text-sm text-slate-400 mb-6">
          Configure how your profile is indexed and processed across opportunities.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-slate-300 mb-2">
              Profile Visibility Level
            </label>
            <select
              value={settings?.profile_visibility}
              onChange={(e) =>
                setSettings(
                  settings ? { ...settings, profile_visibility: e.target.value as any } : null
                )
              }
              className="w-full sm:w-64 px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
            >
              <option value="PUBLIC">Public (Visible to Verified Recruiters)</option>
              <option value="ANONYMIZED">Anonymized (Skills only, hide identity)</option>
              <option value="PRIVATE">Private (Direct applications only)</option>
            </select>
          </div>

          <div className="pt-4 border-t border-slate-800 space-y-3">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings?.ai_processing_enabled}
                onChange={() => handleToggle("ai_processing_enabled")}
                className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
              />
              <span className="text-sm text-slate-200">
                Enable AI Skill Fit & Semantic Resume Analysis
              </span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings?.opportunity_alerts}
                onChange={() => handleToggle("opportunity_alerts")}
                className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
              />
              <span className="text-sm text-slate-200">
                Allow High-Fit Career Alerts & Autonomous Opportunity Notifications
              </span>
            </label>

            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings?.data_usage_research}
                onChange={() => handleToggle("data_usage_research")}
                className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
              />
              <span className="text-sm text-slate-200">
                Allow Anonymized Aggregate Salary & Skill Benchmark Research
              </span>
            </label>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              type="button"
              onClick={handleSaveSettings}
              disabled={saving}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white font-medium text-sm transition-colors"
            >
              {saving ? "Saving..." : "Save Settings"}
            </button>
          </div>
        </div>
      </section>

      {/* Auditable Consent Log */}
      <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h2 className="text-lg font-bold text-white mb-2">Consent History & Rights</h2>
        <p className="text-sm text-slate-400 mb-4">
          Auditable log of explicit processing permissions granted to RIGHT FIT.
        </p>

        <div className="space-y-3">
          {consents.length > 0 ? (
            consents.map((c) => (
              <div
                key={c.id}
                className="p-3 bg-slate-800/60 border border-slate-800 rounded-lg flex justify-between items-center"
              >
                <div>
                  <span className="font-semibold text-sm text-white">{c.purpose}</span>
                  <span className="ml-2 text-xs text-slate-400">
                    (v{c.policy_version}) - {new Date(c.created_at).toLocaleDateString()}
                  </span>
                  <div className="text-xs mt-1">
                    Status:{" "}
                    <span className={c.granted ? "text-emerald-400" : "text-amber-400"}>
                      {c.granted ? "ACTIVE GRANT" : "WITHDRAWN"}
                    </span>
                  </div>
                </div>
                {c.granted && (
                  <button
                    onClick={() => handleWithdrawConsent(c.id)}
                    className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-amber-300 rounded border border-slate-700"
                  >
                    Withdraw
                  </button>
                )}
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-400">No additional elective consents logged.</p>
          )}
        </div>
      </section>

      {/* Candidate Data Export */}
      <section className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg">
        <h2 className="text-lg font-bold text-white mb-2">Download Your Personal Data (GDPR / CCPA)</h2>
        <p className="text-sm text-slate-400 mb-4">
          Generate a structured, portable JSON export containing your complete profile, education,
          experience, preferences, and auditable consent log.
        </p>

        <div className="flex items-center space-x-4">
          <button
            onClick={handleRequestExport}
            disabled={exporting}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-indigo-300 font-medium text-sm rounded-lg border border-slate-700 transition-colors"
          >
            {exporting ? "Generating Export..." : "Generate Machine-Readable Export"}
          </button>

          {exportUrl && (
            <a
              href={exportUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-sm rounded-lg transition-colors"
            >
              Download Export JSON
            </a>
          )}
        </div>
      </section>

      {/* Account Deletion */}
      <section className="bg-red-950/20 border border-red-900/40 p-6 rounded-xl shadow-lg">
        <h2 className="text-lg font-bold text-red-200 mb-2">Delete Candidate Account</h2>
        <p className="text-sm text-slate-400 mb-4">
          Initiates permanent deletion of your profile, resume files, and coordinates data deletion
          with satellite search crawlers. A 30-day statutory grace period applies.
        </p>

        <button
          onClick={() => setShowDeleteModal(true)}
          className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-medium text-sm rounded-lg transition-colors"
        >
          Initiate Account Deletion
        </button>
      </section>

      {/* Account Deletion Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-red-800/60 max-w-md w-full p-6 rounded-xl shadow-2xl">
            <h3 className="text-lg font-bold text-red-400 mb-2">Confirm Account Deletion</h3>
            <p className="text-sm text-slate-300 mb-4">
              This action terminates all active sessions, marks your account as DELETION_PENDING, and
              schedules permanent erasure.
            </p>

            <form onSubmit={handleDeleteAccount} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Type <span className="text-red-400 font-mono">DELETE MY ACCOUNT</span> to confirm:
                </label>
                <input
                  type="text"
                  required
                  value={deleteConfirmation}
                  onChange={(e) => setDeleteConfirmation(e.target.value)}
                  placeholder="DELETE MY ACCOUNT"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Reason for leaving (Optional):
                </label>
                <textarea
                  value={deleteReason}
                  onChange={(e) => setDeleteReason(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={deleting || deleteConfirmation !== "DELETE MY ACCOUNT"}
                  className="px-4 py-2 rounded bg-red-600 hover:bg-red-500 disabled:opacity-40 text-white text-sm font-medium"
                >
                  {deleting ? "Scheduling Deletion..." : "Permanently Delete"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

