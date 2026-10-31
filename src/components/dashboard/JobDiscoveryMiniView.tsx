'use client';

import React, { useState } from 'react';
import {
  Compass,
  Sparkles,
  ShieldCheck,
  Send,
  MapPin,
  DollarSign,
  ArrowRight,
  ExternalLink,
  CheckCircle2,
} from 'lucide-react';
import { mockJobDiscoveryData } from '@/services/mockData';

interface JobDiscoveryMiniViewProps {
  onOpenFullSection: () => void;
}

export function JobDiscoveryMiniView({ onOpenFullSection }: JobDiscoveryMiniViewProps) {
  const [appliedId, setAppliedId] = useState<string | null>(null);

  const handleApply = (id: string) => {
    setAppliedId(id);
    setTimeout(() => setAppliedId(null), 2500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start pb-4">
      {/* Left 8 Cols: Top Semantic Radar Match Roles */}
      <div className="lg:col-span-8 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div className="flex items-center justify-between pb-2 border-b border-gray-100">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-[#171c23]">
                Top Calibrated Job Matches (Live Radar)
              </h3>
              <span className="bg-emerald-50 text-emerald-700 border border-emerald-200/60 rounded-full px-2 py-0.5 text-[10px] font-bold">
                Radar Active
              </span>
            </div>
            <p className="text-xs text-[#5d5e63] mt-0.5">
              Ranked by semantic vector similarity with candidate master resume.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3">
          {mockJobDiscoveryData.jobs.slice(0, 3).map((job) => (
            <div
              key={job.id}
              className="bg-white border border-gray-200/80 rounded-xl p-4 flex flex-col gap-2.5 shadow-sm hover:border-gray-300 transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                      {job.company}
                    </span>
                    {job.verifiedType === 'direct' && (
                      <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold px-1.5 py-0.2 rounded-md flex items-center gap-1">
                        <ShieldCheck className="size-2.5" />
                        <span>Direct Verified</span>
                      </span>
                    )}
                  </div>
                  <h4 className="text-sm font-bold text-gray-900 mt-0.5">{job.role}</h4>
                </div>

                <div className="inline-flex items-center gap-1 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-extrabold text-[11px] px-2.5 py-0.5 rounded-full shadow-sm shrink-0">
                  <Sparkles className="size-3" />
                  <span>{job.matchScore}% Match</span>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                <span className="flex items-center gap-1">
                  <MapPin className="size-3 text-gray-400" />
                  <span>{job.location}</span>
                </span>
                <span className="font-semibold text-emerald-700">
                  {job.salary}
                </span>
                <span className="text-gray-400">{job.postedAgo}</span>
              </div>

              {/* Skills */}
              <div className="flex flex-wrap gap-1">
                {job.skills.slice(0, 4).map((skill) => (
                  <span
                    key={skill}
                    className="text-[10px] bg-gray-100 text-gray-700 px-2 py-0.5 rounded-md font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs">
                <span className="text-[11px] text-gray-400">{job.summary.slice(0, 75)}...</span>
                <button
                  onClick={() => handleApply(job.id)}
                  className="bg-black hover:bg-gray-800 text-white font-semibold px-3 py-1 rounded-full text-xs shadow-sm transition-all flex items-center gap-1 shrink-0"
                >
                  <Send className="size-2.5" />
                  <span>{appliedId === job.id ? 'Dispatched!' : 'Quick Apply'}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right 4 Cols: Radar Telemetry & Full Suite Jump */}
      <div className="lg:col-span-4 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
            Radar Summary
          </div>
          <h4 className="text-base font-bold text-[#171c23] mt-0.5">
            48 Verified Openings
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">
            Real-time scraping across Greenhouse, Lever, Workday, and SEC Form D filings.
          </p>
        </div>

        {/* Telemetry Stats */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3 flex flex-col">
            <span className="text-[10px] font-bold text-gray-500 uppercase">New Today</span>
            <span className="text-xl font-extrabold text-[#171c23] mt-0.5">14 Roles</span>
            <span className="text-[10px] text-emerald-600 font-semibold mt-0.5">High signal</span>
          </div>

          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3 flex flex-col">
            <span className="text-[10px] font-bold text-gray-500 uppercase">Median Target</span>
            <span className="text-xl font-extrabold text-[#171c23] mt-0.5">$185k</span>
            <span className="text-[10px] text-emerald-600 font-semibold mt-0.5">+$20k over base</span>
          </div>
        </div>

        {/* Cryptographic Trust Callout */}
        <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-col gap-2 shadow-md">
          <div className="flex items-center gap-1.5 text-emerald-400 font-bold text-[10px] uppercase">
            <ShieldCheck className="size-3.5" />
            <span>DKIM Verified Headcounts</span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            All featured postings have verified DKIM email signatures from hiring managers with active Greenhouse requisition budgets.
          </p>
        </div>

        {/* Full Suite Jump CTA */}
        <button
          onClick={onOpenFullSection}
          className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2 group mt-1"
        >
          <span>Open Full Job Discovery Radar</span>
          <ArrowRight className="size-3.5 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
}

