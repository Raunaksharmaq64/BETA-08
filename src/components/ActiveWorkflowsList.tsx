'use client';

import React from 'react';
import {
  FileText,
  Search,
  Mic,
  Zap,
  CheckCircle2,
  ChevronRight,
} from 'lucide-react';
import { WorkflowExecution } from '@/services/types';

interface ActiveWorkflowsListProps {
  workflows: WorkflowExecution[];
  onSelectWorkflow?: (wf: WorkflowExecution) => void;
}

export function ActiveWorkflowsList({
  workflows,
  onSelectWorkflow,
}: ActiveWorkflowsListProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'document':
        return <FileText className="size-4 text-indigo-600" />;
      case 'search':
        return <Search className="size-4 text-blue-600" />;
      case 'interview':
        return <Mic className="size-4 text-emerald-600" />;
      default:
        return <Zap className="size-4 text-amber-600" />;
    }
  };

  return (
    <div className="flex flex-col gap-3.5 w-full">
      {/* Header with Title and Running Status Pill */}
      <div className="flex items-center justify-between w-full">
        <div>
          <h3 className="text-[#171c23] text-sm sm:text-[15px] font-bold tracking-tight">
            Active Workflow Executions
          </h3>
          <p className="text-[#46474b] text-xs">
            Live telemetry from automated pipeline match engines
          </p>
        </div>

        <div className="bg-[#eff4fe] border border-blue-100/60 px-2.5 py-1 rounded-full flex items-center gap-1.5 shrink-0 shadow-sm">
          <div className="size-2 rounded-full bg-[#10b981] animate-pulse" />
          <span className="text-[#171c23] text-xs font-medium">Running</span>
        </div>
      </div>

      {/* List of Workflow Execution Items */}
      <div className="flex flex-col gap-2.5">
        {workflows.map((wf) => (
          <div
            key={wf.id}
            onClick={() => onSelectWorkflow?.(wf)}
            className="bg-[rgba(239,244,254,0.5)] border border-[rgba(255,255,255,0.85)] hover:border-black/20 rounded-2xl p-3 sm:p-3.5 flex items-center justify-between gap-3 transition-all duration-150 hover:bg-[rgba(239,244,254,0.75)] cursor-pointer group shadow-sm"
          >
            {/* Left Icon & Information */}
            <div className="flex items-center gap-3 min-w-0">
              <div className="size-8 sm:size-9 rounded-xl bg-white shadow-sm flex items-center justify-center shrink-0 border border-white">
                {getIcon(wf.iconType)}
              </div>

              <div className="flex flex-col min-w-0">
                <span className="text-[#171c23] text-xs sm:text-[13px] font-bold truncate">
                  {wf.title}
                </span>
                <span className="text-[#46474b] text-[11px] truncate">
                  {wf.description}
                </span>
              </div>
            </div>

            {/* Right Status Badge & Processed Time */}
            <div className="flex items-center gap-3 shrink-0">
              <div className="flex flex-col items-end">
                <span className="text-[#171c23] text-[11px] font-bold">
                  {wf.badgeText}
                </span>
                <span className="text-[#76777b] text-[11px]">
                  {wf.processedAgo}
                </span>
              </div>

              <ChevronRight className="size-4 text-gray-400 group-hover:translate-x-0.5 transition-transform" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

