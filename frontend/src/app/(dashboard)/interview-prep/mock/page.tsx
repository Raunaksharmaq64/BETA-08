"use client";

import React, { useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";
import { useAuth } from "@/context/AuthContext";

interface MockQuestion {
  id: string;
  question_text: string;
  question_type: string;
  competency_focus: string;
  expected_points: string[];
  candidate_response?: string;
  rubric_evaluation?: {
    relevance: number;
    clarity: number;
    structure: number;
    evidence: number;
    technical_correctness: number;
    communication: number;
    overall_score: number;
    strengths: string[];
    improvements: string[];
  };
}

interface MockSession {
  id: string;
  user_id: string;
  target_role: string;
  target_company?: string;
  round_type: string;
  status: string;
  questions: MockQuestion[];
}

export default function MockInterviewPage() {
  const { user } = useAuth();

  // Session Setup State
  const [session, setSession] = useState<MockSession | null>(null);
  const [targetRole, setTargetRole] = useState("Senior Backend Engineer");
  const [targetCompany, setTargetCompany] = useState("");
  const [roundType, setRoundType] = useState("BEHAVIORAL");
  const [startingSession, setStartingSession] = useState(false);

  // Active Question & Response State
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [responseText, setResponseText] = useState("");
  const [evaluating, setEvaluating] = useState(false);

  const handleStartSession = async (e: React.FormEvent) => {
    e.preventDefault();
    setStartingSession(true);
    try {
      const res = await apiClient<MockSession>("/interview-prep/mock-sessions", {
        method: "POST",
        body: JSON.stringify({
          target_role: targetRole.trim(),
          target_company: targetCompany.trim() || undefined,
          round_type: roundType,
        }),
      });
      setSession(res.data);
      setCurrentQIndex(0);
      setResponseText("");
    } catch (err: any) {
      alert(err.message || "Failed to start mock interview session.");
    } finally {
      setStartingSession(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !responseText.trim()) return;
    const currentQ = session.questions[currentQIndex];
    if (!currentQ) return;

    setEvaluating(true);
    try {
      const res = await apiClient<MockSession>(
        `/interview-prep/mock-sessions/${session.id}/answer`,
        {
          method: "POST",
          body: JSON.stringify({
            question_id: currentQ.id,
            response_text: responseText.trim(),
          }),
        }
      );
      setSession(res.data);
    } catch (err: any) {
      alert(err.message || "Failed to evaluate response.");
    } finally {
      setEvaluating(false);
    }
  };

  const currentQuestion = session?.questions[currentQIndex];
  const evalResult = currentQuestion?.rubric_evaluation;

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
            <span>🎙️ Interactive Mock Practice & Rubric</span>
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Simulate live interview questions with rigorous evaluation across 6 transparent scoring
            factors.
          </p>
        </div>

        {session && (
          <button
            onClick={() => setSession(null)}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700"
          >
            Start New Session
          </button>
        )}
      </div>

      {!session ? (
        /* Setup Session Card */
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-xl mx-auto shadow-2xl space-y-6">
          <div>
            <h2 className="text-xl font-bold text-white">Configure Mock Session</h2>
            <p className="text-xs text-slate-400 mt-1">
              Select your target role and interview category to generate realistic practice
              prompts.
            </p>
          </div>

          <form onSubmit={handleStartSession} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Target Role *
              </label>
              <input
                type="text"
                required
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Target Company (Optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Stripe, AWS, Netflix"
                value={targetCompany}
                onChange={(e) => setTargetCompany(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Round Type *
              </label>
              <select
                value={roundType}
                onChange={(e) => setRoundType(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
              >
                <option value="BEHAVIORAL">Behavioral & Leadership (STAR)</option>
                <option value="TECHNICAL">Technical & Core Coding</option>
                <option value="SYSTEM_DESIGN">System Design & Scale</option>
                <option value="HIRING_MANAGER">Hiring Manager Alignment</option>
              </select>
            </div>

            <div className="pt-2">
              <button
                type="submit"
                disabled={startingSession}
                className="w-full py-2.5 text-sm font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50 transition"
              >
                {startingSession ? "Generating Session Prompts..." : "Begin Mock Interview"}
              </button>
            </div>
          </form>
        </div>
      ) : (
        /* Active Practice Session */
        <div className="space-y-6">
          {/* Question Stepper */}
          <div className="flex items-center justify-between bg-slate-900 border border-slate-800 px-5 py-3 rounded-xl text-xs">
            <span className="font-semibold text-slate-300">
              {session.target_role} ({session.round_type})
            </span>
            <div className="flex items-center space-x-2">
              {session.questions.map((q, idx) => {
                const isCurrent = idx === currentQIndex;
                const isAnswered = !!q.rubric_evaluation;
                return (
                  <button
                    key={q.id}
                    onClick={() => {
                      setCurrentQIndex(idx);
                      setResponseText(q.candidate_response || "");
                    }}
                    className={`w-7 h-7 rounded-full text-xs font-bold transition ${
                      isCurrent
                        ? "bg-indigo-600 text-white ring-2 ring-indigo-400"
                        : isAnswered
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                        : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                    }`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
          </div>

          {currentQuestion && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* Question & Answer Input (7 cols) */}
              <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                <div className="flex items-center space-x-2 text-xs text-indigo-400 font-semibold uppercase tracking-wider">
                  <span>Question {currentQIndex + 1} of {session.questions.length}</span>
                  <span>•</span>
                  <span>{currentQuestion.competency_focus}</span>
                </div>

                <h2 className="text-xl font-bold text-white leading-snug">
                  {currentQuestion.question_text}
                </h2>

                {currentQuestion.expected_points && currentQuestion.expected_points.length > 0 && (
                  <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs space-y-1">
                    <span className="font-semibold text-slate-400 uppercase text-[10px]">
                      Key Points Interviewer Looks For:
                    </span>
                    <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                      {currentQuestion.expected_points.map((pt, pIdx) => (
                        <li key={pIdx}>{pt}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="space-y-2 pt-2">
                  <label className="block text-xs font-semibold text-slate-300">
                    Your Response:
                  </label>
                  <textarea
                    rows={8}
                    placeholder="Structure your answer using STAR: state the context, your task, actions taken with engineering specifics, and quantifiable outcomes..."
                    value={responseText}
                    onChange={(e) => setResponseText(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 leading-relaxed font-sans"
                  />
                </div>

                <div className="flex justify-between items-center pt-2">
                  <span className="text-[11px] text-slate-500">
                    {responseText.trim().split(/\s+/).filter(Boolean).length} words
                  </span>
                  <button
                    onClick={handleSubmitAnswer}
                    disabled={evaluating || !responseText.trim()}
                    className="px-5 py-2 text-xs font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow disabled:opacity-50 transition"
                  >
                    {evaluating ? "Evaluating Against Rubric..." : "Submit for Rubric Evaluation"}
                  </button>
                </div>
              </div>

              {/* Rubric Evaluation (5 cols) */}
              <div className="lg:col-span-5 space-y-4">
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
                  <h3 className="text-base font-bold text-white flex items-center justify-between">
                    <span>6-Factor Rubric Feedback</span>
                    {evalResult && (
                      <span className="text-xs px-2 py-0.5 rounded font-mono font-bold bg-indigo-950 text-indigo-300 border border-indigo-800">
                        {evalResult.overall_score}% Score
                      </span>
                    )}
                  </h3>

                  {!evalResult ? (
                    <div className="py-16 text-center text-xs text-slate-500">
                      Submit your response on the left to receive transparent rubric scores and
                      actionable strengths & gaps.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* Factor Scores */}
                      <div className="space-y-2 text-xs">
                        {[
                          { label: "Relevance", score: evalResult.relevance },
                          { label: "Clarity", score: evalResult.clarity },
                          { label: "Structure", score: evalResult.structure },
                          { label: "Evidence", score: evalResult.evidence },
                          { label: "Technical Correctness", score: evalResult.technical_correctness },
                          { label: "Communication", score: evalResult.communication },
                        ].map((factor) => (
                          <div key={factor.label} className="space-y-1">
                            <div className="flex justify-between text-slate-400">
                              <span>{factor.label}</span>
                              <span className="font-semibold text-slate-200">{factor.score} / 5</span>
                            </div>
                            <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-indigo-500 h-1.5 rounded-full transition-all duration-500"
                                style={{ width: `${(factor.score / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Strengths */}
                      {evalResult.strengths && evalResult.strengths.length > 0 && (
                        <div className="p-3 bg-emerald-950/30 border border-emerald-800/50 rounded-xl space-y-1 text-xs">
                          <span className="font-bold text-emerald-400 uppercase text-[10px]">
                            Strengths:
                          </span>
                          <ul className="list-disc list-inside text-emerald-200/90 space-y-0.5">
                            {evalResult.strengths.map((str, sIdx) => (
                              <li key={sIdx}>{str}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Improvements */}
                      {evalResult.improvements && evalResult.improvements.length > 0 && (
                        <div className="p-3 bg-amber-950/30 border border-amber-800/50 rounded-xl space-y-1 text-xs">
                          <span className="font-bold text-amber-400 uppercase text-[10px]">
                            Areas for Improvement:
                          </span>
                          <ul className="list-disc list-inside text-amber-200/90 space-y-0.5">
                            {evalResult.improvements.map((imp, iIdx) => (
                              <li key={iIdx}>{imp}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

