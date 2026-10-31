# Startup Problem & Opportunity Normalization Mapping
## Workstream C & D Specification

- **Module:** `startup-intelligence`
- **Component:** `app.services.startup_service.StartupService.import_startup_leads`

---

## 1. Field Mapping Matrix

Raw leads from `Startups-problrms-hunter` are ingested into Core's relational database models according to strict non-hallucination rules:

| Upstream Field (`leads.json`) | Core Target Table | Core Column | Transformation Rule |
|---|---|---|---|
| `id` | `startup_opportunities` | `service_record_id` | Preserved as upstream identifier mapping. |
| `startup_name` | `startup_opportunities` | `startup_name` | Cleaned string; default to "Unnamed Startup" if empty. |
| `url` | `startup_opportunities` | `website_url` | Validated URL string. |
| `url` | `startup_opportunities` | `domain` | Normalized hostname via `urlparse` (e.g. `acme.io`). |
| `category` | `startup_opportunities` | `category` | Standardized category ('Development', 'Performance', 'UI/UX', 'SEO', 'AI'). |
| `detected_signal` | `startup_opportunities` | `detected_signal` | Verbatim signal text from founder post/issue. |
| `insight` | `startup_opportunities` | `ai_insight` | Isolated as machine-generated interpretation. |
| `opportunity` | `startup_opportunities` | `ai_opportunity` | Isolated as machine-generated recommendation. |
| `pitch_idea` | `startup_opportunities` | `ai_pitch_idea` | Preserved as baseline pitch suggestion. |
| `score` | `startup_opportunities` | `urgency_score` | Integer clamped between 1 and 10 (default: 5). |
| `score_explanation` | `startup_opportunities` | `score_explanation` | Preserved rationale for rating. |
| `source` | `startup_opportunities` | `primary_source` | Preserved originating platform string. |
| `created_at` | `startup_opportunities` | `published_at` | Parsed ISO 8601 UTC timestamp or `None`. |
| `raw_text` | `startup_evidence` | `observation_excerpt` | Verbatim post body up to 2,000 characters. |
| `tech_audit.tech_stack` | `startup_tech_findings` | `technology_name` | Individual records linked with finding type `AUDIT_DETECTED`. |
| `matched_skills` | `startup_tech_findings` | `technology_name` | Individual records linked with finding type `KEYWORD_MENTION`. |

---

## 2. Anti-Hallucination Policy

1. **Unknown Fields Remain Unknown**: If a founder's name, email, funding round, revenue, or team size is missing, the field remains `NULL`. It is never guessed or synthesized.
2. **No Inferred Budget Claims**: Urgency score indicates problem severity, not authorized financial budget.
3. **No Fabricated Endorsements**: Core never claims that the target company requested RIGHT FIT or approved outreach.

