import {
  DashboardData,
  UserProfile,
  WorkflowExecution,
  ApplicationCRMData,
  JobDiscoveryData,
  FreelanceData,
  MarketSkillsData,
  InterviewIntelData,
  StartupPainPointsData,
  KanbanCard,
} from './types';
import {
  mockDashboardData,
  mockUserProfile,
  mockApplicationCRMData,
  mockJobDiscoveryData,
  mockFreelanceData,
  mockMarketSkillsData,
  mockInterviewIntelData,
  mockStartupPainPointsData,
} from './mockData';
import { apiClient, IS_MOCK_MODE, delay } from './apiClient';
import { API_ENDPOINTS } from './endpoints';

let localDashboardData: DashboardData = { ...mockDashboardData };
let localCRMData: ApplicationCRMData = { ...mockApplicationCRMData };
let localFreelanceData: FreelanceData = { ...mockFreelanceData };
let localPainPointsData: StartupPainPointsData = { ...mockStartupPainPointsData };

export const DashboardService = {
  /**
   * Fetch full homepage dashboard telemetry
   */
  async getDashboardData(): Promise<DashboardData> {
    if (IS_MOCK_MODE) {
      await delay(120);
      return { ...localDashboardData };
    }
    return apiClient.get<DashboardData>(API_ENDPOINTS.DASHBOARD_DATA);
  },

  /**
   * Filter active workflows by search query
   */
  async searchWorkflows(query: string): Promise<WorkflowExecution[]> {
    if (IS_MOCK_MODE) {
      await delay(80);
      if (!query.trim()) return localDashboardData.activeWorkflows;
      const q = query.toLowerCase();
      return localDashboardData.activeWorkflows.filter(
        (wf) =>
          wf.title.toLowerCase().includes(q) ||
          wf.description.toLowerCase().includes(q)
      );
    }
    return apiClient.get<WorkflowExecution[]>(API_ENDPOINTS.ACTIVE_WORKFLOWS, {
      params: { q: query },
    });
  },

  /**
   * Trigger a new action / workflow run
   */
  async triggerNewAction(title: string): Promise<WorkflowExecution> {
    const newWorkflow: WorkflowExecution = {
      id: `wf-${Date.now()}`,
      title,
      description: 'Pipeline execution initiated via RightFit AI orchestrator',
      badgeText: 'Running',
      processedAgo: 'Just now',
      status: 'running',
      iconType: 'zap',
    };

    if (IS_MOCK_MODE) {
      await delay(150);
      localDashboardData.activeWorkflows = [
        newWorkflow,
        ...localDashboardData.activeWorkflows,
      ];
      // Increment execution counter
      const currentCount = parseInt(
        localDashboardData.metrics.executions.value,
        10
      );
      localDashboardData.metrics.executions.value = String(currentCount + 1);
      return newWorkflow;
    }

    return apiClient.post<WorkflowExecution>(API_ENDPOINTS.RUN_WORKFLOW, {
      title,
    });
  },

  /**
   * Fetch user profile
   */
  async getUserProfile(): Promise<UserProfile> {
    if (IS_MOCK_MODE) {
      return { ...mockUserProfile };
    }
    return apiClient.get<UserProfile>(API_ENDPOINTS.USER_PROFILE);
  },

  /**
   * Application CRM
   */
  async getApplicationCRMData(): Promise<ApplicationCRMData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...localCRMData };
    }
    return apiClient.get<ApplicationCRMData>('/api/crm');
  },

  async updateCardStage(cardId: string, newStage: KanbanCard['stage']): Promise<ApplicationCRMData> {
    if (IS_MOCK_MODE) {
      await delay(120);
      localCRMData.cards = localCRMData.cards.map((c) =>
        c.id === cardId ? { ...c, stage: newStage } : c
      );
      return { ...localCRMData };
    }
    return apiClient.patch<ApplicationCRMData>(`/api/crm/cards/${cardId}`, { stage: newStage });
  },

  /**
   * AI Job Discovery
   */
  async getJobDiscoveryData(): Promise<JobDiscoveryData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...mockJobDiscoveryData };
    }
    return apiClient.get<JobDiscoveryData>('/api/jobs');
  },

  /**
   * Freelance Finder
   */
  async getFreelanceData(): Promise<FreelanceData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...localFreelanceData };
    }
    return apiClient.get<FreelanceData>('/api/freelance');
  },

  async sendFreelancePitch(leadId: string, pitchText: string): Promise<FreelanceData> {
    if (IS_MOCK_MODE) {
      await delay(150);
      localFreelanceData.leads = localFreelanceData.leads.map((l) =>
        l.id === leadId ? { ...l, status: 'pitch_sent' as const, draftedPitch: pitchText } : l
      );
      const currentSent = parseInt(localFreelanceData.metrics.pitchesSent.count, 10);
      localFreelanceData.metrics.pitchesSent.count = String(currentSent + 1);
      return { ...localFreelanceData };
    }
    return apiClient.post<FreelanceData>(`/api/freelance/${leadId}/pitch`, { pitchText });
  },

  /**
   * Market & Skill Intelligence
   */
  async getMarketSkillsData(): Promise<MarketSkillsData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...mockMarketSkillsData };
    }
    return apiClient.get<MarketSkillsData>('/api/market-skills');
  },

  /**
   * Interview Intelligence
   */
  async getInterviewIntelData(): Promise<InterviewIntelData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...mockInterviewIntelData };
    }
    return apiClient.get<InterviewIntelData>('/api/interview');
  },

  /**
   * Startup Pain Points
   */
  async getStartupPainPointsData(): Promise<StartupPainPointsData> {
    if (IS_MOCK_MODE) {
      await delay(100);
      return { ...localPainPointsData };
    }
    return apiClient.get<StartupPainPointsData>('/api/pain-points');
  },

  async submitSolutionArchitecture(painPointId: string, solutionMemo: string): Promise<boolean> {
    if (IS_MOCK_MODE) {
      await delay(200);
      return true;
    }
    return apiClient.post<boolean>(`/api/pain-points/${painPointId}/solution`, { solutionMemo });
  },
};

