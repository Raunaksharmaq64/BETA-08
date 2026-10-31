'use client';

import React from 'react';
import {
  Flame,
  DollarSign,
  MessageSquare,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Send,
} from 'lucide-react';
import { mockStartupPainPointsData } from '@/services/mockData';

interface StartupPainPointsMiniViewProps {
  onOpenFullSection: () => void;
}

export function StartupPainPointsMiniView({ onOpenFullSection }: StartupPainPointsMiniViewProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start pb-4">
      {/* Left 8 Cols: Top Verified Founder Bottlenecks */}
      <div className="lg:col-span-8 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-[#171c23]">
              Startup Pain Points & Verified Founder Bounties
            </h3>
            <span className="bg-rose-50 text-rose-700 border border-rose-200/60 rounded-full px-2 py-0.5 text-[10px] font-bold">
              Page 1 Spec
            </span>
          </div>
          <p className="text-xs text-[#5d5e63] mt-0.5">
            Technical bottlenecks scraped directly from Hacker News, Twitter, and YC founders.
          </p>
        </div>

        <div className="flex flex-col gap-3">
          {mockStartupPainPointsData.painPoints.slice(0, 2).map((pt) => (
            <div
              key={pt.id}
              className="bg-white border border-gray-200/80 rounded-2xl p-4 flex flex-col gap-3 shadow-sm hover:border-gray-300 transition-all"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold px-2 py-0.2 rounded-full flex items-center gap-1">
                      <Flame className="size-2.5" />
                      <span>Confirmed Pain</span>
                    </span>
                    <span className="text-xs text-gray-500 font-semibold">{pt.companyStage}</span>
                  </div>
                  <h4 className="text-sm font-bold text-gray-900 mt-1">{pt.title}</h4>
                </div>

                {pt.bountyAmount && (
                  <div className="bg-emerald-50 text-emerald-800 border border-emerald-200 font-extrabold text-xs px-2.5 py-1 rounded-full shadow-sm shrink-0 flex items-center gap-1">
                    <DollarSign className="size-3" />
                    <span>{pt.bountyAmount} Bounty</span>
                  </div>
                )}
              </div>

              <p className="text-xs text-gray-600 leading-relaxed line-clamp-2">
                {pt.bottleneckAbstract}
              </p>

              {/* Founder Quote Evidence Mini Snippet */}
              <div className="bg-slate-900 text-white rounded-xl p-3 flex flex-col gap-1 text-xs shadow-inner">
                <div className="flex items-center gap-1 text-[10px] text-amber-400 font-bold uppercase">
                  <MessageSquare className="size-3" />
                  <span>Founder Quote Evidence:</span>
                </div>
                <blockquote className="text-gray-300 italic text-[11px] leading-relaxed">
                  &ldquo;{pt.founderQuote.quote.slice(0, 140)}...&rdquo;
                </blockquote>
                <div className="text-[10px] text-gray-400 pt-1 border-t border-white/10">
                  — {pt.founderQuote.author}
                </div>
              </div>

              <div className="flex items-center justify-between pt-1 border-t border-gray-100 text-xs">
                <div className="flex gap-1.5">
                  {pt.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-md font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
                <button
                  onClick={onOpenFullSection}
                  className="font-bold text-gray-900 hover:text-black flex items-center gap-1 text-xs"
                >
                  <span>Submit Solution Architecture →</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right 4 Cols: Bounties Pool & Full Feed Jump */}
      <div className="lg:col-span-4 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
            Founder Bounties Pool
          </div>
          <h4 className="text-base font-bold text-[#171c23] mt-0.5">
            $145,000 Open Budget
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">
            Direct consulting and solution bounty contracts available for claim.
          </p>
        </div>

        {/* Pool Metrics Card */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3 flex flex-col">
            <span className="text-[10px] font-bold text-gray-500 uppercase">Cataloged</span>
            <span className="text-xl font-extrabold text-[#171c23] mt-0.5">128 Points</span>
            <span className="text-[10px] text-emerald-600 font-semibold mt-0.5">+18% growth</span>
          </div>

          <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3 flex flex-col">
            <span className="text-[10px] font-bold text-gray-500 uppercase">High Conf</span>
            <span className="text-xl font-extrabold text-[#171c23] mt-0.5">42 Issues</span>
            <span className="text-[10px] text-indigo-600 font-semibold mt-0.5">+92% confidence</span>
          </div>
        </div>

        {/* Consulting Alert */}
        <div className="bg-amber-50/70 border border-amber-200/60 rounded-xl p-3.5 text-xs text-amber-950 flex flex-col gap-1">
          <div className="font-bold flex items-center gap-1.5 text-amber-900">
            <Sparkles className="size-3.5 text-amber-600" />
            <span>High-Bounty Advisory</span>
          </div>
          <p className="text-[11px] text-amber-900/90 leading-relaxed">
            Startups with open bounties prioritize candidate architects who submit an initial 1-page solution memo before formal interview loops.
          </p>
        </div>

        {/* Full Suite Jump CTA */}
        <button
          onClick={onOpenFullSection}
          className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2 group mt-1"
        >
          <span>Open Full Startup Pain Points Feed</span>
          <ArrowRight className="size-3.5 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
}

