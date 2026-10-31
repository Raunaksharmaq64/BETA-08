'use client';

import React from 'react';
import { ArrowRight, TrendingUp } from 'lucide-react';
import { MetricCardData } from '@/services/types';

interface MetricCardsRowProps {
  metrics: {
    executions: MetricCardData;
    atsScore: MetricCardData;
    interviewPipeline: MetricCardData;
    targetSalary: MetricCardData;
  };
  onLinkClick: (action: string) => void;
}

export function MetricCardsRow({ metrics, onLinkClick }: MetricCardsRowProps) {
  const cards = [
    metrics.executions,
    metrics.atsScore,
    metrics.interviewPipeline,
    metrics.targetSalary,
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full select-none">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="backdrop-blur-[14px] bg-[rgba(255,255,255,0.85)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_16px_0px_rgba(0,0,0,0.02)] flex flex-col justify-between hover:shadow-md transition-all duration-200"
        >
          {/* Top: Title, Big Value & Badge */}
          <div className="flex flex-col gap-2">
            <span className="text-[#46474b] text-xs tracking-[-0.065px] font-medium">
              {card.title}
            </span>

            <div className="flex items-baseline gap-2.5 flex-wrap">
              <div className="flex items-baseline">
                <span className="text-[#171c23] text-4xl sm:text-[44px] font-normal tracking-[-1.44px] leading-none">
                  {card.value}
                </span>
                {card.subValue && (
                  <span className="text-[#46474b] text-lg font-normal ml-0.5 tracking-tight">
                    {card.subValue}
                  </span>
                )}
              </div>

              {/* Green Metric Pill Badge */}
              <div className="bg-[#e8f5ed] text-[#459364] px-2 py-0.5 rounded-full text-[11px] font-bold tracking-[0.11px] flex items-center gap-1 shadow-sm shrink-0">
                <span>{card.changeBadge}</span>
              </div>
            </div>
          </div>

          {/* Bottom: Action Link */}
          <div className="pt-4 mt-2 border-t border-[rgba(228,232,242,0.5)]">
            <button
              onClick={() => onLinkClick(card.linkAction || 'report')}
              className="text-[#171c23] text-xs font-medium hover:text-black flex items-center gap-1 group transition-colors"
            >
              <span>{card.linkText}</span>
              <ArrowRight className="size-3.5 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

