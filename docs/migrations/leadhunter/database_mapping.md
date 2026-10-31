# LeadHunter to RIGHT FIT Database Architecture & Entity Mapping

**Project:** RIGHT FIT — Freelance Intelligence Integration  
**Date:** 2026-10-31  
**Status:** MAPPED  

---

## 1. Architectural Principles

1. **Single Canonical Database:** RIGHT FIT owns the primary PostgreSQL database (with SQLite support for local dev/testing).
2. **Core Domain Authority:** The Core Career Engine is the single source of truth for all user identities, opportunities, contact evidence, and outreach logs.
3. **Tenant & User Isolation:** All candidate-specific records (saved opportunities, outreach drafts, notes, search history) are explicitly scoped to the candidate's Core UUID `user_id`.
4. **Idempotent Ingestion & Deduplication:** Multi-signal deduplication prevents duplicate opportunity records using `place_id`, `(business_name, city)`, and contact points.
5. **Contact Evidence Provenance:** Discovered contact information is preserved with audit provenance in `contact_evidence` records.
6. **No Runtime Remote Database:** The legacy LeadHunter PostgreSQL database is strictly not accessed at runtime.

---

## 2. Entity Mapping Matrix

| Original LeadHunter Table (`ai agents`) | Canonical RIGHT FIT Table (`rightFIT`) | Primary Key Type | Key Changes & Architecture Notes |
|:---|:---|:---:|:---|
| `users` | `users` | UUID (`String(36)`) | Reuses Core user accounts. LeadHunter integer user IDs are eliminated. |
| `leads` | `freelance_opportunities` | UUID (`String(36)`) | Lead attributes are normalized into canonical opportunity fields. Original LeadHunter ID preserved in `leadhunter_lead_id` for provenance. |
| Contact fields on `leads` (phone, email, website) | `contact_evidence` | UUID (`String(36)`) | Each discovered contact point is recorded with verification status (`OBSERVED`, `VERIFIED`), method, and timestamp. |
| `leads` bookmarks & notes | `saved_freelance_opportunities` | UUID (`String(36)`) | Stores candidate-saved leads, customized notes, and pipeline status. Foreign keys link to `users.id` and `freelance_opportunities.id`. |
| `message_log` (drafts) | `outreach_drafts` | UUID (`String(36)`) | Candidate-governed drafts. Tracks subject, body, proposed service, approval status (`is_approved`), and body hash for tamper detection. |
| `message_log` (sent messages) | `outreach_delivery_logs` | UUID (`String(36)`) | Audit log of dispatched messages, SMTP/API provider response codes, message IDs, and delivery statuses. |
| Unsubscribe / opt-outs | `outreach_suppression_list` | UUID (`String(36)`) | Suppressed contacts list. Prevents sending emails to unsubscribed recipients. |
| `search_history` | `freelance_search_history` | UUID (`String(36)`) | Stores historical searches per candidate (query, city, deep scan flag, zone filters, discovered count). |
| `smtp_settings`, `imap_settings`, BYOK keys | `freelance_candidate_settings` | UUID (`String(36)`) | Candidate-level encrypted BYOK keys (SerpApi, Apify, Gemini) and optional custom SMTP/IMAP credentials. |

---

## 3. Schema Definitions

### 3.1 `freelance_opportunities` (Already in Core)
```sql
CREATE TABLE freelance_opportunities (
    id VARCHAR(36) PRIMARY KEY,
    leadhunter_lead_id VARCHAR(64) INDEX,
    place_id VARCHAR(255) INDEX,
    business_name VARCHAR(255) NOT NULL,
    opportunity_title VARCHAR(255) NOT NULL,
    service_category VARCHAR(120) NOT NULL DEFAULT 'Web Development',
    description TEXT NOT NULL,
    city VARCHAR(120) NOT NULL INDEX,
    location VARCHAR(255),
    is_remote BOOLEAN NOT NULL DEFAULT TRUE,
    website VARCHAR(2000),
    is_broken_website BOOLEAN NOT NULL DEFAULT FALSE,
    rating FLOAT NOT NULL DEFAULT 0.0,
    reviews_count INTEGER NOT NULL DEFAULT 0,
    phone VARCHAR(50),
    email VARCHAR(255),
    required_skills JSON NOT NULL DEFAULT '[]',
    suggested_service VARCHAR(255),
    suggested_pitch TEXT,
    classification_state VARCHAR(50) NOT NULL DEFAULT 'POTENTIAL_FREELANCE_OPPORTUNITY' INDEX,
    classification_reason TEXT,
    relevance_score FLOAT NOT NULL DEFAULT 85.0,
    source VARCHAR(60) NOT NULL DEFAULT 'leadhunter_google_maps',
    original_source_url VARCHAR(2000),
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 3.2 `contact_evidence` (Already in Core)
```sql
CREATE TABLE contact_evidence (
    id VARCHAR(36) PRIMARY KEY,
    opportunity_id VARCHAR(36) NOT NULL REFERENCES freelance_opportunities(id) ON DELETE CASCADE INDEX,
    contact_type VARCHAR(30) NOT NULL, -- EMAIL, PHONE, WEBSITE, WHATSAPP
    contact_value VARCHAR(255) NOT NULL,
    source VARCHAR(60) NOT NULL DEFAULT 'leadhunter',
    source_evidence_url VARCHAR(2000),
    evidence_status VARCHAR(30) NOT NULL DEFAULT 'OBSERVED',
    verification_method VARCHAR(60),
    verification_notes TEXT,
    discovered_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 3.3 `saved_freelance_opportunities` (Already in Core)
```sql
CREATE TABLE saved_freelance_opportunities (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE INDEX,
    opportunity_id VARCHAR(36) NOT NULL REFERENCES freelance_opportunities(id) ON DELETE CASCADE INDEX,
    status VARCHAR(30) NOT NULL DEFAULT 'SAVED',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(user_id, opportunity_id)
);
```

### 3.4 `outreach_drafts` (Already in Core)
```sql
CREATE TABLE outreach_drafts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE INDEX,
    opportunity_id VARCHAR(36) NOT NULL REFERENCES freelance_opportunities(id) ON DELETE CASCADE INDEX,
    channel VARCHAR(30) NOT NULL DEFAULT 'EMAIL',
    recipient_name VARCHAR(150),
    recipient_contact VARCHAR(255) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    message_body TEXT NOT NULL,
    proposed_service VARCHAR(150),
    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT' INDEX,
    is_approved BOOLEAN NOT NULL DEFAULT FALSE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_recipient VARCHAR(255),
    approved_subject VARCHAR(255),
    approved_body_hash VARCHAR(64),
    candidate_edits_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 3.5 `outreach_delivery_logs` (Already in Core)
```sql
CREATE TABLE outreach_delivery_logs (
    id VARCHAR(36) PRIMARY KEY,
    draft_id VARCHAR(36) NOT NULL REFERENCES outreach_drafts(id) ON DELETE CASCADE INDEX,
    provider VARCHAR(50) NOT NULL DEFAULT 'SMTP',
    provider_message_id VARCHAR(255),
    provider_response_code INTEGER,
    provider_raw_response TEXT,
    delivery_status VARCHAR(30) NOT NULL DEFAULT 'SENT',
    webhook_verified BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### 3.6 New Model: `freelance_search_history`
```sql
CREATE TABLE freelance_search_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE INDEX,
    query VARCHAR(255) NOT NULL,
    city VARCHAR(150) NOT NULL,
    results_count INTEGER NOT NULL DEFAULT 0,
    leads_count INTEGER NOT NULL DEFAULT 0,
    deep_scan BOOLEAN NOT NULL DEFAULT FALSE,
    zones TEXT,
    include_with_website BOOLEAN NOT NULL DEFAULT FALSE,
    searched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 3.7 New Model: `freelance_candidate_settings`
```sql
CREATE TABLE freelance_candidate_settings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE INDEX,
    encrypted_serpapi_key TEXT,
    encrypted_apify_token TEXT,
    encrypted_gemini_key TEXT,
    maps_provider VARCHAR(50) NOT NULL DEFAULT 'serpapi',
    sender_name VARCHAR(150),
    sender_brand VARCHAR(150),
    smtp_host VARCHAR(255),
    smtp_port INTEGER DEFAULT 465,
    smtp_email VARCHAR(255),
    encrypted_smtp_password TEXT,
    smtp_use_ssl BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Multi-Signal Deduplication Strategy

When a business is discovered from SerpApi or Apify:
1. **Signal 1:** Match on `place_id`.
2. **Signal 2:** Match on `leadhunter_lead_id`.
3. **Signal 3:** Match on `LOWER(business_name) AND LOWER(city)`.
4. If match found: Update `last_verified_at`, website status, and rating. Do not duplicate the opportunity record.
5. If new: Create canonical `FreelanceOpportunityRecord` and associate `ContactEvidenceRecord` instances for email, phone, and website.
