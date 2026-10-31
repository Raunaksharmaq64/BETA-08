export interface MetricCardData {
  title: string;
  value: string;
  subValue?: string;
  changeBadge: string;
  isPositive: boolean;
  linkText: string;
  linkAction?: string;
}

export interface WorkflowExecution {
  id: string;
  title: string;
  description: string;
  badgeText: string;
  processedAgo: string;
  status: 'running' | 'completed' | 'ready';
  iconType: 'document' | 'search' | 'interview' | 'zap';
}

export interface ActivityDay {
  day: 'Mon' | 'Tue' | 'Wed' | 'Thu' | 'Fri' | 'Sat' | 'Sun';
  height: number; // percentage
  isPeak?: boolean;
}

export interface HighValueSignal {
  id: string;
  company: string;
  companyInitial: string;
  role: string;
  compensation: string;
  matchScore: number;
  priorityLabel: string;
  urgency: string;
}

export interface DashboardData {
  metrics: {
    executions: MetricCardData;
    atsScore: MetricCardData;
    interviewPipeline: MetricCardData;
    targetSalary: MetricCardData;
  };
  activeWorkflows: WorkflowExecution[];
  activityDays: ActivityDay[];
  activitySummary: {
    title: string;
    precisionStat: string;
  };
  signals: HighValueSignal[];
}

export interface UserProfile {
  name: string;
  initials: string;
  role: string;
  avatarUrl?: string;
}

// ================= Application CRM Types =================
export interface KanbanCard {
  id: string;
  company: string;
  role: string;
  salary?: string;
  equity?: string;
  signOn?: string;
  stage: 'saved' | 'ready' | 'applied' | 'assessment' | 'interview' | 'offer';
  dateAdded: string;
  tags: string[];
  priority?: 'high' | 'medium' | 'urgent';
  interviewer?: string;
  roundDetails?: string;
  notes?: string;
}

export interface ApplicationCRMData {
  stats: {
    totalActive: { value: string; delta: string };
    responseRate: { value: string; benchmark: string };
    interviewConversion: { value: string; rating: string };
    pendingFollowUps: { value: string; badge: string };
  };
  cards: KanbanCard[];
}

// ================= AI Job Discovery Types =================
export interface JobMatchCard {
  id: string;
  company: string;
  role: string;
  location: string;
  salary: string;
  matchScore: number;
  matchPercentile: string;
  verifiedType: 'direct' | 'public' | 'inferred';
  skills: string[];
  postedAgo: string;
  summary: string;
  headcountApproved: boolean;
  dkimSignature: string;
  atsSyncStatus: string;
  fundingTelemetry: string;
}

export interface JobDiscoveryData {
  stats: {
    verifiedMatches: { count: string; delta: string };
    newToday: { count: string; label: string };
    avgMatch: { percentage: string; note: string };
    medianSalary: { amount: string; delta: string };
  };
  jobs: JobMatchCard[];
}

// ================= Freelance Finder Types =================
export interface FreelanceLead {
  id: string;
  company: string;
  contactName: string;
  contactRole: string;
  avatarUrl?: string;
  fundingStage: string;
  budget: string;
  sprintDuration: string;
  affinityMatch: number;
  tags: string[];
  bottleneckSummary: string;
  rawSignal: string;
  draftedPitch: string;
  status: 'new' | 'contact_ready' | 'pitch_sent' | 'contract_awarded';
}

export interface FreelanceData {
  metrics: {
    activeLeads: { count: string; badge: string };
    contactReady: { count: string; label: string };
    pitchesSent: { count: string; note: string };
    pipelineValue: { total: string; sprintAvg: string };
  };
  leads: FreelanceLead[];
}

// ================= Market & Skill Intelligence Types =================
export interface SkillArbitrageItem {
  id: string;
  name: string;
  premium: string;
  demandLevel: 'Extreme' | 'Very High' | 'High' | 'Moderate';
  difficulty: 'Low' | 'Medium' | 'High' | 'Expert';
  userStatus: 'Mastered' | 'In Progress' | 'Recommended Next';
  growthYoY: string;
  description: string;
}

export interface UpskillingMilestone {
  step: number;
  duration: string;
  title: string;
  description: string;
  actionItem: string;
}

export interface MarketSkillsData {
  metrics: {
    marketBaseP75: { value: string; delta: string };
    equityMedian: { value: string; label: string };
    topSkillPremium: { value: string; skill: string };
    activeDemand: { value: string; location: string };
  };
  percentiles: { label: string; amount: string; height: number }[];
  skills: SkillArbitrageItem[];
  roadmap: UpskillingMilestone[];
}

// ================= Interview Intelligence Types =================
export interface InterviewTask {
  id: string;
  day: 1 | 2;
  stepNumber: string;
  title: string;
  description: string;
  isComplete: boolean;
  isActive?: boolean;
}

export interface InterviewIntelData {
  metrics: {
    readinessScore: { score: string; benchmark: string; delta: string };
    targetRound: { round: string; totalRounds: string; focus: string };
    questionClusters: { count: string; rehearsed: string; status: string };
    mockRuns: { completed: string; total: string; remaining: string };
  };
  itinerary: InterviewTask[];
  simulatorScorecard: {
    architectureDepth: number;
    tradeoffClarity: number;
    communication: number;
  };
  phrasingRefinement: {
    raw: string;
    aiRefinement: string;
  };
  interviewerPersona: {
    archetype: string;
    bias: string;
    counselNote: string;
  };
}

// ================= Startup Pain Points Types =================
export interface PainPointItem {
  id: string;
  title: string;
  companyStage: string;
  scrapedAgo: string;
  bottleneckAbstract: string;
  matchScore: number;
  verificationSource: string;
  founderQuotesCount: number;
  companiesAffected: number;
  bountyAmount?: string;
  urgency: string;
  founderQuote: {
    quote: string;
    author: string;
    source: string;
  };
  tags: string[];
}

export interface StartupPainPointsData {
  metrics: {
    catalogedPoints: { count: string; delta: string; sources: string };
    highConfidence: { count: string; conf: string; status: string };
    directFounderSignals: { count: string; stages: string; issues: string };
    bountiesPool: { count: string; poolAmount: string; note: string };
  };
  painPoints: PainPointItem[];
}
