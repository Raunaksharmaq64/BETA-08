'use client';

import React, { useState, useEffect } from 'react';
import { NavigationDock, NavSection } from '@/components/NavigationDock';
import { DashboardHeader } from '@/components/DashboardHeader';
import { MetricCardsRow } from '@/components/MetricCardsRow';
import { WorkflowTabs, SubTab } from '@/components/WorkflowTabs';
import { ActiveWorkflowsList } from '@/components/ActiveWorkflowsList';
import { ActivityChart } from '@/components/ActivityChart';
import { HighValueSignals } from '@/components/HighValueSignals';
import { CreateActionModal } from '@/components/CreateActionModal';
import { ReportModal } from '@/components/ReportModal';
import { BackendGuideModal } from '@/components/BackendGuideModal';

// Intelligence Section Full Components
import { ResumeIntelligenceSection } from '@/components/sections/ResumeIntelligenceSection';
import { OpportunityIntelligenceSection } from '@/components/sections/OpportunityIntelligenceSection';
import { ApplicationCRMSection } from '@/components/sections/ApplicationCRMSection';
import { JobDiscoverySection } from '@/components/sections/JobDiscoverySection';
import { FreelanceFinderSection } from '@/components/sections/FreelanceFinderSection';
import { MarketSkillsSection } from '@/components/sections/MarketSkillsSection';
import { InterviewIntelligenceSection } from '@/components/sections/InterviewIntelligenceSection';
import { StartupPainPointsSection } from '@/components/sections/StartupPainPointsSection';

// Miniature Dashboard Inline Views (Keep User On Dashboard Without Redirecting)
import { ResumeEvidenceMiniView } from '@/components/dashboard/ResumeEvidenceMiniView';
import { JobDiscoveryMiniView } from '@/components/dashboard/JobDiscoveryMiniView';
import { ApplicationCRMMiniView } from '@/components/dashboard/ApplicationCRMMiniView';
import { StartupPainPointsMiniView } from '@/components/dashboard/StartupPainPointsMiniView';

import { DashboardService } from '@/services/dashboardService';
import { DashboardData, WorkflowExecution } from '@/services/types';
import { mockDashboardData } from '@/services/mockData';

export default function HomePage() {
  const [activeSection, setActiveSection] = useState<NavSection>('dashboard');
  const [activeSubTab, setActiveSubTab] = useState<SubTab>('workflows');
  const [searchQuery, setSearchQuery] = useState('');
  const [dashboardData, setDashboardData] = useState<DashboardData>(mockDashboardData);
  const [displayedWorkflows, setDisplayedWorkflows] = useState<WorkflowExecution[]>(
    mockDashboardData.activeWorkflows
  );
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [reportModalType, setReportModalType] = useState<string | null>(null);
  const [isBackendGuideOpen, setIsBackendGuideOpen] = useState(false);
  const [exportNotice, setExportNotice] = useState(false);

  // Load live or mock telemetry
  useEffect(() => {
    DashboardService.getDashboardData().then((data) => {
      setDashboardData(data);
      setDisplayedWorkflows(data.activeWorkflows);
    });
  }, []);

  // Filter workflows on search
  useEffect(() => {
    DashboardService.searchWorkflows(searchQuery).then((filtered) => {
      setDisplayedWorkflows(filtered);
    });
  }, [searchQuery]);

  const handleCreateAction = async (title: string) => {
    const created = await DashboardService.triggerNewAction(title);
    setDisplayedWorkflows((prev) => [created, ...prev]);
  };

  const handleExport = () => {
    setExportNotice(true);
    setTimeout(() => setExportNotice(false), 2500);
  };

  // Subtab switching stays ON the dashboard - no redirect
  const handleSubTabChange = (tab: SubTab) => {
    setActiveSubTab(tab);
    // Explicitly keep section as dashboard so user is not redirected
    if (activeSection !== 'dashboard') {
      setActiveSection('dashboard');
    }
  };

  // Metric card clicks stay ON the dashboard and switch the subtab to show mini data
  const handleMetricCardClick = (action?: string) => {
    if (!action) return;
    if (action === 'report') {
      setReportModalType('report');
    } else if (action === 'ats_proof') {
      setActiveSection('dashboard');
      setActiveSubTab('resume_evidence');
    } else if (action === 'crm') {
      setActiveSection('dashboard');
      setActiveSubTab('application_crm');
    } else if (action === 'opportunities') {
      setActiveSection('dashboard');
      setActiveSubTab('job_discovery');
    }
  };

  return (
    <main className="min-h-screen w-full flex items-center justify-center p-2 sm:p-4 md:p-6 select-none">
      {/* Fluid Workspace Container scaling to any browser screen */}
      <div className="flex gap-3 sm:gap-5 w-full max-w-[1560px] h-[94vh] min-h-[700px] items-start">
        {/* LEFT TACTILE GRAPHITE PILL DOCK (Reagle Style Capsule) */}
        <NavigationDock
          activeSection={activeSection}
          onSelectSection={(sec) => {
            setActiveSection(sec);
            if (sec === 'dashboard') setActiveSubTab('workflows');
          }}
          onOpenSettings={() => setIsBackendGuideOpen(true)}
        />

        {/* MASTER FROSTED GLASS SHELL CONTAINER */}
        <div className="flex-1 min-w-0 flex flex-col h-full backdrop-blur-[24px] bg-[rgba(244,245,248,0.78)] border border-[rgba(255,255,255,0.85)] rounded-[28px] sm:rounded-[36px] shadow-[0px_24px_48px_-12px_rgba(24,26,31,0.08),0px_8px_16px_-4px_rgba(24,26,31,0.04)] overflow-hidden">
          {/* Top Content Bar with Breadcrumb / Search / Action Buttons */}
          <DashboardHeader
            activeSection={activeSection}
            onSelectSection={setActiveSection}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            onExport={handleExport}
            onCreateAction={() => setIsActionModalOpen(true)}
          />

          {/* Export Toast Notification */}
          {exportNotice && (
            <div className="bg-black text-white text-xs px-4 py-2 rounded-full absolute top-16 right-8 shadow-xl z-30 flex items-center gap-2 animate-fade-in">
              <span>Telemetry report exported to RightFit_Audit.json</span>
            </div>
          )}

          {/* Dynamic Scrollable Work Surface */}
          <div className="flex-1 overflow-y-auto px-6 sm:px-8 py-5 flex flex-col gap-6">
            {/* DEDICATED FULL SECTIONS (Only when user explicitly selects via Left Dock or Open Full Suite CTA) */}
            {activeSection === 'resume' ? (
              <ResumeIntelligenceSection />
            ) : activeSection === 'discovery' ? (
              <JobDiscoverySection />
            ) : activeSection === 'opportunity' ? (
              <OpportunityIntelligenceSection />
            ) : activeSection === 'crm' ? (
              <ApplicationCRMSection />
            ) : activeSection === 'pain_points' ? (
              <StartupPainPointsSection />
            ) : activeSection === 'market' ? (
              <MarketSkillsSection />
            ) : activeSection === 'interview' ? (
              <InterviewIntelligenceSection />
            ) : activeSection === 'documents' ? (
              <ResumeIntelligenceSection />
            ) : (
              /* MASTER HOMEPAGE DASHBOARD (Frame 5:3595) */
              <>
                {/* Quick Stat Metric Blocks (Executions, ATS Score, Interview Pipeline, Salary Fit) */}
                <MetricCardsRow
                  metrics={dashboardData.metrics}
                  onLinkClick={handleMetricCardClick}
                />

                {/* Secondary Horizontal Segmented Tabs (Switches mini views right here on Dashboard) */}
                <WorkflowTabs
                  activeTab={activeSubTab}
                  onTabChange={handleSubTabChange}
                  activeCount={displayedWorkflows.length}
                />

                {/* Subtab Content: Inline Miniature Summaries on Dashboard */}
                {activeSubTab === 'resume_evidence' ? (
                  <ResumeEvidenceMiniView
                    onOpenFullSection={() => setActiveSection('resume')}
                  />
                ) : activeSubTab === 'job_discovery' ? (
                  <JobDiscoveryMiniView
                    onOpenFullSection={() => setActiveSection('discovery')}
                  />
                ) : activeSubTab === 'application_crm' ? (
                  <ApplicationCRMMiniView
                    onOpenFullSection={() => setActiveSection('crm')}
                  />
                ) : activeSubTab === 'pain_points' ? (
                  <StartupPainPointsMiniView
                    onOpenFullSection={() => setActiveSection('pain_points')}
                  />
                ) : (
                  /* Default 'workflows' tab */
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start pb-4">
                    {/* Left 8 Cols (Approx 65% width): Executions Log & Activity Chart */}
                    <div className="lg:col-span-8 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-5">
                      <ActiveWorkflowsList
                        workflows={displayedWorkflows}
                        onSelectWorkflow={(wf) => setReportModalType('report')}
                      />

                      <ActivityChart
                        days={dashboardData.activityDays}
                        title={dashboardData.activitySummary.title}
                        precisionStat={dashboardData.activitySummary.precisionStat}
                      />
                    </div>

                    {/* Right 4 Cols (Approx 35% width): Opportunity Intel Recommendations */}
                    <div className="lg:col-span-4 bg-[rgba(255,255,255,0.88)] border border-[rgba(255,255,255,0.9)] rounded-2xl p-5 shadow-[0px_4px_20px_0px_rgba(0,0,0,0.03)] flex flex-col gap-4">
                      <HighValueSignals
                        signals={dashboardData.signals}
                        onInspectSignal={(sig) => {
                          setActiveSubTab('job_discovery');
                        }}
                      />
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Action Creation Modal */}
      <CreateActionModal
        isOpen={isActionModalOpen}
        onClose={() => setIsActionModalOpen(false)}
        onSubmit={handleCreateAction}
      />

      {/* Interactive Report & Audit Proof Modal */}
      <ReportModal
        isOpen={!!reportModalType}
        type={reportModalType || 'report'}
        onClose={() => setReportModalType(null)}
      />

      {/* Backend Integration & API Service Layer Guide Drawer */}
      <BackendGuideModal
        isOpen={isBackendGuideOpen}
        onClose={() => setIsBackendGuideOpen(false)}
      />
    </main>
  );
}
