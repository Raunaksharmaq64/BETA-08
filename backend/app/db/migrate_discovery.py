"""
RIGHT FIT Core — Continuous Discovery & Skill Taxonomy Migration
Creates tables for:
  - market_skill_relationships
  - discovery_task_executions
  - discovery_schedule_configs
Updates candidate_skills table with provenance, confidence, and confirmation fields.
Seeds canonical skill relationships and baseline discovery schedule configs.
"""

import sys
import os
from datetime import datetime, timezone

# Ensure backend path is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models import (
    Base,
    SkillTaxonomyRecord,
    SkillRelationshipRecord,
    DiscoveryScheduleConfigRecord,
    DiscoveryTaskExecutionRecord,
    utc_now,
)


def run_migration():
    print(f"[Discovery Migration] Target DATABASE_URL: {settings.DATABASE_URL}")
    db_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")
    engine = create_engine(db_url, echo=False)

    print("[Discovery Migration] Creating tables...")
    Base.metadata.create_all(
        bind=engine,
        tables=[
            SkillRelationshipRecord.__table__,
            DiscoveryTaskExecutionRecord.__table__,
            DiscoveryScheduleConfigRecord.__table__,
        ],
    )
    print("[Discovery Migration] Tables created successfully.")

    # In SQLite or Postgres, check if columns exist on candidate_skills
    with engine.connect() as conn:
        try:
            if "sqlite" in db_url:
                cols_res = conn.execute(text("PRAGMA table_info(candidate_skills)"))
                existing_cols = {row[1] for row in cols_res.fetchall()}
                
                if "canonical_skill_id" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN canonical_skill_id VARCHAR(36)"))
                if "source_of_evidence" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN source_of_evidence VARCHAR(64) DEFAULT 'USER_ENTERED'"))
                if "resume_section" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN resume_section VARCHAR(100)"))
                if "extraction_confidence" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN extraction_confidence FLOAT DEFAULT 1.0"))
                if "confirmation_status" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN confirmation_status VARCHAR(32) DEFAULT 'CONFIRMED'"))
                if "last_updated_at" not in existing_cols:
                    conn.execute(text("ALTER TABLE candidate_skills ADD COLUMN last_updated_at TIMESTAMP"))
                conn.commit()
                print("[Discovery Migration] candidate_skills SQLite columns checked/added.")
        except Exception as e:
            print(f"[Discovery Migration] Column check note: {e}")

    # Seed Canonical Skill Taxonomy & Relationships
    with Session(engine) as session:
        # 1. Seed Core Skills if not present
        skills_to_seed = [
            ("javascript", "JavaScript", "Frontend / Scripting", "Web Development"),
            ("typescript", "TypeScript", "Frontend / Full-Stack", "Web Development"),
            ("react", "React", "Frontend Libraries", "Web Development"),
            ("next-js", "Next.js", "Full-Stack Frameworks", "Web Development"),
            ("python", "Python", "Backend / AI", "Programming Languages"),
            ("fastapi", "FastAPI", "Backend Frameworks", "Web Development"),
            ("postgresql", "PostgreSQL", "Relational Databases", "Data Storage"),
            ("sql", "SQL", "Database Querying", "Data Storage"),
            ("docker", "Docker", "Containers", "DevOps & Cloud"),
            ("kubernetes", "Kubernetes", "Container Orchestration", "DevOps & Cloud"),
            ("aws", "AWS", "Cloud Providers", "DevOps & Cloud"),
            ("cloud-computing", "Cloud Computing", "Infrastructure", "DevOps & Cloud"),
        ]

        skill_records = {}
        for slug, name, cat, tech_fam in skills_to_seed:
            existing = session.query(SkillTaxonomyRecord).filter_by(slug=slug).first()
            if not existing:
                existing = SkillTaxonomyRecord(
                    slug=slug,
                    canonical_name=name,
                    category=cat,
                    technology_family=tech_fam,
                    is_active=True,
                )
                session.add(existing)
                session.flush()
            skill_records[slug] = existing

        # 2. Seed Structured Skill Relationships
        relationships = [
            ("javascript", "typescript", "TRANSFERABLE", 0.85, "TypeScript is typed superset of JavaScript"),
            ("typescript", "javascript", "TRANSFERABLE", 0.95, "TypeScript expertise directly transfers to JavaScript"),
            ("react", "next-js", "PARENT_CHILD", 0.90, "Next.js builds directly on React architecture"),
            ("next-js", "react", "TRANSFERABLE", 0.95, "Next.js developers master React fundamentals"),
            ("python", "fastapi", "PARENT_CHILD", 0.85, "FastAPI is modern async Python framework"),
            ("fastapi", "python", "TRANSFERABLE", 0.95, "FastAPI developers have strong Python skills"),
            ("postgresql", "sql", "PARENT_CHILD", 0.95, "PostgreSQL is an advanced SQL dialect"),
            ("sql", "postgresql", "RELATED", 0.75, "SQL foundation maps to PostgreSQL"),
            ("docker", "kubernetes", "RELATED", 0.80, "Kubernetes manages Docker containerized workloads"),
            ("kubernetes", "docker", "RELATED", 0.85, "Kubernetes operators understand container runtimes"),
            ("aws", "cloud-computing", "PARENT_CHILD", 0.90, "AWS is leading cloud computing provider"),
            ("cloud-computing", "aws", "RELATED", 0.80, "General cloud concepts apply to AWS"),
        ]

        for s_slug, t_slug, rel_type, strength, notes in relationships:
            s_rec = skill_records.get(s_slug)
            t_rec = skill_records.get(t_slug)
            if s_rec and t_rec:
                existing_rel = session.query(SkillRelationshipRecord).filter_by(
                    source_skill_id=s_rec.id,
                    target_skill_id=t_rec.id,
                ).first()
                if not existing_rel:
                    rel_item = SkillRelationshipRecord(
                        source_skill_id=s_rec.id,
                        target_skill_id=t_rec.id,
                        relationship_type=rel_type,
                        strength=strength,
                        notes=notes,
                    )
                    session.add(rel_item)

        # 3. Seed Baseline Discovery Schedule Configs
        default_configs = [
            ("greenhouse-ats", "Greenhouse Public ATS", 1800, 50, 30),
            ("lever-ats", "Lever Job Postings", 1800, 50, 30),
            ("ashby-ats", "Ashby Ingestion Engine", 1800, 50, 30),
            ("remoteok-feed", "RemoteOK Job Board Feed", 3600, 50, 20),
            ("leadhunter-satellite", "LeadHunter AI Freelance Adapter", 1800, 40, 20),
            ("startup-hunter-satellite", "Startup Problems Hunter Satellite", 3600, 30, 15),
            ("job-link-verifier", "Automated Link Verifier & Checker", 3600, 100, 60),
            ("deduplication-sweeper", "Cross-Source Deduplication Sweeper", 7200, 200, 60),
        ]

        for src_id, name, interval, max_recs, rate_lim in default_configs:
            cfg = session.query(DiscoveryScheduleConfigRecord).filter_by(source_id=src_id).first()
            if not cfg:
                cfg = DiscoveryScheduleConfigRecord(
                    source_id=src_id,
                    source_name=name,
                    interval_seconds=interval,
                    is_paused=False,
                    max_records_per_run=max_recs,
                    rate_limit_per_minute=rate_lim,
                    last_run_at=utc_now(),
                    next_run_at=utc_now(),
                )
                session.add(cfg)

        session.commit()
        print("[Discovery Migration] Complete: Canonical skill relationships & discovery configs seeded.")


if __name__ == "__main__":
    run_migration()
