# RightFit — Frontend Application

Sleek, minimal, high-fidelity frontend for **RightFit** (AI Career & Opportunity Intelligence Platform), faithfully crafted according to the design specification across **Page 1**, **Page 2**, and **Page 3** of the Figma design file.

---

## 📐 Completed Multi-Page Design Hierarchy

| Page in Figma | Node ID | Module / Section | Built Component | Key Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Page 3** | `5:3595` | **Homepage / Master Overview Dashboard** | [`src/app/page.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/app/page.tsx) | 4 Bento quick stat cards, 7-day activity visualizer, live workflow telemetry, high-value signals |
| **Page 2** | `5:3` | **Resume Intelligence & ATS Proof** | [`ResumeIntelligenceSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/ResumeIntelligenceSection.tsx) | Master Architecture resume, 94.8% ATS verification, core competencies matrix |
| **Page 2** | `5:538` | **Opportunity Intelligence** | [`OpportunityIntelligenceSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/OpportunityIntelligenceSection.tsx) | Time Budget Optimizer, Decision Velocity, 5-Metric Scoring Engine, Triage Dossier |
| **Page 2** | `5:968` | **Application CRM** | [`ApplicationCRMSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/ApplicationCRMSection.tsx) | 6-Stage Kanban Board (Saved, Ready, Applied, Assessment, Interview, Offer), Gmail sync, Stage transitions |
| **Page 2** | `5:1717` | **AI Job Discovery** | [`JobDiscoverySection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/JobDiscoverySection.tsx) | Semantic radar feed, discrete multi-filters, cryptographic DKIM & ATS API verification drawer |
| **Page 2** | `5:2181` | **Freelance Finder** | [`FreelanceFinderSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/FreelanceFinderSection.tsx) | High-bounty sprints ($8k–$18k), Tokyo/Frankfurt bottleneck teardown, editable proposal pitch card |
| **Page 2** | `5:2711` | **Market & Skill Intelligence** | [`MarketSkillsSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/MarketSkillsSection.tsx) | Real-time compensation percentiles (P25 to P90), skill arbitrage index, 7/30/60-day upskilling roadmap |
| **Page 2** | `5:3180` | **Interview Intelligence** | [`InterviewIntelligenceSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/InterviewIntelligenceSection.tsx) | Readiness index 88/100, 48h structured itinerary, AI simulator scorecard, interviewer archetype advice |
| **Page 1** | `3:7` | **Startup Pain Points** | [`StartupPainPointsSection.tsx`](file:///Users/abhaysharma/all_codes/untitled%20folder%203/src/components/sections/StartupPainPointsSection.tsx) | Cataloged founder pain points, $25k bounty from Infra.ai, verified quotes, solution architecture submission |

---

## 🖥️ Screen Layout & Responsive Design Philosophy

- **Zero Fixed-Width Cropping**: All containers scale fluidly (`max-w-[1560px] w-full h-[94vh]`) adapting cleanly to any browser viewport without awkward horizontal scrolling.
- **Left Tactile Graphite Pill Dock**: Reagle-style `#1a1c21` pill capsule with multi-layered box shadows (`0px 16px 32px -4px rgba(24,26,31,0.28)`), vertical micro-subtitle `INTEL 2025 NAV`, and active state highlights.
- **Frosted Glass Container**: `backdrop-blur-[24px]` with `rgba(244,245,248,0.78)` background and `rgba(255,255,255,0.85)` borders.
- **Seamless 1-Click Navigation**:
  - Click any icon in the **Left Tactile Dock** to instantly jump to that section.
  - Click any tab in the **Secondary Workflow Tabs** on the dashboard.
  - Click any quick link on the 4 Bento metric cards (`Audit ATS Proof →`, `View Kanban CRM →`, `Review Opportunities →`).
  - Use the breadcrumb **`← Overview`** button in the header bar to return to the Homepage Overview anytime.

---

## 🔌 Decoupled Backend Integration

All frontend interactions route cleanly through the abstracted service layer in `src/services/`:
- `src/services/apiClient.ts`: Modular fetch wrapper with error handling and mock toggle.
- `src/services/endpoints.ts`: REST endpoint contracts.
- `src/services/types.ts`: Clean TypeScript interfaces.
- `src/services/dashboardService.ts`: Decoupled methods (`getApplicationCRMData`, `getJobDiscoveryData`, `sendFreelancePitch`, etc.).

### To Connect Your Premade Backend:
1. Open `.env.local`
2. Change:
   ```env
   NEXT_PUBLIC_USE_MOCK_DATA=false
   NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
   ```
3. Your premade backend will immediately receive all API calls matching the contracts in `src/services/endpoints.ts`.

---

## 🚀 Running the Frontend

```bash
# Install dependencies
npm install

# Start local development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.
