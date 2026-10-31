'use client';

import React, { useRef } from 'react';
import { Search, Download, Plus, ArrowLeft } from 'lucide-react';
import { NavSection } from './NavigationDock';

interface DashboardHeaderProps {
  activeSection?: NavSection;
  onSelectSection?: (sec: NavSection) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onExport: () => void;
  onCreateAction: () => void;
}

const sectionMeta: Record<NavSection, { title: string; subtitle: string }> = {
  dashboard: {
    title: 'Dashboard',
    subtitle: 'All Your Workflows And Permissions Map',
  },
  resume: {
    title: 'Resume Intelligence',
    subtitle: 'Master Architecture Resume & Cryptographic ATS Proof',
  },
  discovery: {
    title: 'AI Job Discovery',
    subtitle: 'Semantic Radar & Cryptographic Recruiter Verification',
  },
  opportunity: {
    title: 'Opportunity Intelligence',
    subtitle: 'Time Budget Optimizer & 5-Metric Scoring Engine',
  },
  crm: {
    title: 'Application CRM',
    subtitle: '6-Stage Kanban Pipeline & Live Recruiter Sync',
  },
  pain_points: {
    title: 'Startup Pain Points',
    subtitle: 'Founder Bounties & Bottleneck Dossier (Page 1)',
  },
  market: {
    title: 'Market & Skills',
    subtitle: 'Real-Time Compensation Trends & Skill Arbitrage Index',
  },
  interview: {
    title: 'Interview Intelligence',
    subtitle: '48h Preparation Track & Architecture Simulator Scorecard',
  },
  documents: {
    title: 'Documents & Collections',
    subtitle: 'Verified Resumes, Exported Audits, and Encryption Keys',
  },
};

export function DashboardHeader({
  activeSection = 'dashboard',
  onSelectSection,
  searchQuery,
  onSearchChange,
  onExport,
  onCreateAction,
}: DashboardHeaderProps) {
  const searchInputRef = useRef<HTMLInputElement>(null);
  const currentMeta = sectionMeta[activeSection] || sectionMeta.dashboard;

  // Keyboard shortcut ⌘K
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <header className="border-b border-[rgba(228,232,242,0.5)] pb-4 pt-4 px-6 sm:px-8 flex flex-col md:flex-row md:items-center justify-between gap-4 w-full select-none shrink-0">
      {/* Title, Breadcrumb & Subtitle */}
      <div className="flex flex-col">
        <div className="flex items-center gap-2.5">
          {activeSection !== 'dashboard' && onSelectSection && (
            <button
              onClick={() => onSelectSection('dashboard')}
              className="bg-white/90 hover:bg-white border border-gray-200/80 rounded-full px-2.5 py-1 text-xs font-semibold text-gray-700 shadow-sm flex items-center gap-1 transition-all"
              title="Return to Overview Dashboard"
            >
              <ArrowLeft className="size-3" />
              <span>Overview</span>
            </button>
          )}
          <h1 className="text-[#171c23] text-2xl sm:text-[26px] font-bold tracking-[-0.65px] leading-tight">
            {currentMeta.title}
          </h1>
        </div>
        <p className="text-[#46474b] text-[13px] tracking-[-0.065px] mt-0.5">
          {currentMeta.subtitle}
        </p>
      </div>

      {/* Right Controls: Search & Primary Actions */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Pill Search Bar */}
        <div className="bg-[rgba(255,255,255,0.85)] border border-[rgba(255,255,255,0.95)] rounded-full px-3.5 py-1.5 flex items-center shadow-[0px_2px_8px_0px_rgba(0,0,0,0.02)] w-full sm:w-64 transition-all focus-within:ring-2 focus-within:ring-black/10 focus-within:bg-white">
          <Search className="size-3.5 text-gray-400 mr-2 shrink-0" />
          <input
            ref={searchInputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search workflows, jobs..."
            className="bg-transparent border-none outline-none text-xs text-[#171c23] placeholder:text-gray-400 w-full"
          />
          <span className="hidden sm:inline-block text-[10px] text-gray-400 font-mono bg-gray-100 px-1.5 py-0.5 rounded-full ml-1">
            ⌘K
          </span>
        </div>

        {/* Export Button */}
        <button
          onClick={onExport}
          className="bg-white border border-[rgba(255,255,255,0.9)] rounded-full px-4 py-2 text-xs font-semibold text-[#171c23] drop-shadow-[0px_1px_1px_rgba(0,0,0,0.05)] hover:bg-gray-50 transition-all flex items-center gap-1.5 active:scale-95 shrink-0"
        >
          <Download className="size-3.5" />
          <span>Export</span>
        </button>

        {/* Create Action Button */}
        <button
          onClick={onCreateAction}
          className="bg-black rounded-full px-5 py-2 text-xs font-semibold text-white shadow-[0px_1px_3px_0px_rgba(0,0,0,0.1),0px_1px_2px_-1px_rgba(0,0,0,0.1)] hover:bg-gray-800 transition-all flex items-center gap-1.5 active:scale-95 shrink-0"
        >
          <Plus className="size-3.5 stroke-[2.5]" />
          <span>Create Action</span>
        </button>
      </div>
    </header>
  );
}

