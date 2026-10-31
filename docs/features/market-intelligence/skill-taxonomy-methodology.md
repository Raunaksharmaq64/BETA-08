# Skill Taxonomy Methodology

## 1. Principles of Taxonomy Design
The Skill Taxonomy in RIGHT FIT represents an authoritative ontology of engineering, product, data, infrastructure, and technical competencies.
- **Canonical Representation**: Every distinct technology or skill is represented by a single canonical node in `skills_taxonomy`.
- **Slug Uniqueness**: Slugs are normalized, URL-safe identifiers (e.g. `javascript`, `python`, `kubernetes`, `postgresql`, `react`).
- **Semantic Families**: Skills are grouped into higher-level technology families (e.g. `Cloud & Containers`, `Relational Databases`, `Frontend Runtimes`) allowing hierarchical analysis.
- **Category Isolation**: Categories define functional disciplines:
  - `PROGRAMMING_LANGUAGE`: Core syntax and runtime environments (Python, TypeScript, Go).
  - `FRAMEWORK`: Application frameworks and libraries (React, FastAPI, Django, Next.js).
  - `DATABASE`: Persistence engines and storage solutions (PostgreSQL, Redis, MySQL).
  - `INFRASTRUCTURE`: Cloud providers, container orchestration, and CI/CD tools (Kubernetes, Docker, AWS).
  - `AI_ML`: Artificial intelligence, machine learning, and data engineering libraries (PyTorch, TensorFlow, LLMs).

## 2. Table Definition: `skills_taxonomy`
```sql
CREATE TABLE skills_taxonomy (
    id UUID PRIMARY KEY,
    canonical_name VARCHAR(128) NOT NULL,
    slug VARCHAR(128) UNIQUE NOT NULL,
    category VARCHAR(64) NOT NULL,
    technology_family VARCHAR(128),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. Avoiding Circular and Lossy Merges
- Distinct technologies that share parent ecosystems are **never merged** into a single node. For instance, `JavaScript` and `TypeScript` are strictly independent canonical skills, even though both belong to the `Web Platforms` technology family.
- Frameworks are never merged into their base languages (e.g. `FastAPI` is distinct from `Python`; `React` is distinct from `JavaScript`).
- This preservation ensures fine-grained precision when matching candidate qualifications to opportunity requirements.

