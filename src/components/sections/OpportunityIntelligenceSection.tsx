'use client';

import React, { useState } from 'react';
import {
  Sparkles,
  Clock,
  TrendingUp,
  ShieldCheck,
  Building2,
  MapPin,
  DollarSign,
  ArrowUpRight,
  ChevronRight,
  X,
  Bookmark,
  Send,
  CheckCircle2,
  ArrowUpDown,
} from 'lucide-react';

interface Opportunity {
  id: string;
  title: string;
  company: string;
  companyInitial: string;
  location: string;
  compensation: string;
  tag: string;
  matchScore: number;
  status: 'recommended' | 'consider' | 'skip' | 'saved';
  stageBadge?: string;
  prepTimeHours: number;
  turnaroundLabel: string;
  scores: {
    skillMatch: number;
    eligibility: number;
    projectRelevance: number;
    preferenceMatch: number;
    trustConfidence: string;
    trustPercentage: number;
  };
  aiJustification: string;
}

export function OpportunityIntelligenceSection() {
  const [activeTab, setActiveTab] = useState<'recommended' | 'consider' | 'skip' | 'saved'>('recommended');
  const [selectedId, setSelectedId] = useState('opp-1');
  const [actionFeedback, setActionFeedback] = useState<string | null>(null);

  const initialOpportunities: Opportunity[] = [
    {
      id: 'opp-1',
      title: 'Staff Systems Architect',
      company: 'Cognition AI',
      companyInitial: 'C',
      location: 'San Francisco, CA (Hybrid / Remote Option)',
      compensation: '$175k – $190k + Equity',
      tag: 'Top 1% Fit',
      matchScore: 97,
      status: 'recommended',
      stageBadge: 'ACTIVE EVALUATION',
      prepTimeHours: 2.5,
      turnaroundLabel: 'In Scope',
      scores: {
        skillMatch: 97,
        eligibility: 95,
        projectRelevance: 92,
        preferenceMatch: 98,
        trustConfidence: 'High',
        trustPercentage: 99,
      },
      aiJustification:
        "This position precisely maps to Alex Mercer's recent lead architecture work in distributed runtime safety and deterministic sandboxing. Cognition's current engineering bottleneck revolves around large-scale code synthesis evaluation runners, directly matching Alex's published framework on isolated IPC state.",
    },
    {
      id: 'opp-2',
      title: 'Distributed Runtime Lead',
      company: 'Vercel Edge Labs',
      companyInitial: 'V',
      location: 'San Francisco, CA • Remote',
      compensation: '$170k - $185k',
      tag: 'SERIES A • REMOTE',
      matchScore: 94,
      status: 'recommended',
      prepTimeHours: 1.0,
      turnaroundLabel: 'Quick Turnaround',
      scores: {
        skillMatch: 94,
        eligibility: 92,
        projectRelevance: 96,
        preferenceMatch: 91,
        trustConfidence: 'High',
        trustPercentage: 98,
      },
      aiJustification:
        'Vercel Edge Labs seeks an isolation lead for serverless V8 runtimes. Strong alignment with your micro-benchmarks on deterministic sandbox initialization bounds.',
    },
    {
      id: 'opp-3',
      title: 'Principal Cloud Architect',
      company: 'Datadog Core',
      companyInitial: 'D',
      location: 'New York, NY • Hybrid',
      compensation: '$190k - $210k',
      tag: 'PUBLIC TECH • HYBRID',
      matchScore: 91,
      status: 'recommended',
      prepTimeHours: 3.5,
      turnaroundLabel: 'High Effort Tailoring',
      scores: {
        skillMatch: 91,
        eligibility: 89,
        projectRelevance: 90,
        preferenceMatch: 93,
        trustConfidence: 'High',
        trustPercentage: 97,
      },
      aiJustification:
        'Datadog Core telemetry ingestion requires deep knowledge of distributed log replication and lockless ring buffer queues.',
    },
    {
      id: 'opp-4',
      title: 'Head of Foundations',
      company: 'Stealth AI',
      companyInitial: 'S',
      location: 'Bay Area, CA • On-site',
      compensation: '$200k - $225k',
      tag: 'STEALTH AI • BAY AREA',
      matchScore: 88,
      status: 'recommended',
      prepTimeHours: 4.0,
      turnaroundLabel: 'High Leverage',
      scores: {
        skillMatch: 88,
        eligibility: 85,
        projectRelevance: 90,
        preferenceMatch: 86,
        trustConfidence: 'Medium',
        trustPercentage: 94,
      },
      aiJustification:
        'Early-stage frontier AI research lab building autonomous agent execution kernels. Substantial founder equity upside.',
    },
  ];

  const [opportunities, setOpportunities] = useState<Opportunity[]>(initialOpportunities);

  const selectedOpp = opportunities.find((o) => o.id === selectedId) || opportunities[0];

  const handleAction = (status: 'consider' | 'skip' | 'saved', label: string) => {
    setActionFeedback(label);
    setOpportunities((prev) =>
      prev.map((o) => (o.id === selectedOpp.id ? { ...o, status } : o))
    );
    setTimeout(() => setActionFeedback(null), 2000);
  };

  const counts = {
    recommended: opportunities.filter((o) => o.status === 'recommended').length,
    consider: opportunities.filter((o) => o.status === 'consider').length,
    skip: opportunities.filter((o) => o.status === 'skip').length,
    saved: opportunities.filter((o) => o.status === 'saved').length,
  };

  const filteredOpportunities = opportunities.filter((o) => o.status === activeTab);

  return (
    <div className="flex flex-col gap-6 w-full select-none">
      {/* Toast feedback */}
      {actionFeedback && (
        <div className="fixed top-20 right-10 z-50 bg-black text-white text-xs px-4 py-2 rounded-full shadow-2xl flex items-center gap-2 animate-fade-in">
          <CheckCircle2 className="size-4 text-emerald-400" />
          <span>Moved {selectedOpp.company} to {actionFeedback}</span>
        </div>
      )}

      {/* Module Title & Status Tabs Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight">
            Opportunity Intelligence
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-lg mt-0.5">
            High-fidelity decision engine & budget optimizer for senior architecture positions.
          </p>
        </div>

        {/* Segmented Category Tabs Capsule */}
        <div className="bg-[rgba(255,255,255,0.7)] border border-[rgba(255,255,255,0.85)] rounded-full p-1 flex items-center gap-1 shadow-sm backdrop-blur-md self-start sm:self-auto">
          {(['recommended', 'consider', 'skip', 'saved'] as const).map((tab) => {
            const isActive = activeTab === tab;
            const count = counts[tab];
            return (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs transition-all capitalize ${
                  isActive
                    ? 'bg-white font-semibold text-[#171c23] shadow-sm'
                    : 'text-[#5d5e63] hover:text-black hover:bg-white/40'
                }`}
              >
                <span>{tab}</span>
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.2 rounded-full ${
                    isActive ? 'bg-[#181a1f] text-white' : 'text-gray-400'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Bento Row: Weekly Time Budget Optimizer & Decision Velocity */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Widget 1: Weekly Time Budget Optimizer (8 cols) */}
        <div className="lg:col-span-8 backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-[32px] p-5 shadow-sm flex flex-col justify-between gap-4">
          <div className="flex items-start justify-between w-full">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[#76777b] text-[11px] font-medium tracking-wider uppercase">
                  WEEKLY TIME BUDGET OPTIMIZER
                </span>
                <div className="bg-[#10b981] size-1.5 rounded-full animate-pulse" />
              </div>
              <h3 className="text-[#171c23] text-lg sm:text-xl font-semibold tracking-tight mt-1">
                Weekly Application Budget: 6.0 hrs / 10.0 hrs used
              </h3>
            </div>

            <div className="bg-[#e8f5ed] border border-emerald-200/60 rounded-full px-3 py-1 text-[#459364] text-xs font-semibold flex items-center gap-1.5 shrink-0">
              <Clock className="size-3.5" />
              <span>4.0 hrs remaining</span>
            </div>
          </div>

          {/* Visual Progress Track */}
          <div className="flex flex-col gap-1.5 w-full">
            <div className="bg-[#e4e8f2] border border-white rounded-full h-2.5 p-[2px] flex items-center w-full overflow-hidden shadow-inner">
              <div style={{ width: '40%' }} className="bg-black h-full rounded-full" />
              <div style={{ width: '20%' }} className="bg-[#76777b] h-full rounded-full ml-1" />
            </div>
            <div className="flex items-center justify-between text-[11px] text-[#5d5e63]">
              <span>Tailored Deep Applications (4.0 hrs)</span>
              <span>Quick Signals (2.0 hrs)</span>
              <span className="font-semibold text-black">Target Max: 10.0 hrs/wk</span>
            </div>
          </div>

          {/* Recommendation Callout */}
          <div className="bg-white/90 border border-white rounded-2xl px-3.5 py-2 flex items-center justify-between shadow-sm text-xs">
            <div className="flex items-center gap-2 truncate pr-2">
              <Sparkles className="size-3.5 text-amber-600 shrink-0" />
              <p className="truncate">
                <span className="font-bold text-black">Strong → AI Strategy: </span>
                <span className="text-gray-700">
                  High leverage detected for <span className="font-semibold italic">Cognition AI</span>. Invest 2.5 hrs on custom distributed topology deck; skip standard quick form.
                </span>
              </p>
            </div>
            <span className="font-semibold text-black text-[11px] shrink-0">Priority Action</span>
          </div>
        </div>

        {/* Widget 2: Metric Stat Block (4 cols) */}
        <div className="lg:col-span-4 backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-[32px] p-5 shadow-sm flex flex-col justify-between gap-3">
          <div>
            <span className="text-[#76777b] text-[11px] font-medium tracking-wider uppercase">
              DECISION VELOCITY
            </span>
            <div className="flex items-baseline gap-3 my-1">
              <span className="text-4xl sm:text-[44px] font-normal tracking-tight text-[#171c23]">
                94.2%
              </span>
              <div className="bg-[#e8f5ed] text-[#459364] px-2 py-0.5 rounded-full text-xs font-bold shadow-sm">
                +18%
              </div>
            </div>
            <p className="text-xs text-[#5d5e63]">
              Avg 1.8 mins triage time per detected opening
            </p>
          </div>

          <div className="border-t border-[rgba(228,232,242,0.6)] pt-2.5 flex items-center justify-between text-xs">
            <span className="text-[#5d5e63]">12 queued for review</span>
            <span className="font-semibold text-black flex items-center gap-0.5">
              <span>Optimized SLA</span>
              <ArrowUpRight className="size-3" />
            </span>
          </div>
        </div>
      </div>

      {/* Main Triage Workspace: 8 cols Detail Dossier + 4 cols Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Dossier (8 cols) */}
        <div className="lg:col-span-8 backdrop-blur-[14px] bg-[rgba(255,255,255,0.75)] border border-white rounded-[32px] p-6 shadow-sm flex flex-col gap-5">
          {/* Header Card */}
          <div className="border-b border-gray-100 pb-5 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="flex items-start gap-3.5">
              <div className="bg-black size-11 rounded-2xl flex items-center justify-center text-white font-bold text-lg shadow-md shrink-0">
                {selectedOpp.companyInitial}
              </div>
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="text-xl sm:text-2xl font-bold text-[#171c23]">
                    {selectedOpp.title}
                  </h3>
                  <span className="bg-black text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                    {selectedOpp.tag}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-[#5d5e63] flex-wrap">
                  <span className="font-semibold text-black">{selectedOpp.company}</span>
                  <span>•</span>
                  <span>{selectedOpp.location}</span>
                  <span>•</span>
                  <span className="font-semibold text-black">{selectedOpp.compensation}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 shrink-0 self-end sm:self-start">
              <button
                onClick={() => handleAction('skip', 'Skipped')}
                className="border border-gray-300 rounded-full px-3.5 py-1.5 text-xs font-semibold text-gray-600 hover:bg-black/5 hover:text-black transition-all"
              >
                SKIP
              </button>
              <button
                onClick={() => handleAction('consider', 'Consider List')}
                className="bg-white border border-gray-200 rounded-full px-3.5 py-1.5 text-xs font-semibold text-black shadow-sm hover:bg-gray-50 transition-all"
              >
                CONSIDER
              </button>
              <button
                onClick={() => handleAction('saved', 'Applied')}
                className="bg-black text-white rounded-full px-4 py-1.5 text-xs font-semibold shadow-md hover:bg-gray-800 transition-all flex items-center gap-1.5"
              >
                <Send className="size-3" />
                <span>APPLY</span>
              </button>
            </div>
          </div>

          {/* 5-Metric Scoring Engine */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
            <div className="bg-white/80 p-3 rounded-2xl border border-white shadow-sm">
              <span className="text-[11px] text-gray-500 font-medium">Skill Match</span>
              <p className="text-lg font-bold text-black mt-1">{selectedOpp.scores.skillMatch}%</p>
              <div className="bg-gray-200 h-1 rounded-full w-full mt-1.5 overflow-hidden">
                <div style={{ width: `${selectedOpp.scores.skillMatch}%` }} className="bg-black h-full rounded-full" />
              </div>
            </div>

            <div className="bg-white/80 p-3 rounded-2xl border border-white shadow-sm">
              <span className="text-[11px] text-gray-500 font-medium">Eligibility</span>
              <p className="text-lg font-bold text-black mt-1">{selectedOpp.scores.eligibility}%</p>
              <div className="bg-gray-200 h-1 rounded-full w-full mt-1.5 overflow-hidden">
                <div style={{ width: `${selectedOpp.scores.eligibility}%` }} className="bg-black h-full rounded-full" />
              </div>
            </div>

            <div className="bg-white/80 p-3 rounded-2xl border border-white shadow-sm">
              <span className="text-[11px] text-gray-500 font-medium">Project Relevance</span>
              <p className="text-lg font-bold text-black mt-1">{selectedOpp.scores.projectRelevance}%</p>
              <div className="bg-gray-200 h-1 rounded-full w-full mt-1.5 overflow-hidden">
                <div style={{ width: `${selectedOpp.scores.projectRelevance}%` }} className="bg-black h-full rounded-full" />
              </div>
            </div>

            <div className="bg-white/80 p-3 rounded-2xl border border-white shadow-sm">
              <span className="text-[11px] text-gray-500 font-medium">Preference Match</span>
              <p className="text-lg font-bold text-black mt-1">{selectedOpp.scores.preferenceMatch}%</p>
              <div className="bg-gray-200 h-1 rounded-full w-full mt-1.5 overflow-hidden">
                <div style={{ width: `${selectedOpp.scores.preferenceMatch}%` }} className="bg-black h-full rounded-full" />
              </div>
            </div>

            <div className="bg-white/80 p-3 rounded-2xl border border-white shadow-sm col-span-2 sm:col-span-1">
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-gray-500 font-medium">Trust Confidence</span>
                <ShieldCheck className="size-3 text-emerald-600" />
              </div>
              <p className="text-lg font-bold text-emerald-700 mt-1">{selectedOpp.scores.trustConfidence}</p>
              <p className="text-[10px] text-gray-500">Verified ({selectedOpp.scores.trustPercentage}%)</p>
            </div>
          </div>

          {/* AI Justification Panel */}
          <div className="bg-indigo-50/60 border border-indigo-100/80 rounded-2xl p-4 flex flex-col gap-2">
            <div className="flex items-center gap-1.5 text-xs font-bold text-black">
              <Sparkles className="size-3.5 text-indigo-600" />
              <span>AI Justification & Candidate Synergy</span>
            </div>
            <p className="text-xs text-gray-700 leading-relaxed">
              {selectedOpp.aiJustification}
            </p>
          </div>
        </div>

        {/* Right Queue Stream (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-3">
          <div className="flex items-center justify-between px-1 text-xs">
            <span className="text-gray-500 font-bold uppercase tracking-wider text-[11px]">
              UPCOMING DECISION QUEUE ({filteredOpportunities.length})
            </span>
            <span className="text-gray-500 font-medium">Sorted by Match ↓</span>
          </div>

          <div className="flex flex-col gap-2.5">
            {filteredOpportunities.map((opp) => {
              const isSelected = opp.id === selectedOpp.id;
              return (
                <div
                  key={opp.id}
                  onClick={() => setSelectedId(opp.id)}
                  className={`p-4 rounded-2xl transition-all duration-150 cursor-pointer ${
                    isSelected
                      ? 'bg-white border-2 border-black shadow-md'
                      : 'backdrop-blur-[14px] bg-[rgba(255,255,255,0.7)] border border-white hover:bg-white/90 shadow-sm'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-[10px] font-bold text-black uppercase tracking-wider">
                      {opp.tag}
                    </span>
                    <span className="text-xs font-bold text-black">
                      {opp.matchScore}% Match
                    </span>
                  </div>

                  <h4 className="text-sm font-bold text-black leading-tight">
                    {opp.title}
                  </h4>
                  <p className="text-xs text-gray-500 mb-2.5">
                    {opp.company} • {opp.compensation.split('+')[0].trim()}
                  </p>

                  <div className="border-t border-gray-100 pt-2 flex items-center justify-between text-[11px] text-gray-500">
                    <span>Prep: ~{opp.prepTimeHours} hrs</span>
                    <span className="font-semibold text-black">{opp.turnaroundLabel}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

