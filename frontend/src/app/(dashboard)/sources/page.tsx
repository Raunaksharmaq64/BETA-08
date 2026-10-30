"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface JobSource {
  id: string;
  source_key: string;
  display_name: string;
  source_type: string;
  provider: string;
  base_url: string;
  enabled: boolean;
  policy_status: string;
  rate_limit_per_minute: number;
  circuit_breaker_state: string;
  consecutive_failures: number;
  last_success_at: string | null;
  last_failure_at: string | null;
}

export default function SourcesPage() {
  const [sources, setSources] = useState<JobSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // New source form state
  const [formKey, setFormKey] = useState("");
  const [formName, setFormName] = useState("");
  const [formProvider, setFormProvider] = useState("synthetic");
  const [formUrl, setFormUrl] = useState("synthetic://default");
  const [formRateLimit, setFormRateLimit] = useState(60);

  const fetchSources = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient<JobSource[]>("/sources");
      setSources(res.data);
    } catch (err: any) {
      setError(err?.message || "Failed to load job sources.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleCreateSource = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setActionMessage(null);
      await apiClient("/sources", {
        method: "POST",
        body: JSON.stringify({
          source_key: formKey,
          display_name: formName,
          provider: formProvider,
          base_url: formUrl,
          rate_limit_per_minute: Number(formRateLimit),
        }),
      });
      setShowRegisterModal(false);
      setFormKey("");
      setFormName("");
      setActionMessage("Source registered successfully (Status: DRAFT).");
      await fetchSources();
    } catch (err: any) {
      setError(err?.message || "Registration failed.");
    }
  };

  const getPolicyBadge = (status: string) => {
    switch (status) {
      case "ACTIVE":
        return "bg-emerald-950 text-emerald-400 border border-emerald-800";
      case "APPROVED":
        return "bg-blue-950 text-blue-400 border border-blue-800";
      case "PENDING_REVIEW":
        return "bg-yellow-950 text-yellow-400 border border-yellow-800";
      case "BLOCKED":
        return "bg-rose-950 text-rose-400 border border-rose-800";
      case "PAUSED":
        return "bg-amber-950 text-amber-400 border border-amber-800";
      default:
        return "bg-slate-800 text-slate-400 border border-slate-700";
    }
  };

  const getCircuitBadge = (state: string) => {
    switch (state) {
      case "CLOSED":
        return "bg-emerald-950 text-emerald-400 border border-emerald-800";
      case "OPEN":
        return "bg-rose-950 text-rose-400 border border-rose-800";
      case "HALF_OPEN":
        return "bg-yellow-950 text-yellow-400 border border-yellow-800";
      default:
        return "bg-slate-800 text-slate-400 border border-slate-700";
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-8 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Job Source Framework</h1>
          <p className="mt-2 text-sm text-slate-400 max-w-3xl">
            Register and govern external job boards, ATS feeds, and direct APIs. Complete with 3-state circuit breaking,
            sliding-window rate limiting, and governance policy lifecycle gating.
          </p>
        </div>
        <button
          onClick={() => setShowRegisterModal(true)}
          className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 focus:outline-none transition-colors"
        >
          + Register Source
        </button>
      </div>

      {actionMessage && (
        <div className="mt-6 p-4 rounded-lg bg-emerald-950 border border-emerald-800 text-emerald-300 text-sm">
          {actionMessage}
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 rounded-lg bg-rose-950 border border-rose-800 text-rose-300 text-sm">
          {error}
        </div>
      )}

      {/* Sources Table */}
      <div className="mt-8 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-6 border-b border-slate-800 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-slate-200">Registered Ingestion Sources</h2>
          <span className="text-xs text-slate-400">{sources.length} Total Sources</span>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-400">Loading sources registry...</div>
        ) : sources.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            No sources registered yet. Click &quot;+ Register Source&quot; above to create your first feed.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Source / Slug</th>
                  <th className="px-6 py-4">Provider</th>
                  <th className="px-6 py-4">Policy Gate</th>
                  <th className="px-6 py-4">Circuit Breaker</th>
                  <th className="px-6 py-4">Rate Quota</th>
                  <th className="px-6 py-4">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {sources.map((src) => (
                  <tr key={src.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{src.display_name}</div>
                      <div className="text-xs font-mono text-slate-400">{src.source_key}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                        {src.provider}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${getPolicyBadge(src.policy_status)}`}>
                        {src.policy_status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${getCircuitBadge(src.circuit_breaker_state)}`}>
                        {src.circuit_breaker_state}
                      </span>
                      {src.consecutive_failures > 0 && (
                        <div className="text-xs text-rose-400 mt-1">{src.consecutive_failures} failures</div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-xs text-slate-300">{src.rate_limit_per_minute} req/min</span>
                    </td>
                    <td className="px-6 py-4 space-x-2">
                      <Link
                        href={`/sources/${src.id}`}
                        className="text-xs font-medium text-indigo-400 hover:text-indigo-300 underline"
                      >
                        Manage & Logs &rarr;
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Registration Modal */}
      {showRegisterModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Register New Opportunity Source</h3>
            <form onSubmit={handleCreateSource} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Source Slug (unique)</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. greenhouse-stripe"
                  value={formKey}
                  onChange={(e) => setFormKey(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Display Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Stripe Public Board"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Provider Adapter</label>
                <select
                  value={formProvider}
                  onChange={(e) => {
                    const prov = e.target.value;
                    setFormProvider(prov);
                    if (prov === "greenhouse") setFormUrl("https://boards-api.greenhouse.io/v1/boards/stripe/jobs");
                    else if (prov === "ashby") setFormUrl("https://api.ashbyhq.com/posting-api/job-board/notion");
                    else setFormUrl("synthetic://default");
                  }}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="synthetic">Synthetic (Deterministic Test Feed)</option>
                  <option value="greenhouse">Greenhouse (Public Board API)</option>
                  <option value="ashby">Ashby (Public Posting API)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Base Endpoint URL</label>
                <input
                  type="text"
                  required
                  value={formUrl}
                  onChange={(e) => setFormUrl(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Rate Limit (requests per minute)</label>
                <input
                  type="number"
                  required
                  min="1"
                  max="1200"
                  value={formRateLimit}
                  onChange={(e) => setFormRateLimit(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowRegisterModal(false)}
                  className="px-4 py-2 text-sm text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  Register Source
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
