# Database Indexing & Performance Optimization

- **Title:** PostgreSQL Indexing & Performance Guidelines
- **Purpose:** Mandates indexing patterns, composite index strategies, query plan checks, and VACUUM maintenance.
- **Status:** APPROVED
- **Owner:** Database Architect (TBD)
- **Last Updated:** 2026-10-30

---

## 1. Indexing Strategy by Workload
1. **Foreign Key Indexing:** Every foreign key column (e.g., `user_id`, `job_id`, `company_id`) must have a B-tree index to prevent table-scan locks during cascaded updates.
2. **Search & Filter Indexes:**
   - Composite B-tree for job filtering: `CREATE INDEX idx_jobs_filter ON core.jobs (is_active, location_type, created_at DESC);`
   - GIN index for skill array matching: `CREATE INDEX idx_jobs_skills ON core.jobs USING gin (required_skills);`
3. **Vector Similarity Search (pgvector):**
   - HNSW index for high-dimensional resume & job embedding lookups:
     `CREATE INDEX idx_jobs_embedding ON core.jobs USING hnsw (embedding vector_cosine_ops);`

## 2. Query Performance Guidelines
- **Always `EXPLAIN ANALYZE`:** Any query expected to run on tables with > 50,000 rows must be verified with query plans.
- **Eliminate `N+1` Queries:** Use SQLAlchemy `selectinload()` or `joinedload()` for relational dependencies.
- **Selective Columns:** Never execute `SELECT *` in high-throughput endpoints; query explicit model attributes.

## 3. Maintenance & Vacuuming
- Enable PostgreSQL autovacuum with aggressive scale factor on fast-churn tables (`core.job_matches`, `leadhunter.leads`): `autovacuum_vacuum_scale_factor = 0.05`.

## 4. Open Questions & TBDs
- [TBD] Table partitioning on `core.jobs` by creation month for multi-million row retention.

