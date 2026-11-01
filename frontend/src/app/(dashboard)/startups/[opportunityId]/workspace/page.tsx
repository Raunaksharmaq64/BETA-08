"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { apiClient } from "@/services/apiClient";

interface ChecklistItem {
  id: string;
  label: string;
  completed: boolean;
}

interface WorkspaceData {
  id: string;
  opportunity_id: string;
  user_id: string;
  startup_name: string;
  detected_signal: string;
  pain_point_description?: string;
  urgency_score: number;
  validation_state: string;
  target_persona?: string;
  hypotheses: string[];
  competitor_notes?: string;
  interview_questions: string[];
  validation_checklist: ChecklistItem[];
  solution_architecture?: string;
  candidate_notes?: string;
  updated_at?: string;
}

export default function StartupOpportunityWorkspacePage() {
  const params = useParams();
  const oppId = params.opportunityId as string;

  const [workspace, setWorkspace] = useState<WorkspaceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [targetPersona, setTargetPersona] = useState("");
  const [hypotheses, setHypotheses] = useState<string[]>([]);
  const [newHypothesis, setNewHypothesis] = useState("");
  const [competitorNotes, setCompetitorNotes] = useState("");
  const [interviewQuestions, setInterviewQuestions] = useState<string[]>([]);
  const [newQuestion, setNewQuestion] = useState("");
  const [checklist, setChecklist] = useState<ChecklistItem[]>([]);
  const [solutionArch, setSolutionArch] = useState("");
  const [candidateNotes, setCandidateNotes] = useState("");

  const fetchWorkspace = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.get<any>(`/startups/${oppId}/workspace`);
      if (res.data) {
        const d: WorkspaceData = res.data;
        setWorkspace(d);
        setTargetPersona(d.target_persona || "");
        setHypotheses(d.hypotheses || []);
        setCompetitorNotes(d.competitor_notes || "");
        setInterviewQuestions(d.interview_questions || []);
        setChecklist(d.validation_checklist || []);
        setSolutionArch(d.solution_architecture || "");
        setCandidateNotes(d.candidate_notes || "");
      }
    } catch (err: any) {
      setError(err?.message || "Failed to load opportunity workspace.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (oppId) fetchWorkspace();
  }, [oppId]);

  const handleAddHypothesis = () => {
    if (!newHypothesis.trim()) return;
    setHypotheses([...hypotheses, newHypothesis.trim()]);
    setNewHypothesis("");
  };

  const handleRemoveHypothesis = (idx: number) => {
    setHypotheses(hypotheses.filter((_, i) => i !== idx));
  };

  const handleAddQuestion = () => {
    if (!newQuestion.trim()) return;
    setInterviewQuestions([...interviewQuestions, newQuestion.trim()]);
    setNewQuestion("");
  };

  const handleRemoveQuestion = (idx: number) => {
    setInterviewQuestions(interviewQuestions.filter((_, i) => i !== idx));
  };

  const handleToggleChecklist = (id: string) => {
    setChecklist(
      checklist.map((item) =>
        item.id === id ? { ...item, completed: !item.completed } : item
      )
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveSuccessMsg(null);
    try {
      await apiClient.put(`/startups/${oppId}/workspace`, {
        target_persona: targetPersona,
        hypotheses: hypotheses,
        competitor_notes: competitorNotes,
        interview_questions: interviewQuestions,
        validation_checklist: checklist,
        solution_architecture: solutionArch,
        candidate_notes: candidateNotes,
      });
      setSaveSuccessMsg("Opportunity workspace saved successfully!");
      setTimeout(() => setSaveSuccessMsg(null), 3000);
    } catch (err: any) {
      alert("Failed to save workspace: " + (err?.message || "Unknown error"));
    } finally {
      setSaving(false);
    }
  };

  const completedChecklistCount = checklist.filter((c) => c.completed).length;
  const progressPercent = checklist.length > 0 ? Math.round((completedChecklistCount / checklist.length) * 100) : 0;

  if (loading) {
    return (
      <div className="py-16 text-center text-sm text-slate-400 max-w-5xl mx-auto">
        Initializing opportunity validation canvas...
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="max-w-4xl mx-auto p-6 space-y-4">
        <Link href={`/startups/${oppId}`} className="text-xs font-semibold text-indigo-400 hover:underline">
          &larr; Back to Startup Opportunity
        </Link>
        <div className="p-4 bg-rose-950/40 border border-rose-800 text-rose-300 text-sm rounded-xl">
          {error || "Workspace not found."}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-16">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-1">
            <Link href="/startups" className="hover:text-white">
              Startups
            </Link>
            <span>/</span>
            <Link href={`/startups/${oppId}`} className="hover:text-white">
              {workspace.startup_name}
            </Link>
            <span>/</span>
            <span className="text-purple-400 font-semibold">Validation Workspace</span>
          </div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2.5">
            <span>🚀 Opportunity Canvas:</span> {workspace.startup_name}
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href={`/startups/${oppId}/pitch`}
            className="px-4 py-2 text-xs font-semibold text-slate-300 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-colors"
          >
            Bridge to Pitch Draft &rarr;
          </Link>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-5 py-2 text-xs font-bold text-white bg-purple-600 hover:bg-purple-500 rounded-lg shadow-lg shadow-purple-600/30 disabled:opacity-50 transition-all"
          >
            {saving ? "Saving Canvas..." : "Save Canvas"}
          </button>
        </div>
      </div>

      {saveSuccessMsg && (
        <div className="p-3 bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs rounded-xl">
          ✓ {saveSuccessMsg}
        </div>
      )}

      {/* Signal Briefing Bar */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-4 items-center">
        <div className="md:col-span-3 space-y-1">
          <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Verified Signal / Pain Point
          </div>
          <p className="text-sm font-semibold text-slate-200">{workspace.detected_signal}</p>
        </div>
        <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-center">
          <div className="text-[10px] uppercase font-bold text-slate-400">Validation State</div>
          <div
            className={`text-xs font-bold mt-1 px-2 py-0.5 rounded-full inline-block ${workspace.validation_state === "INDEPENDENTLY_CORROBORATED"
                ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                : workspace.validation_state === "REPEATED_OBSERVATIONS"
                  ? "bg-blue-950 text-blue-300 border border-blue-800"
                  : "bg-amber-950 text-amber-300 border border-amber-800"
              }`}
          >
            {workspace.validation_state.replace(/_/g, " ")}
          </div>
        </div>
      </div>

      {/* Main Canvas Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Canvas Elements */}
        <div className="lg:col-span-2 space-y-6">
          {/* Target Persona */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">
                1. Target Decision-Maker & Persona
              </h2>
              <span className="text-[11px] text-slate-400">Who experiences this pain point</span>
            </div>
            <input
              type="text"
              value={targetPersona}
              onChange={(e) => setTargetPersona(e.target.value)}
              placeholder="e.g. VP of Engineering / Lead Data Platform Engineer"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Testable Hypotheses */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">
                2. Testable Business & Tech Hypotheses
              </h2>
              <span className="text-[11px] text-slate-400">Assumptions to validate</span>
            </div>

            <div className="space-y-2">
              {hypotheses.map((hyp, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-200"
                >
                  <span>• {hyp}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveHypothesis(idx)}
                    className="text-slate-500 hover:text-rose-400 text-xs ml-3"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newHypothesis}
                onChange={(e) => setNewHypothesis(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddHypothesis())}
                placeholder="Add testable hypothesis..."
                className="flex-1 px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-purple-500"
              />
              <button
                type="button"
                onClick={handleAddHypothesis}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                + Add
              </button>
            </div>
          </div>

          {/* Competitor & Alternatives */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">
                3. Competitor Landscape & Alternatives
              </h2>
              <span className="text-[11px] text-slate-400">Why current workarounds fail</span>
            </div>
            <textarea
              rows={3}
              value={competitorNotes}
              onChange={(e) => setCompetitorNotes(e.target.value)}
              placeholder="What tools are they currently evaluating or hacking together in-house? What are their limitations?"
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Solution Architecture Blueprint */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider text-indigo-400">
                4. Proposed Technical Solution & Architecture
              </h2>
              <span className="text-[11px] text-slate-400">How you would build or fix it</span>
            </div>
            <textarea
              rows={4}
              value={solutionArch}
              onChange={(e) => setSolutionArch(e.target.value)}
              placeholder="Describe the high-level architecture, components, API endpoints, or database refactoring strategy..."
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white font-mono focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>

        {/* Right Col: Validation Checklist & Interview Questions */}
        <div className="space-y-6">
          {/* Validation Checklist Card */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider text-emerald-400">
                Validation Checklist
              </h3>
              <span className="text-xs font-bold text-emerald-400">{progressPercent}%</span>
            </div>

            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-emerald-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              />
            </div>

            <div className="space-y-2.5 pt-1">
              {checklist.map((item) => (
                <label
                  key={item.id}
                  className="flex items-start gap-2.5 p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 cursor-pointer hover:border-slate-700 transition"
                >
                  <input
                    type="checkbox"
                    checked={item.completed}
                    onChange={() => handleToggleChecklist(item.id)}
                    className="mt-0.5 rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-0"
                  />
                  <span
                    className={`text-xs ${item.completed ? "line-through text-slate-500" : "text-slate-200"
                      }`}
                  >
                    {item.label}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Customer Discovery Questions */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider text-purple-400">
                Customer Discovery Script
              </h3>
              <span className="text-[11px] text-slate-400">{interviewQuestions.length} Questions</span>
            </div>

            <div className="space-y-2">
              {interviewQuestions.map((q, idx) => (
                <div
                  key={idx}
                  className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-start justify-between gap-2"
                >
                  <span>
                    <strong className="text-purple-400">Q{idx + 1}:</strong> {q}
                  </span>
                  <button
                    type="button"
                    onClick={() => handleRemoveQuestion(idx)}
                    className="text-slate-500 hover:text-rose-400 text-xs shrink-0"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>

            <div className="flex gap-2">
              <input
                type="text"
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), handleAddQuestion())}
                placeholder="Add interview question..."
                className="flex-1 px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-purple-500"
              />
              <button
                type="button"
                onClick={handleAddQuestion}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                +
              </button>
            </div>
          </div>

          {/* Candidate Working Notes */}
          <div className="p-6 bg-slate-900 border border-slate-800 rounded-2xl space-y-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider text-slate-400">
              Private Workspace Notes
            </h3>
            <textarea
              rows={4}
              value={candidateNotes}
              onChange={(e) => setCandidateNotes(e.target.value)}
              placeholder="Record call notes, founder reactions, follow-up dates..."
              className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white focus:outline-none focus:border-purple-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

