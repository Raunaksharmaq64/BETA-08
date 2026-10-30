# RIGHT FIT --- Master Implementation Blueprint

**Document:** Product requirements, architecture, phase-wise
implementation roadmap, engineering standards, migration strategy, and
documentation governance. **Product and existing project root:**
`RIGHT FIT/` --- already created by the project owner. **Approved
architecture:** Option A --- Hybrid Architecture. **Baseline:** 30
October 2026. **Status:** Planning baseline; no feature is claimed
implemented by this document.

> Implement phase by phase. Keep all new project files inside the
> existing RIGHT FIT root. Never create a nested root or duplicate
> project.

## How to use this blueprint

-   Read AGENTS.md and relevant feature docs before editing.
-   Inspect existing implementations before creating replacements.
-   Classify legacy capabilities as REUSE, API_INTEGRATION, REWRITE, or
    DROP with evidence.
-   Do not copy or modify legacy repositories without explicit approval.
-   Do not mark planned or placeholder work as implemented.
-   Update documentation in the same pull request as code.
-   Use TBD for unresolved decisions; never invent facts.
-   Keep each phase within its scope and exit criteria.
-   Never submit applications or send outreach without explicit user
    approval.
-   Respect source terms, API quotas, robots directives, rate limits,
    and access controls.

## Requirement language

-   MUST: release-blocking unless an ADR approves an exception.
-   SHOULD: strong recommendation; defer with reason.
-   MAY: optional.
-   TBD: unresolved decision.
-   NOT IMPLEMENTED: planned, not available.
-   VERIFIED: supported by test or reproducible evidence.
-   Store timestamps in UTC and display in user locale.
-   Explain meaning, evidence, limitations, and confidence for every
    score.

## Contents

1.  Product vision and problem statement
2.  Principles, boundaries, personas, journeys
3.  Nine product modules
4.  Hybrid architecture
5.  Legacy audit and reuse
6.  RIGHT FIT repository structure
7.  Domain model and contracts
8.  Multi-source Job Intelligence Engine
9.  Source catalogue and acquisition policies
10. Freshness, verification, trust, deduplication
11. AI, matching, ranking, explainability
12. Frontend architecture
13. Backend/API standards
14. Database ownership and migrations
15. Queues, events, background jobs
16. Security and privacy
17. Observability and operations
18. Testing and quality gates
19. Documentation governance
20. Phase-wise implementation roadmap
21. Acceptance criteria
22. Deployment
23. Risks and open decisions
24. Definition of done
25. Templates and detailed checklists

# 1. Product vision and problem statement

## 1.1 Product identity

RIGHT FIT is a Career Intelligence Platform, not merely a job board or
resume builder. It helps candidates discover trustworthy opportunities,
understand fit and eligibility, manage applications, prepare for
interviews, find freelance work, identify startup pain points, and
improve career readiness.

## 1.2 Problem statement

Candidates search across fragmented portals, company pages, communities,
and aggregators. Listings may be stale, duplicated, misleading, or
closed. Candidates cannot reliably determine original source, posting
date, last verification time, eligibility, missing skills, or whether a
match score is meaningful. Application progress, interview preparation,
freelance opportunities, and market signals are scattered.

-   Candidates need broad but permission-aware discovery.
-   They need source provenance and last-check time.
-   They need separate skill fit, mandatory eligibility, trust, and
    freshness.
-   They need evidence-backed resume and interview guidance.
-   They need application tracking and next actions.
-   They need freelance and startup opportunity discovery with source
    evidence.
-   They need market and compensation insights with sample size,
    geography, and date range.
-   They need privacy, export, deletion, and control over external
    actions.

## 1.3 Outcomes and boundaries

-   Reduce manual search and validation effort.
-   Increase confidence in provenance and current status.
-   Improve understanding of strengths, gaps, and eligibility.
-   Connect discovery to applications, preparation, and skills.
-   Unify job, freelance, and startup views without treating them as
    identical.
-   Show observed source coverage instead of claiming complete internet
    coverage.
-   Do not guarantee employment, interviews, salary, or job
    availability.
-   A search result/social post is not proof a vacancy is open.
-   An inaccessible page is not proof a job is fake.
-   AI edits and pitches remain drafts until reviewed.
-   Public visibility does not automatically permit scraping.

# 2. Principles, personas, and user journeys

### Evidence before confidence

Recommendations show evidence, source, timestamp, and limitations. -
Identify affected module and service owner. - Define dependency failure
behaviour. - Add a test proving the principle. - Record exceptions in an
ADR with owner and review date.

### Freshness is not posting age

Old jobs may remain open; new jobs may already be closed. Keep
timestamps separate. - Identify affected module and service owner. -
Define dependency failure behaviour. - Add a test proving the
principle. - Record exceptions in an ADR with owner and review date.

### Source independence

No single API, portal, search engine, or scraping vendor is the only
source. - Identify affected module and service owner. - Define
dependency failure behaviour. - Add a test proving the principle. -
Record exceptions in an ADR with owner and review date.

### Permission-aware acquisition

Prefer official APIs, licensed feeds, public ATS endpoints, permitted
pages, and partnerships. - Identify affected module and service owner. -
Define dependency failure behaviour. - Add a test proving the
principle. - Record exceptions in an ADR with owner and review date.

### Human approval

No application submission or outreach sending without explicit
approval. - Identify affected module and service owner. - Define
dependency failure behaviour. - Add a test proving the principle. -
Record exceptions in an ADR with owner and review date.

### Explainable scores

Skill fit, eligibility, trust, freshness, and confidence remain
separate. - Identify affected module and service owner. - Define
dependency failure behaviour. - Add a test proving the principle. -
Record exceptions in an ADR with owner and review date.

### Service ownership

Each service owns its database, migrations, and domain rules. - Identify
affected module and service owner. - Define dependency failure
behaviour. - Add a test proving the principle. - Record exceptions in an
ADR with owner and review date.

### Frontend replaceability

Frontend consumes versioned APIs and owns no canonical business rules. -
Identify affected module and service owner. - Define dependency failure
behaviour. - Add a test proving the principle. - Record exceptions in an
ADR with owner and review date.

### Honest documentation

Unknown, planned, implemented, verified, deferred, and deprecated are
distinct. - Identify affected module and service owner. - Define
dependency failure behaviour. - Add a test proving the principle. -
Record exceptions in an ADR with owner and review date.

### Privacy by default

Minimise candidate data, protect resumes, restrict scopes, support
retention/deletion. - Identify affected module and service owner. -
Define dependency failure behaviour. - Add a test proving the
principle. - Record exceptions in an ADR with owner and review date.

### Graceful degradation

One failed connector/service must not take down the platform. - Identify
affected module and service owner. - Define dependency failure
behaviour. - Add a test proving the principle. - Record exceptions in an
ADR with owner and review date.

## 2.1 Personas

-   Primary: student, fresher, early-career, experienced candidate, or
    career switcher.
-   Secondary: mentor/placement support user, platform administrator,
    internal quality analyst.
-   Candidate controls their personal data and all external actions.

## 2.2 Main candidate journey

1.  Register and review privacy/consent.
2.  Complete education, experience, location, target role, and
    preferences.
3.  Upload/build resume and review extracted facts.
4.  Confirm skills and evidence.
5.  Set job preferences and eligibility constraints.
6.  Discover multi-source jobs with provenance and freshness.
7.  Review fit, eligibility, trust, compensation, and missing
    requirements separately.
8.  Save, dismiss, shortlist, or add to CRM.
9.  Prepare resume/interview plan with review.
10. Track application and reminders.
11. Review skill demand and improve profile.
12. Export or delete personal data.

## 2.3 Opportunity lifecycle

1.  Discovered.
2.  Normalized.
3.  Deduplicated or grouped as possible duplicate.
4.  Verified with timestamp and method.
5.  Ranked for relevance.
6.  Presented with evidence.
7.  Saved or dismissed.
8.  Applied/contacted only after user action.
9.  Closed, expired, withdrawn, or unavailable when evidence supports
    it.
10. Archived under retention policy.

# 3. Nine product modules

## Overview Dashboard

**Purpose:** Candidate home for opportunities, activity, applications,
interview tasks, and skill signals.

### Functional requirements

1.  Personalised opportunity summary and drill-downs
2.  Freshness summary separates new discovery from recent verification
3.  Application counts reconcile with CRM
4.  Upcoming interviews and preparation tasks
5.  Saved jobs and new matches
6.  Skill-gap summary from explainable job demand
7.  Freelance/startup summaries when enabled
8.  Useful empty states
9.  Accessible responsive widgets

### Owned data

-   Candidate profile
-   Opportunities
-   Applications
-   Interviews
-   Skill insights

### API surface

-   Dashboard aggregation
-   Candidate summary
-   Opportunity feed
-   Application summary

### Acceptance tests

-   Counts reconcile
-   User isolation
-   Partial data state
-   Responsive and accessible

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Resume Intelligence

**Purpose:** Extract candidate evidence while preserving review and
control.

### Functional requirements

1.  Secure PDF/DOCX upload initially
2.  Validate size, MIME, extension, parser limits, malware strategy
3.  Private file storage and short-lived access links
4.  Extract contact, education, experience, projects, certifications,
    skills, achievements
5.  Show section/page evidence
6.  Allow correction/removal/confirmation
7.  Build profile only from confirmed facts
8.  Detect inconsistency without rewriting facts
9.  Job-specific ATS keyword coverage with evidence
10. Suggestions must not invent experience
11. Multiple versions and version history
12. Parser version and extraction timestamp
13. Export, replacement, retention, deletion
14. Control third-party AI processing

### Owned data

-   Resume file metadata
-   Extraction result
-   Candidate profile
-   Skill evidence
-   Resume versions

### API surface

-   Upload
-   Parse task
-   Extraction result
-   Profile correction
-   Secure file

### Acceptance tests

-   Parser regression
-   Evidence traceability
-   Private access
-   Correction persistence
-   Deletion

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## AI Job Discovery

**Purpose:** Discover relevant jobs across independent, permission-aware
sources.

### Functional requirements

1.  Prioritise employer pages and public ATS endpoints
2.  Audit/reuse existing ATS adapters before replacement
3.  Support official APIs and licensed feeds
4.  Public-page extraction only where permitted
5.  Search/news/community results are leads, not proof
6.  Maintain source registry and policy review
7.  Independent connectors and failure isolation
8.  Canonical normalization
9.  Preserve source URL, ID, retrieval metadata, timestamps
10. Deduplicate while retaining source observations
11. Separate posted/discovered/seen/verified/status timestamps
12. Verify application URL with bounded retries
13. Timeout/block/CAPTCHA is not proof of fake/closed
14. Filter role, skill, location, mode, type, experience
15. Show source, posted, discovered, last checked
16. Collect stale/duplicate/broken-link reports
17. Admin source health and coverage
18. Budgets, concurrency, backoff, circuit breaker, kill switch
19. Disclose observed latency and coverage

### Owned data

-   Source registry
-   Source observation
-   Canonical job
-   Source-job mapping
-   Verification history
-   Candidate preferences

### API surface

-   Source registry
-   Job search
-   Job detail
-   Feedback
-   Source health

### Acceptance tests

-   Connector contracts
-   Freshness
-   Dedup quality
-   Outage isolation
-   Terms compliance
-   Expired suppression

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Opportunity Intelligence Engine

**Purpose:** Unify jobs, freelance leads, and startup pain points
without erasing type differences.

### Functional requirements

1.  Common opportunity envelope and typed payloads
2.  Preserve owning service and source record ID
3.  Type-specific detail endpoint
4.  Separate relevance from trust and eligibility
5.  Explain matched/missing evidence
6.  Retain source lineage and timestamps
7.  Deduplicate only with strong evidence
8.  Do not merge distinct requisitions
9.  Filter type/location/compensation/source/freshness/status
10. Saved searches and user-controlled alerts
11. Stable IDs and versioned contracts
12. Partial results during service outage

### Owned data

-   Opportunity envelope
-   Typed job/freelance/startup payloads
-   Source lineage

### API surface

-   Unified feed
-   Opportunity detail
-   Saved item
-   Feedback

### Acceptance tests

-   Contract compatibility
-   No cross-service DB
-   Partial failure
-   Evidence preservation

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Application CRM

**Purpose:** Manage applications and follow-ups with an auditable state
machine.

### Functional requirements

1.  Create from job or manually
2.  Statuses: saved, preparing, applied, assessment, interview, offer,
    rejected, withdrawn, archived
3.  Record applied_at, job, resume version, notes, contacts, next action
4.  Prevent accidental duplicates but allow distinct requisitions
5.  Status history and actor
6.  Reminders and follow-up dates
7.  Interview rounds and outcomes
8.  Apply click is not submission
9.  External submission requires separately approved integration
10. Export and deletion

### Owned data

-   Application
-   Status history
-   Job ref
-   Resume version
-   Interview
-   Reminder

### API surface

-   Application CRUD
-   Transition
-   Timeline
-   Reminder
-   Export

### Acceptance tests

-   State transitions
-   Duplicate prevention
-   History
-   Timezone
-   No false applied status

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Freelance Opportunity Finder

**Purpose:** Integrate LeadHunter as an independent freelance discovery
service.

### Functional requirements

1.  Call authenticated versioned LeadHunter APIs
2.  LeadHunter owns discovery, audits, contacts, outreach state
3.  Import relevant leads into unified opportunity view
4.  Preserve IDs and evidence
5.  Show observable need for service
6.  Separate verified from inferred contacts
7.  Draft outreach; approval before sending
8.  Track delivery only with provider evidence
9.  Respect suppression/anti-spam/rate limits
10. Prevent duplicate outreach
11. Allow disconnect without corrupting career data

### Owned data

-   Business
-   Lead
-   Website audit
-   Contact evidence
-   Outreach draft
-   Delivery event

### API surface

-   LeadHunter adapter
-   Lead import
-   Draft
-   Approval workflow

### Acceptance tests

-   Contract
-   Provenance
-   No unapproved send
-   Dedup
-   Isolation

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Startup Pain Point Discovery

**Purpose:** Discover startup problems from public community signals.

### Functional requirements

1.  Integrate Startups-problrms-hunter via versioned API
2.  Preserve source URL/publication/retrieval time
3.  Separate reported pain point from proposed solution
4.  Distinguish quotes from AI summaries
5.  Source diversity/corroboration informs confidence
6.  Repeated posts are not proof of market size
7.  Technology signals require evidence
8.  Pitch drafts include assumptions
9.  Contact discovery follows policy/privacy
10. Test JSON-to-Postgres migration if approved
11. Approval before pitch sending
12. Show source age/corroboration

### Owned data

-   Startup
-   Pain point
-   Evidence
-   Technology finding
-   Pitch draft
-   Source record

### API surface

-   Startup adapter
-   Pain point feed
-   Evidence detail
-   Pitch draft

### Acceptance tests

-   Provenance
-   Freshness
-   Dedup
-   Migration
-   No unsupported claims

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Market & Skill Intelligence

**Purpose:** Explain demand, skills, and compensation using disclosed
samples.

### Functional requirements

1.  Aggregate requirements over explicit time window
2.  Report sample/source mix/geography/method
3.  Separate platform sample from labour market estimate
4.  Skill co-occurrence and role clusters
5.  Only report trends with sufficient sample/time series
6.  Do not present scraped count as total market demand
7.  Compensation includes currency/geography/seniority/period
8.  Separate base/bonus/equity/benefits
9.  Label estimates; no fabricated salary
10. Link evidence where permitted
11. Compare roles and skill gaps
12. Record freshness/method version

### Owned data

-   Job aggregates
-   Skill taxonomy
-   Compensation observations
-   Methodology

### API surface

-   Market trends
-   Skill demand
-   Compensation
-   Methodology

### Acceptance tests

-   Sample disclosure
-   Geographic relevance
-   Time window
-   No false precision

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

## Interview Intelligence

**Purpose:** Prepare candidates using target role and confirmed
experience.

### Functional requirements

1.  Plan for selected job/interview date
2.  48-hour mode without guarantee
3.  Use job description and confirmed candidate evidence
4.  Likely topics with uncertainty
5.  Technical/behavioural/system design/role-specific prep
6.  STAR from user experience only
7.  Mock questions and answers
8.  Rubric feedback and concrete suggestions
9.  Track preparation tasks
10. Interview rounds/conflicts/debrief
11. Label generated content
12. No claim of private interview bank

### Owned data

-   Job detail
-   Candidate evidence
-   Prep plan
-   Question set
-   Answer feedback
-   Schedule

### API surface

-   Prep
-   Mock session
-   STAR story
-   Debrief
-   Schedule

### Acceptance tests

-   Evidence
-   No invented story
-   Rubric
-   Timezone
-   Privacy

### Common requirements

-   Loading, empty, success, partial, stale, and error states
-   Confirm irreversible actions
-   Stable IDs, pagination, accessible controls
-   Explicit timezone
-   Logs exclude secrets and unnecessary personal data
-   Backend owns business rules
-   No direct cross-service DB query
-   Versioned contracts and compatibility tests
-   Export, deletion, rollback documentation

# 4. Selected hybrid architecture

Option A is approved: existing `agentic-career-search` evolves into Core
Career Engine after audit; LeadHunter and Startup Intelligence remain
independent API services; one unified Next.js frontend presents RIGHT
FIT.

### Next.js frontend

Presentation, navigation, accessible UI, API clients, forms, approval
flows; no canonical business rules.

### Core Career FastAPI

Auth, candidate profile, resume, job orchestration, matching,
opportunity aggregation, CRM, interviews, market intelligence after
audit.

### LeadHunter FastAPI

Business discovery, audits, contacts, outreach drafts and delivery
events.

### Startup Intelligence FastAPI

Community ingestion, pain points, evidence, tech signals, pitch drafts.

### PostgreSQL

Separate service-owned DBs: career_core, leadhunter_db,
startup_intel_db.

### Redis

Queues: career_tasks, lead_tasks, startup_tasks, notification_tasks.

### Object storage

Private resumes/reports, encryption, lifecycle, short-lived signed
access.

### Nginx/API gateway

TLS, routing, request limits, security headers, rate limits, upstream
health.

## 4.1 Architecture invariants

-   No duplicate Core FastAPI without ADR.
-   No copying legacy repositories into RIGHT FIT initially.
-   No public internal service ports.
-   No cross-service database access.
-   No frontend calls to private ports.
-   No provider-specific data shape in UI.
-   No secrets in source control/browser bundles.
-   Optional service outage must not block core job search.

## 4.2 Example routing

  Public route                  Destination
  ----------------------------- ---------------------------------------
  `app.example.com`             Next.js frontend
  `api.example.com/api/v1/*`    Core Career API
  Internal integration routes   Core adapters to independent services

Exact domain, port, hosting topology, and budget remain TBD until
deployment planning. \# 5. Legacy codebase audit and reuse

## agentic-career-search

**Role:** Core Career Engine Inspect ATS adapters, resume parsing,
normalization, fit, decision traces, compensation, interview prep, CRM,
auth, migrations, tests, dependencies. Reuse only verified capabilities.

### Read-only audit checklist

-   Record repo path and commit hash.
-   Inventory runtime/framework/dependencies/entry
    points/routes/workers/schedules.
-   Inventory data models/migrations/storage/env vars.
-   Run tests and record exact output.
-   Inspect auth, privacy, secrets, logging.
-   Map capabilities to RIGHT FIT modules.
-   Choose REUSE/API_INTEGRATION/REWRITE/DROP with evidence.
-   List defects, risks, blockers, required tests.
-   Define API contract and owner.
-   Preserve repo until explicit migration approval.

## ai agents / LeadHunter AI

**Role:** Independent Freelance Opportunity Service Inspect FastAPI
endpoints, Next.js coupling, PostgreSQL/SQLModel, Celery/Redis,
SerpApi/Apify terms/quotas, website audits, contacts, SMTP/IMAP, scan
persistence, outreach safeguards. Integrate via API; do not copy UI.

### Read-only audit checklist

-   Record repo path and commit hash.
-   Inventory runtime/framework/dependencies/entry
    points/routes/workers/schedules.
-   Inventory data models/migrations/storage/env vars.
-   Run tests and record exact output.
-   Inspect auth, privacy, secrets, logging.
-   Map capabilities to RIGHT FIT modules.
-   Choose REUSE/API_INTEGRATION/REWRITE/DROP with evidence.
-   List defects, risks, blockers, required tests.
-   Define API contract and owner.
-   Preserve repo until explicit migration approval.

## Startups-problrms-hunter

**Role:** Independent Startup Intelligence Service Inspect Reddit, RSS,
Product Hunt, BetaList, Hacker News, GitHub, Dev.to, IndieHackers,
Gemini prompts, tech detection, JSON persistence, evidence, contact
discovery. Integrate via API first.

### Read-only audit checklist

-   Record repo path and commit hash.
-   Inventory runtime/framework/dependencies/entry
    points/routes/workers/schedules.
-   Inventory data models/migrations/storage/env vars.
-   Run tests and record exact output.
-   Inspect auth, privacy, secrets, logging.
-   Map capabilities to RIGHT FIT modules.
-   Choose REUSE/API_INTEGRATION/REWRITE/DROP with evidence.
-   List defects, risks, blockers, required tests.
-   Define API contract and owner.
-   Preserve repo until explicit migration approval.

## 5.1 Decision definitions

-   REUSE: compatible, tested, maintainable business logic.
-   API_INTEGRATION: preserve separate runtime/service and call through
    documented API.
-   REWRITE: evidence shows incompatibility, unacceptable risk, or
    critical missing requirement.
-   DROP: irrelevant, duplicated, non-compliant, or not worth
    maintaining.

# 6. RIGHT FIT repository structure

All new project files stay inside the existing RIGHT FIT root. Inspect
first and preserve contents. Never create nested RIGHT FIT or
`career-intelligence-platform`.

``` text
RIGHT FIT/
  frontend/
    public/{images,icons,fonts}/
    src/app/(auth)/
    src/app/(dashboard)/{overview,resume,jobs,opportunities,applications,freelance,startup-insights,market-intelligence,interview-prep,compensation,settings}/
    src/components/{ui,layout,shared,dashboard}/
    src/features/{auth,resume,jobs,opportunities,applications,freelance,startup-insights,market-intelligence,interviews,compensation}/
    src/{services,hooks,lib,types,config,styles}/
    tests/{unit,integration,e2e}/
    Dockerfile .dockerignore .env.example
  backend/
    app/core/
    app/api/v1/endpoints/
    app/modules/{auth,users,resume,jobs,matching,verification,applications,opportunities,interviews,compensation,market_intelligence,privacy}/
    app/integrations/{career_engine,leadhunter,startup_intelligence,ai_providers,job_sources}/
    app/workers/{tasks,shared}/
    alembic/ tests/{unit,integration,contract}/
    Dockerfile .dockerignore .env.example
  services/{leadhunter,startup_intelligence}/
  contracts/{common,auth,users,resumes,jobs,opportunities,applications,leads,pain_points}/
  infrastructure/{docker,nginx,aws,monitoring,backups}/
  docs/{product,architecture,development,standards,api,database,integrations,migration,deployment,security,testing,operations,decisions,runbooks}/
  scripts/{development,deployment,database,maintenance}/
  .github/workflows/
  docker-compose.yml docker-compose.prod.yml
  .env.example .gitignore .dockerignore .editorconfig .gitattributes
  Makefile README.md AGENTS.md
```

-   Use .gitkeep for intentionally empty directories.
-   Keep legacy repos outside RIGHT FIT until migration approval.
-   Keep service adapters in Core; do not duplicate legacy UI.
-   Contracts live in contracts/ and are linked from service docs.
-   Mark configuration templates TEMPLATE / NOT CONFIGURED.
-   Avoid redundant folders for appearance only.

# 7. Domain model and canonical contracts

## 7.1 Identity and ownership

-   RIGHT FIT owns internal UUIDs.
-   External provider IDs are namespaced separately.
-   URLs are evidence/locators, not universal primary keys.
-   One job may have multiple source observations and reposts.
-   Application is separate from job posting.
-   Job, freelance lead, startup pain point remain different types.

## 7.2 Canonical opportunity envelope

Illustrative only; validate against audited schemas before
implementation.

``` json
{
  "id": "uuid",
  "type": "job",
  "title": "string",
  "company": {"id": "string|null", "name": "string|null"},
  "source": {"service": "string", "provider": "string", "source_record_id": "string|null", "original_url": "uri"},
  "timestamps": {"date_posted": "datetime|null", "first_discovered_at": "datetime", "last_seen_at": "datetime|null", "last_verified_at": "datetime|null"},
  "status": {"lifecycle": "discovered|open|closed|expired|withdrawn|unknown", "verification": "verified_open|unverified|source_unavailable|closed|needs_review"},
  "evidence": [],
  "scores": {"skill_fit": "number|null", "eligibility": "pass|fail|unknown|needs_review", "trust": "number|null", "confidence": "number|null"},
  "schema_version": "1.0"
}
```

## 7.3 Contract rules

-   Explicit enums; reject unknown values safely.
-   Unknown remains null; do not invent defaults.
-   Include schema version and compatibility policy.
-   UTC ISO-8601 timestamps.
-   Preserve raw source values where useful and permitted.
-   Typed payloads per opportunity type.
-   Provenance for extracted/AI claims.
-   No secrets or unnecessary personal data in events.

## 7.4 Candidate evidence

-   Separate account identity from profile.
-   Profile: education, work, skills, projects, certifications,
    preferences, location.
-   Record skill evidence source.
-   A skill label without evidence is not verified proficiency.
-   Allow correction and removal.

# 8. Multi-source Job Intelligence Engine

## 8.1 Acquisition priority

1.  Employer career pages and public ATS endpoints.
2.  Official APIs and licensed feeds.
3.  Permitted public job-board pages/feeds.
4.  Search engines, news, communities, social posts as discovery leads.
5.  User-submitted opportunities, labelled until checked.

## 8.2 Source registry fields

-   Stable source ID/name/category.
-   Owner service and connector name.
-   Domain and permitted endpoint patterns.
-   Acquisition method and terms/permission review.
-   Robots/terms review URL and date where applicable.
-   Auth type and minimum scopes.
-   Rate limit, concurrency cap, request budget.
-   Polling interval and backoff policy.
-   Source timezone/date parsing rules.
-   Source-specific status mapping.
-   Last success/failure/current health.
-   Coverage limitations and known gaps.
-   Connector version, owner, review date.
-   Kill-switch and operator notes.

## 8.3 Connector lifecycle

1.  Register source and document permission.
2.  Define config and secrets.
3.  Implement bounded fetch/feed reader.
4.  Parse to source observation schema.
5.  Validate fields and preserve URL/source ID.
6.  Normalize dates/title/company/location/work mode.
7.  Persist observation and run metadata.
8.  Deduplicate against known records.
9.  Schedule verification where appropriate.
10. Emit downstream event.
11. Record metrics/errors/cursor.
12. Review health and policy periodically.

## 8.4 Failure isolation

-   One connector failure must not fail all job search.
-   Per-source timeout and concurrency.
-   Exponential backoff with jitter.
-   Circuit breaker for repeated failures.
-   Do not retry permanent errors indefinitely.
-   Persist cursor after successful page processing.
-   Idempotent ingestion.
-   Show partial results when relevant.
-   Alert on failures, zero-result anomalies, volume changes.

## 8.5 Search orchestration

-   Candidate filters and saved-search criteria.
-   Respect source budgets and freshness expectations.
-   Prioritise sources without starving others.
-   Bound interactive search time.
-   Background tasks for long-running discovery.
-   Return task ID/progress.
-   Separate discovery and verification status.
-   Return partial results with coverage metadata.
-   Empty response is not proof no jobs exist.

## 8.6 Freshness timestamps

-   date_posted: publisher claim.
-   first_discovered_at: first RIGHT FIT observation.
-   last_seen_at: latest source observation.
-   last_verified_at: latest status check.
-   status_changed_at: observed lifecycle change.
-   Old job may still be open; new job may already be closed.
-   Show timestamp and timezone.
-   Do not reset posting date on rediscovery.
-   Record repost evidence separately.

## 8.7 Suggested polling targets

Initial targets only; tune to terms, quotas, measured latency, and cost.
\| Source \| Target \| \|---\|---:\| \| Public ATS \| 5--10 min where
permitted \| \| Priority career pages \| 10--15 min \| \| Other career
pages \| 30--60 min \| \| Licensed APIs \| 5--15 min within quota \| \|
RSS \| 5--15 min \| \| Communities \| 15--30 min \| \| Previously open
jobs \| Adaptive \|

-   Use ETag/Last-Modified when supported.
-   Use authorised webhooks when available.
-   Never exceed source limits.
-   Use adaptive scheduling rather than global fixed polling.
-   Do not poll more often than permitted.

# 9. Source catalogue and acquisition policy

## ATS

A provider in this catalogue is a research target, not proof that API
access or scraping permission exists. \### Greenhouse

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Lever

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Ashby

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Workday

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### SmartRecruiters

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Workable

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Recruitee

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Personio

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### BambooHR

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Teamtailor

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Breezy HR

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Jobvite

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### iCIMS

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Oracle Recruiting

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### SAP SuccessFactors

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### ADP Recruiting

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### JazzHR

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Pinpoint

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Comeet

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Taleo

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

## Job boards and aggregators

A provider in this catalogue is a research target, not proof that API
access or scraping permission exists. \### LinkedIn Jobs

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Indeed

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Naukri.com

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Foundit

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Internshala

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Wellfound

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Glassdoor

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Cutshort

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Instahyre

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Hirist

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Shine

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### TimesJobs

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Freshersworld

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Apna

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Adzuna

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Jooble

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### ZipRecruiter

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### CareerBuilder

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Monster

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

## Community/discovery

A provider in this catalogue is a research target, not proof that API
access or scraping permission exists. \### Reddit hiring communities

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Hacker News --- Who is Hiring

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### GitHub organization announcements

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### GitHub issues explicitly mentioning hiring

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Product Hunt announcements

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### BetaList

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Dev.to

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Indie Hackers

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### RSS feeds

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Google Search

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Google News

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Company engineering blogs

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### University placement pages

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

### Government employment portals

-   Identify exact endpoint and acquisition method.
-   Prefer official API, public ATS endpoint, RSS, licensed feed, or
    partnership.
-   Review current terms, robots, rate limits, auth, regional
    restrictions.
-   Never bypass login, CAPTCHA, paywall, anti-bot controls.
-   Store original URL and source ID where available.
-   Separate publisher date from discovery/verification times.
-   Map status without losing raw value.
-   Add permitted fixture and connector contract test.
-   Configure rate limits, timeout, retry, circuit breaker.
-   Document connector limitations.

## 9.1 Source tiers

  --------------------------------------------------------------------------
  Tier                  Definition                     UI treatment
  --------------------- ------------------------------ ---------------------
  Primary               Employer-controlled page/ATS   Strong provenance;
                                                       show verification
                                                       time

  Licensed              Contractually permitted        Show provider and
                        feed/API                       freshness

  Secondary             Aggregator/repost              Show aggregator and
                                                       original link

  Discovery lead        Community/search/news/social   Label as lead until
                                                       original vacancy
                                                       verified

  User submitted        Candidate-provided             Label and
                                                       independently verify
  --------------------------------------------------------------------------

## 9.2 Source onboarding checklist

-   Relevant to candidate segment?
-   Official API/feed available?
-   Terms and permission reviewed?
-   Quota and request volume?
-   Stable job ID?
-   Reliable publication timestamp?
-   Original application URL?
-   Reliable open/closed status?
-   Missing/unreliable fields?
-   Expected update delay?
-   Monitoring owner?
-   Connector maintenance owner?
-   Disable procedure if access disallowed?

# 10. Freshness, verification, trust, and deduplication

## 10.1 Verification states

  -----------------------------------------------------------------------
  State                   Meaning                 UI behaviour
  ----------------------- ----------------------- -----------------------
  verified_open           Authoritative evidence  Show verified + checked
                          supports open           time

  unverified              Discovered,             Show unverified/source
                          confirmation incomplete 

  source_unavailable      Source                  Do not call fake/closed
                          unreachable/ambiguous   

  closed                  Reliable evidence says  Suppress active or show
                          applications closed     history

  expired                 Explicit expiry or      Mark expired
                          supported expiry policy 

  withdrawn               Employer/source         Mark withdrawn
                          withdrew listing        

  needs_review            Conflicting/ambiguous   Flag for review
                          evidence                
  -----------------------------------------------------------------------

## 10.2 Verification evidence

-   HTTP status and final URL after redirects.
-   Page title and relevant structured metadata.
-   Application button/form availability.
-   Explicit closed/filled signal.
-   Source API response and job ID.
-   Timestamp and verification method.
-   Content fingerprint or selected stable fields.
-   Error category: timeout, DNS, TLS, 403, 404, 410, CAPTCHA, rate
    limit, parser failure, unknown.
-   Retain only necessary evidence and respect source rules.

## 10.3 Separate dimensions

-   Freshness: when listing was observed/verified.
-   Trust: source provenance/evidence quality.
-   Eligibility: candidate meets mandatory constraints?
-   Skill fit: overlap of candidate evidence and job requirements.
-   Confidence: uncertainty in assessment.
-   Never collapse these into one unexplained score.

## 10.4 Deduplication

1.  Exact provider + source job ID.
2.  Canonical application URL.
3.  Employer identity/domain evidence.
4.  Title similarity and location.
5.  Description fingerprint with safeguards.
6.  Requisition ID extraction.
7.  Manual review/soft group when confidence is low.

-   Do not merge distinct requisitions just because title/company match.
-   Store canonical job and source observations.
-   Record merge rationale/confidence.
-   Support unmerge and audit history.
-   Preserve source posting dates and verification times.
-   Do not treat every repost as a new requisition.

## 10.5 Trust assessment and feedback

-   Prefer employer-controlled evidence.
-   Check domain/redirect consistency.
-   Flag suspicious payment requests or unrelated messaging channels.
-   Do not accuse fraud without evidence.
-   Show source type and trust rationale.
-   Allow user reports and admin review.
-   Measure false positives/negatives.
-   Do not use trust to infer skill fit.
-   Feedback: stale, duplicate, broken link, misleading description,
    suspected scam.
-   Rate-limit abuse and protect reporter privacy.

# 11. AI, matching, ranking, and explainability

## 11.1 Provider abstraction

-   Do not hard-code one LLM vendor.
-   Keep keys backend-only and in protected secrets.
-   Timeout, retry, usage logs, configured failover.
-   Validate output against typed schema.
-   Scraped content is untrusted and cannot override policy.
-   Deterministic eligibility separate from LLM interpretation.
-   Record model/version, prompt version, input references, generation
    time.
-   Minimise personal data sent to providers.
-   Provide deterministic fallback.

## 11.2 Separate scores

  ------------------------------------------------------------------------
  Dimension              Question               Output
  ---------------------- ---------------------- --------------------------
  Skill fit              Evidence matches       Score + matched/missing
                         required skills?       

  Eligibility            Mandatory constraints  Pass/fail/unknown/review
                         met?                   

  Trust                  Source/listing         Evidence label/score
                         evidence quality?      

  Freshness              When last checked?     Timestamp

  Confidence             How complete/reliable? Level + reason
  ------------------------------------------------------------------------

## 11.3 Explainability and prompt governance

-   Show matched skills and evidence.
-   Show missing/weak skills.
-   Show mandatory eligibility separately.
-   Mark inferred requirements.
-   Show source evidence and timestamps.
-   Explain ranking reasons.
-   Allow profile correction.
-   Version scoring rules.
-   Do not claim employer uses same criteria.
-   Version prompts.
-   Use structured outputs.
-   Test malicious job-page prompt injection.
-   Retrieved text cannot request secrets, policy changes, or messages.
-   Record invalid-output fallback.
-   Evaluate bias, hallucination, unsupported inference.

# 12. Frontend architecture

## Responsibilities

-   Present nine modules consistently.
-   Use typed API clients.
-   Keep business rules in backend.
-   Feature-owned components.
-   No direct private service calls from browser.
-   Handle loading/empty/partial/stale/offline/error.
-   Responsive desktop/tablet/mobile.
-   Keyboard, focus, contrast, labels, semantics.

## Design direction

-   RIGHT FIT identity.
-   Clean professional industry-ready UI.
-   Solid palette; no unnecessary gradients.
-   Avoid decorative AI visuals that reduce clarity.
-   Consistent real icons and labels.
-   Readable job/CRM data density.
-   Status badges only where meaningful.
-   Charts show units, dates, source.
-   Consistent forms/tables/dialogs/empty states.

## Component boundaries

-   Shared components domain-neutral.
-   Feature components own feature presentation.
-   API clients in service layer.
-   Hooks encapsulate client state, not business rules.
-   Routes compose features.
-   Avoid unrelated cross-feature imports.
-   Stable list keys/IDs.
-   Document complex props/interactions.

## Migration readiness

-   Every workflow has API documentation.
-   Statuses map to backend enums.
-   No critical business calculation only in UI.
-   No authoritative workflow state only in local storage.
-   Auth contract framework-independent.
-   File transfer contract documented.
-   Pagination/filtering server-defined.
-   Stable errors mapped to user-friendly copy.
-   E2E tests describe user outcomes.
-   New frontend uses same APIs without data migration.

## State resilience

-   Server is source of truth.
-   Optimistic updates rollback.
-   Prevent duplicate submissions.
-   Ignore stale requests after filter changes.
-   Persist only justified non-sensitive preferences.
-   Handle session expiry without losing unsaved work.
-   Show partial service availability.
-   Avoid shared caching of sensitive resume content.

# 13. Backend and API standards

## Boundaries

-   Use FastAPI/Pydantic if compatible with audited Core.
-   Thin routers; business logic in use cases/services.
-   Separate persistence models from API schemas.
-   Dependency injection for DB/auth/external clients.
-   Async I/O for network-bound work where appropriate.
-   Long scraping/parsing/AI tasks in workers.
-   Structured logs and correlation IDs.
-   Isolate integration adapters.
-   Avoid circular imports.

## API conventions

-   Prefix `/api/v1/`.
-   Plural resource names and consistent methods.
-   Validate body/query parameters.
-   Stable error codes and safe messages.
-   Pagination/filtering/sorting.
-   Idempotency keys for retryable operations.
-   Document auth scopes.
-   Timeouts and bounded retries.
-   Safe OpenAPI exposure.
-   Request/trace IDs.
-   No stack traces/secrets to clients.

## Background task API

-   Return task ID.
-   Expose status/progress/start/completion/safe error.
-   Idempotent task creation where needed.
-   Cancellation only when safe.
-   Persist task state across worker restart.
-   Do not expose Celery internals to frontend.

## 13.1 Response envelope

``` json
{"success":true,"data":{},"meta":{"request_id":"uuid","schema_version":"1.0"},"error":null}
```

For errors: success=false, data=null, error has stable code, safe
message, and optional field details.

# 14. Database ownership and lifecycle

  -----------------------------------------------------------------------
  Database                Owner                   Example data
  ----------------------- ----------------------- -----------------------
  career_core             Core Career             Users, profiles,
                                                  resumes, jobs, matches,
                                                  applications,
                                                  interviews, market data

  leadhunter_db           LeadHunter              Businesses, leads,
                                                  audits, contacts,
                                                  outreach

  startup_intel_db        Startup Intelligence    Startups, pain points,
                                                  evidence, technology
                                                  findings, pitch drafts
  -----------------------------------------------------------------------

## Schema rules

-   PostgreSQL and service-owned migrations.
-   snake_case and stable keys.
-   Foreign keys only inside owning DB.
-   No cross-service foreign keys.
-   Indexes based on measured query patterns.
-   Unique provider IDs within namespace.
-   Transactions for multi-record changes.
-   UTC timestamps.
-   No unnecessary raw payload retention.

## Data lifecycle

-   Retention for resumes, parsed text, logs, snapshots, reports.
-   Account export/deletion.
-   Backup retention and restore objectives.
-   Separate source retention from profile retention.
-   Minimise sensitive logs/analytics.
-   Encryption in transit/at rest.
-   Document deletion propagation to backups.

## Migration policy

-   Plan and expected counts/constraints.
-   Back up source DB/files.
-   Test in disposable environment.
-   Validate counts/checksums/foreign keys/samples.
-   Run app tests on migrated data.
-   Expand-contract for breaking schema.
-   Rollback and forward-fix options.
-   Record logs and approval.
-   Do not delete legacy data before reconciliation and approval.

# 15. Queues, events, and background jobs

-   career_tasks: ingestion, resume parsing, matching, interview
    generation, market aggregation.
-   lead_tasks: LeadHunter scans, audits, enrichment, approved outreach.
-   startup_tasks: community ingestion, pain point analysis, tech
    detection, pitch drafts.
-   notification_tasks: reminders and user notifications.
-   Separate worker concurrency/resource limits.
-   Timeouts, retries, dead-letter handling, idempotency.
-   No secrets/unnecessary resume text in queue payloads.

## 15.1 Event envelope

``` json
{"event_id":"uuid","event_type":"job.discovered","event_version":"1","occurred_at":"2026-10-30T12:00:00Z","producer":"career-source-worker","aggregate_id":"uuid","correlation_id":"uuid","data":{"job_id":"uuid"}}
```

-   Events are immutable facts, not RPC.
-   Consumers idempotent.
-   Version payloads and compatibility.
-   No secrets/unnecessary PII.
-   Outbox pattern where reliable DB-to-event is needed.
-   Define retention/replay.
-   Assume at-least-once delivery.

# 16. Security, privacy, and responsible automation

### Authentication and recovery

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Password hashing and credentials

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Session/token lifecycle

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Role and resource authorization

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Service-to-service authentication

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Secret storage and rotation

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### TLS

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### CORS/security headers

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Rate limiting/abuse prevention

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Input validation/output encoding

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### SQL injection protection

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### SSRF protection for URL fetchers

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### File validation and malware scanning

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Private resume/report storage

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Short-lived signed links

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### PII minimisation in logs

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### User consent/provider scopes

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Export and deletion

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Retention and backup lifecycle

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Audit logs

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Approval for applications/outreach

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Prompt injection defence

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Dependency/container scanning

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

### Incident response

-   Define protected assets and threat.
-   Identify owning service.
-   Specify secure default behaviour.
-   Document config/secrets.
-   Add automated test or repeatable check.
-   Log events without secrets.
-   Document response/recovery.

# 17. Observability, reliability, operations

## Telemetry

-   Structured logs: timestamp, level, service, env, request/correlation
    IDs.
-   API latency, errors, throughput, queue depth, worker
    duration/retries/failures.
-   Source fetch/parse success, discovered/changed counts, zero-result
    runs, quota.
-   Verification outcomes by state.
-   DB pool/query latency/storage/migration health.
-   Frontend performance and critical journey errors.
-   External provider latency/failures.
-   Alert thresholds based on observed baselines.

## Health

-   Liveness means process alive.
-   Readiness means required dependencies ready.
-   Optional sources are not Core liveness dependencies.
-   Detailed health only for authorised operators.
-   Graceful shutdown and safe worker acknowledgement.

## Reliability

-   Define SLIs before SLOs.
-   Measure p50/p95/p99.
-   Track freshness separately from API uptime.
-   Define RPO/RTO per DB.
-   Test restore, not just backup creation.
-   Failure drills for Redis/Postgres/providers/connectors.
-   Document degradation per module.

# 18. Testing and quality gates

## Test layers

-   Unit tests for domain rules/normalization.
-   Integration tests for DB/queues/adapters using fixtures/mocks.
-   Contract tests Core-to-LeadHunter and Core-to-Startup.
-   API tests auth/validation/pagination/errors/permissions.
-   E2E critical candidate journeys.
-   Migration tests.
-   Security tests auth/files/SSRF/prompt injection.
-   Load tests fan-out/ingestion/queues.
-   Accessibility tests.
-   Manual source-policy review before enabling connector.

## Tools

-   Backend pytest, HTTPX, coverage, type checking.
-   Frontend component tests, Playwright, accessibility.
-   OpenAPI/schema and consumer/provider contract tests.
-   Docker build and Compose smoke tests.
-   Dependency, secret, container scanning, static analysis.
-   Migration upgrade/downgrade tests where supported.

## Release gates

-   Formatting/lint.
-   Type checks.
-   Unit/integration tests.
-   Contract tests.
-   Critical E2E.
-   Migration review/test.
-   No unresolved critical security findings.
-   Docs updated.
-   Flags/rollback verified.
-   Product acceptance.

# 19. Documentation and migration governance

## docs/product/

-   product-overview.md
-   problem-statement.md
-   product-requirements.md
-   feature-catalog.md
-   personas-and-user-journeys.md
-   roadmap.md
-   non-goals.md

## docs/architecture/

-   system-architecture.md
-   service-boundaries.md
-   architecture-decisions.md
-   data-flow.md
-   service-communication.md
-   failure-modes.md

## docs/development/

-   development-setup.md
-   development-workflow.md
-   local-environment.md
-   troubleshooting.md
-   contribution-guide.md

## docs/standards/

-   coding-standards.md
-   naming-conventions.md
-   git-conventions.md
-   api-standards.md
-   documentation-standards.md
-   folder-ownership.md

## docs/api/

-   api-overview.md
-   authentication.md
-   error-handling.md
-   api-versioning.md
-   pagination-and-filtering.md

## docs/database/

-   database-architecture.md
-   schema-ownership.md
-   migration-policy.md
-   backup-recovery.md
-   indexing-and-performance.md
-   data-retention.md

## docs/integrations/

-   career-engine.md
-   leadhunter.md
-   startup-intelligence.md
-   integration-contracts.md
-   external-providers.md
-   job-source-registry.md

## docs/migration/

-   legacy-audit.md
-   reuse-matrix.md
-   compatibility-analysis.md
-   migration-roadmap.md
-   rollback-plan.md
-   frontend-migration-guide.md

## docs/deployment/

-   docker-guide.md
-   production-deployment.md
-   aws-deployment.md
-   nginx-configuration.md
-   rollback-procedure.md

## docs/security/

-   security-policy.md
-   secrets-management.md
-   privacy-and-data-retention.md
-   authentication-and-authorization.md
-   secure-file-handling.md
-   threat-model.md

## docs/testing/

-   testing-strategy.md
-   test-environments.md
-   quality-gates.md
-   api-contract-testing.md
-   source-connector-testing.md

## docs/operations/

-   observability.md
-   source-operations.md
-   incident-response.md
-   backup-restore-runbook.md
-   queue-operations.md

## docs/decisions/

-   README.md
-   ADR-001-hybrid-architecture.md
-   ADR-002-service-database-ownership.md
-   ADR-003-api-first-integration.md
-   ADR-004-job-provenance-and-freshness.md
-   ADR-005-human-approval-for-external-actions.md

## 19.1 Feature documentation template

1.  Feature name and stable ID.
2.  Status.
3.  Problem and outcome.
4.  Personas/permissions.
5.  User journey/edge cases.
6.  Functional/non-functional requirements.
7.  API endpoints and examples.
8.  Data entities and owner.
9.  State machine/transitions.
10. Dependencies/provider limits.
11. Security/privacy.
12. Failure/fallback.
13. Metrics/alerts.
14. Tests and evidence.
15. Acceptance criteria.
16. Known limitations/deferred scope.
17. Migration/compatibility.
18. Rollback.
19. Owner/review date.

## 19.2 Maintenance rules

-   Update docs in same PR as code.
-   Document every module/API/schema/integration/env
    var/queue/event/migration/deployment/security change.
-   Mark unimplemented items clearly.
-   Never describe code as implemented until verified.
-   Use synthetic valid examples.
-   Never include credentials or production identifiers.
-   Update changelog for user-visible changes.
-   Review architecture docs on boundary changes.
-   Review connector docs when provider terms/endpoints change.
-   Keep deprecation and removal dates.

## 19.3 Naming conventions

-   Python files/functions/variables: snake_case.
-   Python classes: PascalCase.
-   Constants: UPPER_SNAKE_CASE.
-   React components/TS types: PascalCase.
-   Hooks: useSomething.
-   TS variables/functions: camelCase.
-   DB: snake_case, consistent plural tables.
-   PK id; FK entity_id.
-   Timestamps created_at, updated_at, explicit domain times.
-   Booleans is\_*/has\_*/can\_\*.
-   Frontend routes/features: kebab-case where suitable.
-   Docs filenames: lowercase kebab-case.
-   Branches: feature/, fix/, refactor/, docs/, test/, chore/.
-   Commits: feat:, fix:, refactor:, docs:, test:, chore:, build:, ci:.

## 19.4 ADR template

``` markdown
# ADR-NNN: Decision title
## Status
Proposed | Accepted | Superseded | Deprecated
## Context
## Options considered
## Decision
## Rationale
## Consequences
## Security and privacy impact
## Migration and rollback
## Review date
```

# 20. Phase-wise implementation roadmap

Implement sequentially. Parallel work only after contracts and ownership
are stable. Do not start a later phase until exit criteria are accepted
or deferral is recorded.

## Phase 0 --- Repository discovery and legacy audit

**Goal:** Establish facts before changing code.

### Implementation tasks

1.  Confirm existing RIGHT FIT root and inspect files.
2.  Locate three legacy repos and record paths/commit hashes.
3.  Inventory languages, frameworks, entry points, APIs, workers,
    stores, env vars, deployment.
4.  Run tests read-only and record exact output.
5.  Map features to product modules.
6.  Classify capabilities REUSE/API_INTEGRATION/REWRITE/DROP.
7.  Inspect resume capabilities in agentic-career-search before building
    parser.
8.  Inventory claimed ATS adapters and verify actual behaviour.
9.  Audit LeadHunter providers, quotas, queues, persistence, outreach.
10. Audit startup sources, Gemini prompts, JSON persistence, evidence.
11. Create risk register, dependency matrix, open decisions.

### Exit criteria

-   No legacy files modified.
-   All repos/commits identified.
-   Feature evidence or explicit unknown.
-   Test results recorded.
-   Reuse matrix reviewed.

### Explicit exclusions

-   No migration.
-   No copying.
-   No rewrite/deploy.
-   No large dependency installation before audit.

### Deliverables

-   Legacy audit
-   Reuse matrix
-   Dependency inventory
-   ADRs
-   Risk register

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 1 --- Product foundation and governance

**Goal:** Create governed RIGHT FIT skeleton.

### Implementation tasks

1.  Create missing folders inside existing root.
2.  Create AGENTS.md.
3.  Create README with identity/architecture.
4.  Create dev, naming, API, DB, security, docs standards.
5.  Create hybrid and ownership ADRs.
6.  Add safe .gitignore/.editorconfig/.gitattributes/env examples.
7.  Add contribution and PR templates.
8.  Create docs index and feature template.
9.  Use .gitkeep; label templates honestly.
10. Add initial diagrams and ownership map.

### Exit criteria

-   Existing files preserved.
-   All files inside RIGHT FIT.
-   README links resolve.
-   AGENTS clear.
-   No secrets.
-   No false completion claims.

### Explicit exclusions

-   No full implementation.
-   No migration.
-   No fake prod config.
-   No duplicate Core.

### Deliverables

-   Governed repo
-   AGENTS
-   README
-   Docs skeleton
-   ADRs

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 2 --- Contracts and local foundation

**Goal:** Define service communication.

### Implementation tasks

1.  Confirm Core entry point after audit.
2.  Define API/error conventions.
3.  Define auth and service identity contracts.
4.  Define opportunity envelope and typed payloads.
5.  Define Core-to-LeadHunter contract.
6.  Define Core-to-Startup contract.
7.  Define DB ownership/migration boundaries.
8.  Define queue names/task contract.
9.  Create safe local Compose.
10. Add health checks.
11. Add mock providers.
12. Add contract tests.

### Exit criteria

-   Contracts reviewed/versioned.
-   No cross-service DB access.
-   Services start independently.
-   Health distinguishes liveness/readiness.
-   Contract tests pass.

### Explicit exclusions

-   No public production exposure.
-   No credentials in Git.
-   No premature event bus.

### Deliverables

-   OpenAPI
-   Schemas
-   Compose
-   Integration docs

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 3 --- Identity, profile, privacy

**Goal:** Build candidate foundation.

### Implementation tasks

1.  Adapt auth after audit.
2.  Account lifecycle/recovery.
3.  Candidate profile/preferences.
4.  Field validation/provenance.
5.  Resource auth and tenant isolation.
6.  Privacy/consent records.
7.  Export/deletion flows.
8.  Security audit events.
9.  Rate limiting/abuse.
10. Unit/API/auth tests.

### Exit criteria

-   Auth/profile work.
-   Cross-user tests pass.
-   Privacy settings persist.
-   Sensitive logs excluded.
-   Export/deletion tested.

### Explicit exclusions

-   No broad email scopes.
-   No public resume URLs.
-   No automatic outreach.

### Deliverables

-   Auth
-   Profile
-   Privacy
-   Security tests

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 4 --- Resume Intelligence

**Goal:** Create reviewed candidate evidence.

### Implementation tasks

1.  Inspect/reuse parser if reliable.
2.  Secure upload/validation.
3.  Parse task/status.
4.  Extract sections/skills evidence.
5.  Show evidence/confidence.
6.  Correction/confirmation.
7.  Resume versions/secure retrieval.
8.  ATS keyword analysis.
9.  Suggestions without invention.
10. Regression fixtures/deletion tests.

### Exit criteria

-   Upload/inspect/correct/version.
-   No fabricated facts.
-   Private access.
-   Recoverable parser errors.
-   Export/deletion tests.

### Explicit exclusions

-   No auto submission.
-   No unreviewed AI edits.
-   No unnecessary parsed-text retention.

### Deliverables

-   Resume APIs
-   Data model
-   Parser tests
-   Docs

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 5 --- Job source framework

**Goal:** Build registry and connectors.

### Implementation tasks

1.  Source registry schema/admin workflow.
2.  Source observation schema.
3.  Connector interface/lifecycle.
4.  Config, timeout, retry, rate limit, circuit breaker.
5.  Select ATS adapters after audit.
6.  Official API/permitted feeds.
7.  Normalizer/canonical schema.
8.  Persist provenance/timestamps.
9.  Source run logs/metrics.
10. Fixtures/contract tests.
11. Source policy gate.

### Exit criteria

-   Independent source controls.
-   Failure isolation.
-   Provenance retained.
-   Idempotent ingestion.
-   Rate limits enforced.

### Explicit exclusions

-   No restricted scraping.
-   Search results are not verified vacancies.
-   No complete coverage claim.

### Deliverables

-   Registry
-   Connector interface
-   Initial ATS
-   Normalizer

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 6 --- Verification and dedup

**Goal:** Make status trustworthy.

### Implementation tasks

1.  Independent timestamps.
2.  Verification states/evidence.
3.  Bounded permitted URL checks.
4.  Source-specific status interpretation.
5.  Retry/ambiguous handling.
6.  Dedup/source mappings.
7.  Repost and merge/unmerge audit.
8.  Stale/broken link feedback.
9.  Closed/expired suppression.
10. Duplicate evaluation fixtures.
11. Outage/false-positive tests.

### Exit criteria

-   Old open stays visible.
-   New closed not labelled open.
-   Unavailable not fake.
-   Distinct requisitions not merged.
-   Every check has time/method.

### Explicit exclusions

-   No unbounded crawling.
-   No anti-bot bypass.
-   No unsupported fraud accusation.

### Deliverables

-   Verification engine
-   Dedup
-   Freshness UI
-   Quality dashboard

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 7 --- Job search and matching

**Goal:** Deliver candidate discovery.

### Implementation tasks

1.  Search API/pagination.
2.  Role/location/work-mode/type/experience/source filters.
3.  Skill fit from confirmed evidence.
4.  Mandatory eligibility separately.
5.  Trust/freshness separately.
6.  Ranking and missing-skill explanations.
7.  Saved searches/user-controlled alerts.
8.  Source coverage/partial results.
9.  Ranking evaluation.
10. Accessibility/E2E.

### Exit criteria

-   Candidate discovers jobs.
-   Scores defined.
-   Filters consistent.
-   Original links preserved.
-   Partial results explained.

### Explicit exclusions

-   No opaque composite score.
-   No false eligibility.
-   No hidden paid ranking.

### Deliverables

-   Search UI/API
-   Matching
-   Methodology

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 8 --- CRM and interviews

**Goal:** Connect discovery to execution.

### Implementation tasks

1.  Application state machine.
2.  Save/apply tracking without assuming submission.
3.  Status history/notes.
4.  Reminders/calendar.
5.  Interview plans.
6.  48-hour mode.
7.  STAR from user evidence.
8.  Mock interview/rubric.
9.  Debrief/conflicts.
10. Notifications/preferences.
11. Lifecycle tests.

### Exit criteria

-   Auditable status.
-   Apply click not submission.
-   Prep grounded.
-   Timezone reminders.

### Explicit exclusions

-   No auto applications.
-   No invented stories.
-   No private interview bank.

### Deliverables

-   CRM
-   Interview Intelligence
-   Notifications

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 9 --- LeadHunter integration

**Goal:** Connect freelance service safely.

### Implementation tasks

1.  Complete API audit/contract.
2.  Authenticated Core adapter.
3.  Map leads to freelance opportunity.
4.  Preserve audit/contact evidence.
5.  Import/dedup.
6.  Outreach draft/approval.
7.  Track delivery only with provider evidence.
8.  Suppression/rate limits.
9.  Downtime/recovery tests.
10. Independent deployment docs.

### Exit criteria

-   Freelance view works.
-   LeadHunter deploys independently.
-   No DB coupling.
-   No unapproved send.

### Explicit exclusions

-   Do not copy UI.
-   No mass unsolicited outreach.
-   Inferred contact not verified.

### Deliverables

-   Adapter
-   Freelance UI
-   Approval
-   Integration tests

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 10 --- Startup Intelligence

**Goal:** Connect pain points with evidence.

### Implementation tasks

1.  Source-by-source audit.
2.  API/evidence contract.
3.  Integrate startup/pain point records.
4.  Preserve URL/publication/retrieval.
5.  Separate observation from AI summary.
6.  Dedup/corroboration.
7.  Technology findings/audit evidence.
8.  Pitch drafts with assumptions.
9.  Test JSON-to-Postgres migration if approved.
10. Downtime/partial tests.

### Exit criteria

-   Evidence/time shown.
-   AI summaries labelled.
-   Market claims disclose sample.
-   Service independently deployable.

### Explicit exclusions

-   No unsupported founder claims.
-   No auto pitch send.
-   No cross-service DB.

### Deliverables

-   Adapter
-   Pain point feed
-   Evidence UI
-   Migration report

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 11 --- Unified opportunities/dashboard

**Goal:** Unify types while preserving meaning.

### Implementation tasks

1.  Common envelope.
2.  Type-aware details.
3.  Unified filters/saved items.
4.  Lineage/dedup.
5.  Partial service failures.
6.  Dashboard summaries/drill-down.
7.  Feedback/relevance tuning.
8.  Contract/E2E tests.

### Exit criteria

-   Types distinguishable.
-   Evidence survives.
-   Counts reconcile.
-   One outage does not blank dashboard.

### Explicit exclusions

-   No universal trust score.
-   No duplicated UI rules.

### Deliverables

-   Unified engine
-   Dashboard
-   Aggregation contracts

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 12 --- Market and compensation

**Goal:** Add evidence-backed context.

### Implementation tasks

1.  Define permitted datasets/methodology.
2.  Aggregate skills by time window.
3.  Record sample/source/geography.
4.  Taxonomy/aliases.
5.  Role/skill trends.
6.  Compensation and currency.
7.  Separate base/total compensation.
8.  Confidence/sample disclosure.
9.  Skill-gap recommendations.
10. False precision tests.

### Exit criteria

-   Charts disclose date/sample.
-   Units clear.
-   No market-wide claim from biased sample.

### Explicit exclusions

-   No fabricated salary.
-   No unsupported predictions.

### Deliverables

-   Market APIs
-   Taxonomy
-   Compensation
-   Methodology

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 13 --- Production/AWS

**Goal:** Prepare deployment and recovery.

### Implementation tasks

1.  Choose AWS topology.
2.  Containerize services.
3.  Private networking/security groups.
4.  TLS/Nginx.
5.  Protected secrets.
6.  RDS or documented PostgreSQL.
7.  Private Redis.
8.  Object storage/lifecycle.
9.  Monitoring/logs/alerts/backups.
10. Restore/disaster tests.
11. Load/security/smoke tests.
12. Rollback/runbooks.

### Exit criteria

-   No public DB/Redis.
-   TLS works.
-   Backups restore.
-   Health/alerts work.
-   Repeatable deploy.
-   Rollback tested.

### Explicit exclusions

-   No prod secrets in Git.
-   No deploy before gates.

### Deliverables

-   Deployment docs
-   Infra templates
-   Runbooks
-   Release checklist

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

## Phase 14 --- Beta and improvement

**Goal:** Validate workflows and quality.

### Implementation tasks

1.  Small consented beta.
2.  Usability/data quality feedback.
3.  Freshness/connector metrics.
4.  Duplicate/broken-link metrics.
5.  Ranking usefulness/corrections.
6.  Privacy/security/support review.
7.  Evidence-based priorities.
8.  Retire weak/non-compliant sources.
9.  Review docs/ADRs.
10. Release notes/limitations.

### Exit criteria

-   Critical journeys work.
-   Quality baselines exist.
-   Limitations visible.
-   No critical security issue.
-   Support owner known.

### Explicit exclusions

-   No unrelated expansion before reliability.

### Deliverables

-   Beta report
-   Quality scorecard
-   Backlog
-   Release notes

### Execution record

-   Owner assigned before work.
-   Dates recorded only after approval.
-   Branch/PR references added after creation.
-   Actual test evidence linked.
-   Risks/deferred items have owner/review date.
-   Product acceptance recorded.
-   Exact documentation files linked.

# 21. Global acceptance criteria

-   Documented user problem/outcome.
-   User journey and permissions.
-   API/data contracts.
-   Explicit service owner.
-   Missing/stale/malformed/unavailable handling.
-   Unit/integration tests.
-   E2E critical journeys.
-   Security/privacy review.
-   Observability.
-   Accessible loading/empty/error/success states.
-   Migration/rollback.
-   No unapproved external action.
-   Docs match actual implementation.

## 21.1 Job discovery acceptance

-   At least two independent source categories before multi-source
    claim.
-   Each connector independently enabled/disabled.
-   Original URL/source name retained.
-   Posting date and discovery time separate.
-   Last verification visible.
-   Unavailable is not fake.
-   Duplicate grouping preserves lineage.
-   Closed/expired not shown verified open.
-   One outage does not block others.
-   Terms/limits documented.
-   Coverage claims match observations.

## 21.2 AI acceptance

-   Schema validation.
-   Untrusted content cannot override policy.
-   Unsupported facts not known.
-   Candidate facts grounded in confirmed evidence.
-   Confidence/uncertainty visible.
-   Provider fallback.
-   Prompt/model version tracked.
-   Sensitive data minimised and disclosed.

# 22. Deployment and environments

## Environments

-   Local with synthetic data/test credentials.
-   CI test with isolated DB/provider mocks.
-   Staging production-like, non-production data, restricted access.
-   Production least privilege, secrets, backups, monitoring, approved
    release.

## Docker

-   One Dockerfile per deployable service.
-   Pinned images/dependencies.
-   Non-root user where practical.
-   Health checks/graceful shutdown.
-   Exclude secrets/local DB/cache from build.
-   Separate dev/prod Compose.
-   Persistent volumes only where intended.
-   No secrets baked into image.
-   Document build args/runtime secrets.

## AWS

-   EC2 may host containers initially.
-   RDS for managed PostgreSQL if budget permits.
-   S3 for private resumes/reports with encryption/lifecycle.
-   Secrets Manager or equivalent.
-   Private networking/security groups.
-   TLS and DNS.
-   Billing alerts/resource budgets.
-   Size from measured load.
-   Keep PEM key backup securely, never only on server.

## Release safety

-   Immutable image versions.
-   Controlled migrations.
-   Health before traffic shift.
-   Known-good rollback image.
-   Do not destroy persistent volumes on deploy.
-   Staged rollout for breaking changes.
-   Verify logs/metrics/core journeys.

# 23. Risks and open decisions

### Source access changes

Risk: Terms/APIs/endpoints change. Mitigation: Registry, policy review,
connector isolation, alternate permitted sources.

### False freshness

Risk: Recent fetch may not mean open. Mitigation: Separate timestamps
and verification.

### False scam classification

Risk: Unavailable page looks suspicious. Mitigation: Use
source_unavailable/needs_review and evidence.

### Duplicate inflation

Risk: Reposts/aggregators inflate counts. Mitigation: Canonical records
and conservative merge.

### Provider costs

Risk: APIs and LLMs become expensive. Mitigation: Budgets, quotas,
caching, metrics, kill switches.

### Parser fragility

Risk: HTML changes break parsers. Mitigation: Fixtures, health metrics,
fallback sources, alerts.

### Service coupling

Risk: Core depends synchronously on all services. Mitigation: Timeouts,
partial results, async aggregation.

### Legacy defects

Risk: Prior audit incomplete. Mitigation: Read-only audit/tests before
reuse.

### Privacy leakage

Risk: Resume/contact data sensitive. Mitigation: Minimisation,
encryption, access, retention, audit.

### AI hallucination

Risk: Generated content invents facts. Mitigation: Evidence grounding,
schemas, review, evaluation.

### Frontend migration cost

Risk: Rules leak into UI. Mitigation: Backend-owned rules, APIs, typed
clients, E2E.

### Operational overload

Risk: Many sources exceed budget. Mitigation: Prioritise, measure, limit
concurrency, phase rollout.

## 23.1 Open decisions --- keep TBD

-   Auth/session after Core audit.
-   Exact Next.js/Python versions after compatibility review.
-   Hosting topology and budget.
-   Object storage provider.
-   LLM providers/models; abstraction required.
-   Source-by-source permission/API/quota.
-   Retention periods after privacy/legal review.
-   Skill taxonomy and compensation sources.
-   Service authentication mechanism.
-   Monitoring stack.
-   Beta metrics and thresholds.

# 24. Definition of done

## Product

-   Solves documented problem.
-   UI discoverable/understandable.
-   Happy path and edge cases work.
-   Recover from common errors.
-   No misrepresented data/AI certainty.
-   Accessible/responsive.
-   User controls external actions.

## Engineering

-   Standards followed.
-   Contracts/schemas versioned.
-   DB migrations included.
-   CI tests pass.
-   Logs/metrics added.
-   Security review complete.
-   No secrets/private data committed.
-   Docs/examples updated.
-   Rollback/compatibility considered.

## Release

-   Scope/owner recorded.
-   Acceptance checked.
-   Known issues documented.
-   Migrations/backups confirmed.
-   Flags/kill switches configured.
-   Monitoring active.
-   Support contacts known.
-   Smoke tests pass.
-   Release notes published.
-   Product owner approves.

# 25. Templates and appendices

## 25.1 Status vocabulary

  Status        Meaning
  ------------- -----------------------------------------------
  Proposed      Requirement under consideration
  Planned       Assigned to roadmap phase
  In progress   Work started
  Implemented   Code exists; acceptance evidence pending
  Verified      Acceptance/tests passed
  Deferred      Postponed with reason/review date
  Deprecated    Scheduled for replacement
  Removed       No longer supported; migration notes retained

## 25.2 Reuse matrix template

  ------------------------------------------------------------------------------
  Capability   Legacy   Evidence   Decision          Changes   Tests    Owner
               repo                                                     
  ------------ -------- ---------- ----------------- --------- -------- --------
  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       

  TBD          TBD      TBD        REUSE /           TBD       TBD      TBD
                                   API_INTEGRATION /                    
                                   REWRITE / DROP                       
  ------------------------------------------------------------------------------

## 25.3 API contract review

-   Stable identity?
-   Validated request?
-   Versioned response?
-   Safe stable errors?
-   Pagination/filtering documented?
-   Resource authorization?
-   Timeout/rate limits?
-   Idempotency?
-   Events/callbacks?
-   Compatibility/deprecation?
-   Synthetic valid examples?
-   Contract tests?

## 25.4 Database migration review

-   Reversible or forward-fix?
-   Large-table lock risk?
-   Old app coexistence?
-   Bounded resumable backfill?
-   Safe index creation?
-   Nullability/defaults correct?
-   Constraints validated?
-   Counts/checksums compared?
-   Backup/restore tested?
-   Rollback owner assigned?

## 25.5 Source connector review

-   Relevant source?
-   Permitted acquisition?
-   Terms/limits reviewed?
-   Timeout/retry/circuit breaker?
-   Independent kill switch?
-   Source ID/URL retained?
-   Timestamps mapped?
-   Fixtures maintained?
-   Duplicate/status tests?
-   Metrics/alerts?
-   Outage behaviour?
-   Owner/review date?

## 25.6 Incident template

``` markdown
# Incident: <title>
## Summary
## Start/end time (UTC)
## Affected services/users
## Severity and impact
## Detection
## Timeline
## Root cause
## Contributing factors
## Resolution
## Data integrity assessment
## Security/privacy assessment
## Corrective actions, owners, due dates
## Documentation and tests updated
```

## 25.7 Pull request checklist

-   Requirement linked.
-   Service owner confirmed.
-   Existing implementation searched.
-   Contracts/DB reviewed.
-   Tests added and passing.
-   Security/privacy assessed.
-   Logs/metrics added.
-   Docs updated in same PR.
-   Migration/rollback included.
-   No unrelated refactor/dependency.

## 25.8 Product metrics

  -----------------------------------------------------------------------
  Metric                  Definition              Purpose
  ----------------------- ----------------------- -----------------------
  Source success rate     Successful runs /       Connector reliability
                          attempted runs          

  Freshness lag           Source update to RIGHT  Freshness
                          FIT observation where   
                          measurable              

  Verification coverage   Recently checked active Status quality
                          listings / active       
                          listings                

  Verified-open precision Sampled verified-open   Avoid false open
                          listings actually open  

  Broken-link rate        Sampled unusable        Candidate experience
                          application links       

  Duplicate rate          Duplicate records shown Search quality
                          / total records         

  Time to first relevant  Search request to       Speed
  result                  useful result           

  Match feedback          Useful/not useful       Ranking
                          candidate feedback      

  Application             Applications with       CRM
  completeness            current status/next     
                          action                  

  AI correction rate      Generated claims        Model quality
                          corrected by users      

  Service availability    Successful valid        Reliability
                          requests / total        

  Queue age               Oldest pending task age Worker capacity
  -----------------------------------------------------------------------

## 25.9 Engineering workflow

1.  Read requirement/docs.
2.  Inspect current implementation.
3.  Confirm service/data owner.
4.  Choose legacy reuse decision.
5.  Define contract before cross-service change.
6.  Plan schema/migration.
7.  Implement behind flag where useful.
8.  Add tests.
9.  Update docs/diagrams/ADRs.
10. Review security/privacy/observability/rollback.
11. Run CI and obtain acceptance.
12. Merge/release through approved process.

## 25.10 Coding-agent instructions

-   Read AGENTS.md/docs before edits.
-   Inspect before creating module.
-   Do not invent endpoints/fields/permissions/completion.
-   Do not modify legacy repos without approval.
-   Do not move root/create nested root.
-   No credentials in code/docs/logs/commits.
-   No access-control bypass.
-   No application/outreach without approval.
-   No deletion without tested migration/approval.
-   Keep scope to phase.
-   Run tests and report exact results.
-   Update docs in same change.
-   Stop for material unresolved architecture/security decision.

# 26. Focused implementation review checklists

## Overview Dashboard

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Resume Intelligence

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## AI Job Discovery

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Opportunity Intelligence Engine

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Application CRM

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Freelance Opportunity Finder

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Startup Pain Point Discovery

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Market & Skill Intelligence

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

## Interview Intelligence

Complete this review before implementation sign-off and repeat it before
a major migration or frontend replacement.

### Product and UX review

-   [ ] Confirm the exact candidate problem this capability solves.
-   [ ] Identify the user persona, permission level, and entry point.
-   [ ] Document the happy path from first action to completed outcome.
-   [ ] Document first-time and empty states.
-   [ ] Document partial-profile and incomplete-data states.
-   [ ] Document loading, progress, and long-running task states.
-   [ ] Document upstream timeout and unavailable-service states.
-   [ ] Document permission-denied and expired-session states.
-   [ ] Document duplicate submission and concurrent-edit behaviour.
-   [ ] Document destructive-action confirmation and recovery.
-   [ ] Document keyboard, focus, contrast, and screen-reader behaviour.
-   [ ] Document responsive layout for desktop, tablet, and mobile.

### API and service review

-   [ ] Confirm the owning service and module boundary.
-   [ ] Confirm whether existing code already provides the capability.
-   [ ] Define versioned request and response schemas.
-   [ ] Define stable error codes and safe user-facing messages.
-   [ ] Define authentication and resource-level authorization.
-   [ ] Define pagination, filtering, and sorting semantics.
-   [ ] Define idempotency for retryable writes.
-   [ ] Define timeout, retry, and circuit-breaker behaviour.
-   [ ] Define service-to-service authentication where applicable.
-   [ ] Define correlation IDs and structured operational events.
-   [ ] Define backward compatibility and deprecation policy.
-   [ ] Add consumer/provider contract tests.

### Data and migration review

-   [ ] Identify every entity and its owning database.
-   [ ] Define internal IDs separately from external provider IDs.
-   [ ] Define required, optional, and unknown fields.
-   [ ] Define uniqueness and duplicate-handling rules.
-   [ ] Define indexes from actual query patterns.
-   [ ] Define UTC timestamps and domain-specific time semantics.
-   [ ] Define state history and audit requirements.
-   [ ] Define evidence and provenance retention.
-   [ ] Define personal/sensitive fields and encryption requirements.
-   [ ] Define export and deletion behaviour.
-   [ ] Define schema migration and backfill strategy.
-   [ ] Define reconciliation and rollback evidence.

### Quality and operations review

-   [ ] Add unit tests for domain rules.
-   [ ] Add integration tests for persistence and dependencies.
-   [ ] Add API tests for validation and permissions.
-   [ ] Add end-to-end tests for critical user outcomes.
-   [ ] Add failure tests for timeout, malformed data, and unavailable
    services.
-   [ ] Add security and privacy tests relevant to the feature.
-   [ ] Add metrics for latency, volume, failures, and data quality.
-   [ ] Add structured logs without secrets or unnecessary PII.
-   [ ] Define alerts and thresholds from observed baselines.
-   [ ] Write a runbook for common operational failures.
-   [ ] Document known limitations and deferred scope.
-   [ ] Attach actual acceptance evidence before marking verified.

### Module-specific acceptance evidence

-   [ ] The user-facing status matches the backend source of truth.
-   [ ] The feature works when optional integrations are unavailable.
-   [ ] The feature does not expose another user's data.
-   [ ] All important facts can be traced to a source or user-confirmed
    input.
-   [ ] The module's documentation links to API, data, test, and runbook
    pages.
-   [ ] The module can be rendered by a replacement frontend using
    documented APIs.

# 27. Phase handover and release checklists

## Phase 0 --- Repository discovery and legacy audit

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 1 --- Product foundation and governance

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 2 --- Contracts and local development foundation

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 3 --- Identity, candidate profile, and privacy

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 4 --- Resume Intelligence

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 5 --- Multi-source Job Intelligence foundation

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 6 --- Freshness, verification, and deduplication

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 7 --- Job search, filters, matching, and explainability

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 8 --- Application CRM and Interview Intelligence

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 9 --- LeadHunter integration and Freelance Finder

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 10 --- Startup Intelligence integration

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 11 --- Opportunity Intelligence and unified dashboard

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 12 --- Market, skills, and compensation intelligence

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 13 --- Production readiness, AWS, and operations

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

## Phase 14 --- Beta, evaluation, and continuous improvement

### Before handover

-   [ ] Confirm the phase scope and exclusions were respected.
-   [ ] Confirm all work is inside the existing RIGHT FIT project root.
-   [ ] Confirm legacy repositories were not modified without approval.
-   [ ] Confirm the service owner and product reviewer are recorded.
-   [ ] Confirm every changed API/schema has a version and compatibility
    note.
-   [ ] Confirm database changes have tested migrations.
-   [ ] Confirm secrets and personal data are absent from source
    control.
-   [ ] Confirm source acquisition remains within documented
    permissions.

### Evidence required

-   [ ] Link the implementation pull request and commit.
-   [ ] Link automated test and CI results.
-   [ ] Link updated product and feature documentation.
-   [ ] Link API contract and schema changes.
-   [ ] Link migration, reconciliation, and rollback evidence if
    relevant.
-   [ ] Link security/privacy review where applicable.
-   [ ] Link operational metrics, dashboard, or runbook changes.
-   [ ] Record known defects and deferred work with owners.

### Acceptance and closure

-   [ ] Check every exit criterion against actual evidence.
-   [ ] Verify no feature is described as complete when only a
    placeholder exists.
-   [ ] Verify user-visible copy accurately describes limitations.
-   [ ] Verify critical journeys in the running environment.
-   [ ] Record product owner acceptance and date.
-   [ ] Update roadmap status and next-phase dependencies.
-   [ ] Create follow-up work only for in-scope, justified requirements.
-   [ ] Do not start dependent phase until acceptance or approved
    deferral.

# 28. Frontend replacement and service migration playbook

## Before replacing the frontend

-   [ ] Freeze and document the current API contract versions.
-   [ ] Inventory all frontend routes and user journeys.
-   [ ] Map each route to backend APIs and permission scopes.
-   [ ] Record every status label and its backend enum.
-   [ ] Identify calculations or rules incorrectly located in the
    frontend.
-   [ ] Move authoritative workflow state to backend-owned persistence.
-   [ ] Prepare typed API clients and contract tests.
-   [ ] Prepare E2E tests based on user outcomes, not component
    internals.
-   [ ] Confirm file upload/download and signed URL behaviour.
-   [ ] Confirm auth, session expiry, and CSRF/CORS behaviour.
-   [ ] Run the old and new frontend against the same staging APIs.
-   [ ] Compare critical flows and data consistency before cutover.
-   [ ] Keep rollback to the old frontend available until acceptance.

## Before replacing a backend service

-   [ ] Document service responsibilities and owned entities.
-   [ ] Document API/event versions and all consumers.
-   [ ] Export service-owned data in a documented format.
-   [ ] Prepare transformation and reconciliation scripts.
-   [ ] Run a shadow implementation against sampled traffic or fixtures.
-   [ ] Compare output and state transitions.
-   [ ] Verify authorization and tenant isolation.
-   [ ] Verify event idempotency and ordering assumptions.
-   [ ] Plan cutover and rollback with an explicit operator.
-   [ ] Do not retire the old service before data reconciliation and
    approval.

## Before changing a database schema

-   [ ] Identify all code and services that read/write affected fields.
-   [ ] Use expand-contract for breaking changes.
-   [ ] Add new nullable fields or compatible structures first.
-   [ ] Deploy readers/writers that support both versions where
    necessary.
-   [ ] Backfill in bounded, resumable batches.
-   [ ] Validate row counts, constraints, and sample records.
-   [ ] Switch reads only after reconciliation.
-   [ ] Remove old fields only after all consumers are migrated.
-   [ ] Test rollback and restore in a non-production environment.
-   [ ] Update schema docs and ADRs.

# 29. Job-source quality review

## Source access and policy

-   [ ] Confirm the source is relevant to a defined candidate segment.
-   [ ] Prefer official API, public ATS endpoint, licensed feed, RSS, or
    partnership.
-   [ ] Record the current terms and permitted use.
-   [ ] Record robots directives where applicable.
-   [ ] Record API quotas, request budgets, and commercial restrictions.
-   [ ] Do not bypass login walls, CAPTCHA, paywalls, or anti-bot
    controls.
-   [ ] Record a review date and connector owner.
-   [ ] Provide a kill switch if access becomes disallowed.

## Freshness and status

-   [ ] Store publisher posting date separately from first discovery.
-   [ ] Store last_seen_at separately from last_verified_at.
-   [ ] Record source timezone and date parsing rules.
-   [ ] Use conditional requests when supported.
-   [ ] Use adaptive polling within source limits.
-   [ ] Treat source timeout as unavailable, not closed.
-   [ ] Treat ambiguous redirect as needs_review.
-   [ ] Do not reset posting date merely because a job is rediscovered.
-   [ ] Retain status-change history.
-   [ ] Show the last successful check time.

## Duplicate and quality controls

-   [ ] Use source ID before fuzzy matching.
-   [ ] Preserve original URLs and all source observations.
-   [ ] Compare employer identity, title, location, requisition ID, and
    content.
-   [ ] Use conservative thresholds for automatic merge.
-   [ ] Keep uncertain matches as possible duplicates.
-   [ ] Support unmerge and audit history.
-   [ ] Sample verified-open listings for precision review.
-   [ ] Track broken-link and stale-report rates.
-   [ ] Review false positives and false negatives.
-   [ ] Use confirmed reports to improve fixtures and rules.

# 30. Document maintenance and change review

-   [ ] Update the feature document in the same pull request as code.
-   [ ] Update API documentation whenever a contract changes.
-   [ ] Update data dictionary and migration policy when schema changes.
-   [ ] Update architecture diagrams when service boundaries or data
    flows change.
-   [ ] Update security docs when auth, secrets, or personal data
    handling changes.
-   [ ] Update source registry when endpoints, permissions, quotas, or
    polling change.
-   [ ] Update runbooks when failure recovery changes.
-   [ ] Update release notes for user-visible changes.
-   [ ] Mark deprecated endpoints and fields with a removal plan.
-   [ ] Review this master blueprint at the end of each phase.

**Document owner:** RIGHT FIT product owner/team --- assign during Phase
0. **Next review:** End of Phase 0 and whenever an architecture decision
changes.

> This is a living engineering document. Add detail only when it
> improves implementation, testing, operations, security, or migration.
> Do not add unrelated scope or claim placeholders are complete.
