'use client';

import React, { useState } from 'react';
import {
  Briefcase,
  Search,
  Filter,
  ArrowRight,
  CheckCircle,
  Clock,
  Sparkles,
  Trophy,
  Mail,
  ChevronRight,
  ExternalLink,
  Plus,
  AlertCircle,
  Check,
} from 'lucide-react';
import { ApplicationCRMData, KanbanCard } from '@/services/types';
import { mockApplicationCRMData } from '@/services/mockData';
import { DashboardService } from '@/services/dashboardService';

export function ApplicationCRMSection() {
  const [crmData, setCrmData] = useState<ApplicationCRMData>(mockApplicationCRMData);
  const [filterText, setFilterText] = useState('');
  const [selectedTag, setSelectedTag] = useState<string>('All');
  const [activeView, setActiveView] = useState<'board' | 'list'>('board');
  const [syncNotice, setSyncNotice] = useState(false);
  const [selectedCard, setSelectedCard] = useState<KanbanCard | null>(null);

  const stages: { id: KanbanCard['stage']; label: string; count: number; accent: string }[] = [
    {
      id: 'saved',
      label: 'SAVED',
      count: crmData.cards.filter((c) => c.stage === 'saved').length,
      accent: 'border-slate-300 text-slate-700',
    },
    {
      id: 'ready',
      label: 'READY TO APPLY',
      count: crmData.cards.filter((c) => c.stage === 'ready').length,
      accent: 'border-sky-300 text-sky-700',
    },
    {
      id: 'applied',
      label: 'APPLIED',
      count: crmData.cards.filter((c) => c.stage === 'applied').length,
      accent: 'border-amber-300 text-amber-700',
    },
    {
      id: 'assessment',
      label: 'ASSESSMENT',
      count: crmData.cards.filter((c) => c.stage === 'assessment').length,
      accent: 'border-purple-300 text-purple-700',
    },
    {
      id: 'interview',
      label: 'INTERVIEW STAGE',
      count: crmData.cards.filter((c) => c.stage === 'interview').length,
      accent: 'border-indigo-400 text-indigo-700',
    },
    {
      id: 'offer',
      label: 'OFFER RECEIVED',
      count: crmData.cards.filter((c) => c.stage === 'offer').length,
      accent: 'border-amber-400 text-amber-800 bg-amber-50/40',
    },
  ];

  const handleStageMove = async (cardId: string, nextStage: KanbanCard['stage']) => {
    const updated = await DashboardService.updateCardStage(cardId, nextStage);
    setCrmData({ ...updated });
    if (selectedCard && selectedCard.id === cardId) {
      setSelectedCard({ ...selectedCard, stage: nextStage });
    }
  };

  const filteredCards = crmData.cards.filter((c) => {
    const matchSearch =
      c.company.toLowerCase().includes(filterText.toLowerCase()) ||
      c.role.toLowerCase().includes(filterText.toLowerCase()) ||
      c.tags.some((t) => t.toLowerCase().includes(filterText.toLowerCase()));

    if (!matchSearch) return false;
    if (selectedTag === 'All') return true;
    if (selectedTag === 'Urgent') return c.priority === 'urgent';
    return c.tags.includes(selectedTag);
  });

  return (
    <div className="flex flex-col gap-5 w-full select-none pb-8">
      {/* Top Banner / Gmail Live Sync Header */}
      <div className="bg-gradient-to-r from-[#171c23] via-[#232936] to-[#171c23] text-white rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg border border-white/10">
        <div className="flex items-start sm:items-center gap-3.5">
          <div className="size-10 rounded-xl bg-emerald-500/20 border border-emerald-400/40 flex items-center justify-center shrink-0">
            <Mail className="size-5 text-emerald-400 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm sm:text-base font-bold tracking-tight text-white">
                Recruiter Sync Active
              </h3>
              <span className="bg-emerald-400/20 border border-emerald-400/30 text-emerald-300 text-[10px] font-semibold px-2 py-0.5 rounded-full">
                Live IMAP Feed
              </span>
            </div>
            <p className="text-gray-300 text-xs mt-0.5">
              4 recruiter status updates parsed automatically from Datadog, Anthropic, Linear, and Cursor.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => {
              setSyncNotice(true);
              setTimeout(() => setSyncNotice(false), 2000);
            }}
            className="bg-white/10 hover:bg-white/20 border border-white/20 text-white rounded-full px-4 py-1.5 text-xs font-semibold transition-all shadow-sm flex items-center gap-1.5"
          >
            <Sparkles className="size-3.5 text-amber-300" />
            <span>{syncNotice ? 'Synced Just Now' : 'Sync Inboxes'}</span>
          </button>
        </div>
      </div>

      {/* 4 Metric Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Total Active Applications
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {crmData.stats.totalActive.value}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
            <span>↑</span>
            <span>{crmData.stats.totalActive.delta}</span>
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Recruiter Response Rate
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {crmData.stats.responseRate.value}
          </div>
          <div className="text-[11px] text-[#5d5e63] font-medium mt-1">
            {crmData.stats.responseRate.benchmark}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Interview Conversion
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {crmData.stats.interviewConversion.value}
          </div>
          <div className="text-[11px] text-indigo-600 font-semibold mt-1">
            {crmData.stats.interviewConversion.rating}
          </div>
        </div>

        <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col">
          <div className="text-[11px] font-semibold text-[#5d5e63] uppercase tracking-wider">
            Pending Follow-ups
          </div>
          <div className="text-2xl sm:text-3xl font-extrabold text-[#171c23] tracking-tight mt-1">
            {crmData.stats.pendingFollowUps.value}
          </div>
          <div className="text-[11px] text-amber-700 font-semibold mt-1 flex items-center gap-1">
            <span className="size-1.5 rounded-full bg-amber-500 animate-ping" />
            <span>{crmData.stats.pendingFollowUps.badge}</span>
          </div>
        </div>
      </div>

      {/* View Controls & Filter Strip */}
      <div className="bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-3 sm:p-4 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-2.5 size-4 text-gray-400" />
          <input
            type="text"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Filter company, role, tag..."
            className="w-full pl-9 pr-3 py-1.5 bg-gray-50/80 hover:bg-gray-100/80 focus:bg-white border border-gray-200/80 rounded-full text-xs text-gray-900 placeholder-gray-400 outline-none focus:ring-2 focus:ring-black/10 transition-all"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          {['All', 'Urgent', 'Rust', 'PostgreSQL', 'Distributed'].map((tag) => (
            <button
              key={tag}
              onClick={() => setSelectedTag(tag)}
              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap transition-all ${
                selectedTag === tag
                  ? 'bg-black text-white shadow-sm'
                  : 'bg-white hover:bg-gray-100 text-[#46474b] border border-gray-200/80'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1 bg-gray-100/80 p-1 rounded-full border border-gray-200/60 self-start sm:self-auto">
          <button
            onClick={() => setActiveView('board')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              activeView === 'board' ? 'bg-white text-black shadow-sm' : 'text-gray-500 hover:text-black'
            }`}
          >
            Board
          </button>
          <button
            onClick={() => setActiveView('list')}
            className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
              activeView === 'list' ? 'bg-white text-black shadow-sm' : 'text-gray-500 hover:text-black'
            }`}
          >
            List
          </button>
        </div>
      </div>

      {/* FULL KANBAN PIPELINE BOARD */}
      {activeView === 'board' ? (
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-4 min-w-[1240px] items-start">
            {stages.map((stage) => {
              const cardsInStage = filteredCards.filter((c) => c.stage === stage.id);
              const isOfferStage = stage.id === 'offer';
              const isInterviewStage = stage.id === 'interview';

              return (
                <div
                  key={stage.id}
                  className={`flex-1 min-w-[210px] rounded-2xl flex flex-col gap-3 p-3 transition-colors ${
                    isOfferStage
                      ? 'bg-gradient-to-b from-amber-500/10 via-amber-500/5 to-transparent border border-amber-300/80 shadow-[0px_4px_24px_rgba(245,158,11,0.12)]'
                      : isInterviewStage
                      ? 'bg-indigo-50/50 border border-indigo-200/70 shadow-[0px_4px_20px_rgba(99,102,241,0.06)]'
                      : 'bg-[rgba(248,249,252,0.85)] border border-[rgba(230,233,242,0.8)]'
                  }`}
                >
                  {/* Column Header */}
                  <div className="flex items-center justify-between px-1 pb-1 border-b border-gray-200/50">
                    <div className="flex items-center gap-2">
                      <span className="text-[11px] font-bold tracking-wider text-[#171c23]">
                        {stage.label}
                      </span>
                      {isOfferStage && <Trophy className="size-3.5 text-amber-600 animate-bounce" />}
                    </div>
                    <span className="text-[11px] font-semibold bg-white/90 border border-gray-200 px-2 py-0.5 rounded-full text-[#46474b]">
                      {cardsInStage.length}
                    </span>
                  </div>

                  {/* Cards List in Column */}
                  <div className="flex flex-col gap-2.5">
                    {cardsInStage.length === 0 ? (
                      <div className="py-8 text-center text-xs text-gray-400 border border-dashed border-gray-200 rounded-xl">
                        No applications
                      </div>
                    ) : (
                      cardsInStage.map((card) => {
                        const isUrgent = card.priority === 'urgent';
                        return (
                          <div
                            key={card.id}
                            onClick={() => setSelectedCard(card)}
                            className={`rounded-xl p-3.5 flex flex-col gap-2 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 select-none ${
                              isOfferStage
                                ? 'bg-gradient-to-br from-amber-500 to-amber-600 text-white shadow-lg border border-amber-400'
                                : 'bg-white border border-gray-200/80 hover:border-gray-300 shadow-[0px_2px_8px_rgba(0,0,0,0.04)] hover:shadow-md'
                            }`}
                          >
                            {/* Card Top Row: Company & Priority */}
                            <div className="flex items-start justify-between gap-2">
                              <span
                                className={`text-[11px] font-bold uppercase tracking-wider ${
                                  isOfferStage ? 'text-amber-100' : 'text-gray-500'
                                }`}
                              >
                                {card.company}
                              </span>
                              {isUrgent && !isOfferStage && (
                                <span className="bg-rose-50 text-rose-700 border border-rose-200 text-[10px] font-bold px-1.5 py-0.2 rounded-md">
                                  Urgent
                                </span>
                              )}
                              {isOfferStage && (
                                <span className="bg-amber-300 text-black text-[10px] font-extrabold px-2 py-0.5 rounded-full shadow-sm">
                                  Top Match
                                </span>
                              )}
                            </div>

                            {/* Card Role */}
                            <h4
                              className={`text-xs font-bold leading-snug line-clamp-2 ${
                                isOfferStage ? 'text-white text-sm' : 'text-[#171c23]'
                              }`}
                            >
                              {card.role}
                            </h4>

                            {/* Compensation or Offer Breakdown */}
                            {card.salary && (
                              <div
                                className={`text-[11px] font-semibold ${
                                  isOfferStage ? 'text-amber-100 font-bold' : 'text-emerald-700'
                                }`}
                              >
                                {card.salary}
                              </div>
                            )}

                            {isOfferStage && (
                              <div className="bg-black/20 rounded-lg p-2 text-[10px] flex flex-col gap-0.5 border border-amber-300/30">
                                <div>{card.equity}</div>
                                <div>{card.signOn}</div>
                              </div>
                            )}

                            {/* Round Details for Interview Stage */}
                            {card.roundDetails && (
                              <div className="bg-indigo-50 border border-indigo-100 rounded-lg p-2 text-[11px] text-indigo-900 font-medium flex items-center gap-1.5">
                                <Clock className="size-3 text-indigo-600 shrink-0" />
                                <span className="truncate">{card.roundDetails}</span>
                              </div>
                            )}

                            {/* Tags */}
                            <div className="flex flex-wrap gap-1 mt-1">
                              {card.tags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className={`text-[9px] font-medium px-2 py-0.5 rounded-md ${
                                    isOfferStage
                                      ? 'bg-amber-700/60 text-white'
                                      : 'bg-gray-100 text-gray-600'
                                  }`}
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>

                            {/* Card Footer: Added Time + Quick Stage Advance */}
                            <div
                              className={`flex items-center justify-between text-[10px] pt-1.5 border-t ${
                                isOfferStage
                                  ? 'border-amber-400/40 text-amber-200'
                                  : 'border-gray-100 text-gray-400'
                              }`}
                            >
                              <span>{card.dateAdded}</span>
                              <div className="flex items-center gap-1 font-semibold text-gray-700 hover:text-black">
                                <span className={isOfferStage ? 'text-white' : ''}>Inspect</span>
                                <ChevronRight className="size-3" />
                              </div>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        /* List View */
        <div className="bg-white border border-gray-200/80 rounded-2xl overflow-hidden shadow-sm">
          <div className="grid grid-cols-12 gap-3 px-5 py-3 bg-gray-50/80 border-b border-gray-200 text-[11px] font-bold text-gray-600 uppercase tracking-wider">
            <div className="col-span-4">Company & Role</div>
            <div className="col-span-2">Stage</div>
            <div className="col-span-3">Compensation / Focus</div>
            <div className="col-span-2">Date Added</div>
            <div className="col-span-1 text-right">Action</div>
          </div>
          <div className="divide-y divide-gray-100">
            {filteredCards.map((card) => (
              <div
                key={card.id}
                onClick={() => setSelectedCard(card)}
                className="grid grid-cols-12 gap-3 px-5 py-3.5 items-center hover:bg-gray-50/80 cursor-pointer transition-colors"
              >
                <div className="col-span-4 flex flex-col">
                  <span className="text-xs font-bold text-gray-900">{card.company}</span>
                  <span className="text-xs text-gray-600 truncate">{card.role}</span>
                </div>
                <div className="col-span-2">
                  <span className="inline-block px-2.5 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider bg-gray-100 text-gray-700 border border-gray-200">
                    {card.stage}
                  </span>
                </div>
                <div className="col-span-3 text-xs font-semibold text-emerald-700">
                  {card.salary || card.roundDetails || '—'}
                </div>
                <div className="col-span-2 text-xs text-gray-500">{card.dateAdded}</div>
                <div className="col-span-1 text-right">
                  <button className="text-xs font-semibold text-indigo-600 hover:text-indigo-800">
                    View →
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Card Details & Stage Transition Modal */}
      {selectedCard && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
          onClick={() => setSelectedCard(null)}
        >
          <div
            className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-gray-100 flex flex-col gap-4 relative animate-scale-up"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                  {selectedCard.company}
                </span>
                <h3 className="text-lg font-bold text-gray-900">{selectedCard.role}</h3>
              </div>
              <button
                onClick={() => setSelectedCard(null)}
                className="size-7 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-600 flex items-center justify-center font-bold text-sm"
              >
                ✕
              </button>
            </div>

            {selectedCard.salary && (
              <div className="bg-emerald-50 border border-emerald-100 rounded-xl p-3 text-xs text-emerald-800 font-semibold flex items-center justify-between">
                <span>Compensation Target:</span>
                <span className="text-sm font-extrabold">{selectedCard.salary}</span>
              </div>
            )}

            {selectedCard.stage === 'offer' && (
              <div className="bg-amber-500 text-white rounded-xl p-3 text-xs flex flex-col gap-1 shadow-md">
                <div className="font-bold flex items-center gap-1.5">
                  <Trophy className="size-4" />
                  <span>OFFER DETAILS</span>
                </div>
                <div>{selectedCard.equity}</div>
                <div>{selectedCard.signOn}</div>
                <div className="text-amber-100 mt-1">{selectedCard.notes}</div>
              </div>
            )}

            {selectedCard.roundDetails && (
              <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-3 text-xs text-indigo-900">
                <div className="font-bold">Next Milestone:</div>
                <div className="mt-0.5">{selectedCard.roundDetails}</div>
                {selectedCard.interviewer && (
                  <div className="text-indigo-700 font-medium mt-1">
                    Interviewer: {selectedCard.interviewer}
                  </div>
                )}
              </div>
            )}

            {selectedCard.notes && selectedCard.stage !== 'offer' && (
              <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded-xl border border-gray-200/60">
                <span className="font-semibold text-gray-800">Dossier Notes: </span>
                {selectedCard.notes}
              </div>
            )}

            {/* Advance Stage Control */}
            <div className="border-t border-gray-100 pt-3 flex flex-col gap-2">
              <label className="text-[11px] font-bold text-gray-500 uppercase tracking-wider">
                Pipeline Stage Progression:
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['saved', 'ready', 'applied', 'assessment', 'interview', 'offer'] as const).map(
                  (st) => (
                    <button
                      key={st}
                      onClick={() => handleStageMove(selectedCard.id, st)}
                      className={`text-xs font-semibold py-1.5 rounded-lg border transition-all ${
                        selectedCard.stage === st
                          ? 'bg-black text-white border-black shadow-sm'
                          : 'bg-white hover:bg-gray-100 text-gray-700 border-gray-200'
                      }`}
                    >
                      {st.toUpperCase()}
                    </button>
                  )
                )}
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setSelectedCard(null)}
                className="bg-black text-white text-xs font-bold px-5 py-2 rounded-full hover:bg-gray-800 shadow-md"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

