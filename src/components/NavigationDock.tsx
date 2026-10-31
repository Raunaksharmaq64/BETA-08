'use client';

import React from 'react';
import {
  LayoutGrid,
  FileText,
  Compass,
  Target,
  Briefcase,
  Flame,
  TrendingUp,
  Mic,
  FolderOpen,
  Sliders,
} from 'lucide-react';

export type NavSection =
  | 'dashboard'
  | 'resume'
  | 'discovery'
  | 'opportunity'
  | 'crm'
  | 'pain_points'
  | 'market'
  | 'interview'
  | 'documents';

interface NavigationDockProps {
  activeSection: NavSection;
  onSelectSection: (section: NavSection) => void;
  onOpenSettings?: () => void;
}

export function NavigationDock({
  activeSection,
  onSelectSection,
  onOpenSettings,
}: NavigationDockProps) {
  const navItems: { id: NavSection; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: 'dashboard', label: 'Dashboard Overview', icon: LayoutGrid },
    { id: 'resume', label: 'Resume Evidence', icon: FileText },
    { id: 'discovery', label: 'Job Discovery', icon: Compass },
    { id: 'opportunity', label: 'Opportunity Intel', icon: Target },
    { id: 'crm', label: 'Application CRM', icon: Briefcase },
    { id: 'pain_points', label: 'Startup Pain Points', icon: Flame },
    { id: 'market', label: 'Market & Skills', icon: TrendingUp },
    { id: 'interview', label: 'Interview Intel', icon: Mic },
    { id: 'documents', label: 'Documents & Collections', icon: FolderOpen },
  ];

  return (
    <aside
      className="bg-[#1a1c21] w-14 sm:w-16 h-full max-h-[96vh] rounded-full flex flex-col items-center justify-between py-4 px-2 shadow-[0px_0px_0px_1px_rgba(255,255,255,0.1),0px_16px_32px_-4px_rgba(24,26,31,0.28)] shrink-0 select-none z-20"
      aria-label="Tactile Graphite Pill Dock"
    >
      {/* Top Action Group */}
      <div className="flex flex-col items-center w-full gap-1">
        {/* Logo / Spark Icon */}
        <button
          onClick={() => onSelectSection('dashboard')}
          title="RightFit Platform"
          className="size-10 rounded-full flex items-center justify-center hover:bg-white/10 transition-colors group relative"
        >
          <div className="size-8 rounded-full bg-gradient-to-tr from-amber-400 via-orange-500 to-amber-600 flex items-center justify-center text-black font-extrabold text-[11px] shadow-md tracking-tight">
            RF
          </div>
          <span className="absolute left-16 px-2.5 py-1 bg-[#171c23] text-white text-[11px] rounded-md shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap border border-white/10">
            RightFit Platform
          </span>
        </button>

        {/* Divider */}
        <div className="w-6 h-px bg-white/10 my-1.5" />

        {/* Navigation Items */}
        <nav className="flex flex-col items-center gap-1 w-full">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onSelectSection(item.id)}
                title={item.label}
                className={`relative size-9 sm:size-10 rounded-full flex items-center justify-center transition-all duration-150 group ${
                  isActive
                    ? 'bg-white text-black shadow-md scale-105'
                    : 'text-gray-400 hover:text-white hover:bg-white/10'
                }`}
              >
                <Icon className={`size-4 sm:size-4.5 ${isActive ? 'stroke-[2.5]' : 'stroke-[1.75]'}`} />
                <span className="absolute left-16 px-2.5 py-1 bg-[#171c23] text-white text-[11px] rounded-md shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap border border-white/10">
                  {item.label}
                </span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Dock Vertical Micro Subtitle */}
      <div className="hidden md:flex items-center justify-center py-2 text-[9px] font-mono tracking-[1.5px] text-white/20 uppercase rotate-180 [writing-mode:vertical-rl]">
        INTEL 2025 NAV
      </div>

      {/* Bottom Controls */}
      <div className="flex flex-col items-center gap-2 pt-2 border-t border-white/10 w-full">
        <button
          onClick={onOpenSettings}
          title="System Settings & Backend Integration"
          className="size-9 rounded-full flex items-center justify-center text-gray-400 hover:text-white hover:bg-white/10 transition-colors group relative"
        >
          <Sliders className="size-4" />
          <span className="absolute left-16 px-2.5 py-1 bg-[#171c23] text-white text-[11px] rounded-md shadow-xl opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity z-50 whitespace-nowrap border border-white/10">
            Backend Integration & API
          </span>
        </button>

        {/* User Avatar */}
        <div
          title="Alex Mercer (Signed In)"
          className="size-8 sm:size-9 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 border border-white/20 flex items-center justify-center text-white text-[11px] font-bold shadow-inner cursor-pointer hover:border-white/50 transition-colors"
        >
          AM
        </div>
      </div>
    </aside>
  );
}

