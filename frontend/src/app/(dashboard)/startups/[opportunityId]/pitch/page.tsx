"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { apiClient } from "@/services/apiClient";

export default function StartupPitchDraftEditorPage() {
  const params = useParams();
  const router = useRouter();
  const oppId = params.opportunityId as string;

  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Opportunity summary
  const [opportunityName, setOpportunityName] = useState<string>("Startup");
  const [category, setCategory] = useState<string>("Development");
  const [problemStatement, setProblemStatement] = useState<string>("");

  // Draft state
  const [draftId, setDraftId] = useState<string | null>(null);
  const [tone, setTone] = useState<string>("casual");
  const [subject, setSubject] = useState<string>("");
  const [body, setBody] = useState<string>("");
  const [groundedSkills, setGroundedSkills] = useState<string[]>([]);
  const [assumptions, setAssumptions] = useState<string[]>([]);
  const [editsCount, setEditsCount] = useState<number>(0);

  useEffect(() => {
    if (!oppId) return;

    const loadOppAndInitialDraft = async () => {
      setLoading(true);
      setError(null);
      try {
        // 1. Fetch opportunity detail
        const oppRes = await apiClient.get<any>(`/startups/${oppId}`);
        const opp = oppRes.data?.opportunity;
        if (opp) {
          setOpportunityName(opp.startup_name);
          setCategory(opp.category);
          setProblemStatement(opp.detected_signal);
        }

        // 2. Generate initial draft
        const draftRes: any = await apiClient.post(`/startups/${oppId}/pitch`, { tone: "casual" });
        const draft = draftRes.data;
        if (draft) {
          setDraftId(draft.id);
          setSubject(draft.subject);
          setBody(draft.body);
          setTone(draft.tone);
          setEditsCount(draft.candidate_edits_count || 0);

          try {
            setGroundedSkills(JSON.parse(draft.candidate_grounded_skills || "[]"));
          } catch {
            setGroundedSkills([]);
          }

          try {
            setAssumptions(JSON.parse(draft.explicit_assumptions || "[]"));
          } catch {
            setAssumptions([]);
          }
        }
      } catch (err: any) {
        setError(err?.message || "Failed to load pitch draft editor.");
      } finally {
        setLoading(false);
      }
    };

    loadOppAndInitialDraft();
  }, [oppId]);

  const handleRegenerateTone = async (newTone: string) => {
    setTone(newTone);
    setGenerating(true);
    try {
      const res: any = await apiClient.post(`/startups/${oppId}/pitch`, { tone: newTone });
      const draft = res.data;
      if (draft) {
        setDraftId(draft.id);
        setSubject(draft.subject);
        setBody(draft.body);
        setEditsCount(0);
      }
    } catch (err: any) {
      alert("Failed to regenerate pitch: " + (err?.message || "Error"));
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!draftId) return;
    setSaving(true);
    try {
      await apiClient.put(`/startups/pitches/${draftId}`, {
        subject,
        body,
        tone,
      });
      setEditsCount((prev) => prev + 1);
      alert("Pitch draft saved successfully!");
    } catch (err: any) {
      alert("Failed to save draft: " + (err?.message || "Error"));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-slate-500">
        <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
        Grounding candidate skills and preparing pitch draft...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Breadcrumb */}
      <div className="flex items-center justify-between">
        <Link href={`/startups/${oppId}`} className="text-sm font-semibold text-indigo-600 hover:underline">
          &larr; Back to Opportunity Detail
        </Link>
        <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-600 font-medium">
          Edits: {editsCount}
        </span>
      </div>

      {/* Mandatory Anti-Hallucination Warning */}
      <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-xs space-y-1">
        <div className="font-bold flex items-center gap-1.5 text-amber-800">
          <span>⚠️</span> Governance Guardrail: Draft Only Policy
        </div>
        <p>
          This pitch is grounded in publicly observed technical bottlenecks. Never fabricate client references, budget guarantees, or unauthorized endorsements.
        </p>
        <p className="font-semibold text-rose-700">
          Phase 10 does not authorize automatic message sending. Pitches remain local drafts for human review.
        </p>
      </div>

      {/* Context Card */}
      <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-2">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-50 text-indigo-700">
            {category}
          </span>
          <h2 className="font-bold text-slate-900 text-base">{opportunityName}</h2>
        </div>
        <p className="text-xs text-slate-600">
          <strong>Observed Bottleneck:</strong> {problemStatement}
        </p>
      </div>

      {/* Grounded Candidate Skills */}
      <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2">
        <div className="text-xs font-bold text-slate-600 uppercase tracking-wider">
          Grounded in Your Confirmed Skills
        </div>
        <div className="flex flex-wrap gap-2">
          {groundedSkills.length > 0 ? (
            groundedSkills.map((s, idx) => (
              <span key={idx} className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-100 text-indigo-800">
                ✓ {s}
              </span>
            ))
          ) : (
            <span className="text-xs text-slate-400">General engineering skills applied</span>
          )}
        </div>
      </div>

      {/* Explicit Assumptions Checklist */}
      <div className="p-5 bg-white rounded-xl border border-slate-200 shadow-sm space-y-3">
        <div className="text-xs font-bold text-slate-900 uppercase tracking-wider">
          Mandatory Explicit Assumptions Checklist
        </div>
        <p className="text-xs text-slate-500">
          Review these unconfirmed premises before customizing or presenting this proposal to a client:
        </p>
        <div className="space-y-2">
          {assumptions.map((asm, idx) => (
            <div key={idx} className="flex items-start gap-2 p-2 bg-slate-50 rounded-lg text-xs text-slate-700 border border-slate-100">
              <span className="text-indigo-600 font-bold">ℹ</span>
              <span>{asm}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Pitch Editor Workspace */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">
            Draft Outreach Message
          </h3>
          <div className="flex flex-wrap items-center gap-1.5 text-xs">
            <span className="text-slate-500 mr-1">Tone:</span>
            {["casual", "formal", "short"].map((t) => (
              <button
                key={t}
                onClick={() => handleRegenerateTone(t)}
                disabled={generating}
                className={`px-3 py-1 rounded-lg font-medium capitalize transition-colors ${tone === t
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                  }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Subject Line</label>
          <input
            type="text"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Message Body (Personalize your offer)
          </label>
          <textarea
            rows={10}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            className="w-full px-3 py-2 text-sm font-mono border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 leading-relaxed"
          />
          <div className="flex justify-between items-center text-xs text-slate-400 mt-1">
            <span>{body.length} characters</span>
            <span>Grounded in public observations only</span>
          </div>
        </div>

        {/* Buttons */}
        <div className="pt-4 border-t border-slate-100 flex flex-col-reverse sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <button
            onClick={() => router.push(`/startups/${oppId}`)}
            className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 text-center"
          >
            Discard Changes
          </button>
          <button
            onClick={handleSaveDraft}
            disabled={saving}
            className="px-5 py-2 text-xs font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 shadow-sm text-center"
          >
            {saving ? "Saving Draft..." : "Save Pitch Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}

