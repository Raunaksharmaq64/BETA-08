"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";

interface AuditRecommendation {
  category: string;
  title: string;
  description: string;
  severity: string;
}

interface AuditScorecard {
  overall_score: number;
  status: string;
  scores: {
    speed: number;
    seo: number;
    mobile: number;
    ssl: number;
    alt: number;
  };
  recommendations: AuditRecommendation[];
  details?: {
    has_viewport?: boolean;
    ssl_active?: boolean;
    broken_links?: number;
    word_count?: number;
    missing_alt_images?: number;
  };
}

export default function FreelanceDetailPage() {
  const { opportunityId } = useParams();
  const router = useRouter();

  const [opp, setOpp] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [drafting, setDrafting] = useState(false);

  // Technical Audit State
  const [auditing, setAuditing] = useState(false);
  const [auditData, setAuditData] = useState<AuditScorecard | null>(null);
  const [auditMessage, setAuditMessage] = useState<string | null>(null);

  // SVG Mockup State
  const [showMockup, setShowMockup] = useState(false);
  const [mockupSvg, setMockupSvg] = useState<string | null>(null);
  const [loadingMockup, setLoadingMockup] = useState(false);

  // WhatsApp Outreach State
  const [whatsAppCustomMsg, setWhatsAppCustomMsg] = useState("");
  const [generatingWhatsApp, setGeneratingWhatsApp] = useState(false);
  const [whatsAppSuccess, setWhatsAppSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!opportunityId) return;
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<any>(`/freelance/${opportunityId}`);
        setOpp(res.data);
      } catch (err: any) {
        setError(err?.message || "Failed to load freelance opportunity details.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [opportunityId]);

  const handleToggleSave = async () => {
    setSaving(true);
    setSaveMessage(null);
    try {
      if (isSaved) {
        await apiClient.delete(`/freelance/${opportunityId}/save`);
        setIsSaved(false);
        setSaveMessage("Removed from saved leads.");
      } else {
        await apiClient.post(`/freelance/${opportunityId}/save`, { notes: "Saved from detail workbench" });
        setIsSaved(true);
        setSaveMessage("✓ Bookmarked in saved leads.");
      }
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to update bookmark status.");
    } finally {
      setSaving(false);
    }
  };

  const handleRunAudit = async () => {
    setAuditing(true);
    setAuditMessage(null);
    try {
      const res: any = await apiClient.post(`/freelance/${opportunityId}/audit`, {});
      if (res?.audit) {
        setAuditData(res.audit);
        setAuditMessage(`Audit complete. Score: ${res.audit.overall_score}/100.`);
        if (res.emails_discovered && res.emails_discovered.length > 0) {
          setAuditMessage(
            `Audit complete! Score: ${res.audit.overall_score}/100. Discovered ${res.emails_discovered.length} new contact email(s)!`
          );
          // Refresh details to update contact evidence
          const refreshed = await apiClient.get<any>(`/freelance/${opportunityId}`);
          setOpp(refreshed.data);
        }
      } else {
        setAuditMessage(res?.message || "Audit completed.");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to perform technical website audit.");
    } finally {
      setAuditing(false);
    }
  };

  const handleLoadMockup = async () => {
    if (mockupSvg) {
      setShowMockup(!showMockup);
      return;
    }
    setLoadingMockup(true);
    try {
      const res: any = await apiClient.get<string>(`/freelance/${opportunityId}/mockup`);
      setMockupSvg(typeof res.data === "string" ? res.data : "");
      setShowMockup(true);
    } catch (err: any) {
      setError(err?.message || "Failed to load SVG mockup.");
    } finally {
      setLoadingMockup(false);
    }
  };

  const handleWhatsAppOutreach = async () => {
    setGeneratingWhatsApp(true);
    setWhatsAppSuccess(null);
    try {
      const res: any = await apiClient.post(`/freelance/${opportunityId}/whatsapp-link`, {
        message: whatsAppCustomMsg.trim() || undefined,
      });
      if (res?.whatsapp_link) {
        setWhatsAppSuccess("Redirecting to WhatsApp web chat...");
        window.open(res.whatsapp_link, "_blank", "noopener,noreferrer");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to generate WhatsApp chat link.");
    } finally {
      setGeneratingWhatsApp(false);
    }
  };

  const handleCreateDraft = async () => {
    setDrafting(true);
    try {
      const res = await apiClient.post<any>(`/freelance/${opportunityId}/draft?channel=EMAIL`, {});
      const draftId = res.data?.id;
      router.push(`/freelance/${opportunityId}/draft?draftId=${draftId}`);
    } catch (err: any) {
      setError(err?.message || "Failed to generate outreach draft.");
    } finally {
      setDrafting(false);
    }
  };

  const downloadSvgMockup = () => {
    if (!mockupSvg) return;
    const blob = new Blob([mockupSvg], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${(opp?.business_name || "client").toLowerCase().replace(/\s+/g, "_")}_concept_mockup.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
        <p className="text-slate-400">Loading opportunity details...</p>
      </div>
    );
  }

  if (error && !opp) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
        <div className="max-w-3xl mx-auto bg-rose-950/80 border border-rose-600 p-6 rounded-xl">
          <p className="text-rose-200">{error || "Opportunity not found"}</p>
          <Link href="/freelance" className="text-xs text-rose-300 underline mt-4 inline-block">
            ← Back to Freelance Opportunities
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Navigation Breadcrumb */}
        <div className="flex items-center justify-between">
          <Link href="/freelance" className="text-xs font-semibold text-indigo-400 hover:underline">
            ← Back to Opportunities Dashboard
          </Link>
          <span className="text-xs text-slate-500">
            ID: <span className="font-mono text-slate-400">{opp.id}</span>
          </span>
        </div>

        {/* Global Feedback Alert */}
        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-600 rounded-xl text-rose-200 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button onClick={() => setError(null)} className="text-xs text-rose-400 hover:text-white">✕</button>
          </div>
        )}
        {saveMessage && (
          <div className="p-4 bg-indigo-950/80 border border-indigo-600 rounded-xl text-indigo-200 text-sm">
            {saveMessage}
          </div>
        )}
        {auditMessage && (
          <div className="p-4 bg-emerald-950/80 border border-emerald-600 rounded-xl text-emerald-200 text-sm">
            {auditMessage}
          </div>
        )}

        {/* Header Profile Card */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-lg flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1 ${
                  opp.priority === "HIGH"
                    ? "bg-rose-950 text-rose-300 border border-rose-600 shadow-sm shadow-rose-950"
                    : opp.priority === "MEDIUM"
                    ? "bg-amber-950 text-amber-300 border border-amber-600"
                    : "bg-slate-800 text-slate-400 border border-slate-700"
                }`}
              >
                {opp.priority === "HIGH" ? "⚡ HIGH PRIORITY" : `${opp.priority || "MEDIUM"} PRIORITY`}
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                {opp.service_category}
              </span>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                  opp.is_broken_website
                    ? "bg-rose-950 text-rose-300 border border-rose-700"
                    : !opp.website
                    ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                    : "bg-slate-800 text-slate-300"
                }`}
              >
                {opp.is_broken_website
                  ? "Broken Website (Repair Required)"
                  : !opp.website
                  ? "No Website on Listing"
                  : "Active Website"}
              </span>
              {opp.rating > 0 && (
                <span className="text-xs px-2 py-0.5 bg-amber-950 text-amber-300 border border-amber-700/60 rounded-full font-medium">
                  ⭐ {opp.rating} ({opp.reviews_count} reviews)
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-white mt-1.5">{opp.business_name}</h1>
            <p className="text-sm text-slate-400 mt-0.5">
              {opp.city} • Discovered via Native Maps Scanner • Fit Score:{" "}
              <span className="text-indigo-400 font-semibold">{opp.relevance_score}%</span>
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={handleToggleSave}
              disabled={saving}
              className={`px-4 py-2 text-xs font-semibold rounded-lg border transition ${
                isSaved
                  ? "bg-amber-600/30 text-amber-300 border-amber-600 hover:bg-amber-600/40"
                  : "bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-700"
              }`}
            >
              {saving ? "Updating..." : isSaved ? "★ Bookmarked" : "☆ Bookmark Lead"}
            </button>
            <button
              onClick={handleCreateDraft}
              disabled={drafting}
              className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition shadow-md shadow-indigo-900/40"
            >
              {drafting ? "Generating Draft..." : "Prepare AI Outreach Pitch →"}
            </button>
          </div>
        </div>

        {/* Opportunity Scope & Synthesis */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h2 className="text-base font-bold text-white mb-2">{opp.opportunity_title}</h2>
          <p className="text-sm text-slate-300 leading-relaxed">{opp.description}</p>

          <div className="mt-4 pt-4 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Recommended Solution
              </p>
              <p className="text-sm text-indigo-300 font-medium mt-1">
                {opp.suggested_service || "Modern Responsive Web Rebuild & SEO"}
              </p>
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Target Technical Skills
              </p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {opp.required_skills?.map((sk: string, i: number) => (
                  <span
                    key={i}
                    className="text-xs px-2.5 py-0.5 bg-slate-800 text-slate-200 rounded border border-slate-700"
                  >
                    {sk}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Website Technical Health & Diagnostics Section */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>🔬</span> Website Health & Technical Audit
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Evaluates site performance, mobile viewport, SSL certificate validity, and search engine readiness.
              </p>
            </div>
            <button
              onClick={handleRunAudit}
              disabled={auditing || !opp.website}
              className="px-4 py-2 bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition"
            >
              {auditing ? "Auditing Website..." : "Audit Website Now ⚡"}
            </button>
          </div>

          {!opp.website ? (
            <div className="p-4 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-amber-300">
              ⚠️ No website URL listed for this business on Google Maps. This makes them a prime candidate for a brand-new digital presence pitch!
            </div>
          ) : auditData ? (
            <div className="space-y-4 pt-2">
              {/* Scorecard Overview */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">Overall</p>
                  <p className={`text-2xl font-black mt-1 ${
                    auditData.overall_score >= 70 ? "text-emerald-400" : auditData.overall_score >= 50 ? "text-amber-400" : "text-rose-400"
                  }`}>
                    {auditData.overall_score}/100
                  </p>
                  <p className="text-[10px] text-slate-500 mt-0.5">{auditData.status}</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">Speed</p>
                  <p className="text-xl font-bold text-slate-200 mt-1">{auditData.scores.speed}/25</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Response Time</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">SEO</p>
                  <p className="text-xl font-bold text-slate-200 mt-1">{auditData.scores.seo}/25</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Meta & Structure</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">Mobile</p>
                  <p className="text-xl font-bold text-slate-200 mt-1">{auditData.scores.mobile}/20</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Viewport Config</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-center">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase">SSL / Sec</p>
                  <p className="text-xl font-bold text-slate-200 mt-1">{auditData.scores.ssl}/20</p>
                  <p className="text-[10px] text-slate-500 mt-0.5">HTTPS Protection</p>
                </div>
              </div>

              {/* Actionable Recommendations */}
              {auditData.recommendations && auditData.recommendations.length > 0 && (
                <div className="space-y-2 pt-2">
                  <p className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Pitchable Technical Flaws & Opportunities ({auditData.recommendations.length}):
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {auditData.recommendations.map((rec, idx) => (
                      <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-semibold text-white">{rec.title}</span>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            rec.severity === "HIGH"
                              ? "bg-rose-950 text-rose-300 border border-rose-700"
                              : rec.severity === "MEDIUM"
                              ? "bg-amber-950 text-amber-300 border border-amber-700"
                              : "bg-slate-800 text-slate-300"
                          }`}>
                            {rec.severity}
                          </span>
                        </div>
                        <p className="text-slate-400 leading-relaxed">{rec.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800/80 text-xs text-slate-400 flex items-center justify-between">
              <span>Website: <a href={opp.website} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:underline">{opp.website}</a></span>
              <span>Click "Audit Website Now" to run a live 100-point diagnostic scan.</span>
            </div>
          )}
        </div>

        {/* Dynamic Concept Mockup Preview */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <span>🎨</span> Interactive Landing Page Mockup Generator
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Generates a clean, modern concept design showcase tailored to this business category for your proposal.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleLoadMockup}
                disabled={loadingMockup}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              >
                {loadingMockup ? "Generating..." : showMockup ? "Hide Mockup" : "Preview Mockup Concept"}
              </button>
              {mockupSvg && showMockup && (
                <button
                  onClick={downloadSvgMockup}
                  className="px-3 py-2 bg-indigo-600/80 hover:bg-indigo-600 text-white text-xs font-semibold rounded-lg transition"
                >
                  Download SVG 📥
                </button>
              )}
            </div>
          </div>

          {showMockup && mockupSvg && (
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-hidden shadow-inner">
              <div
                className="w-full max-w-3xl mx-auto rounded-lg overflow-hidden border border-slate-700/80"
                dangerouslySetInnerHTML={{ __html: mockupSvg }}
              />
            </div>
          )}
        </div>

        {/* Multi-Channel Outreach Bar (WhatsApp & Direct) */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>💬</span> Direct WhatsApp Pitch Messenger
          </h2>
          <p className="text-xs text-slate-400">
            Open a pre-formatted, compliant click-to-chat WhatsApp session with verified mobile contacts.
          </p>

          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              placeholder={`Hi ${opp.business_name} team, noticed your Google listing and wanted to share a quick digital growth proposal.`}
              value={whatsAppCustomMsg}
              onChange={(e) => setWhatsAppCustomMsg(e.target.value)}
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3.5 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleWhatsAppOutreach}
              disabled={generatingWhatsApp || !opp.phone}
              className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white text-xs font-semibold rounded-lg transition flex items-center justify-center space-x-1.5"
            >
              <span>{generatingWhatsApp ? "Generating Link..." : "Open WhatsApp Chat 📲"}</span>
            </button>
          </div>
          {whatsAppSuccess && (
            <p className="text-xs text-emerald-400">{whatsAppSuccess}</p>
          )}
          {!opp.phone && (
            <p className="text-xs text-slate-500">No phone number available on listing for WhatsApp dispatch.</p>
          )}
        </div>

        {/* Contact Evidence Panel */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h2 className="text-base font-bold text-white mb-1">Contact Verification & Evidence Ledger</h2>
          <p className="text-xs text-slate-400 mb-4">
            Discovered through deep website scraping, contact page parsing, and public Google Maps records.
          </p>

          <div className="space-y-3">
            {opp.contact_evidence && opp.contact_evidence.length > 0 ? (
              opp.contact_evidence.map((ev: any) => (
                <div
                  key={ev.id}
                  className="bg-slate-950 p-4 rounded-lg border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-mono">
                        {ev.contact_type}
                      </span>
                      <span className="text-sm font-semibold text-white font-mono">{ev.contact_value}</span>
                    </div>
                    {ev.verification_notes && (
                      <p className="text-xs text-slate-400 mt-1">{ev.verification_notes}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-3">
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold ${
                        ev.evidence_status === "VERIFIED"
                          ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                          : ev.evidence_status === "INVALID"
                          ? "bg-rose-950 text-rose-300 border border-rose-700"
                          : "bg-indigo-950 text-indigo-300 border border-indigo-700"
                      }`}
                    >
                      {ev.evidence_status}
                    </span>
                    <span className="text-[11px] text-slate-500">
                      Discovered: {new Date(ev.discovered_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-3">No direct contact records discovered yet. Run website audit above to crawl contact pages.</div>
            )}
          </div>
        </div>

        {/* Provenance & Audit Panel */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
          <h2 className="text-base font-bold text-white mb-3">Source Provenance & Metadata</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-300">
            <div>
              <p className="text-slate-500 font-semibold uppercase">Discovery Source</p>
              <p className="mt-0.5 font-mono text-slate-300">{opp.source}</p>
            </div>
            <div>
              <p className="text-slate-500 font-semibold uppercase">Maps Place Reference</p>
              <p className="mt-0.5 font-mono text-slate-300">{opp.leadhunter_lead_id || opp.place_id || "N/A"}</p>
            </div>
            <div>
              <p className="text-slate-500 font-semibold uppercase">First Discovered Instant</p>
              <p className="mt-0.5">{new Date(opp.discovered_at).toUTCString()}</p>
            </div>
            <div>
              <p className="text-slate-500 font-semibold uppercase">Original Listing Link</p>
              {opp.original_source_url ? (
                <a
                  href={opp.original_source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-0.5 text-indigo-400 hover:underline block truncate"
                >
                  View on Google Maps ↗
                </a>
              ) : (
                <p className="mt-0.5 text-slate-500">None</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
