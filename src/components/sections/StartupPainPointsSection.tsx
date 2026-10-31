'use client';

import React, { useState } from 'react';
import {
  Flame,
  Search,
  DollarSign,
  Sparkles,
  ShieldCheck,
  Send,
  MessageSquare,
  Building,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  ExternalLink,
  Layers,
} from 'lucide-react';
import { StartupPainPointsData, PainPointItem } from '@/services/types';
import { mockStartupPainPointsData } from '@/services/mockData';
import { DashboardService } from '@/services/dashboardService';

export function StartupPainPointsSection() {
  const [data, setData] = useState<StartupPainPointsData>(mockStartupPainPointsData);
  const [selectedPoint, setSelectedPoint] = useState<PainPointItem>(mockStartupPainPointsData.painPoints[0]);
  const [dossierTab, setDossierTab] = useState<'overview' | 'quotes' | 'startups' | 'architecture'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('All Domains');
  const [solutionProposal, setSolutionProposal] = useState(
    'Edge streaming event broker utilizing Rust and zero-copy ring buffers. Decouples LLM token generation from synchronous vector DB search, reducing p95 latency from 14s to 1.8s.'
  );
  const [submittedNotice, setSubmittedNotice] = useState(false);

  const filteredPoints = data.painPoints.filter((pt) => {
    const matchesSearch =
      pt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pt.bottleneckAbstract.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pt.tags.some((t) => t.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!matchesSearch) return false;
    if (selectedDomain === 'Data Pipelines')
      return pt.tags.some((t) => ['PostgreSQL', 'Connection Pooling', 'Kafka'].includes(t));
    if (selectedDomain === 'B2B SaaS Operations')
      return pt.tags.some((t) => ['Multi-tenant', 'CI/CD'].includes(t));
    return true;
  });

  const handleSubmitProposal = async () => {
    await DashboardService.submitSolutionArchitecture(selectedPoint.id, solutionProposal);
    setSubmittedNotice(true);
    setTimeout(() => setSubmittedNotice(false), 3000);
  };

  return (
    <div className="flex flex-col gap-6 w-full select-none pb-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight flex items-center gap-2">
            <span>Startup Pain Points & Founder Bounties</span>
            <span className="bg-amber-100 text-amber-800 border border-amber-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full">
              Page 1 Spec
            </span>
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-xl mt-0.5">
            Verified technical bottlenecks extracted from Hacker News, Twitter, and YC founder communities with open bounty budgets.
          </p>
        </div>

        {/* Domain Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['All Domains', 'Data Pipelines', 'B2B SaaS Operations'].map((dom) => (
            <button
              key={dom}
              onClick={() => setSelectedDomain(dom)}
              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedDomain === dom
                  ? 'bg-black text-white shadow-sm'
                  : 'bg-white hover:bg-gray-100 text-[#46474b] border border-gray-200/80'
              }`}
            >
              {dom}
            </button>
          ))}
        </div>
      </div>

      {/* 4 Bento Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Cataloged Pain Points
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.catalogedPoints.count}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.metrics.catalogedPoints.delta} · {data.metrics.catalogedPoints.sources}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            High-Confidence Intel
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.highConfidence.count}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {data.metrics.highConfidence.conf} · {data.metrics.highConfidence.status}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Direct Founder Signals
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.directFounderSignals.count}
          </div>
          <div className="text-[11px] text-[#5d5e63] font-medium mt-1">
            {data.metrics.directFounderSignals.stages}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Open Bounties & Contracts
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.bountiesPool.count}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.metrics.bountiesPool.poolAmount} available
          </div>
        </div>
      </div>

      {/* Discrete Search Bar */}
      <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-3 sm:p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-2.5 size-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search bottlenecks or founders..."
            className="w-full pl-9 pr-3 py-1.5 bg-gray-50/80 hover:bg-gray-100/80 focus:bg-white border border-gray-200/80 rounded-full text-xs text-gray-900 placeholder-gray-400 outline-none focus:ring-2 focus:ring-black/10 transition-all"
          />
        </div>
        <div className="text-xs text-gray-400 hidden sm:block">
          Showing {filteredPoints.length} verified technical bottlenecks
        </div>
      </div>

      {/* Two-Column Split: Bottleneck Feed (Left) + Bottleneck Dossier (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Bottleneck Cards Feed */}
        <div className="lg:col-span-7 flex flex-col gap-3">
          {filteredPoints.map((pt) => {
            const isSelected = selectedPoint.id === pt.id;
            return (
              <div
                key={pt.id}
                onClick={() => setSelectedPoint(pt)}
                className={`bg-[rgba(255,255,255,0.92)] rounded-2xl p-5 border cursor-pointer transition-all duration-200 shadow-[0px_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md flex flex-col gap-3 ${
                  isSelected
                    ? 'border-black ring-1 ring-black/10 bg-white'
                    : 'border-[rgba(230,233,242,0.85)] hover:border-gray-300'
                }`}
              >
                {/* Header: Stage & Bounty */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="bg-rose-50 text-rose-700 border border-rose-200/70 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Flame className="size-3" />
                        <span>Confirmed Founder Pain</span>
                      </span>
                      <span className="text-xs text-gray-500 font-semibold">
                        {pt.companyStage} • {pt.scrapedAgo}
                      </span>
                    </div>
                    <h3 className="text-base sm:text-lg font-bold text-[#171c23] mt-1">
                      {pt.title}
                    </h3>
                  </div>

                  {pt.bountyAmount && (
                    <div className="text-right shrink-0">
                      <div className="inline-flex items-center gap-1 bg-emerald-500 text-white font-extrabold text-xs px-2.5 py-1 rounded-full shadow-sm">
                        <DollarSign className="size-3" />
                        <span>{pt.bountyAmount} Bounty</span>
                      </div>
                      <div className="text-[10px] text-gray-400 font-medium mt-0.5">
                        {pt.urgency}
                      </div>
                    </div>
                  )}
                </div>

                {/* Abstract */}
                <p className="text-xs text-gray-600 leading-relaxed line-clamp-2">
                  {pt.bottleneckAbstract}
                </p>

                {/* Badges: Match, Quotes, Companies */}
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  <span className="bg-emerald-50 text-emerald-800 border border-emerald-200 font-bold px-2 py-0.5 rounded-md text-[10px]">
                    {pt.matchScore}% Match
                  </span>
                  <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md text-[10px] font-medium">
                    {pt.verificationSource}
                  </span>
                  <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md text-[10px] font-medium">
                    {pt.founderQuotesCount} Founder Quotes
                  </span>
                  <span className="bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md text-[10px] font-medium">
                    {pt.companiesAffected} Startups Affected
                  </span>
                </div>

                {/* Card Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs">
                  <span className="text-[11px] text-gray-400">
                    {isSelected ? '● Currently Inspecting Dossier' : 'Click to inspect dossier'}
                  </span>
                  <span className="font-semibold text-gray-700 hover:text-black">
                    View Dossier →
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Bottleneck Dossier & Architecture Proposal Form */}
        <div className="lg:col-span-5 bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_24px_rgba(0,0,0,0.04)] sticky top-4 flex flex-col gap-4">
          {/* Dossier Header */}
          <div>
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-bold uppercase tracking-wider text-rose-600">
                VERIFIED CORE BOTTLENECK
              </span>
              <span className="bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold px-2 py-0.5 rounded-full">
                {selectedPoint.urgency}
              </span>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mt-1">{selectedPoint.title}</h3>
          </div>

          {/* Dossier Segmented Tabs */}
          <div className="flex items-center gap-2 border-b border-gray-200 pb-2 text-xs">
            {(['overview', 'quotes', 'startups', 'architecture'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setDossierTab(tab)}
                className={`font-semibold capitalize pb-1 transition-all ${
                  dossierTab === tab
                    ? 'text-black border-b-2 border-black'
                    : 'text-gray-400 hover:text-black'
                }`}
              >
                {tab === 'quotes' ? `Quotes (${selectedPoint.founderQuotesCount})` : tab}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {dossierTab === 'overview' && (
            <div className="flex flex-col gap-3 text-xs">
              <p className="text-gray-600 leading-relaxed">{selectedPoint.bottleneckAbstract}</p>

              {/* Founder Quote Evidence Box */}
              <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-col gap-2 shadow-md">
                <div className="flex items-center gap-1.5 text-amber-400 font-bold text-[10px] uppercase tracking-wider">
                  <MessageSquare className="size-3.5" />
                  <span>FOUNDER QUOTE EVIDENCE</span>
                </div>
                <blockquote className="text-xs text-gray-200 italic leading-relaxed">
                  &ldquo;{selectedPoint.founderQuote.quote}&rdquo;
                </blockquote>
                <div className="text-[11px] text-gray-400 font-semibold pt-1 border-t border-white/10 flex items-center justify-between">
                  <span>{selectedPoint.founderQuote.author}</span>
                  <span className="text-gray-500">{selectedPoint.founderQuote.source}</span>
                </div>
              </div>
            </div>
          )}

          {dossierTab === 'quotes' && (
            <div className="flex flex-col gap-2 text-xs">
              <div className="bg-gray-50 border border-gray-200 p-3 rounded-xl">
                <p className="italic text-gray-700">&ldquo;{selectedPoint.founderQuote.quote}&rdquo;</p>
                <div className="text-[10px] text-gray-500 mt-1 font-bold">
                  — {selectedPoint.founderQuote.author}
                </div>
              </div>
              <div className="bg-gray-50 border border-gray-200 p-3 rounded-xl">
                <p className="italic text-gray-700">
                  &ldquo;We rewrote our agent step parser 3 times. If anyone has solved non-blocking memory pooling for this, DM me immediately.&rdquo;
                </p>
                <div className="text-[10px] text-gray-500 mt-1 font-bold">
                  — CTO @ Stealth Series A Agent Studio
                </div>
              </div>
            </div>
          )}

          {dossierTab === 'startups' && (
            <div className="flex flex-col gap-2 text-xs">
              <div className="bg-gray-50 border border-gray-200 p-2.5 rounded-xl flex items-center justify-between">
                <span className="font-bold text-gray-900">Infra.ai (Series A)</span>
                <span className="text-emerald-700 font-bold">$25k Bounty Open</span>
              </div>
              <div className="bg-gray-50 border border-gray-200 p-2.5 rounded-xl flex items-center justify-between">
                <span className="font-bold text-gray-900">CognitiveLoops (Seed YC)</span>
                <span className="text-indigo-700 font-bold">Actively Hiring Lead</span>
              </div>
              <div className="bg-gray-50 border border-gray-200 p-2.5 rounded-xl flex items-center justify-between">
                <span className="font-bold text-gray-900">AgentFlow (Seed)</span>
                <span className="text-gray-600 font-medium">Bounty Scoped</span>
              </div>
            </div>
          )}

          {dossierTab === 'architecture' && (
            <div className="flex flex-col gap-2 text-xs">
              <div className="bg-indigo-50 border border-indigo-100 p-3 rounded-xl text-indigo-950">
                <div className="font-bold">Recommended Architecture Blueprint:</div>
                <div className="text-[11px] mt-1 text-indigo-900">
                  Deploy edge proxy with ring buffer queueing. Use Rust worker nodes with shared memory IPC to decouple token streaming from synchronous database queries.
                </div>
              </div>
            </div>
          )}

          {/* Interactive Solution Architecture Submission Form */}
          <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
            <label className="text-xs font-bold text-gray-900">
              Submit Solution Architecture & Claim Bounty:
            </label>
            <textarea
              rows={4}
              value={solutionProposal}
              onChange={(e) => setSolutionProposal(e.target.value)}
              className="w-full p-3 bg-white border border-gray-200 rounded-xl text-xs text-gray-800 outline-none focus:ring-2 focus:ring-black/10 resize-none"
            />
            <button
              onClick={handleSubmitProposal}
              className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              <Send className="size-3.5" />
              <span>
                {submittedNotice
                  ? 'Solution Architecture Submitted to Founder!'
                  : 'Submit Solution Architecture'}
              </span>
            </button>
            <p className="text-[10px] text-center text-gray-400">
              Direct submission to founder inbox with your Master Architecture Resume attached
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

