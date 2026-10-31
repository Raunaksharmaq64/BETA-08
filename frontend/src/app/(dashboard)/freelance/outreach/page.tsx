"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface CandidateSettings {
  maps_provider: string;
  has_serpapi_key: boolean;
  has_apify_token: boolean;
  has_gemini_key: boolean;
  sender_name?: string;
  sender_brand?: string;
  smtp_email?: string;
  smtp_host?: string;
  smtp_port?: number;
  smtp_use_ssl?: boolean;
}

export default function OutreachActivityPage() {
  const [drafts, setDrafts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Suppression form
  const [suppressInput, setSuppressInput] = useState("");
  const [suppressReason, setSuppressReason] = useState("MANUAL_SUPPRESSION");
  const [suppressSuccess, setSuppressSuccess] = useState<string | null>(null);

  // Candidate Settings state
  const [settings, setSettings] = useState<CandidateSettings | null>(null);
  const [mapsProvider, setMapsProvider] = useState("serpapi");
  const [serpapiKey, setSerpapiKey] = useState("");
  const [apifyToken, setApifyToken] = useState("");
  const [geminiKey, setGeminiKey] = useState("");
  const [senderName, setSenderName] = useState("");
  const [senderBrand, setSenderBrand] = useState("");
  const [smtpEmail, setSmtpEmail] = useState("");
  const [smtpPassword, setSmtpPassword] = useState("");
  const [smtpHost, setSmtpHost] = useState("");
  const [smtpPort, setSmtpPort] = useState(587);
  const [smtpUseSsl, setSmtpUseSsl] = useState(true);
  const [savingSettings, setSavingSettings] = useState(false);
  const [settingsSuccess, setSettingsSuccess] = useState<string | null>(null);

  const fetchActivityAndSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      // 1. Fetch opportunities to aggregate drafts
      const oppsRes = await apiClient.get<any>("/freelance?per_page=50");
      const allDrafts: any[] = [];
      oppsRes.data?.forEach((opp: any) => {
        opp.drafts?.forEach((d: any) => {
          allDrafts.push({ ...d, business_name: opp.business_name });
        });
      });
      setDrafts(allDrafts);

      // 2. Fetch candidate settings
      const settingsRes = await apiClient.get<any>("/freelance/settings");
      if (settingsRes.data) {
        const s = settingsRes.data;
        setSettings(s);
        setMapsProvider(s.maps_provider || "serpapi");
        setSenderName(s.sender_name || "");
        setSenderBrand(s.sender_brand || "");
        setSmtpEmail(s.smtp_email || "");
        setSmtpHost(s.smtp_host || "");
        setSmtpPort(s.smtp_port || 587);
        setSmtpUseSsl(s.smtp_use_ssl ?? true);
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load outreach activity or settings.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivityAndSettings();
  }, []);

  const handleAddSuppression = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!suppressInput) return;
    setSuppressSuccess(null);
    setError(null);
    try {
      await apiClient.post("/freelance/suppression", {
        recipient_contact: suppressInput,
        reason: suppressReason,
      });
      setSuppressSuccess(`Recipient ${suppressInput} successfully added to suppression list.`);
      setSuppressInput("");
    } catch (err: any) {
      setError(err?.message || "Failed to suppress contact.");
    }
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingSettings(true);
    setSettingsSuccess(null);
    setError(null);
    try {
      const payload: any = {
        maps_provider: mapsProvider,
        sender_name: senderName || undefined,
        sender_brand: senderBrand || undefined,
        smtp_email: smtpEmail || undefined,
        smtp_host: smtpHost || undefined,
        smtp_port: smtpPort,
        smtp_use_ssl: smtpUseSsl,
      };
      if (serpapiKey.trim()) payload.serpapi_key = serpapiKey.trim();
      if (apifyToken.trim()) payload.apify_token = apifyToken.trim();
      if (geminiKey.trim()) payload.gemini_key = geminiKey.trim();
      if (smtpPassword.trim()) payload.smtp_password = smtpPassword.trim();

      const res = await apiClient.post<any>("/freelance/settings", payload);
      setSettings(res.data);
      setSettingsSuccess("✓ Candidate freelance settings and BYOK credentials saved securely.");
      setSerpapiKey("");
      setApifyToken("");
      setGeminiKey("");
      setSmtpPassword("");
    } catch (err: any) {
      setError(err?.message || "Failed to save candidate settings.");
    } finally {
      setSavingSettings(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        <div>
          <Link href="/freelance" className="text-xs font-semibold text-indigo-400 hover:underline">
            ← Back to Opportunities Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-white mt-2">Outreach Activity & Delivery Gateway</h1>
          <p className="text-xs text-slate-400 mt-1">
            Audit ledger of drafted, approved, and dispatched outreach messages, suppression list, and candidate settings.
          </p>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-600 rounded-xl text-rose-200 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
          </div>
        )}
        {suppressSuccess && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm flex items-center justify-between">
            <span>{suppressSuccess}</span>
            <button onClick={() => setSuppressSuccess(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
          </div>
        )}
        {settingsSuccess && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm flex items-center justify-between">
            <span>{settingsSuccess}</span>
            <button onClick={() => setSettingsSuccess(null)} className="text-xs text-emerald-400 hover:text-white">✕</button>
          </div>
        )}

        {/* Candidate BYOK & Settings Panel */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4 shadow-sm">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <span>⚙️</span> Candidate BYOK API Keys & Custom SMTP Gateway
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Optionally provide your personal API keys for dedicated high-quota scraping, AI writing, and custom SMTP email sending.
            </p>
          </div>

          <form onSubmit={handleSaveSettings} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Primary Maps Discovery Provider
                </label>
                <select
                  value={mapsProvider}
                  onChange={(e) => setMapsProvider(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="serpapi">SerpApi (Google Maps Engine)</option>
                  <option value="apify">Apify (Google Places Crawler)</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  SerpApi Key {settings?.has_serpapi_key && <span className="text-emerald-400 font-bold">(Configured ✓)</span>}
                </label>
                <input
                  type="password"
                  value={serpapiKey}
                  onChange={(e) => setSerpapiKey(e.target.value)}
                  placeholder={settings?.has_serpapi_key ? "••••••••••••" : "Paste SerpApi key"}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Apify Token {settings?.has_apify_token && <span className="text-emerald-400 font-bold">(Configured ✓)</span>}
                </label>
                <input
                  type="password"
                  value={apifyToken}
                  onChange={(e) => setApifyToken(e.target.value)}
                  placeholder={settings?.has_apify_token ? "••••••••••••" : "Paste Apify token"}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">
                  Google Gemini AI Key {settings?.has_gemini_key && <span className="text-emerald-400 font-bold">(Configured ✓)</span>}
                </label>
                <input
                  type="password"
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                  placeholder={settings?.has_gemini_key ? "••••••••••••" : "Paste Gemini API key"}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Sender Name</label>
                <input
                  type="text"
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  placeholder="e.g. Alex Morgan"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="block text-[11px] text-slate-400 mb-1">Agency / Studio Brand</label>
                <input
                  type="text"
                  value={senderBrand}
                  onChange={(e) => setSenderBrand(e.target.value)}
                  placeholder="e.g. Apex Digital Studios"
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* SMTP Settings */}
            <div className="pt-2 border-t border-slate-800">
              <p className="text-[11px] font-semibold uppercase text-slate-400 mb-2">
                Custom SMTP Delivery Server (Optional — defaults to server-configured pool)
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block text-[10px] text-slate-400 mb-0.5">SMTP Host</label>
                  <input
                    type="text"
                    value={smtpHost}
                    onChange={(e) => setSmtpHost(e.target.value)}
                    placeholder="smtp.gmail.com"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-0.5">SMTP Port</label>
                  <input
                    type="number"
                    value={smtpPort}
                    onChange={(e) => setSmtpPort(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-0.5">SMTP Email</label>
                  <input
                    type="email"
                    value={smtpEmail}
                    onChange={(e) => setSmtpEmail(e.target.value)}
                    placeholder="your-email@domain.com"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-[10px] text-slate-400 mb-0.5">App Password / Auth</label>
                  <input
                    type="password"
                    value={smtpPassword}
                    onChange={(e) => setSmtpPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                type="submit"
                disabled={savingSettings}
                className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition"
              >
                {savingSettings ? "Saving Settings..." : "Save Configuration"}
              </button>
            </div>
          </form>
        </div>

        {/* Suppression Management Card */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-1">
            Recipient Do-Not-Contact Suppression
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Proactively blocks all outreach attempts to unsubscribed or opted-out contacts.
          </p>
          <form onSubmit={handleAddSuppression} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder="e.g. optout@company.com or +15551234567"
              value={suppressInput}
              onChange={(e) => setSuppressInput(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500 font-mono"
              required
            />
            <select
              value={suppressReason}
              onChange={(e) => setSuppressReason(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-100 focus:outline-none"
            >
              <option value="MANUAL_SUPPRESSION">Manual Suppression</option>
              <option value="UNSUBSCRIBED">Unsubscribed</option>
              <option value="BOUNCED">Previous Bounce</option>
            </select>
            <button
              type="submit"
              className="px-4 py-2 bg-rose-700 hover:bg-rose-600 text-white text-xs font-semibold rounded-lg transition"
            >
              Add to Suppression List
            </button>
          </form>
        </div>

        {/* Outreach List */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Recent Outreach Records ({drafts.length})
          </h2>
          {loading ? (
            <div className="py-8 text-center text-slate-400 text-xs">Loading activity...</div>
          ) : drafts.length === 0 ? (
            <div className="py-8 text-center text-slate-500 text-xs">
              No outreach messages prepared yet. Visit an opportunity to compose a draft!
            </div>
          ) : (
            <div className="space-y-3">
              {drafts.map((d) => (
                <div
                  key={d.id}
                  className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-white">{d.business_name}</span>
                      <span className="text-xs text-slate-400 font-mono">({d.recipient_contact})</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 font-medium">{d.subject}</p>
                    <p className="text-[11px] text-slate-500 mt-1">
                      Updated: {new Date(d.updated_at).toLocaleString()} • Edits: {d.candidate_edits_count}
                    </p>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold uppercase ${
                        d.status === "SENT" || d.status === "DELIVERY_CONFIRMED"
                          ? "bg-indigo-950 text-indigo-300 border border-indigo-700"
                          : d.status === "APPROVED"
                          ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                          : "bg-amber-950 text-amber-300 border border-amber-700"
                      }`}
                    >
                      {d.status}
                    </span>
                    <Link
                      href={`/freelance/${d.opportunity_id}/draft?draftId=${d.id}`}
                      className="text-xs text-indigo-400 hover:underline"
                    >
                      Open Editor →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
