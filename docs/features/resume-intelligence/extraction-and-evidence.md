# Information Extraction, Evidence Tracking & Confidence Scoring

## 1. Principles of Evidenced Extraction

A major vulnerability in automated hiring tools is the generation of unverified candidate claims ("hallucinations"). In **RIGHT FIT**, every extracted fact is permanently linked to traceable evidence from the original document.

If an attribute cannot be found in the document text, **it is not created**. Missing sections remain empty rather than populated with fictional defaults.

---

## 2. Evidence Data Model (`EvidenceDTO`)

The Core Career Engine standardizes evidence under `contracts/resume/schemas.py`:

```json
{
  "field_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "field_name": "education[0].institution",
  "extracted_value": "Stanford University",
  "source_section": "EDUCATION",
  "excerpt": "Stanford University | B.S. in Computer Science | 2014 - 2018",
  "page_number": 1,
  "extraction_method": "SECTION_PARSER",
  "confidence_score": 0.88,
  "confidence_level": "HIGH",
  "review_status": "PENDING",
  "user_correction": null,
  "reviewed_at": null
}
```

### Field Definitions

1. `field_name`: Semantic path identifying the attribute (e.g. `personal_info.phone`, `skills.languages.python`, `experience[0].company`).
2. `extracted_value`: Raw parsed value.
3. `source_section`: Document section where the fact was located (e.g. `HEADER`, `SUMMARY`, `EDUCATION`, `SKILLS`).
4. `excerpt`: Exact sentence or phrase snippet from the resume supporting this fact.
5. `page_number`: 1-based page index of the supporting excerpt (handles multi-page PDFs).
6. `extraction_method`: Classification method (`STRUCTURED_PARSER`, `REGEX`, `KEYWORD_MATCHER`).
7. `confidence_score`: Algorithmic score between `0.0` and `1.0`.
8. `confidence_level`: UI classification (`HIGH`, `MEDIUM`, `LOW`, `EVIDENCE_UNAVAILABLE`).
9. `review_status`: State in the verification workbench (`PENDING`, `CONFIRMED`, `EDITED`, `REJECTED`).

---

## 3. Confidence Classification Rules

Confidence reflects **extraction quality**, NOT candidate competence:

- **HIGH Confidence ($\ge 0.85$)**:
  - Direct matches with unambiguous delimiters or RFC patterns (e.g. RFC 5322 email addresses, verified URLs, skills found inside the dedicated `SKILLS` header section).
- **MEDIUM Confidence ($0.70 - 0.84$)**:
  - Entity inferred from context or body paragraphs (e.g. technical keywords found in general experience text rather than a skills section).
- **LOW Confidence ($< 0.70$)**:
  - Ambiguous dates, unusual phrasing, or non-standard formatting.
- **EVIDENCE UNAVAILABLE**:
  - Values entered manually by candidate during editing that do not originate from document text.

---

## 4. Skills Taxonomy & Boundary Matching

Skills are extracted using word boundary regex (`\b{skill}\b`) against a curated multi-tier taxonomy:

| Category | Representative Extracted Skills |
|---|---|
| **Languages** | Python, TypeScript, JavaScript, Go, Rust, Java, C++, C#, SQL, Ruby, Swift, Kotlin |
| **Frameworks** | FastAPI, React, Next.js, Django, Flask, Node.js, Express, Spring Boot, Vue, Angular |
| **Databases** | PostgreSQL, MySQL, Redis, MongoDB, Elasticsearch, Cassandra, DynamoDB, SQLite |
| **Cloud & DevOps** | AWS, GCP, Azure, Docker, Kubernetes, Terraform, Cloudflare, Linux, Nginx |
| **Developer Tools**| Git, GitHub, GitLab, Jira, CI/CD, Postman, Celery, Kafka, Pytest, Datadog |
| **Soft Skills** | Leadership, Mentorship, Agile, Scrum, Collaboration, Problem Solving |

### False Positive Prevention
Single-letter keywords or common English words (such as 'c', 'go', 'r') are subjected to strict section and casing verification to avoid false positives (e.g., preventing words like "cat" or "go to" from being extracted as C or Go).

