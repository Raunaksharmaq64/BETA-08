'use client';

import React from 'react';
import {
  Briefcase,
  Trophy,
  Clock,
  Mail,
  ArrowRight,
  Sparkles,
  ChevronRight,
  AlertCircle,
} from 'lucide-react';
import { mockApplicationCRMData } from '@/services/mockData';

interface ApplicationCRMMiniViewProps {
  onOpenFullSection: () => void;
}

export function ApplicationCRMMiniView({ onOpenFullSection }: ApplicationCRMMiniViewProps) {
  const spotlightCards = mockApplicationCRMData.cards.filter(
    (c) => c.stage === 'offer' || c.stage === 'interview'
  );

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start pb-4">
      {/* Left 8 Cols: Pipeline Progression Strip & Active Spotlight Applications */}
      <div className="lg:col-span-8 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-5">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-[#171c23]">
              Application Pipeline Progression (18 Active)
            </h3>
            <span className="bg-indigo-50 text-indigo-700 border border-indigo-200/60 rounded-full px-2 py-0.5 text-[10px] font-bold">
              Kanban Live
            </span>
          </div>
          <p className="text-xs text-[#5d5e63] mt-0.5">
            Stage distribution and active recruiter interview rounds.
          </p>
        </div>

        {/* Horizontal Pipeline Progression Bar */}
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
          {[
            { stage: 'Saved', count: 4, color: 'border-slate-300 text-slate-700 bg-slate-50/60' },
            { stage: 'Ready', count: 2, color: 'border-sky-300 text-sky-700 bg-sky-50/60' },
            { stage: 'Applied', count: 5, color: 'border-amber-300 text-amber-700 bg-amber-50/60' },
            { stage: 'Assessment', count: 3, color: 'border-purple-300 text-purple-700 bg-purple-50/60' },
            { stage: 'Interview', count: 3, color: 'border-indigo-400 text-indigo-700 bg-indigo-50/70 font-bold' },
            { stage: 'Offer', count: 1, color: 'border-amber-400 text-amber-800 bg-amber-500/10 font-bold' },
          ].map((item) => (
            <div
              key={item.stage}
              className={`rounded-xl p-2.5 border flex flex-col items-center justify-center text-center ${item.color}`}
            >
              <span className="text-[10px] uppercase font-bold tracking-wider">{item.stage}</span>
              <span className="text-lg font-extrabold mt-0.5">{item.count}</span>
            </div>
          ))}
        </div>

        {/* Spotlight Cards (Offer & Round 3 Datadog) */}
        <div className="flex flex-col gap-3">
          <div className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
            High Priority Active Focus:
          </div>

          {spotlightCards.map((card) => {
            const isOffer = card.stage === 'offer';
            return (
              <div
                key={card.id}
                className={`rounded-2xl p-4 border flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm transition-all ${
                  isOffer
                    ? 'bg-gradient-to-r from-amber-500/15 via-amber-500/5 to-transparent border-amber-300/80 shadow-[0px_4px_20px_rgba(245,158,11,0.08)]'
                    : 'bg-white border-gray-200/80 hover:border-gray-300'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div
                    className={`size-9 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 ${
                      isOffer ? 'bg-amber-500 text-white shadow-md' : 'bg-indigo-50 text-indigo-700 border border-indigo-100'
                    }`}
                  >
                    {isOffer ? <Trophy className="size-4" /> : card.company.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-gray-500 uppercase">{card.company}</span>
                      <span
                        className={`text-[10px] font-bold px-2 py-0.2 rounded-full ${
                          isOffer
                            ? 'bg-amber-500 text-white'
                            : 'bg-indigo-100 text-indigo-800'
                        }`}
                      >
                        {isOffer ? 'OFFER RECEIVED' : card.dateAdded}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-gray-900 mt-0.5">{card.role}</h4>
                    {card.roundDetails && (
                      <div className="text-xs text-indigo-700 font-medium flex items-center gap-1 mt-1">
                        <Clock className="size-3 text-indigo-500" />
                        <span>{card.roundDetails}</span>
                      </div>
                    )}
                    {isOffer && (
                      <div className="text-xs text-emerald-800 font-bold mt-1">
                        {card.salary} · {card.equity}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                  <button
                    onClick={onOpenFullSection}
                    className="text-xs font-semibold text-gray-700 hover:text-black flex items-center gap-1"
                  >
                    <span>View Kanban Card</span>
                    <ChevronRight className="size-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Right 4 Cols: Recruiter Live Sync & Full CRM Jump */}
      <div className="lg:col-span-4 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-gray-400">
            Pipeline Health
          </div>
          <h4 className="text-base font-bold text-[#171c23] mt-0.5">
            Recruiter Live Feed
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">
            Real-time status updates parsed automatically from incoming recruiter emails.
          </p>
        </div>

        {/* Sync Status Banner */}
        <div className="bg-emerald-50/80 border border-emerald-200/70 rounded-2xl p-4 flex items-start gap-3">
          <Mail className="size-4 text-emerald-600 shrink-0 mt-0.5" />
          <div className="text-xs text-emerald-900">
            <div className="font-bold">IMAP Sync Connected</div>
            <div className="text-[11px] text-emerald-800 mt-0.5">
              4 recruiter messages parsed from Datadog, Anthropic, Linear, and Cursor today.
            </div>
          </div>
        </div>

        {/* Conversion Rate Card */}
        <div className="bg-gray-50 border border-gray-200/80 rounded-xl p-3.5 flex flex-col gap-2">
          <div className="flex justify-between items-center text-xs">
            <span className="font-semibold text-gray-700">Recruiter Response Rate</span>
            <span className="font-extrabold text-indigo-600">42%</span>
          </div>
          <div className="text-[11px] text-gray-500">
            Industry benchmark is 18%. Your profile achieves 2.3x higher screening conversion.
          </div>
        </div>

        {/* Full Suite Jump CTA */}
        <button
          onClick={onOpenFullSection}
          className="w-full bg-black hover:bg-gray-800 text-white font-bold py-2.5 rounded-full text-xs shadow-md transition-all flex items-center justify-center gap-2 group mt-1"
        >
          <span>Open Full Application CRM Board</span>
          <ArrowRight className="size-3.5 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </div>
  );
}

