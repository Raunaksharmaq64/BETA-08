import { DashboardData, UserProfile } from './types';

export const mockUserProfile: UserProfile = {
  name: 'Alex Mercer',
  initials: 'AM',
  role: 'Lead Systems & Distributed Runtime Architect',
};

export const mockDashboardData: DashboardData = {
  metrics: {
    executions: {
      title: 'Executions',
      value: '340',
      changeBadge: '↑ 204%',
      isPositive: true,
      linkText: 'See Report',
      linkAction: 'report',
    },
    atsScore: {
      title: 'Resume ATS Score',
      value: '94',
      subValue: '/100',
      changeBadge: '↑ +12%',
      isPositive: true,
      linkText: 'Audit ATS Proof',
      linkAction: 'ats_proof',
    },
    interviewPipeline: {
      title: 'Interview Pipeline',
      value: '8',
      changeBadge: '2 this week',
      isPositive: true,
      linkText: 'View Kanban CRM',
      linkAction: 'crm',
    },
    targetSalary: {
      title: 'Target Salary Fit',
      value: '$165',
      subValue: 'k',
      changeBadge: '98% fit',
      isPositive: true,
      linkText: 'Review Opportunities',
      linkAction: 'opportunities',
    },
  },
  activeWorkflows: [
    {
      id: 'wf-1',
      title: 'Semantic Resume Parser & ATS Alignment',
      description:
        'Source: Principal_Architect_Alex_Mercer.pdf • 12 models checked',
      badgeText: '94.8% Match',
      processedAgo: 'Processed 4m ago',
      status: 'completed',
      iconType: 'document',
    },
    {
      id: 'wf-2',
      title: 'Stealth AI Startup Lead Scraper',
      description:
        'Targeting Series A/B founders in SF & Remote • 8 signals verified',
      badgeText: '+6 Pain Points',
      processedAgo: 'Processed 18m ago',
      status: 'running',
      iconType: 'search',
    },
    {
      id: 'wf-3',
      title: '48h Interview Intelligence Synthesizer',
      description:
        'Anthropic & Datadog interview question clusters generated',
      badgeText: 'Ready',
      processedAgo: 'Updated 1h ago',
      status: 'ready',
      iconType: 'interview',
    },
  ],
  activityDays: [
    { day: 'Mon', height: 60 },
    { day: 'Tue', height: 75 },
    { day: 'Wed', height: 50 },
    { day: 'Thu', height: 80 },
    { day: 'Fri', height: 95, isPeak: true },
    { day: 'Sat', height: 68 },
    { day: 'Sun', height: 35 },
  ],
  activitySummary: {
    title: 'Throughput & Match Accuracy (Last 7 Days)',
    precisionStat: 'Avg. 92.4% precision',
  },
  signals: [
    {
      id: 'sig-1',
      company: 'Cognition AI',
      companyInitial: 'C',
      role: 'Staff Systems Architect',
      compensation: '$175k - $190k',
      matchScore: 97,
      priorityLabel: 'Apply Priority: High',
      urgency: 'Active Evaluation',
    },
    {
      id: 'sig-2',
      company: 'Vercel Edge Labs',
      companyInitial: 'V',
      role: 'Distributed Runtime Lead',
      compensation: '$170k - $185k',
      matchScore: 94,
      priorityLabel: 'Quick Turnaround',
      urgency: 'Screening Open',
    },
    {
      id: 'sig-3',
      company: 'Datadog Core',
      companyInitial: 'D',
      role: 'Principal Cloud Architect',
      compensation: '$190k - $210k',
      matchScore: 91,
      priorityLabel: 'Deep Alignment',
      urgency: 'Interview Slotted',
    },
  ],
};

// ================= Mock Application CRM Data =================
export const mockApplicationCRMData: import('./types').ApplicationCRMData = {
  stats: {
    totalActive: { value: '18', delta: '+3 this week' },
    responseRate: { value: '42%', benchmark: 'vs 18% avg benchmark' },
    interviewConversion: { value: '28%', rating: 'Top 5% percentile' },
    pendingFollowUps: { value: '3', badge: 'Action required today' },
  },
  cards: [
    // Saved
    {
      id: 'crm-1',
      company: 'OpenAI',
      role: 'Member of Technical Staff, Infra',
      salary: '$240k - $300k',
      stage: 'saved',
      dateAdded: 'Added 2d ago',
      tags: ['GPU Clusters', 'Triton', 'Distributed'],
      priority: 'high',
      notes: 'Referral connection in Core Inference team.',
    },
    {
      id: 'crm-2',
      company: 'Vercel',
      role: 'Staff Platform Architect',
      salary: '$200k - $240k',
      stage: 'saved',
      dateAdded: 'Added 3d ago',
      tags: ['Edge Runtime', 'Turborepo', 'Next.js'],
      priority: 'medium',
    },
    {
      id: 'crm-3',
      company: 'Warp',
      role: 'Distributed Systems Lead',
      salary: '$190k - $230k',
      stage: 'saved',
      dateAdded: 'Added 4d ago',
      tags: ['Rust', 'Wasm', 'Networking'],
    },
    {
      id: 'crm-4',
      company: 'Cloudflare',
      role: 'Principal Edge Systems Eng',
      salary: '$210k - $260k',
      stage: 'saved',
      dateAdded: 'Added 5d ago',
      tags: ['Workers', 'V8 Isolates', 'Anycast'],
    },
    // Ready to Apply
    {
      id: 'crm-5',
      company: 'Neon',
      role: 'Staff Engine Architect',
      salary: '$200k - $250k',
      stage: 'ready',
      dateAdded: 'Ready 1d ago',
      tags: ['PostgreSQL internals', 'Rust', 'Storage'],
      priority: 'urgent',
      notes: 'Resume tailored with 96% ATS match.',
    },
    {
      id: 'crm-6',
      company: 'ClickHouse',
      role: 'Principal Data Infrastructure',
      salary: '$220k - $270k',
      stage: 'ready',
      dateAdded: 'Ready 2d ago',
      tags: ['C++', 'OLAP', 'SIMD Vectorization'],
    },
    // Applied
    {
      id: 'crm-7',
      company: 'Supabase',
      role: 'Head of Core Backend',
      salary: '$195k - $240k',
      stage: 'applied',
      dateAdded: 'Applied 6d ago',
      tags: ['PostgreSQL', 'Go', 'Elixir'],
      priority: 'medium',
    },
    {
      id: 'crm-8',
      company: 'Railway',
      role: 'Systems Runtime Engineer',
      salary: '$180k - $220k',
      stage: 'applied',
      dateAdded: 'Applied 1w ago',
      tags: ['Docker/Nomad', 'Rust', 'Networking'],
    },
    {
      id: 'crm-9',
      company: 'CockroachDB',
      role: 'Principal Query Optimizer',
      salary: '$210k - $255k',
      stage: 'applied',
      dateAdded: 'Applied 1w ago',
      tags: ['Raft Consensus', 'Distributed SQL'],
    },
    // Assessment
    {
      id: 'crm-10',
      company: 'Cursor',
      role: 'AI Code Graph Parsing Engine',
      salary: '$220k - $280k',
      stage: 'assessment',
      dateAdded: 'Due in 48h',
      tags: ['Tree-sitter', 'LLM Indexing', 'C++'],
      priority: 'urgent',
      notes: 'Architecture challenge: AST indexing under 50ms latency.',
    },
    {
      id: 'crm-11',
      company: 'Modal',
      role: 'Distributed Container Scheduler',
      salary: '$200k - $250k',
      stage: 'assessment',
      dateAdded: 'Due in 4d',
      tags: ['gVisor', 'Linux namespaces', 'Python'],
    },
    {
      id: 'crm-12',
      company: 'Temporal',
      role: 'Rust Memory Management Task',
      salary: '$195k - $235k',
      stage: 'assessment',
      dateAdded: 'Due in 5d',
      tags: ['State Machines', 'Deterministic Replay'],
    },
    // Interview Stage (Spotlighted)
    {
      id: 'crm-13',
      company: 'Datadog',
      role: 'Staff Distributed Systems Engineer',
      salary: '$215k - $260k',
      stage: 'interview',
      dateAdded: 'Round 3 of 5',
      tags: ['Kafka Streaming', 'Go', 'Geo-replication'],
      priority: 'urgent',
      roundDetails: 'System Architecture Onsite (Tomorrow 10:00 AM PST)',
      interviewer: 'David Chen (VP of Platform)',
      notes: 'Key focus: Zero-drop message pipelines & tail sampling collectors.',
    },
    {
      id: 'crm-14',
      company: 'Anthropic',
      role: 'Research Engineer, Serving Infra',
      salary: '$250k - $320k',
      stage: 'interview',
      dateAdded: 'Round 4 of 5',
      tags: ['Distributed Inference', 'KV-cache', 'Kubernetes'],
      priority: 'urgent',
      roundDetails: 'Distributed Systems Deep-dive (Thursday 2:00 PM PST)',
      interviewer: 'Elena Rostova (Lead Infra Scientist)',
    },
    {
      id: 'crm-15',
      company: 'Stripe',
      role: 'Staff Infrastructure Engineer',
      salary: '$230k - $285k',
      stage: 'interview',
      dateAdded: 'Bar Raiser Round',
      tags: ['Multi-region Active-Active', 'Fintech SLA'],
      priority: 'high',
      roundDetails: 'Bar Raiser Exec Review (Friday 11:30 AM PST)',
    },
    // Offer (Golden Trophy Glow)
    {
      id: 'crm-16',
      company: 'Linear',
      role: 'Staff Platform Architect',
      salary: '$225,000 Base',
      equity: '$450,000 Equity (4yr grant)',
      signOn: '$50,000 Signing Bonus',
      stage: 'offer',
      dateAdded: 'Offer Expires in 5 Days',
      tags: ['Sync Engine', 'SQLite', 'Tactile UI'],
      priority: 'urgent',
      notes: 'Full remote, unlimited PTO, $5k home office stipend.',
    },
  ],
};

// ================= Mock AI Job Discovery Data =================
export const mockJobDiscoveryData: import('./types').JobDiscoveryData = {
  stats: {
    verifiedMatches: { count: '48', delta: '+12 today' },
    newToday: { count: '14', label: 'High signal opportunities' },
    avgMatch: { percentage: '91.4%', note: 'Top 5% percentile calibration' },
    medianSalary: { amount: '$185k', delta: '+$20k over candidate base' },
  },
  jobs: [
    {
      id: 'job-1',
      company: 'Cognition AI',
      role: 'Staff Systems Architect',
      location: 'San Francisco, CA / Remote US',
      salary: '$190,000 - $240,000',
      matchScore: 96,
      matchPercentile: 'Top 1% Fit',
      verifiedType: 'direct',
      skills: ['Rust', 'Kubernetes', 'Distributed Raft', 'eBPF', 'Linux Kernel'],
      postedAgo: 'Posted 2h ago',
      summary:
        'Architecting low-latency autonomous agent code evaluation environments. Direct ownership over multi-tenant microVM sandboxes.',
      headcountApproved: true,
      dkimSignature: 'hr@cognition-labs.com · Cryptographically Signed (ed25519)',
      atsSyncStatus: 'Greenhouse API Sync Active · 1 Headcount Allocated',
      fundingTelemetry: 'Series A $21M confirmed on SEC Form D (Founders Fund lead)',
    },
    {
      id: 'job-2',
      company: 'Datadog',
      role: 'Staff Distributed Systems Engineer',
      location: 'New York, NY / Remote',
      salary: '$200,000 - $250,000',
      matchScore: 93,
      matchPercentile: 'Top 3% Fit',
      verifiedType: 'public',
      skills: ['Go', 'Kafka Streaming', 'Geo-replication', 'APM Telemetry'],
      postedAgo: 'Posted 5h ago',
      summary:
        'Core event pipelines handling 15TB/sec telemetry streams. Requires deep intuition for queueing theory and tail latency mitigation.',
      headcountApproved: true,
      dkimSignature: 'careers@datadoghq.com · Verified Public Key',
      atsSyncStatus: 'Workday Enterprise Sync · Priority requisition',
      fundingTelemetry: 'Publicly Traded (NASDAQ: DDOG) · $42B Market Cap',
    },
    {
      id: 'job-3',
      company: 'Vectra Labs',
      role: 'Founding Infra Engineer',
      location: 'San Francisco, CA (Hybrid / Remote)',
      salary: '$180,000 - $220,000 + 1.5% Equity',
      matchScore: 91,
      matchPercentile: 'Top 5% Fit',
      verifiedType: 'direct',
      skills: ['Vector Indexing', 'C++20', 'SIMD', 'GPU Memory Transfer'],
      postedAgo: 'Posted 8h ago',
      summary:
        'Building next-generation billion-scale vector indexes with sub-5ms HNSW lookups on sparse high-dimensional embeddings.',
      headcountApproved: true,
      dkimSignature: 'founders@vectralabs.ai · Verified YC W24 Batch',
      atsSyncStatus: 'Ashby Requisition #4092 Active',
      fundingTelemetry: 'Seed Round $4.5M closed Jan 2025',
    },
    {
      id: 'job-4',
      company: 'Warp Terminal',
      role: 'Principal Runtime Engineer',
      location: 'Remote US',
      salary: '$210,000 - $260,000',
      matchScore: 89,
      matchPercentile: 'Top 7% Fit',
      verifiedType: 'public',
      skills: ['Rust', 'Metal / Vulkan', 'PTY Virtualization', 'Wasm'],
      postedAgo: 'Posted 1d ago',
      summary:
        'Rendering and terminal protocol architecture. Delivering 120 FPS rendering on modern operating system compositor pipelines.',
      headcountApproved: true,
      dkimSignature: 'team@warp.dev · Verified Domain Key',
      atsSyncStatus: 'Lever API Integration Verified',
      fundingTelemetry: 'Series B $50M backed by Sequoia',
    },
  ],
};

// ================= Mock Freelance Finder Data =================
export const mockFreelanceData: import('./types').FreelanceData = {
  metrics: {
    activeLeads: { count: '28', badge: '+6 new today' },
    contactReady: { count: '12', label: 'Direct founder emails' },
    pitchesSent: { count: '9', note: '3 accepted & in sprint' },
    pipelineValue: { total: '$68,000', sprintAvg: 'Avg $11,500 / sprint' },
  },
  leads: [
    {
      id: 'free-1',
      company: 'Apex Ledger',
      contactName: 'Marcus Vance',
      contactRole: 'CTO & Co-Founder',
      fundingStage: 'Series A ($14M)',
      budget: '$8,000 – $15,000',
      sprintDuration: '2-3 Weeks Sprint',
      affinityMatch: 96,
      tags: ['Redis Cluster', 'Go', 'AWS Global Accelerator', 'Multi-Region'],
      bottleneckSummary:
        'Scaling latency spikes across Tokyo and Frankfurt clusters under 180k req/sec load. Redis cluster memory fragmentation and cross-region serialization overhead.',
      rawSignal:
        'CTO posted on GitHub issue thread about cross-datacenter Redis replication stall when transatlantic ping exceeds 140ms.',
      draftedPitch: `Hi Marcus,

Saw Apex Ledger is scaling multi-region transaction processing past 180k req/sec. Having spent 6 years hardening high-throughput distributed caching at enterprise scale, I noticed your team is likely confronting Redis active-active sync serialization overhead across transatlantic hops.

Could I share a 3-page teardown memo of how we solved this exact topology last quarter with zero lock contention?

Best regards,
Alex Mercer · Staff Distributed Systems Contractor`,
      status: 'contact_ready',
    },
    {
      id: 'free-2',
      company: 'ScrapeCraft AI',
      contactName: 'Sarah Jenkins',
      contactRole: 'Head of Engineering',
      fundingStage: 'Seed (YC W24)',
      budget: '$6,000 – $10,000',
      sprintDuration: '2 Weeks Sprint',
      affinityMatch: 92,
      tags: ['Python', 'Playwright', 'Residential Proxies', 'Anti-bot'],
      bottleneckSummary:
        'Founder tweeted about headless browser throttling issues blocking LLM training runs. Needs fault-tolerant residential proxy cluster orchestrated in Kubernetes.',
      rawSignal:
        'Twitter/X tweet: "Anyone know how to orchestrate 5,000 headless Chrome instances without getting memory-leaked into oblivion? Paying well for contract help."',
      draftedPitch: `Hi Sarah,

Saw your note regarding Chrome headless memory leaks at 5k concurrency. This is a notorious V8 render-process leak issue that standard pod restarts fail to curb cleanly.

I built a lightweight epoll-based process recycler that reduced browser memory consumption by 74% for a similar data crawler. Happy to plug this into your cluster this week.

Alex Mercer`,
      status: 'new',
    },
    {
      id: 'free-3',
      company: 'HealthVault AI',
      contactName: 'Dr. Aris Thorne',
      contactRole: 'VP of Platform',
      fundingStage: 'Series B ($35M)',
      budget: '$12,000 – $18,000',
      sprintDuration: '3 Weeks Sprint',
      affinityMatch: 88,
      tags: ['AWS', 'Terraform', 'HIPAA Audit', 'IAM Least-Privilege'],
      bottleneckSummary:
        'Audit period starts in 45 days. Seeking experienced AWS/Terraform contractor to automate HIPAA audit logs and least-privilege IAM policies with immutable CloudTrail storage.',
      rawSignal:
        'LinkedIn post: Urgent need for Staff DevOps/SecOps contractor with SOC2/HIPAA Terraform experience.',
      draftedPitch: `Dr. Thorne,

Noticed HealthVault is preparing for HIPAA compliance audit in 45 days. Having automated zero-trust IAM boundaries and tamper-proof CloudTrail logging for healthcare fintechs, I have turnkey Terraform modules ready to deploy.

Can guarantee full audit readiness within 14 business days.

Best, Alex Mercer`,
      status: 'pitch_sent',
    },
  ],
};

// ================= Mock Market & Skill Intelligence Data =================
export const mockMarketSkillsData: import('./types').MarketSkillsData = {
  metrics: {
    marketBaseP75: { value: '$215,000', delta: '+8.4% YoY acceleration' },
    equityMedian: { value: '$320,000', label: '4-Year grant median for Staff' },
    topSkillPremium: { value: '+26%', skill: 'eBPF & Kernel Bypass' },
    activeDemand: { value: '3,420 roles', location: 'Remote US & Tier 1 hubs' },
  },
  percentiles: [
    { label: 'P25', amount: '$160k', height: 45 },
    { label: 'P50 (Median)', amount: '$185k', height: 65 },
    { label: 'P75 (Target)', amount: '$215k', height: 85 },
    { label: 'P90 (Top 10%)', amount: '$255k', height: 100 },
  ],
  skills: [
    {
      id: 'sk-1',
      name: 'eBPF & Kernel Bypass',
      premium: '+26%',
      demandLevel: 'Extreme',
      difficulty: 'Expert',
      userStatus: 'In Progress',
      growthYoY: '+48%',
      description: 'Zero-overhead socket filtering and raw packet interception without kernel context switching.',
    },
    {
      id: 'sk-2',
      name: 'Distributed Raft Consensus in Rust',
      premium: '+22%',
      demandLevel: 'High',
      difficulty: 'High',
      userStatus: 'Mastered',
      growthYoY: '+34%',
      description: 'Deterministic state machine replication, leader election, and snapshotting under network partitions.',
    },
    {
      id: 'sk-3',
      name: 'Deterministic MicroVM Sandboxing (Firecracker)',
      premium: '+24%',
      demandLevel: 'Very High',
      difficulty: 'High',
      userStatus: 'Recommended Next',
      growthYoY: '+62%',
      description: 'Sub-5ms startup isolated container environments for multi-tenant agent execution.',
    },
    {
      id: 'sk-4',
      name: 'Vector Database & SIMD Indexing',
      premium: '+19%',
      demandLevel: 'Extreme',
      difficulty: 'Medium',
      userStatus: 'Mastered',
      growthYoY: '+88%',
      description: 'AVX-512 hardware accelerated cosine distance calculations on billion-scale embeddings.',
    },
  ],
  roadmap: [
    {
      step: 1,
      duration: '7-Day Sprint',
      title: 'eBPF Profiling & BCC Tooling Hands-on',
      description: 'Build ring-buffer telemetry listener capturing raw TCP retransmissions.',
      actionItem: 'Complete BCC C/Rust kernel probe module and verify zero packet drop on 10Gbps loopback.',
    },
    {
      step: 2,
      duration: '30-Day Milestone',
      title: 'Distributed Raft Consensus in Rust',
      description: 'Implement log replication, leader election, and snapshotting with deterministic partition testing.',
      actionItem: 'Pass Jepsen network chaos test suite with zero data corruption under split-brain scenarios.',
    },
    {
      step: 3,
      duration: '60-Day Mastery',
      title: 'Deterministic Sandboxing Architecture',
      description: 'MicroVM orchestration using Firecracker API for multi-tenant LLM code execution.',
      actionItem: 'Deploy prototype edge worker pool achieving sub-10ms warm container dispatch.',
    },
  ],
};

// ================= Mock Interview Intelligence Data =================
export const mockInterviewIntelData: import('./types').InterviewIntelData = {
  metrics: {
    readinessScore: { score: '88', benchmark: '/ 100 benchmark', delta: '+14% this sprint' },
    targetRound: { round: 'Round 03 of 05', totalRounds: '5 Rounds', focus: 'System Architecture' },
    questionClusters: { count: '24', rehearsed: '19 masterfully rehearsed', status: 'Active Evaluation' },
    mockRuns: { completed: '3', total: '5', remaining: '2 Left to complete' },
  },
  itinerary: [
    {
      id: 'it-1',
      day: 1,
      stepNumber: '1.1',
      title: 'Datadog Architecture Deep-Dive Review',
      description:
        'Reviewed Datadog open engineering blogs regarding zero-drop message pipelines and tail-sampling tracing collectors.',
      isComplete: true,
    },
    {
      id: 'it-2',
      day: 1,
      stepNumber: '1.2',
      title: 'Metrics Ingestion System Design Whiteboarding',
      description:
        'High-volume metrics ingestion pipeline with geo-partitioned multi-tenant storage fallbacks and ring buffer caching.',
      isComplete: true,
    },
    {
      id: 'it-3',
      day: 1,
      stepNumber: '1.3',
      title: 'Behavioral Incident Post-Mortem Defense',
      description:
        'Defended latency regression root cause analysis during Q4 2023 infrastructure re-platforming using STAR methodology.',
      isComplete: true,
    },
    {
      id: 'it-4',
      day: 2,
      stepNumber: '2.1',
      title: 'Split-Brain Isolation Scenario (Active Focus)',
      description:
        'Subject: "How would you design zero-data-loss cross-region replication when upstream broker partitions experience split-brain network isolation?"',
      isComplete: false,
      isActive: true,
    },
    {
      id: 'it-5',
      day: 2,
      stepNumber: '2.2',
      title: 'Live Coding: Concurrent Rate Limiter in Go',
      description:
        'Token bucket algorithm implementation with atomic CAS operations and distributed sync via Redis leases.',
      isComplete: false,
    },
  ],
  simulatorScorecard: {
    architectureDepth: 92,
    tradeoffClarity: 88,
    communication: 85,
  },
  phrasingRefinement: {
    raw: '"We just added caching using Redis so that the database doesn\'t get destroyed by queries."',
    aiRefinement:
      '"Implemented a distributed write-through Redis cluster caching layer with probabilistic early expiration (XFetch algorithm) to systematically eliminate cache stampedes under 50k QPS traffic surges."',
  },
  interviewerPersona: {
    archetype: 'Pragmatic Systems Architect',
    bias: 'High skepticism toward over-engineered microservices without empirical SLA data.',
    counselNote:
      'Favors simple decoupled architectures over hyper-complex consensus tricks. Always lead with failure domain boundaries and operational cost implications.',
  },
};

// ================= Mock Startup Pain Points Data (Page 1) =================
export const mockStartupPainPointsData: import('./types').StartupPainPointsData = {
  metrics: {
    catalogedPoints: { count: '128', delta: '+18% growth', sources: 'Scanned 14 sources' },
    highConfidence: { count: '42', conf: '+92% conf', status: 'Ready for pitch' },
    directFounderSignals: { count: '89', stages: 'YC, Seed, Ser A', issues: '89 verified issues' },
    bountiesPool: { count: '14', poolAmount: '$145k pool', note: 'Direct consulting opportunities' },
  },
  painPoints: [
    {
      id: 'pp-1',
      title: 'High LLM Token Latency in Multi-Tenant Agent Loops',
      companyStage: 'Series A',
      scrapedAgo: 'Scraped 3h ago',
      bottleneckAbstract:
        'Startups operating multi-turn reasoning agents are facing 12s+ p95 latency bottlenecks. Autonomous agent architectures performing sequential tree-of-thought operations experience exponential queueing delays when exceeding 4 concurrency workers per customer tenant.',
      matchScore: 92,
      verificationSource: 'HN + X Verified',
      founderQuotesCount: 18,
      companiesAffected: 6,
      bountyAmount: '$25,000',
      urgency: '92% Urgency',
      founderQuote: {
        quote:
          'We’re hemorrhaging Series A retention because agent responses take 14 seconds when calling dual embedding search. We’d pay $25k immediately to anyone who can build an edge streaming broker for this.',
        author: 'Karan S. (CEO @ Infra.ai)',
        source: 'Verified Hacker News Founder Thread',
      },
      tags: ['LLM Streaming', 'Multi-tenant', 'Kafka', 'Edge Brokers'],
    },
    {
      id: 'pp-2',
      title: 'PostgreSQL Connection Exhaustion under Spike Loads',
      companyStage: 'Seed (YC W24)',
      scrapedAgo: 'Scraped 7h ago',
      bottleneckAbstract:
        'Serverless container warmups on Fly.io / AWS ECS causing severe pooler starvations. Dev teams report PgBouncer connection leaks when serverless instances scale down ungracefully.',
      matchScore: 87,
      verificationSource: 'Discord Dev Hub',
      founderQuotesCount: 34,
      companiesAffected: 9,
      bountyAmount: '$12,000',
      urgency: '85% Urgency',
      founderQuote: {
        quote:
          'Every time our marketing email goes out, 80 serverless Lambdas spin up and completely overwhelm PgBouncer max client connections. Database locks up for 8 minutes.',
        author: 'Liam Vance (Co-Founder & CTO @ ScaleFlow)',
        source: 'Supabase & YC Founder Community',
      },
      tags: ['PostgreSQL', 'Connection Pooling', 'Serverless', 'PgBouncer'],
    },
    {
      id: 'pp-3',
      title: 'Docker Image Cold Start Delays in CI/CD Runners',
      companyStage: 'Series A ($8M)',
      scrapedAgo: 'Scraped 12h ago',
      bottleneckAbstract:
        'Heavy 4GB ML development containers taking 4.5 minutes to pull layers from GitHub Container Registry on dynamic runner nodes.',
      matchScore: 84,
      verificationSource: 'GitHub Discussions',
      founderQuotesCount: 12,
      companiesAffected: 4,
      bountyAmount: '$8,500',
      urgency: '79% Urgency',
      founderQuote: {
        quote:
          'Our engineers run 40 PR builds a day. Pulling PyTorch and CUDA layers repeatedly is costing us 3 hours of idle engineer time daily.',
        author: 'Maya Lin (VP Eng @ TensorForge)',
        source: 'GitHub Enterprise Issue #821',
      },
      tags: ['Docker eStargz', 'Container Registry', 'P2P Caching', 'CI/CD'],
    },
  ],
};
