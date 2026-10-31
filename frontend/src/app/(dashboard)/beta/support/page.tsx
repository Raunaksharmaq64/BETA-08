"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface SupportInfo {
  support_email: string;
  security_contact: string;
  sla_commitments: Record<string, string>;
  escalation_levels: Array<{
    tier: string;
    target: string;
    responders: string;
  }>;
  privacy_requests: {
    data_deletion_endpoint: string;
    retention_period_days: number;
    opt_out_process: string;
  };
}

export default function BetaSupportPage() {
  const [supportInfo, setSupportInfo] = useState<SupportInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [withdrawingConsent, setWithdrawingConsent] = useState(false);
  const [consentMsg, setConsentMsg] = useState<string | null>(null);

  useEffect(() => {
    async function loadSupport() {
      try {
        setLoading(true);
        const res = await apiClient<SupportInfo>("/beta/support");
        if (res && res.data) {
          setSupportInfo(res.data);
        }
      } catch (err: any) {
        console.error("Failed to load beta support playbook", err);
      } finally {
        setLoading(false);
      }
    }
    loadSupport();
  }, []);

  const handleWithdrawConsent = async () => {
    if (!confirm("Are you sure you want to withdraw beta testing consent? Your non-essential diagnostic records will be scheduled for immediate privacy purge.")) {
      return;
    }

    try {
      setWithdrawingConsent(true);
      setConsentMsg(null);
      await apiClient("/beta/consent/withdraw", {
        method: "POST",
        body: JSON.stringify({
          consent_type: "BETA_TERMS_AND_DATA_PROCESSING",
          reason: "Candidate exercised self-serve withdrawal option in Beta Support screen.",
        }),
      });
      setConsentMsg("Consent successfully withdrawn. Your records have been purged in compliance with our 90-day data minimization policy.");
    } catch (err: any) {
      setConsentMsg("Failed to withdraw consent. Please contact beta-support@rightfit.ai directly.");
    } finally {
      setWithdrawingConsent(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 mb-2">
            Operations & User Trust
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Support & Incident Escalation Playbook
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Standard operating procedures, response SLAs, on-call contacts, and candidate privacy controls.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Link
            href="/beta/feedback"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            Submit Feedback
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="p-8 text-center text-slate-500">Loading support commitments...</div>
      ) : !supportInfo ? (
        <div className="p-8 text-center text-slate-500">Support information unavailable.</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main SLA and Escalation Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* SLA Table */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Beta Response SLA Commitments
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {Object.entries(supportInfo.sla_commitments).map(([sev, sla]) => (
                  <div
                    key={sev}
                    className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-100 dark:border-slate-800 text-center"
                  >
                    <div className="text-xs font-bold uppercase tracking-wider text-slate-500">
                      {sev}
                    </div>
                    <div className="mt-2 text-xl font-bold text-slate-900 dark:text-white">
                      {sla}
                    </div>
                    <div className="mt-1 text-[11px] text-slate-400">Target response</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Escalation Hierarchy */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Escalation Hierarchy & Responders
              </h2>
              <div className="space-y-3">
                {supportInfo.escalation_levels.map((lvl, i) => (
                  <div
                    key={i}
                    className="p-4 bg-slate-50 dark:bg-slate-800/30 rounded-lg border border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 text-sm"
                  >
                    <div>
                      <div className="font-semibold text-slate-900 dark:text-white">
                        {lvl.tier}
                      </div>
                      <div className="text-xs text-slate-500">{lvl.responders}</div>
                    </div>
                    <span className="text-xs font-mono font-medium px-2.5 py-1 rounded bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 shrink-0">
                      Target: {lvl.target}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Privacy & Self-Serve Withdrawal Column */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Support Channels
              </h2>
              <div className="space-y-3 text-sm">
                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase">Beta Support Email</div>
                  <a
                    href={`mailto:${supportInfo.support_email}`}
                    className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline text-sm"
                  >
                    {supportInfo.support_email}
                  </a>
                </div>
                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase">Security & Privacy Inquiries</div>
                  <a
                    href={`mailto:${supportInfo.security_contact}`}
                    className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline text-sm"
                  >
                    {supportInfo.security_contact}
                  </a>
                </div>
              </div>
            </div>

            {/* Candidate Privacy & Right to be Forgotten */}
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                  Privacy & Data Retention
                </h2>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Beta telemetry and diagnostic records are strictly minimized and automatically purged after {supportInfo.privacy_requests.retention_period_days} days.
              </p>

              {consentMsg && (
                <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-800 dark:text-emerald-300">
                  {consentMsg}
                </div>
              )}

              <button
                onClick={handleWithdrawConsent}
                disabled={withdrawingConsent}
                className="w-full py-2 px-3 text-xs font-medium rounded-lg border border-rose-300 dark:border-rose-800 text-rose-700 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
              >
                {withdrawingConsent ? "Processing Withdrawal..." : "Withdraw Beta Consent / Purge Telemetry"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

