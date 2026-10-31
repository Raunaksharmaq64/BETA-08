# Security & Privacy Review

## Core Protections Implemented

1. **Service-to-Service Authentication**:
   Core uses `INTERNAL_SERVICE_KEY` bearer authentication to communicate with LeadHunter. LeadHunter credentials are never exposed to browser clients or frontend code.

2. **Multi-Tenant Candidate Isolation**:
   Drafts, approvals, and saved freelance opportunities are strictly tied to the authenticated candidate's user ID (`user_id`). Access to another candidate's outreach data returns HTTP 404/403.

3. **Anti-Spam & Human Governance Gate**:
   - Automated message sending without explicit human approval is prohibited.
   - Cryptographic body hash guarantees that sent messages exactly match approved content.
   - Daily sending quotas (20 messages/day) prevent automated abuse.
   - Suppression checking blocks outreach to opted-out contacts immediately before dispatch.

4. **Network & Database Boundaries**:
   - Zero direct cross-service database access.
   - LeadHunter and Core databases run on isolated schemas and connection pools.

