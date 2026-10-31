'use client';

import React, { useState } from 'react';
import {
  Compass,
  Search,
  ShieldCheck,
  CheckCircle2,
  Lock,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Send,
  Building,
  MapPin,
  DollarSign,
  Cpu,
  Layers,
  Zap,
} from 'lucide-react';
import { JobDiscoveryData, JobMatchCard } from '@/services/types';
import { mockJobDiscoveryData } from '@/services/mockData';

export function JobDiscoverySection() {
  const [data, setData] = useState<JobDiscoveryData>(mockJobDiscoveryData);
  const [selectedJob, setSelectedJob] = useState<JobMatchCard>(mockJobDiscoveryData.jobs[0]);
  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('All');
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [appliedNotice, setAppliedNotice] = useState<string | null>(null);

  const filteredJobs = data.jobs.filter((job) => {
    const matchesSearch =
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.skills.some((s) => s.toLowerCase().includes(searchQuery.toLowerCase()));

    if (!matchesSearch) return false;
    if (locationFilter !== 'All' && !job.location.includes(locationFilter)) return false;
    if (verifiedOnly && job.verifiedType !== 'direct') return false;
    return true;
  });

  const handleApply = (jobId: string) => {
    setAppliedNotice(jobId);
    setTimeout(() => setAppliedNotice(null), 3000);
  };

  return (
    <div className="flex flex-col gap-6 w-full select-none pb-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight flex items-center gap-2">
            <span>AI Job Discovery & Semantic Radar</span>
            <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 rounded-full px-2.5 py-0.5 text-[11px] font-bold">
              Radar Active
            </span>
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-xl mt-0.5">
            Real-time semantic matching with cryptographic verification of active recruiter headcounts and DKIM domain proofs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setVerifiedOnly(!verifiedOnly)}
            className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition-all flex items-center gap-1.5 border ${
              verifiedOnly
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
                : 'bg-white hover:bg-gray-50 text-gray-700 border-gray-200 shadow-sm'
            }`}
          >
            <ShieldCheck className="size-3.5" />
            <span>{verifiedOnly ? 'Showing Cryptographic Only' : 'Filter Cryptographic Direct'}</span>
          </button>
        </div>
      </div>

      {/* 4 Metric Bento Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Verified Matches
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.stats.verifiedMatches.count}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.stats.verifiedMatches.delta}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            New Today
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.stats.newToday.count}
          </div>
          <div className="text-[11px] text-[#5d5e63] font-medium mt-1">
            {data.stats.newToday.label}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Avg Match Score
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.stats.avgMatch.percentage}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {data.stats.avgMatch.note}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Median Salary Target
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {data.stats.medianSalary.amount}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {data.stats.medianSalary.delta}
          </div>
        </div>
      </div>

      {/* Discrete Multi-Filter Selector Bar */}
      <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-3 sm:p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-2.5 size-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search roles, tech stack (e.g. Distributed, Rust, Kubernetes)..."
            className="w-full pl-9 pr-3 py-1.5 bg-gray-50/80 hover:bg-gray-100/80 focus:bg-white border border-gray-200/80 rounded-full text-xs text-gray-900 placeholder-gray-400 outline-none focus:ring-2 focus:ring-black/10 transition-all"
          />
        </div>

        {/* Location Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['All', 'Remote', 'San Francisco', 'New York'].map((loc) => (
            <button
              key={loc}
              onClick={() => setLocationFilter(loc)}
              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                locationFilter === loc
                  ? 'bg-black text-white shadow-sm'
                  : 'bg-white hover:bg-gray-100 text-[#46474b] border border-gray-200/80'
              }`}
            >
              {loc}
            </button>
          ))}
        </div>
      </div>

      {/* Two-Column Asymmetric Viewport: Job Cards List + Deep Verification Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left 7-Cols: Job Matches Feed */}
        <div className="lg:col-span-7 flex flex-col gap-3">
          {filteredJobs.map((job) => {
            const isSelected = selectedJob.id === job.id;
            return (
              <div
                key={job.id}
                onClick={() => setSelectedJob(job)}
                className={`bg-[rgba(255,255,255,0.92)] rounded-2xl p-4 sm:p-5 border cursor-pointer transition-all duration-200 shadow-[0px_2px_12px_rgba(0,0,0,0.03)] hover:shadow-md flex flex-col gap-3 ${
                  isSelected
                    ? 'border-black ring-1 ring-black/10 bg-white'
                    : 'border-[rgba(230,233,242,0.85)] hover:border-gray-300'
                }`}
              >
                {/* Header: Company & Badges */}
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                        {job.company}
                      </span>
                      {job.verifiedType === 'direct' ? (
                        <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/70 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                          <ShieldCheck className="size-3" />
                          <span>Direct Verified</span>
                        </span>
                      ) : (
                        <span className="bg-gray-100 text-gray-700 border border-gray-200 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                          Public Requisition
                        </span>
                      )}
                    </div>
                    <h3 className="text-base sm:text-lg font-bold text-[#171c23] mt-0.5">
                      {job.role}
                    </h3>
                  </div>

                  {/* Match Score Badge */}
                  <div className="text-right shrink-0">
                    <div className="inline-flex items-center gap-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-extrabold text-xs px-2.5 py-1 rounded-full shadow-sm">
                      <Sparkles className="size-3" />
                      <span>{job.matchScore}% Match</span>
                    </div>
                    <div className="text-[10px] text-gray-400 font-medium mt-0.5">
                      {job.matchPercentile}
                    </div>
                  </div>
                </div>

                {/* Location & Compensation */}
                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                  <div className="flex items-center gap-1">
                    <MapPin className="size-3.5 text-gray-400" />
                    <span>{job.location}</span>
                  </div>
                  <div className="flex items-center gap-1 font-semibold text-emerald-700">
                    <DollarSign className="size-3.5" />
                    <span>{job.salary}</span>
                  </div>
                  <span className="text-gray-400">• {job.postedAgo}</span>
                </div>

                {/* Summary */}
                <p className="text-xs text-gray-600 leading-relaxed line-clamp-2">
                  {job.summary}
                </p>

                {/* Skills Overlap Chips */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {job.skills.map((skill) => (
                    <span
                      key={skill}
                      className="text-[10px] font-medium bg-gray-100/90 text-gray-700 border border-gray-200/70 px-2 py-0.5 rounded-md"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                {/* Actions Strip */}
                <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleApply(job.id);
                    }}
                    className="bg-black hover:bg-gray-800 text-white font-semibold px-4 py-1.5 rounded-full shadow-sm transition-all flex items-center gap-1.5"
                  >
                    <Send className="size-3" />
                    <span>{appliedNotice === job.id ? 'Dispatched!' : 'Quick Apply'}</span>
                  </button>
                  <span className="text-gray-400 text-[11px] font-medium">
                    Click to inspect cryptographic proof →
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right 5-Cols: Detail Preview Drawer & Trust Verification Intel */}
        <div className="lg:col-span-5 bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_24px_rgba(0,0,0,0.04)] sticky top-4 flex flex-col gap-5">
          {/* Selected Role Header */}
          <div>
            <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
              Selected Opportunity Dossier
            </div>
            <h3 className="text-xl font-extrabold text-[#171c23] mt-1">{selectedJob.role}</h3>
            <div className="text-sm font-semibold text-gray-600">{selectedJob.company}</div>
            <div className="text-xs font-bold text-emerald-700 mt-1">{selectedJob.salary}</div>
          </div>

          <div className="w-full h-px bg-gray-100" />

          {/* Cryptographic Verification Proof Card */}
          <div className="bg-slate-900 text-white rounded-2xl p-4 sm:p-5 flex flex-col gap-3.5 shadow-md">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Lock className="size-4 text-emerald-400" />
                <span className="text-xs font-bold tracking-wider uppercase text-emerald-400">
                  Cryptographic Verification Proof
                </span>
              </div>
              <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-400/30">
                100% Authentic
              </span>
            </div>

            <div className="flex flex-col gap-3 text-xs">
              {/* Step 1 */}
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="size-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-gray-200">DKIM Recruiter Signature</div>
                  <div className="text-[11px] text-gray-400 font-mono mt-0.5">
                    {selectedJob.dkimSignature}
                  </div>
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="size-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-gray-200">Live ATS Pipeline Sync</div>
                  <div className="text-[11px] text-gray-400 mt-0.5">
                    {selectedJob.atsSyncStatus}
                  </div>
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="size-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-gray-200">Funding & Capital Telemetry</div>
                  <div className="text-[11px] text-gray-400 mt-0.5">
                    {selectedJob.fundingTelemetry}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Role Architecture Brief */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold text-gray-900 uppercase tracking-wider">
              System Architecture Context:
            </span>
            <p className="text-xs text-gray-600 leading-relaxed">{selectedJob.summary}</p>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
            <button
              onClick={() => handleApply(selectedJob.id)}
              className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2"
            >
              <Send className="size-3.5" />
              <span>
                {appliedNotice === selectedJob.id
                  ? 'Application Dispatched with ATS Proof!'
                  : 'Dispatch Tailored Architecture Application'}
              </span>
            </button>
            <p className="text-[10px] text-center text-gray-400">
              Includes Alex Mercer ATS Proof (94.8% fit) + Cryptographic DKIM receipts
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

