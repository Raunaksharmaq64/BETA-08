"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface STARAnswer {
  id: string;
  user_id: string;
  title: string;
  competency: string;
  situation: string;
  task: string;
  action: string;
  result: string;
  evidence_reference?: string;
  missing_metrics_flag: boolean;
  created_at: string;
}

const COMPETENCIES = [
  { value: "SYSTEM_DESIGN", label: "System Design & Architecture" },
  { value: "LEADERSHIP", label: "Leadership & Mentorship" },
  { value: "CONFLICT_RESOLUTION", label: "Conflict Resolution & Alignment" },
  { value: "INCIDENT_RESPONSE", label: "Incident Response & Post-Mortem" },
  { value: "PERFORMANCE_OPTIMIZATION", label: "Performance Optimization & Scale" },
  { value: "CROSS_FUNCTIONAL", label: "Cross-Functional Execution" },
];

export default function STARAnswerBuilderPage() {
  const { user, loading: authLoading } = useAuth();

  const [answers, setAnswers] = useState<STARAnswer[]>([]);
  const [loading, setLoading] = useState(true);

  // Form state
  const [title, setTitle] = useState("");
  const [competency, setCompetency] = useState("SYSTEM_DESIGN");
  const [situation, setSituation] = useState("");
  const [task, setTask] = useState("");
  const [action, setAction] = useState("");
  const [result, setResult] = useState("");
  const [evidenceRef, setEvidenceRef] = useState("");
  const [saving, setSaving] = useState(false);
  const [formNotice, setFormNotice] = useState<string | null>(null);

  const fetchAnswers = async () => {
    setLoading(true);
    try {
      const res = await apiClient<STARAnswer[]>("/interview-prep/star-answers");
      setAnswers(res.data || []);
    } catch (err: any) {
      console.error("Failed to load STAR answers:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchAnswers();
    }
  }, [user]);

  // Check if result contains numbers or percentages
  const containsMetrics = /\d+%?|\$\d+|\b(reduced|increased|improved|scaled|saved|cut)\b/i.test(
    result
  );

  const handleSubmitStory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !situation.trim() || !task.trim() || !action.trim() || !result.trim()) {
      alert("All STAR components (Situation, Task, Action, Result) are required.");
      return;
    }

    setSaving(true);
    setFormNotice(null);
    try {
      const res = await apiClient<STARAnswer>("/interview-prep/star-answers", {
        method: "POST",
        body: JSON.stringify({
          title: title.trim(),
          competency,
          situation: situation.trim(),
          task: task.trim(),
          action: action.trim(),
          result: result.trim(),
          evidence_reference: evidenceRef.trim() || undefined,
        }),
      });

      if (res.data?.missing_metrics_flag) {
        setFormNotice(
          "⚠️ Saved with Advisory: Your Result section lacks verifiable quantifiable metrics (percentages, throughput, dollar savings). We recommend editing to include measurable numbers."
        );
      }

      setTitle("");
      setSituation("");
      setTask("");
      setAction("");
      setResult("");
      setEvidenceRef("");
      fetchAnswers();
    } catch (err: any) {
      alert(err.message || "Failed to save STAR story.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <Link
              href="/interview-prep"
              className="text-xs font-semibold text-slate-400 hover:text-white"
            >
              &larr; Interview Prep Hub
            </Link>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1 flex items-center gap-2">
            <span>⭐ Evidence-Grounded STAR Answer Builder</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Build bulletproof behavioral stories strictly anchored in your confirmed career
            evidence.
          </p>
        </div>

        {/* Zero-Hallucination Policy Pill */}
        <div className="bg-emerald-950/60 border border-emerald-800/80 px-3.5 py-2 rounded-xl text-xs text-emerald-300 flex items-center gap-2">
          <span>🛡️</span>
          <span className="font-medium">Strict Policy: Zero Hallucinated Metrics</span>
        </div>
      </div>

      {formNotice && (
        <div className="p-4 bg-amber-950/40 border border-amber-800 rounded-xl text-amber-200 text-xs">
          {formNotice}
        </div>
      )}

      {/* Main Grid: Builder Form (Left 7) + Existing Stories (Right 5) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Builder Form */}
        <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <h2 className="text-lg font-bold text-white flex items-center justify-between">
            <span>Craft New Story</span>
            <span className="text-xs font-normal text-slate-400">Situation • Task • Action • Result</span>
          </h2>

          <form onSubmit={handleSubmitStory} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Story Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Scaling Auth Service to 40K RPS"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Target Competency *
                </label>
                <select
                  value={competency}
                  onChange={(e) => setCompetency(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  {COMPETENCIES.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Situation (Context, stakes & scale) *
              </label>
              <textarea
                rows={2}
                required
                placeholder="At company X, our legacy PostgreSQL auth database experienced connection exhaustion during Black Friday traffic spikes..."
                value={situation}
                onChange={(e) => setSituation(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Task (Your specific mandate & challenge) *
              </label>
              <textarea
                rows={2}
                required
                placeholder="I was tasked with redesigning the session cache layer and introducing read-through Redis clusters without interrupting active customer logins..."
                value={task}
                onChange={(e) => setTask(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Action (What YOU specifically decided, architected, and executed) *
              </label>
              <textarea
                rows={3}
                required
                placeholder="I benchmarked Redis cluster configurations, wrote an async pooling client in Go, designed a zero-downtime shadow dual-write pipeline, and implemented circuit breakers..."
                value={action}
                onChange={(e) => setAction(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="block text-xs font-semibold text-slate-300">
                  Result (Measurable outcomes & numbers) *
                </label>
                {result.length > 5 && !containsMetrics && (
                  <span className="text-[11px] font-medium text-amber-400">
                    ⚠️ Missing quantifiable metric
                  </span>
                )}
                {result.length > 5 && containsMetrics && (
                  <span className="text-[11px] font-medium text-emerald-400">
                    ✓ Quantifiable metrics detected
                  </span>
                )}
              </div>
              <textarea
                rows={2}
                required
                placeholder="Reduced p99 auth latency from 450ms to 18ms (-96%), supported 45k RPS peak load, and achieved 100% uptime through the holiday season."
                value={result}
                onChange={(e) => setResult(e.target.value)}
                className={`w-full bg-slate-950 border rounded-lg p-3 text-xs text-slate-200 focus:outline-none ${
                  result.length > 5 && !containsMetrics
                    ? "border-amber-600 focus:border-amber-500"
                    : "border-slate-800 focus:border-indigo-500"
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Resume / Project Evidence Reference (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Resume Section: Lead Platform Engineer (Acme Corp)"
                value={evidenceRef}
                onChange={(e) => setEvidenceRef(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-800">
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2.5 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50"
              >
                {saving ? "Saving Story..." : "Save Grounded STAR Story"}
              </button>
            </div>
          </form>
        </div>

        {/* Existing Stories List */}
        <div className="lg:col-span-5 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center justify-between">
            <span>Saved Stories ({answers.length})</span>
            <span className="text-xs text-slate-400 font-normal">Candidate Bank</span>
          </h2>

          {loading ? (
            <div className="py-12 text-center text-slate-400">
              <div className="inline-block animate-spin rounded-full h-6 w-6 border-2 border-indigo-500 border-t-transparent mb-2" />
              <p className="text-xs">Loading stories...</p>
            </div>
          ) : answers.length === 0 ? (
            <div className="p-8 text-center bg-slate-900 border border-dashed border-slate-800 rounded-xl text-slate-500 text-xs">
              No STAR stories recorded yet. Use the builder on the left to structure your project
              achievements.
            </div>
          ) : (
            <div className="space-y-4">
              {answers.map((story) => (
                <div
                  key={story.id}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 uppercase tracking-wide border border-indigo-800/60">
                        {story.competency.replace(/_/g, " ")}
                      </span>
                      <h3 className="font-bold text-white text-sm mt-1">{story.title}</h3>
                    </div>
                    {story.missing_metrics_flag && (
                      <span
                        className="text-[10px] font-semibold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800"
                        title="Advisory: No quantifiable metrics detected in Result"
                      >
                        ⚠️ Missing Numbers
                      </span>
                    )}
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <span className="font-semibold text-slate-400">S: </span>
                      <span className="text-slate-300">{story.situation}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-400">T: </span>
                      <span className="text-slate-300">{story.task}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-slate-400">A: </span>
                      <span className="text-slate-300">{story.action}</span>
                    </div>
                    <div>
                      <span className="font-semibold text-emerald-400">R: </span>
                      <span className="text-slate-200 font-medium">{story.result}</span>
                    </div>
                  </div>

                  {story.evidence_reference && (
                    <div className="pt-2 border-t border-slate-800/60 text-[11px] text-slate-500">
                      🔗 Grounded in: {story.evidence_reference}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

