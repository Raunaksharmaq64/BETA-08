# Alias Resolution Engine

## 1. Problem Statement
Job descriptions, applicant resumes, and user search queries frequently refer to identical technical skills using abbreviations, colloquial slang, or case-insensitive synonyms:
- `k8s` -> `Kubernetes`
- `js` -> `JavaScript`
- `ts` -> `TypeScript`
- `postgres`, `pgsql` -> `PostgreSQL`
- `py` -> `Python`
- `tf` -> `TensorFlow`

If raw text searches are executed directly, searches fragment demand counts, divide candidate scores, and produce false negatives. Conversely, naive substring matching produces false positive collisions (e.g. searching `go` matching "good", "algorithm", or "Django").

## 2. Deterministic Alias Modeling
The `skill_aliases` table maintains a strictly verified, many-to-one mapping between colloquial strings and canonical skill nodes:
```sql
CREATE TABLE skill_aliases (
    id UUID PRIMARY KEY,
    skill_id UUID NOT NULL REFERENCES skills_taxonomy(id) ON DELETE CASCADE,
    alias VARCHAR(128) UNIQUE NOT NULL,
    source_type VARCHAR(64) DEFAULT 'MANUAL_CURATION',
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 3. Resolution Pipeline
1. **Case & Punctuation Normalization**: Incoming token is lowercased, leading/trailing whitespace stripped, and hyphens/dots normalized:
   $$\text{token} = \text{strip}(\text{lower}(q))$$
2. **Direct Canonical Match**: Check if `token == lower(skill.canonical_name)` or `token == skill.slug`. If matched, return canonical node immediately with `is_alias = false, confidence = 1.0`.
3. **Alias Table Lookup**: Query `skill_aliases WHERE alias = :token`. If found, resolve to parent `skills_taxonomy` node with `is_alias = true, confidence = alias.confidence`.
4. **Collision Prevention Guard**:
   - Short tokens ($\le 3$ characters like `c`, `go`, `r`, `js`) require strict exact word-boundary matching. Substring inclusion within longer words is blocked.
   - Ambiguous abbreviations are rejected from alias registration unless verified by curation review.

