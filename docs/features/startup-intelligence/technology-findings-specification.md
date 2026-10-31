# Technographic Stack Findings Specification
## Workstream G Specification

- **Module:** `startup-intelligence`
- **Table:** `startup_tech_findings`

---

## 1. Technographic Discovery Taxonomy

Technologies are recorded only when concrete, traceable evidence exists in the raw observation or website audit:

```
+-------------------------------------------------------------+
|               Startup Technographic Finding                 |
+-------------------------------------------------------------+
| - technology_name: "PostgreSQL"                             |
| - category: "Database"                                      |
| - finding_type: "EXPLICIT_MENTION" | "AUDIT_DETECTED"       |
| - confidence_score: 0.95                                    |
| - traceable_evidence: "GitHub issue #42: Connection timeout"|
+-------------------------------------------------------------+
```

### Finding Types:
1. `AUDIT_DETECTED` (Confidence: 0.95): Identified via HTML meta tags, response headers (e.g. `X-Powered-By`), DOM script paths (e.g., `_next/static/`), or PageSpeed technographics.
2. `EXPLICIT_MENTION` (Confidence: 0.85): Specifically named by a founder or developer in the problem description (e.g., *"Our Redis cluster is maxed out"*).
3. `SIGNAL_KEYWORD` (Confidence: 0.70): Mentioned in post tags or hiring requirements.

---

## 2. Prohibition on Speculative Tech Stacks

- **No Industry Guessing**: The engine never claims a fintech startup uses React or AWS unless evidence appears in the crawl.
- **No Private Architecture Claims**: Internal databases or microservice topology are never inferred without public founder statements.

