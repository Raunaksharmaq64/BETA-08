# Pitch Drafts & Explicit Assumptions Policy
## Workstream H Specification

- **Module:** `startup-intelligence`
- **Table:** `startup_pitch_drafts`
- **Frontend Route:** `/startups/[opportunityId]/pitch`

---

## 1. Candidate Capability Grounding

When a candidate requests an outreach pitch draft, Core constructs the proposal grounded strictly in confirmed skills from the candidate's profile and resume (`CandidateSkillRecord`):

- **No Hallucinated Credentials**: If a candidate does not have Kubernetes on their profile, the pitch will never claim they are a Kubernetes expert.
- **Tone Personalization**: Supports 3 distinct cadences:
  - `casual`: Conversational, warm founder-to-developer greeting.
  - `formal`: Executive consulting briefing with structured proposal.
  - `short`: 3-sentence direct inquiry suitable for LinkedIn or Twitter/X.

---

## 2. Mandatory 5-Point Assumptions Checklist

Every pitch draft includes an explicit, visible checklist of unconfirmed premises that the candidate must review:

1. **Assumption 1**: The startup is currently actively experiencing the observed technical bottleneck.
2. **Assumption 2**: The startup is open to engaging an external developer or contractor.
3. **Assumption 3**: The proposed solution fits their current technical roadmap.
4. **Assumption 4**: The company has allocated budget for technical improvements.
5. **Assumption 5**: The suggested expertise aligns with their internal engineering priorities.

---

## 3. Strict Safety Rule: NO AUTOMATIC SENDING

**Phase 10 does not authorize sending pitches.**
- Pitches remain local drafts stored in Core's `startup_pitch_drafts` table.
- No `Send` button exists in the frontend UI.
- The UI exposes only `Save Pitch Draft` and `Discard Changes`.
- Pitch drafts can be copied to the candidate's personal email or messaging client manually by the user.

