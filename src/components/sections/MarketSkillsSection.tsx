'use client';

import React, { useState } from 'react';
import {
  TrendingUp,
  Cpu,
  Zap,
  Target,
  Award,
  ChevronRight,
  Layers,
  Sparkles,
  CheckCircle2,
  Clock,
  ArrowUpRight,
} from 'lucide-react';
import { MarketSkillsData, SkillArbitrageItem } from '@/services/types';
import { mockMarketSkillsData } from '@/services/mockData';

export function MarketSkillsSection() {
  const [marketData, setMarketData] = useState<MarketSkillsData>(mockMarketSkillsData);
  const [selectedSkill, setSelectedSkill] = useState<SkillArbitrageItem>(mockMarketSkillsData.skills[0]);

  return (
    <div className="flex flex-col gap-6 w-full select-none pb-8">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 w-full">
        <div>
          <h2 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-tight flex items-center gap-2">
            <span>Market & Skill Intelligence</span>
            <span className="bg-indigo-50 text-indigo-700 border border-indigo-200/60 rounded-full px-2.5 py-0.5 text-[11px] font-bold">
              Live Index
            </span>
          </h2>
          <p className="text-[#5d5e63] text-xs max-w-xl mt-0.5">
            Real-time telemetry on Staff/Principal compensation percentiles and skill arbitrage premiums across tier-1 distributed infrastructure companies.
          </p>
        </div>
      </div>

      {/* 4 Bento Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Market Base (P75)
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {marketData.metrics.marketBaseP75.value}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {marketData.metrics.marketBaseP75.delta}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Equity Median (4yr)
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {marketData.metrics.equityMedian.value}
          </div>
          <div className="text-[11px] text-[#5d5e63] font-medium mt-1">
            {marketData.metrics.equityMedian.label}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Top Skill Premium
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {marketData.metrics.topSkillPremium.value}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {marketData.metrics.topSkillPremium.skill}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Active Market Requisitions
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {marketData.metrics.activeDemand.value}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {marketData.metrics.activeDemand.location}
          </div>
        </div>
      </div>

      {/* Main Split: Compensation Percentiles & Skill Arbitrage Index */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column: Skill Arbitrage Index Table */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-[#171c23]">
                  Skill Arbitrage Index & Compensation Multipliers
                </h3>
                <p className="text-xs text-gray-500 mt-0.5">
                  High-leverage engineering capabilities that directly unlock top compensation bands.
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-2.5">
              {marketData.skills.map((skill) => {
                const isSelected = selectedSkill.id === skill.id;
                return (
                  <div
                    key={skill.id}
                    onClick={() => setSelectedSkill(skill)}
                    className={`rounded-xl p-3.5 border cursor-pointer transition-all duration-150 flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                      isSelected
                        ? 'bg-black text-white border-black shadow-md'
                        : 'bg-gray-50/70 hover:bg-gray-100/70 text-gray-900 border-gray-200/80'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`size-8 rounded-lg flex items-center justify-center shrink-0 ${
                          isSelected ? 'bg-white/20 text-white' : 'bg-white border border-gray-200 text-gray-700'
                        }`}
                      >
                        <Cpu className="size-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold">{skill.name}</div>
                        <div
                          className={`text-[11px] mt-0.5 ${
                            isSelected ? 'text-gray-300' : 'text-gray-500'
                          }`}
                        >
                          {skill.description}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 self-end sm:self-auto shrink-0">
                      <div className="text-right">
                        <div
                          className={`text-xs font-extrabold ${
                            isSelected ? 'text-emerald-300' : 'text-emerald-700'
                          }`}
                        >
                          {skill.premium}
                        </div>
                        <div
                          className={`text-[10px] ${
                            isSelected ? 'text-gray-300' : 'text-gray-400'
                          }`}
                        >
                          {skill.growthYoY} YoY
                        </div>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                          skill.userStatus === 'Mastered'
                            ? isSelected
                              ? 'bg-emerald-500/20 text-emerald-200 border-emerald-400/40'
                              : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : skill.userStatus === 'In Progress'
                            ? isSelected
                              ? 'bg-amber-500/20 text-amber-200 border-amber-400/40'
                              : 'bg-amber-50 text-amber-700 border-amber-200'
                            : isSelected
                            ? 'bg-indigo-500/20 text-indigo-200 border-indigo-400/40'
                            : 'bg-indigo-50 text-indigo-700 border-indigo-200'
                        }`}
                      >
                        {skill.userStatus}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Structured Milestones Timeline (Upskilling Roadmap) */}
          <div className="bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
            <div>
              <h3 className="text-base font-bold text-[#171c23]">
                Candidate Upskilling Roadmap (P90 Target)
              </h3>
              <p className="text-xs text-gray-500 mt-0.5">
                Targeted technical sprints to push your profile into the $255k+ compensation tier.
              </p>
            </div>

            <div className="flex flex-col gap-3">
              {marketData.roadmap.map((milestone) => (
                <div
                  key={milestone.step}
                  className="bg-gray-50/80 border border-gray-200/80 rounded-xl p-3.5 flex flex-col gap-1.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-indigo-600 bg-indigo-50 border border-indigo-100 px-2 py-0.5 rounded-md">
                      {milestone.duration}
                    </span>
                    <span className="text-xs font-semibold text-gray-400">Step {milestone.step}</span>
                  </div>
                  <h4 className="text-xs font-bold text-gray-900">{milestone.title}</h4>
                  <p className="text-[11px] text-gray-600">{milestone.description}</p>
                  <div className="text-[11px] text-gray-800 bg-white p-2 rounded-lg border border-gray-200 mt-1">
                    <span className="font-semibold text-gray-900">Verification Goal: </span>
                    {milestone.actionItem}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Compensation Percentile Visualizer */}
        <div className="lg:col-span-5 bg-[rgba(255,255,255,0.92)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-5 sticky top-4">
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
              Salary Percentiles
            </span>
            <h3 className="text-lg font-bold text-gray-900 mt-0.5">
              Staff Distributed Systems Base
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">
              Calibration across tier-1 venture-backed tech and hyperscalers.
            </p>
          </div>

          {/* Interactive CSS Bar Visualization */}
          <div className="bg-gray-50/90 border border-gray-200/80 rounded-2xl p-5 flex flex-col gap-4">
            <div className="h-44 flex items-end justify-between gap-3 px-2 pt-4">
              {marketData.percentiles.map((p) => {
                const isTarget = p.label.includes('Target');
                return (
                  <div key={p.label} className="flex-1 flex flex-col items-center gap-2 h-full justify-end">
                    <div className="text-[11px] font-extrabold text-[#171c23]">{p.amount}</div>
                    <div
                      style={{ height: `${p.height}%` }}
                      className={`w-full rounded-t-xl transition-all duration-500 ${
                        isTarget
                          ? 'bg-gradient-to-t from-emerald-600 to-teal-400 shadow-md'
                          : 'bg-gray-300 hover:bg-gray-400'
                      }`}
                    />
                    <div
                      className={`text-[10px] font-bold text-center leading-tight truncate w-full ${
                        isTarget ? 'text-emerald-700' : 'text-gray-500'
                      }`}
                    >
                      {p.label}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="text-xs text-gray-600 bg-white p-3 rounded-xl border border-gray-200/80 flex items-center justify-between">
              <span>Your Current Calibrated Target:</span>
              <span className="font-extrabold text-[#171c23] text-sm">$215k Base + Equity</span>
            </div>
          </div>

          {/* Selected Skill Deep Dive Card */}
          <div className="bg-slate-900 text-white rounded-2xl p-4 flex flex-col gap-2.5 shadow-md">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
                Selected Arbitrage Focus
              </span>
              <span className="text-xs font-bold text-emerald-300">{selectedSkill.premium}</span>
            </div>
            <h4 className="text-sm font-bold text-white">{selectedSkill.name}</h4>
            <p className="text-xs text-gray-300 leading-relaxed">{selectedSkill.description}</p>
            <div className="flex items-center justify-between pt-2 border-t border-white/10 text-xs">
              <span className="text-gray-400">Market Demand: {selectedSkill.demandLevel}</span>
              <span className="text-emerald-300 font-semibold">Status: {selectedSkill.userStatus}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

