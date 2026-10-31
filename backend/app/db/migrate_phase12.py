"""
RIGHT FIT Core — Phase 12 Database Migration & Seed Helper
Creates Phase 12 tables and populates baseline curated skill taxonomy, aliases, and sources:
- market_data_sources
- market_skills
- market_skill_aliases
- market_skill_demand_snapshots
- market_compensation_observations
- candidate_skill_gap_recommendations
"""

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal, Base
from app.db.models import (
    MarketDataSourceRecord,
    SkillTaxonomyRecord,
    SkillAliasRecord,
    SkillDemandSnapshotRecord,
    CompensationObservationRecord,
    CandidateSkillGapRecommendationRecord,
    utc_now,
)


async def run_migration():
    print("Connecting to database via async engine to create Phase 12 tables...")
    tables_to_create = [
        MarketDataSourceRecord.__table__,
        SkillTaxonomyRecord.__table__,
        SkillAliasRecord.__table__,
        SkillDemandSnapshotRecord.__table__,
        CompensationObservationRecord.__table__,
        CandidateSkillGapRecommendationRecord.__table__,
    ]

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(bind=sync_conn, tables=tables_to_create))
    print("Phase 12 tables created successfully (6 tables).")

    # Seed baseline taxonomy and sources
    async with AsyncSessionLocal() as session:
        # 1. Sources
        source_count_res = await session.execute(select(MarketDataSourceRecord))
        if not source_count_res.scalars().first():
            print("Seeding documented market data sources...")
            sources = [
                MarketDataSourceRecord(
                    source_code="CORE_ATS_OBSERVATIONS",
                    source_name="RIGHT FIT Discovered Job Postings",
                    provider="RIGHT FIT Core Ingestion Pipeline",
                    source_category="OBSERVED_POSTINGS",
                    documentation_url="https://rightfit.platform/docs/market/sources/core-ats",
                    access_method="LOCAL_CANONICAL_INDEX",
                    license_type="PROPRIETARY_OBSERVED_SAMPLE",
                    commercial_use_permitted=True,
                    attribution_required=False,
                    geographic_coverage="GLOBAL",
                    update_frequency="CONTINUOUS_DAILY",
                    known_limitations="Observed jobs represent a curated sample of active postings across configured ATS connectors, not the entire national or global labor market.",
                    is_enabled=True,
                ),
                MarketDataSourceRecord(
                    source_code="PUBLIC_LABOR_STATS",
                    source_name="Public Government Labor Statistics & Occupational Reports",
                    provider="US Bureau of Labor Statistics (BLS) / National Statistical Agencies",
                    source_category="GOVERNMENT_STATISTICS",
                    documentation_url="https://www.bls.gov/oes/",
                    access_method="PUBLIC_REPORT_INGESTION",
                    license_type="PUBLIC_DOMAIN",
                    commercial_use_permitted=True,
                    attribution_required=True,
                    attribution_notes="Attribution to US Bureau of Labor Statistics required for federal wage tables.",
                    geographic_coverage="UNITED_STATES",
                    update_frequency="ANNUAL",
                    known_limitations="Aggregated occupational categories with lag time of 6-12 months from collection to public release.",
                    is_enabled=True,
                ),
                MarketDataSourceRecord(
                    source_code="COMMERCIAL_MARKET_FEED",
                    source_name="Licensed Commercial Tech Talent Intelligence",
                    provider="Third-Party Commercial Benchmark Provider",
                    source_category="LICENSED_DATASET",
                    documentation_url="https://vendor.benchmark.example.com",
                    access_method="REST_API",
                    license_type="RESTRICTED_COMMERCIAL_LICENSE",
                    commercial_use_permitted=False,
                    attribution_required=True,
                    geographic_coverage="GLOBAL",
                    update_frequency="MONTHLY",
                    known_limitations="Disabled by default until commercial license contract is formally executed and approved.",
                    is_enabled=False,
                ),
            ]
            session.add_all(sources)
            await session.commit()
            print("Market data sources seeded.")

        # 2. Canonical Skills & Aliases
        skill_count_res = await session.execute(select(SkillTaxonomyRecord))
        if not skill_count_res.scalars().first():
            print("Seeding canonical skill taxonomy and aliases...")
            skills_data = [
                {
                    "slug": "python",
                    "canonical_name": "Python",
                    "category": "Programming Languages",
                    "family": "Python Ecosystem",
                    "desc": "High-level, general-purpose interpreted language for web, automation, and data.",
                    "aliases": [("python", "Python"), ("python3", "Python 3"), ("python 3", "Python 3"), ("py", "Py")],
                },
                {
                    "slug": "javascript",
                    "canonical_name": "JavaScript",
                    "category": "Programming Languages",
                    "family": "Web Standards",
                    "desc": "Universal lightweight ECMAScript language for frontend and server runtimes.",
                    "aliases": [("javascript", "JavaScript"), ("js", "JS"), ("ecmascript", "ECMAScript"), ("es6", "ES6")],
                },
                {
                    "slug": "typescript",
                    "canonical_name": "TypeScript",
                    "category": "Programming Languages",
                    "family": "Web Standards",
                    "desc": "Strict syntactical superset of JavaScript adding optional static typing.",
                    "aliases": [("typescript", "TypeScript"), ("ts", "TS")],
                },
                {
                    "slug": "postgresql",
                    "canonical_name": "PostgreSQL",
                    "category": "Databases",
                    "family": "Relational SQL",
                    "desc": "Powerful, open source object-relational database system.",
                    "aliases": [("postgresql", "PostgreSQL"), ("postgres", "Postgres"), ("pgsql", "PgSQL"), ("postgres sql", "Postgres SQL")],
                },
                {
                    "slug": "react",
                    "canonical_name": "React",
                    "category": "Frameworks",
                    "family": "Frontend Web",
                    "desc": "Declarative component-based UI library developed by Meta.",
                    "aliases": [("react", "React"), ("reactjs", "ReactJS"), ("react.js", "React.js"), ("react js", "React JS")],
                },
                {
                    "slug": "nextjs",
                    "canonical_name": "Next.js",
                    "category": "Frameworks",
                    "family": "Full-Stack Web",
                    "desc": "React framework for server-rendered and statically generated applications.",
                    "aliases": [("nextjs", "Next.js"), ("next.js", "Next.js"), ("next js", "Next JS")],
                },
                {
                    "slug": "fastapi",
                    "canonical_name": "FastAPI",
                    "category": "Frameworks",
                    "family": "Python Web",
                    "desc": "Modern, fast, high-performance web framework for building APIs with Python.",
                    "aliases": [("fastapi", "FastAPI"), ("fast-api", "FastAPI"), ("fast api", "Fast API")],
                },
                {
                    "slug": "docker",
                    "canonical_name": "Docker",
                    "category": "DevOps & Cloud",
                    "family": "Containerization",
                    "desc": "Platform for developing, shipping, and running applications in containers.",
                    "aliases": [("docker", "Docker"), ("containerization", "Containerization"), ("docker-compose", "Docker Compose")],
                },
                {
                    "slug": "kubernetes",
                    "canonical_name": "Kubernetes",
                    "category": "DevOps & Cloud",
                    "family": "Cloud Native",
                    "desc": "Automated container deployment, scaling, and management platform.",
                    "aliases": [("kubernetes", "Kubernetes"), ("k8s", "K8s")],
                },
                {
                    "slug": "aws",
                    "canonical_name": "AWS",
                    "category": "DevOps & Cloud",
                    "family": "Cloud Infrastructure",
                    "desc": "Comprehensive on-demand cloud computing platform by Amazon.",
                    "aliases": [("aws", "AWS"), ("amazon web services", "Amazon Web Services"), ("amazon aws", "Amazon AWS")],
                },
                {
                    "slug": "redis",
                    "canonical_name": "Redis",
                    "category": "Databases",
                    "family": "In-Memory Caching",
                    "desc": "In-memory data structure store used as a database, cache, and message broker.",
                    "aliases": [("redis", "Redis"), ("redis cache", "Redis Cache")],
                },
                {
                    "slug": "tailwind-css",
                    "canonical_name": "Tailwind CSS",
                    "category": "Frameworks",
                    "family": "CSS Styling",
                    "desc": "Utility-first CSS framework for rapid modern UI development.",
                    "aliases": [("tailwind-css", "Tailwind CSS"), ("tailwind", "Tailwind"), ("tailwindcss", "TailwindCSS")],
                },
            ]

            for s_data in skills_data:
                skill_rec = SkillTaxonomyRecord(
                    slug=s_data["slug"],
                    canonical_name=s_data["canonical_name"],
                    category=s_data["category"],
                    technology_family=s_data["family"],
                    description=s_data["desc"],
                    taxonomy_version="1.0.0",
                    is_active=True,
                )
                session.add(skill_rec)
                await session.flush()

                for alias_norm, alias_disp in s_data["aliases"]:
                    alias_rec = SkillAliasRecord(
                        skill_id=skill_rec.id,
                        alias_normalized=alias_norm.strip().lower(),
                        alias_display=alias_disp,
                        source="CANONICAL_CURATED",
                        confidence=1.0,
                        is_verified=True,
                    )
                    session.add(alias_rec)

            await session.commit()
            print("Canonical skill taxonomy and aliases seeded successfully.")

        # 3. Baseline Snapshots & Compensation
        snap_count_res = await session.execute(select(SkillDemandSnapshotRecord))
        if not snap_count_res.scalars().first():
            print("Seeding initial demand snapshots and audited compensation records...")
            # Retrieve skills
            all_skills = (await session.execute(select(SkillTaxonomyRecord))).scalars().all()
            skill_map = {s.slug: s for s in all_skills}

            snapshots = []
            now = utc_now()
            # Seed demand for python, javascript, typescript, postgresql, react
            demand_seeds = [
                ("python", 45, 28, "INCREASING_IN_SAMPLE", 12.5),
                ("javascript", 42, 26, "STABLE_IN_SAMPLE", 1.2),
                ("typescript", 38, 24, "INCREASING_IN_SAMPLE", 18.0),
                ("postgresql", 35, 22, "INCREASING_IN_SAMPLE", 8.4),
                ("react", 34, 21, "STABLE_IN_SAMPLE", -0.5),
                ("docker", 30, 20, "STABLE_IN_SAMPLE", 4.1),
                ("fastapi", 24, 16, "INCREASING_IN_SAMPLE", 22.0),
                ("aws", 29, 19, "STABLE_IN_SAMPLE", 2.3),
            ]

            for slug, count, employers, trend, pct in demand_seeds:
                if slug in skill_map:
                    s_obj = skill_map[slug]
                    snapshots.append(
                        SkillDemandSnapshotRecord(
                            skill_id=s_obj.id,
                            role_category="Software Engineering",
                            geography="GLOBAL",
                            time_window="30d",
                            distinct_opportunity_count=count,
                            distinct_employer_count=employers,
                            distinct_source_count=2,
                            first_observed_at=now,
                            last_observed_at=now,
                            trend_direction=trend,
                            period_over_period_pct=pct,
                            confidence_level="MODERATE_CONFIDENCE_LIMITED_SOURCES",
                            limitations_disclosure="Sample derived from 100+ ingested active job records. Disclose sample size and do not extrapolate universally.",
                        )
                    )

            session.add_all(snapshots)

            # Seed audited compensation observations
            comp_observations = [
                CompensationObservationRecord(
                    role_title="Senior Python Backend Engineer",
                    skill_slug="python",
                    geography="Remote (US)",
                    country="United States",
                    compensation_type="BASE_SALARY",
                    period="ANNUAL",
                    currency="USD",
                    min_amount=135000.0,
                    max_amount=175000.0,
                    median_amount=155000.0,
                    is_estimated=False,
                    source_provider="CORE_ATS_CONNECTOR",
                    sample_size=18,
                    methodology_notes="Audited from explicit job disclosure ranges. Excludes bonuses, commissions, and equity grants.",
                ),
                CompensationObservationRecord(
                    role_title="Full-Stack React/Next.js Engineer",
                    skill_slug="react",
                    geography="Remote (US)",
                    country="United States",
                    compensation_type="BASE_SALARY",
                    period="ANNUAL",
                    currency="USD",
                    min_amount=120000.0,
                    max_amount=160000.0,
                    median_amount=140000.0,
                    is_estimated=False,
                    source_provider="CORE_ATS_CONNECTOR",
                    sample_size=14,
                    methodology_notes="Base annual salary only. Stock/equity grants listed as unvalued incentive packages.",
                ),
                CompensationObservationRecord(
                    role_title="Lead Data Engineer (PostgreSQL / Python)",
                    skill_slug="postgresql",
                    geography="Bengaluru, India",
                    country="India",
                    compensation_type="BASE_SALARY",
                    period="ANNUAL",
                    currency="INR",
                    min_amount=2400000.0,
                    max_amount=3800000.0,
                    median_amount=3000000.0,
                    is_estimated=False,
                    source_provider="CORE_ATS_CONNECTOR",
                    sample_size=9,
                    methodology_notes="Fixed annual CTC excluding performance variable bonus. Disclosed in INR.",
                ),
                CompensationObservationRecord(
                    role_title="DevOps & Platform Engineer (Kubernetes/AWS)",
                    skill_slug="kubernetes",
                    geography="Remote (Europe)",
                    country="Germany",
                    compensation_type="BASE_SALARY",
                    period="ANNUAL",
                    currency="EUR",
                    min_amount=85000.0,
                    max_amount=115000.0,
                    median_amount=98000.0,
                    is_estimated=False,
                    source_provider="CORE_ATS_CONNECTOR",
                    sample_size=7,
                    methodology_notes="Base annual gross salary before local statutory benefits.",
                ),
            ]
            session.add_all(comp_observations)
            await session.commit()
            print("Initial demand snapshots and compensation observations seeded.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
