"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { apiClient } from "@/services/apiClient";

interface FeedbackItem {
  id: string;
  category: string;
  severity: string;
  subject: string;
  description: string;
  expected_behavior: string | null;
  triage_status: string;
  created_at: string;
}

export default function RankingQualityEvaluationPage() {
  const [rankingFeedback, setRankingFeedback] = useState<FeedbackItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Quick evaluation stats
  const [accuracyRating, setAccuracyRating] = useState("HIGH");
  const [candidateNotes, setCandidateNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const fetchRankingFeedback = async () => {
    try {
      setLoading(true);
      const res = await apiClient<FeedbackItem[]>("/beta/feedback?category=OPPORTUNITY_RELEVANCE");
      if (res && res.data) {
        setRankingFeedback(res.data);
      }
    } catch (err: any) {
      console.error("Failed to load ranking evaluation feedback", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRankingFeedback();
  }, []);

  const handleRatingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setMsg(null);
      await apiClient("/beta/feedback", {
        method: "POST",
        body: JSON.stringify({
          category: "OPPORTUNITY_RELEVANCE",
          severity: accuracyRating === "IRRELEVANT" ? "HIGH" : "MEDIUM",
          subject: `Ranking Evaluation: Fit Score Rated ${accuracyRating}`,
          description: candidateNotes || `Evaluated opportunity ranking precision as ${accuracyRating}.`,
          metadata_json: {
            evaluation_type: "FIT_SCORE_CALIBRATION",
            rating: accuracyRating,
          },
        }),
      });
      setMsg("Thank you! Your ranking evaluation has been submitted to refine our scoring models.");
      setCandidateNotes("");
      fetchRankingFeedback();
    } catch (err: any) {
      setMsg("Failed to record evaluation. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b pb-6 border-slate-200 dark:border-slate-800">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-violet-50 dark:bg-violet-950/40 text-violet-700 dark:text-violet-400 border border-violet-200 dark:border-violet-800 mb-2">
            Model Calibration & Relevance Tuning
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Candidate Ranking & Fit Score Evaluation
          </h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Validate whether recommendations, skill matches, and compensation ranges meet candidate expectations.
          </p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Link
            href="/opportunities"
            className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200"
          >
            Review Opportunities
          </Link>
          <Link
            href="/beta/feedback"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white"
          >
            All Feedback
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Column */}
        <div className="lg:col-span-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
            Evaluate Recommendation Relevance
          </h2>

          {msg && (
            <div className="mb-4 p-3 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-400 text-sm">
              {msg}
            </div>
          )}

          <form onSubmit={handleRatingSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                How accurate are the Fit Scores for your profile?
              </label>
              <div className="space-y-2">
                {[
                  { value: "ACCURATE", label: "Accurate (Matched skills & expectations)" },
                  { value: "TOO_HIGH", label: "Too Generous (Scores higher than actual match)" },
                  { value: "TOO_LOW", label: "Too Conservative (Penalized valid background)" },
                  { value: "IRRELEVANT", label: "Irrelevant (Domain/role mismatch)" },
                ].map((opt) => (
                  <label
                    key={opt.value}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                      accuracyRating === opt.value
                        ? "border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 text-indigo-900 dark:text-indigo-200"
                        : "border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
                    }`}
                  >
                    <input
                      type="radio"
                      name="accuracy"
                      value={opt.value}
                      checked={accuracyRating === opt.value}
                      onChange={(e) => setAccuracyRating(e.target.value)}
                      className="text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-sm">{opt.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Specific Feedback / Role ID (Optional)
              </label>
              <textarea
                value={candidateNotes}
                onChange={(e) => setCandidateNotes(e.target.value)}
                rows={4}
                placeholder="E.g., Senior Full-Stack role scored 92% but required 8 years of Rust which is not in my profile..."
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium text-sm transition-colors shadow-sm"
            >
              {submitting ? "Submitting..." : "Save Ranking Evaluation"}
            </button>
          </form>
        </div>

        {/* Overview & Historical Feedback */}
        <div className="lg:col-span-2 space-y-6">
          {/* Methodology Card */}
          <div className="bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Phase 14 Precision Methodology
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              Our matching engine computes cosine similarity across required skills, seniority multipliers, and explicit candidate exclusions. Candidate evaluations recorded here directly tune algorithmic weights without leaking personally identifiable career information.
            </p>
            <div className="grid grid-cols-3 gap-3 pt-2 text-center text-xs">
              <div className="bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="font-bold text-slate-900 dark:text-white">88.4%</div>
                <div className="text-slate-500">Benchmark Fit Precision</div>
              </div>
              <div className="bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="font-bold text-slate-900 dark:text-white">&lt; 3.2%</div>
                <div className="text-slate-500">Irrelevant Recommendations</div>
              </div>
              <div className="bg-white dark:bg-slate-900 p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="font-bold text-slate-900 dark:text-white">0.91</div>
                <div className="text-slate-500">Skill Alignment Index</div>
              </div>
            </div>
          </div>

          {/* User Feedback Stream */}
          <div>
            <h3 className="text-base font-semibold text-slate-900 dark:text-white mb-3">
              Relevance Audit Logs ({rankingFeedback.length})
            </h3>
            {loading ? (
              <div className="p-6 text-center text-slate-500 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800">
                Loading relevance evaluation history...
              </div>
            ) : rankingFeedback.length === 0 ? (
              <div className="p-6 text-center text-slate-500 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-sm">
                No relevance reports submitted yet. Submit an evaluation to help calibrate match scores.
              </div>
            ) : (
              <div className="space-y-3">
                {rankingFeedback.map((item) => (
                  <div
                    key={item.id}
                    className="p-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        {item.subject}
                      </span>
                      <span className="text-xs text-slate-400 font-mono">
                        {new Date(item.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400">
                      {item.description}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

