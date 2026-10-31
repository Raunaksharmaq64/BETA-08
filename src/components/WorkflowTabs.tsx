'use client';

import React from 'react';

export type SubTab =
  | 'workflows'
  | 'resume_evidence'
  | 'job_discovery'
  | 'application_crm'
  | 'pain_points';

interface WorkflowTabsProps {
  activeTab: SubTab;
  onTabChange: (tab: SubTab) => void;
  activeCount?: number;
}

export function WorkflowTabs({
  activeTab,
  onTabChange,
  activeCount = 4,
}: WorkflowTabsProps) {
  const tabs: { id: SubTab; label: string }[] = [
    { id: 'workflows', label: 'Workflows' },
    { id: 'resume_evidence', label: 'Resume Evidence' },
    { id: 'job_discovery', label: 'Job Discovery' },
    { id: 'application_crm', label: 'Application CRM' },
    { id: 'pain_points', label: 'Startup Pain Points' },
  ];

  return (
    <div className="border-b border-[rgba(228,232,242,0.6)] flex flex-col sm:flex-row sm:items-center justify-between gap-2 w-full select-none shrink-0">
      {/* Tab Navigation */}
      <nav className="flex items-center gap-6 overflow-x-auto pb-px">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`text-sm whitespace-nowrap pb-2.5 transition-colors relative ${
                isActive
                  ? 'text-[#171c23] font-semibold'
                  : 'text-[#46474b] hover:text-[#171c23] font-normal'
              }`}
            >
              <span>{tab.label}</span>
              {isActive && (
                <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-black rounded-full" />
              )}
            </button>
          );
        })}
      </nav>

      {/* Right Filter Status Pill */}
      <div className="text-xs text-[#46474b] pb-2 flex items-center gap-1.5 shrink-0">
        <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
        <span>
          {activeTab === 'workflows' && `Filter: Active Workflows (${activeCount})`}
          {activeTab === 'resume_evidence' && 'ATS Verification: 94.8% Match'}
          {activeTab === 'job_discovery' && 'Radar: 48 Matches Detected'}
          {activeTab === 'application_crm' && 'Pipeline: 18 Active Applications'}
          {activeTab === 'pain_points' && 'Bounties: $145k Active Pool'}
        </span>
      </div>
    </div>
  );
}

