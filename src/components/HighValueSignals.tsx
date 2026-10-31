'use client';

import React from 'react';
import { Sparkles, Building2, ArrowUpRight, CheckCircle2 } from 'lucide-react';
import { HighValueSignal } from '@/services/types';

interface HighValueSignalsProps {
  signals: HighValueSignal[];
  onInspectSignal?: (sig: HighValueSignal) => void;
}

export function HighValueSignals({
  signals,
  onInspectSignal,
}: HighValueSignalsProps) {
  return (
    <div className="flex flex-col gap-3.5 w-full select-none">
      {/* Header with Title and Icon */}
      <div className="flex items-center justify-between">
        <h3 className="text-[#171c23] text-sm sm:text-[15px] font-bold tracking-tight">
          High-Value Signals
        </h3>
        <div className="bg-amber-100 p-1 rounded-full">
          <Sparkles className="size-3.5 text-amber-600" />
        </div>
      </div>

      {/* Signal Cards */}
      <div className="flex flex-col gap-3">
        {signals.map((sig) => (
          <div
            key={sig.id}
            onClick={() => onInspectSignal?.(sig)}
            className="bg-[rgba(239,244,254,0.4)] border border-[rgba(255,255,255,0.85)] hover:border-black/20 rounded-2xl p-3.5 flex flex-col gap-2.5 transition-all duration-150 hover:bg-white cursor-pointer group shadow-sm"
          >
            {/* Top row: Priority & Comp */}
            <div className="flex items-center justify-between text-[11px]">
              <span className="bg-[#e8f5ed] text-[#459364] px-2 py-0.5 rounded-full font-semibold">
                {sig.priorityLabel}
              </span>
              <span className="text-[#46474b] font-medium">
                {sig.compensation}
              </span>
            </div>

            {/* Middle: Role & Company */}
            <div className="flex items-start justify-between gap-2">
              <div className="flex flex-col">
                <span className="text-[#171c23] text-xs sm:text-[13px] font-bold leading-tight">
                  {sig.role}
                </span>
                <span className="text-gray-500 text-[11px] mt-0.5">
                  {sig.company}
                </span>
              </div>

              <div className="bg-black text-white text-[11px] font-bold px-2 py-0.5 rounded-full shrink-0">
                {sig.matchScore}%
              </div>
            </div>

            {/* Bottom action bar */}
            <div className="pt-2 border-t border-[rgba(228,232,242,0.5)] flex items-center justify-between text-[11px]">
              <span className="text-gray-500">{sig.urgency}</span>
              <span className="text-[#171c23] font-semibold flex items-center gap-0.5 group-hover:translate-x-0.5 transition-transform">
                <span>View Signal</span>
                <ArrowUpRight className="size-3" />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

