# Lead to Freelance Opportunity Mapping

## Overview
A business lead is not inherently a freelance opportunity. `FreelanceService.map_lead_to_opportunity_fields()` transforms raw Google Maps business data into actionable project proposals.

## Classification Matrix

| Lead Technical Status | Classification State | Opportunity Synthesis | Required Skills |
| :--- | :--- | :--- | :--- |
| **No Website Listed** | `VERIFIED_OPPORTUNITY` | New Modern Website & Digital Presence | Web Development, Responsive Design, Domain & Hosting, Local SEO |
| **Broken Website (is_broken_website: True)** | `VERIFIED_OPPORTUNITY` | Website Restoration & Technical Redesign | Web Development, SSL Configuration, Performance Optimization, Mobile Responsive |
| **Rating < 4.0 with Reviews** | `POTENTIAL_FREELANCE_OPPORTUNITY` | Review Automation & Local SEO | Local SEO, Reputation Management, Customer Engagement |
| **Active Website & High Rating** | `DISCOVERED_LEAD` | Digital Optimization Audit | Digital Strategy, Technical Consulting, Audit |

## Anti-Hallucination Constraints
1. **No Fabricated Budgets**: If compensation/budget is not explicitly stated in the source, the budget field remains `None`.
2. **No Inferred Contacts as Verified**: Inferred emails are marked as `INFERRED` in `ContactEvidenceRecord`, never `VERIFIED`.
3. **No Fake Deliverables**: Proposals suggest standard capabilities matching candidate's verified skills.

