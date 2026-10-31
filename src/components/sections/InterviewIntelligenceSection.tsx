'use client';

import React, { useState } from 'react';
import {
  Mic,
  CheckCircle2,
  Clock,
  Sparkles,
  Play,
  Layers,
  Award,
  ChevronRight,
  TrendingUp,
  Brain,
  MessageSquare,
  ShieldAlert,
  ArrowRight,
} from 'lucide-react';
import { InterviewIntelData, InterviewTask } from '@/services/types';
import { mockInterviewIntelData } from '@/services/mockData';

export function InterviewIntelligenceSection() {
  const [intelData, setIntelData] = useState<InterviewIntelData>(mockInterviewIntelData);
  const [activeTask, setActiveTask] = useState<InterviewTask>(
    mockInterviewIntelData.itinerary.find((t) => t.isActive) || mockInterviewIntelData.itinerary[3]
  );
  const [simRunning, setSimRunning] = useState(false);
  const [simScore, setSimScore] = useState<number | null>(null);

  const handleLaunchSim = () => {
    setSimRunning(true);
    setTimeout(() => {
      setSimRunning(false);
      setSimScore(94);
    }, 2000);
  };

  return (
    <div className="flex flex-col gap-6 w-full select-none pb-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight flex items-center gap-2">
            <span>Interview Intelligence & 48h Simulator</span>
            <span className="bg-indigo-50 text-indigo-700 border border-indigo-200/60 rounded-full px-2.5 py-0.5 text-[11px] font-bold">
              Round 3 Focus
            </span>
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-xl mt-0.5">
            48-hour high-fidelity preparation sequence, simulated whiteboarding, and executive phrasing polish for Alex Mercer.
          </p>
        </div>

        <button
          onClick={handleLaunchSim}
          className="bg-black hover:bg-gray-800 text-white font-bold px-4 py-2 rounded-full text-xs shadow-md transition-all flex items-center gap-2 self-start sm:self-auto"
        >
          <Play className="size-3.5 fill-white" />
          <span>{simRunning ? 'Evaluating Architecture...' : 'Launch Live Simulation'}</span>
        </button>
      </div>

      {/* 4 Bento Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Readiness Index
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {intelData.metrics.readinessScore.score}
            <span className="text-sm text-gray-400 font-normal"> / 100</span>
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {intelData.metrics.readinessScore.delta}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Scheduled Focus
          </div>
          <div className="text-xl sm:text-2xl font-extrabold text-[#171c23] tracking-tight mt-1 truncate">
            {intelData.metrics.targetRound.focus}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {intelData.metrics.targetRound.round}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Question Clusters
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {intelData.metrics.questionClusters.count}
          </div>
          <div className="text-[11px] text-gray-600 font-medium mt-1">
            {intelData.metrics.questionClusters.rehearsed}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Mock Runs Completed
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {intelData.metrics.mockRuns.completed}
            <span className="text-sm text-gray-400 font-normal"> / {intelData.metrics.mockRuns.total}</span>
          </div>
          <div className="text-[11px] text-amber-700 font-semibold mt-1">
            {intelData.metrics.mockRuns.remaining}
          </div>
        </div>
      </div>

      {/* Dual Workspace Split: Itinerary (Left) + AI Simulator & Scorecard (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: 48-Hour Structured Itinerary */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
            <div>
              <h3 className="text-base font-bold text-[#171c23]">
                48-Hour Structured Itinerary (Datadog Onsite)
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Targeted preparation track leading into tomorrow morning&apos;s System Architecture panel.
              </p>
            </div>

            <div className="flex flex-col gap-3">
              {intelData.itinerary.map((task) => {
                const isSelected = activeTask.id === task.id;
                return (
                  <div
                    key={task.id}
                    onClick={() => setActiveTask(task)}
                    className={`rounded-2xl p-4 border cursor-pointer transition-all duration-200 flex flex-col gap-2 ${
                      task.isActive
                        ? 'bg-indigo-50/70 border-indigo-300 ring-1 ring-indigo-200 shadow-sm'
                        : isSelected
                        ? 'bg-white border-black shadow-md'
                        : 'bg-gray-50/70 hover:bg-gray-100/70 border-gray-200/80'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span
                          className={`size-6 rounded-full flex items-center justify-center text-[11px] font-bold ${
                            task.isComplete
                              ? 'bg-emerald-500 text-white'
                              : task.isActive
                              ? 'bg-indigo-600 text-white animate-pulse'
                              : 'bg-gray-200 text-gray-600'
                          }`}
                        >
                          {task.isComplete ? '✓' : task.stepNumber}
                        </span>
                        <h4 className="text-xs font-bold text-[#171c23]">{task.title}</h4>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          task.isComplete
                            ? 'bg-emerald-100 text-emerald-800'
                            : task.isActive
                            ? 'bg-indigo-100 text-indigo-800 font-extrabold'
                            : 'bg-gray-200 text-gray-600'
                        }`}
                      >
                        {task.isComplete ? 'Complete' : task.isActive ? 'Active Focus' : 'Scheduled'}
                      </span>
                    </div>

                    <p className="text-xs text-gray-600 pl-8 leading-relaxed">
                      {task.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: AI Simulator Scorecard & Feedback Intel */}
        <div className="lg:col-span-5 bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_24px_rgba(0,0,0,0.04)] flex flex-col gap-5 sticky top-4">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
              Evaluation Intelligence
            </span>
            <h3 className="text-lg font-bold text-gray-900 mt-0.5">
              Live Architecture Simulator Scorecard
            </h3>
            {simScore && (
              <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold px-3 py-1.5 rounded-xl mt-2 flex items-center justify-between">
                <span>Latest Run Result:</span>
                <span className="text-sm font-extrabold">{simScore}/100 Top Tier</span>
              </div>
            )}
          </div>

          {/* Macro Breakdown Bars */}
          <div className="bg-gray-50/90 border border-gray-200/80 rounded-xl p-4 flex flex-col gap-3">
            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-gray-700">Architecture Depth</span>
                <span className="text-indigo-600 font-bold">
                  {intelData.simulatorScorecard.architectureDepth}%
                </span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                <div
                  style={{ width: `${intelData.simulatorScorecard.architectureDepth}%` }}
                  className="bg-indigo-600 h-full rounded-full"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-gray-700">Tradeoff Clarity</span>
                <span className="text-teal-600 font-bold">
                  {intelData.simulatorScorecard.tradeoffClarity}%
                </span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                <div
                  style={{ width: `${intelData.simulatorScorecard.tradeoffClarity}%` }}
                  className="bg-teal-600 h-full rounded-full"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="text-gray-700">Communication & Brevity</span>
                <span className="text-emerald-600 font-bold">
                  {intelData.simulatorScorecard.communication}%
                </span>
              </div>
              <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                <div
                  style={{ width: `${intelData.simulatorScorecard.communication}%` }}
                  className="bg-emerald-600 h-full rounded-full"
                />
              </div>
            </div>
          </div>

          {/* Phrasing Refinements Suggestion Box */}
          <div className="bg-white border border-gray-200/90 rounded-2xl p-4 flex flex-col gap-2.5 shadow-sm">
            <div className="flex items-center gap-1.5 text-xs font-bold text-gray-800">
              <MessageSquare className="size-3.5 text-indigo-600" />
              <span>Phrasing & Delivery Polish:</span>
            </div>
            <div className="bg-rose-50 border border-rose-100 rounded-lg p-2.5 text-xs text-rose-800">
              <span className="font-semibold block text-[10px] uppercase text-rose-600">Avoid Raw phrasing:</span>
              {intelData.phrasingRefinement.raw}
            </div>
            <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-2.5 text-xs text-emerald-800">
              <span className="font-semibold block text-[10px] uppercase text-emerald-600">AI Refined Delivery:</span>
              {intelData.phrasingRefinement.aiRefinement}
            </div>
          </div>

          {/* Interviewer Archetype Insight Card */}
          <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-col gap-2 shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400">
                Vetting Team Persona
              </span>
              <span className="text-xs font-bold text-gray-300">
                {intelData.interviewerPersona.archetype}
              </span>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              {intelData.interviewerPersona.counselNote}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

