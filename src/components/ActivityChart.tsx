'use client';

import React from 'react';
import { ActivityDay } from '@/services/types';

interface ActivityChartProps {
  days: ActivityDay[];
  title?: string;
  precisionStat?: string;
}

export function ActivityChart({
  days,
  title = 'Throughput & Match Accuracy (Last 7 Days)',
  precisionStat = 'Avg. 92.4% precision',
}: ActivityChartProps) {
  return (
    <div className="border-t border-[rgba(228,232,242,0.6)] pt-4 flex flex-col gap-3 w-full select-none">
      {/* Chart Header */}
      <div className="flex items-center justify-between text-xs">
        <span className="text-[#46474b] font-medium">{title}</span>
        <span className="text-[#171c23] font-semibold">{precisionStat}</span>
      </div>

      {/* Tactile CSS Bar Visualization */}
      <div className="flex items-end justify-between gap-2.5 h-20 pt-2 px-1">
        {days.map((item) => (
          <div
            key={item.day}
            className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end group cursor-pointer"
          >
            {/* The bar */}
            <div
              style={{ height: `${item.height}%` }}
              className={`w-full max-w-[48px] rounded-t-md transition-all duration-300 ${
                item.isPeak
                  ? 'bg-black shadow-sm group-hover:bg-gray-800'
                  : 'bg-[#e4e8f2] group-hover:bg-[#d5dbe8]'
              }`}
              title={`${item.day}: ${item.height}% match throughput`}
            />

            {/* Day Label */}
            <span
              className={`text-[10px] tracking-tight ${
                item.isPeak ? 'font-bold text-[#171c23]' : 'text-[#76777b]'
              }`}
            >
              {item.day}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

