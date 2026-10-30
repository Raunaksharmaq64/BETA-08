# User Journeys & Experience Flows

- **Title:** RIGHT FIT End-to-End User Journeys
- **Purpose:** Maps out primary candidate and freelancer workflows through the platform.
- **Status:** DRAFT
- **Owner:** Product Design / UX (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Journey A: Job Seeker ATS Match & Application Tracking
1. **Onboarding:** Candidate signs up, uploads master resume (PDF), and sets target roles/locations.
2. **Analysis:** Core engine parses resume, extracts 25+ skills, and provides ATS improvement tips.
3. **Discovery:** Candidate searches for "Backend Engineer" roles. Engine returns matching listings sorted by `fit_score`.
4. **Inspection:** Candidate clicks on a top role (92% fit). Inspects exact matching skills (`FastAPI`, `PostgreSQL`) and 2 missing skills (`Kafka`, `Docker`).
5. **Application Preparation:** Candidate requests an AI tailored resume bullet and cover note draft.
6. **CRM Tracking:** Candidate applies directly on employer site and updates pipeline to `Applied`. System schedules a 7-day follow-up reminder.

## 2. Journey B: Freelance Agency Website Modernization Lead
1. **Discovery Setup:** Freelancer searches for "Dentists in Austin, TX" on the Freelance Opportunities tab.
2. **Scanning:** LeadHunter queries Maps API, finding 40 businesses. 6 have no website; 3 have 502 Bad Gateway errors.
3. **Auditing:** Engine generates a downloadable PDF audit report highlighting page load speed (4.2s) and broken SSL.
4. **Outreach:** Freelancer reviews the AI-generated redesign pitch, approves email dispatch via personal SMTP, and tracks replies automatically.

## 3. Journey C: Indie Developer Startup Bug Hunting
1. **Feed Monitoring:** Developer visits the Startup Insights tab.
2. **Opportunity Identification:** Engine highlights a Reddit post: *"Our SaaS database keeps timing out during spikes, need help with Postgres indexing."*
3. **Pitching:** Developer copies technical pitch talking points and founder Twitter/email to propose a consulting engagement.

## 4. Open Questions & TBDs
- [TBD] Multi-tenant team collaboration for agencies sharing leads.

