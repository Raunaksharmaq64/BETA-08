'use client';

import React, { useState } from 'react';
import {
  Briefcase,
  Search,
  DollarSign,
  Clock,
  Sparkles,
  Send,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Flame,
  User,
  Copy,
  Check,
} from 'lucide-react';
import { FreelanceData, FreelanceLead } from '@/services/types';
import { mockFreelanceData } from '@/services/mockData';
import { DashboardService } from '@/services/dashboardService';

export function FreelanceFinderSection() {
  const [data, setData] = useState<FreelanceData>(mockFreelanceData);
  const [selectedLead, setSelectedLead] = useState<FreelanceLead>(mockFreelanceData.leads[0]);
  const [pitchText, setPitchText] = useState(mockFreelanceData.leads[0].draftedPitch);
  const [selectedCategory, setSelectedCategory] = useState('All Leads');
  const [pitchSentNotice, setPitchSentNotice] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleSelectLead = (lead: FreelanceLead) => {
    setSelectedLead(lead);
    setPitchText(lead.draftedPitch);
  };

  const handleSendPitch = async () => {
    const updated = await DashboardService.sendFreelancePitch(selectedLead.id, pitchText);
    setData({ ...updated });
    setPitchSentNotice(true);
    setTimeout(() => setPitchSentNotice(false), 3000);
  };

  const handleCopyPitch = () => {
    navigator.clipboard.writeText(pitchText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredLeads = data.leads.filter((lead) => {
    if (selectedCategory === 'All Leads') return true;
    if (selectedCategory === 'Infrastructure')
      return lead.tags.some((t) => ['AWS', 'Terraform', 'Multi-Region'].includes(t));
    if (selectedCategory === 'Distributed Systems')
      return lead.tags.some((t) => ['Redis Cluster', 'Go'].includes(t));
    if (selectedCategory === 'Performance Optimization')
      return lead.tags.some((t) => ['Playwright', 'Redis Cluster'].includes(t));
    return true;
  });

  return (
    <div className="flex flex-col gap-6 w-full select-none pb-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight flex items-center gap-2">
            <span>Freelance Finder & Architecture Sprints</span>
            <span className="bg-amber-100 text-amber-800 border border-amber-300 text-[11px] font-bold px-2.5 py-0.5 rounded-full">
              High-Bounty Sprints
            </span>
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-xl mt-0.5">
            Fractional consulting opportunities ($8k–$18k sprints) surfaced from founder distress signals, GitHub issues, and bottleneck discussions.
          </p>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['All Leads', 'Infrastructure', 'Distributed Systems', 'Performance Optimization'].map(
            (cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedCategory === cat
                    ? 'bg-black text-white shadow-sm'
                    : 'bg-white hover:bg-gray-100 text-[#46474b] border border-gray-200/80'
                }`}
              >
                {cat}
              </button>
            )
          )}
        </div>
      </div>

      {/* 4 Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Active Leads
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.activeLeads.count}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.metrics.activeLeads.badge}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Contact Ready
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.contactReady.count}
          </div>
          <div className="text-[11px] text-[#5d5e63] font-medium mt-1">
            {data.metrics.contactReady.label}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Pitches Sent
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.pitchesSent.count}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {data.metrics.pitchesSent.note}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Pipeline Value
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.metrics.pipelineValue.total}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.metrics.pipelineValue.sprintAvg}
          </div>
        </div>
      </div>

      {/* Main Split Workspace: Lead Feed (Left) + Action/Outreach Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Lead Cards */}
        <div className="lg:col-span-7 flex flex-col gap-3">
          {filteredLeads.map((lead) => {
            const isSelected = selectedLead.id === lead.id;
            return (
              <div
                key={lead.id}
                onClick={() => handleSelectLead(lead)}
                className={`bg-[rgba(255,255,255,0.92)] rounded-2xl p-5 border cursor-pointer transition-all duration-200 shadow-[0px_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md flex flex-col gap-3.5 ${
                  isSelected
                    ? 'border-black ring-1 ring-black/10 bg-white'
                    : 'border-[rgba(230,233,242,0.85)] hover:border-gray-300'
                }`}
              >
                {/* Header: Company & Stage */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                        {lead.company}
                      </span>
                      <span className="bg-gray-100 text-gray-700 text-[10px] font-semibold px-2 py-0.5 rounded-full border border-gray-200">
                        {lead.fundingStage}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5 flex items-center gap-1">
                      <User className="size-3 text-gray-400" />
                      <span>
                        {lead.contactName} ({lead.contactRole})
                      </span>
                    </div>
                  </div>

                  {/* Affinity Badge */}
                  <div className="text-right shrink-0">
                    <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-extrabold px-2.5 py-1 rounded-full shadow-sm flex items-center gap-1">
                      <Sparkles className="size-3" />
                      <span>{lead.affinityMatch}% Match</span>
                    </span>
                  </div>
                </div>

                {/* Key Data Badges (Budget, Timeframe) */}
                <div className="flex flex-wrap items-center gap-4 text-xs">
                  <div className="bg-emerald-50 border border-emerald-100 rounded-lg px-2.5 py-1 font-bold text-emerald-800 flex items-center gap-1">
                    <DollarSign className="size-3.5" />
                    <span>Estimated Budget: {lead.budget}</span>
                  </div>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg px-2.5 py-1 font-medium text-gray-700 flex items-center gap-1">
                    <Clock className="size-3.5 text-gray-400" />
                    <span>Timeframe: {lead.sprintDuration}</span>
                  </div>
                </div>

                {/* Problem Diagnosis Snippet */}
                <div className="bg-gray-50/80 border border-gray-200/60 rounded-xl p-3 text-xs text-gray-700 italic">
                  &ldquo;{lead.bottleneckSummary}&rdquo;
                </div>

                {/* Tags */}
                <div className="flex flex-wrap gap-1.5">
                  {lead.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] font-medium bg-gray-100 text-gray-600 px-2 py-0.5 rounded-md"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Card Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs">
                  <span className="text-[11px] text-gray-400">
                    Status: {lead.status === 'pitch_sent' ? '✓ Pitch Sent' : 'Contact Ready'}
                  </span>
                  <span className="font-semibold text-gray-700 hover:text-black">
                    Customize Pitch Proposal →
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Interactive Pitch Card & AI Outreach Panel */}
        <div className="lg:col-span-5 bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_24px_rgba(0,0,0,0.04)] sticky top-4 flex flex-col gap-4">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
                Outreach & Proposal Editor
              </span>
              <h3 className="text-lg font-bold text-gray-900 mt-0.5">
                Target: {selectedLead.contactName}
              </h3>
              <div className="text-xs text-gray-500">
                {selectedLead.contactRole} @ {selectedLead.company}
              </div>
            </div>

            <button
              onClick={handleCopyPitch}
              className="bg-white border border-gray-200 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-all flex items-center gap-1"
            >
              {copied ? <Check className="size-3 text-emerald-600" /> : <Copy className="size-3" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <div className="text-xs text-gray-600 bg-amber-50/60 border border-amber-200/60 rounded-xl p-3">
            <span className="font-bold text-amber-900">Detected Trigger: </span>
            {selectedLead.rawSignal}
          </div>

          {/* Editable Pitch Card */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-bold text-gray-700">
              Personalized Technical Teardown Proposal:
            </label>
            <textarea
              rows={9}
              value={pitchText}
              onChange={(e) => setPitchText(e.target.value)}
              className="w-full p-3.5 bg-white border border-gray-200 rounded-xl text-xs text-gray-900 leading-relaxed font-sans outline-none focus:ring-2 focus:ring-black/10 shadow-inner resize-y"
            />
          </div>

          {/* Deliverables Summary */}
          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3 text-xs flex flex-col gap-1">
            <div className="font-bold text-gray-800">Deliverables in Sprint:</div>
            <div className="text-gray-600 text-[11px]">
              • Comprehensive 3-page topology architecture audit & memory leak profiling
            </div>
            <div className="text-gray-600 text-[11px]">
              • Deployment of production hotfix with zero downtime SLA guarantee
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
            <button
              onClick={handleSendPitch}
              className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              <Send className="size-3.5" />
              <span>
                {pitchSentNotice ? 'Pitch Proposal Dispatched!' : 'Send Direct Technical Pitch'}
              </span>
            </button>
            <p className="text-[10px] text-center text-gray-400">
              Sent directly to {selectedLead.contactName.toLowerCase().replace(' ', '.')}@{selectedLead.company.toLowerCase().replace(' ', '')}.com via RightFit verified relay
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

