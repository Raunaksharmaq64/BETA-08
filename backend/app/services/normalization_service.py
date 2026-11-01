"""
RIGHT FIT Core — Opportunity Normalization & Provenance Service
Version: 1.0.0
Phase: 5 — Job Source Framework: Registry, Connectors, Normalization & Provenance

Maps diverse raw ATS and API payloads into the Canonical Opportunity schema:
- HTML sanitization and text cleanup
- Location, remote, and employment type classification
- Grounded compensation extraction (strictly no fabricated estimates)
- Stable SHA-256 deduplication hashing
- Full provenance and timestamp preservation
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.db.models import JobSourceRecord
from app.services.connectors.base import RawJobPayload
from contracts.sources.schemas import EmploymentType, WorkplaceType

NORMALIZER_VERSION = "1.0.0"

# Common skill keywords across all professional disciplines (Engineering, Marketing, Sales, Design, Finance, Ops, HR, etc.)
KNOWN_SKILLS = [
    # Engineering & Technology
    "Python", "FastAPI", "Django", "Flask", "TypeScript", "JavaScript",
    "React", "Next.js", "Vue", "Node.js", "Go", "Golang", "Rust", "Java",
    "Kotlin", "Swift", "C++", "C#", ".NET", "PostgreSQL", "MySQL", "MongoDB",
    "Redis", "Kafka", "RabbitMQ", "Elasticsearch", "AWS", "GCP", "Azure",
    "Docker", "Kubernetes", "Terraform", "CI/CD", "GraphQL", "REST",
    "SQL", "NoSQL", "Git", "Linux", "Microservices", "System Design",
    "PyTorch", "TensorFlow", "Pandas", "Scikit-Learn", "LLM", "RAG",
    # Marketing & Growth
    "SEO", "SEM", "Google Ads", "Meta Ads", "Content Marketing", "Copywriting",
    "Email Marketing", "HubSpot", "Growth Marketing", "Google Analytics", "GA4",
    "Brand Strategy", "Social Media Marketing", "Performance Marketing", "A/B Testing", "CRO",
    # Sales & Business Development
    "B2B Sales", "Salesforce", "Lead Generation", "Cold Outreach", "Account Management",
    "Pipeline Management", "Negotiation", "Prospecting", "Inbound Sales", "Outbound Sales",
    "CRM", "Business Development", "Contract Closing",
    # Product & Design
    "Product Management", "UI/UX", "Figma", "User Research", "Wireframing",
    "Prototyping", "Design Systems", "Adobe XD", "Product Strategy", "Agile", "Scrum",
    "User Journeys", "Usability Testing",
    # Finance & Accounting
    "Accounting", "Financial Modeling", "QuickBooks", "Excel", "P&L", "Auditing",
    "Financial Analysis", "Tax", "Bookkeeping", "Cash Flow", "Forecasting", "Payroll", "ERP", "SAP",
    # Operations & Logistics
    "Supply Chain", "Logistics", "Procurement", "Vendor Management", "Inventory Management",
    "Operations Management", "Process Optimization", "Six Sigma", "Workflow Automation",
    # HR & Talent Acquisition
    "Talent Acquisition", "Technical Recruiting", "Employee Relations", "Onboarding",
    "HRIS", "Workday", "Performance Management", "People Operations", "Greenhouse ATS",
    # Customer Success & Support
    "Customer Success", "Customer Support", "Zendesk", "Intercom", "Client Retention",
    "CSAT", "NPS", "Churn Prevention", "Account Health",
    # Data & Analytics
    "Data Analysis", "Tableau", "Power BI", "Data Modeling", "ETL", "Snowflake",
    "BigQuery", "Data Visualization", "Looker", "Business Intelligence", "Statistics",
    # Legal & Compliance
    "Commercial Contracts", "Compliance", "Contract Negotiation", "GDPR", "Corporate Law",
    "Regulatory Compliance", "Risk Management", "Intellectual Property", "Due Diligence",
    # Healthcare & Life Sciences
    "Clinical Operations", "HIPAA", "Healthcare Administration", "Patient Care",
    "Medical Terminology", "EMR", "EHR", "Clinical Trials"
]


class NormalizationService:
    """Normalizes raw ATS and feed listings to canonical data schema."""

    @staticmethod
    def clean_html(raw_html: Optional[str]) -> str:
        """Strips HTML tags, resolves entities, and produces clean markdown-like text."""
        if not raw_html:
            return ""

        # Replace block tags with newlines
        text = re.sub(r"</?(?:p|div|br|tr|li|ul|ol|h[1-6])[^>]*>", "\n", raw_html, flags=re.IGNORECASE)
        # Strip all remaining tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Decode HTML entities
        text = html.unescape(text)
        # Collapse multi-newlines and spaces
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
        cleaned = "\n".join(line for line in lines if line)
        return cleaned.strip()

    @staticmethod
    def compute_payload_hash(payload: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 hash of a JSON payload."""
        serialized = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def compute_dedup_key(cls, company: str, title: str, location: Optional[str] = None) -> str:
        """Computes deterministic SHA-256 deduplication key for cross-source matching."""
        comp_norm = re.sub(r"\s+", " ", (company or "").strip().lower())
        title_norm = re.sub(r"\s+", " ", (title or "").strip().lower())
        loc_norm = re.sub(r"\s+", " ", (location or "").strip().lower())
        raw_key = f"{comp_norm}|{title_norm}|{loc_norm}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def classify_workplace(
        title: str,
        location: Optional[str] = None,
        is_remote_flag: Optional[bool] = None,
        description: Optional[str] = None
    ) -> Tuple[WorkplaceType, bool]:
        """Infers workplace type (REMOTE, HYBRID, ON_SITE, UNKNOWN) and is_remote boolean."""
        if is_remote_flag is True:
            return WorkplaceType.REMOTE, True

        combined = f"{title} {location or ''} {(description or '')[:300]}".lower()

        if any(term in combined for term in ("remote", "work from home", "wfh", "anywhere", "telecommute")):
            return WorkplaceType.REMOTE, True
        if any(term in combined for term in ("hybrid", "flexible")):
            return WorkplaceType.HYBRID, False
        if any(term in combined for term in ("on-site", "onsite", "in-person", "in office", "office-based")):
            return WorkplaceType.ON_SITE, False

        if is_remote_flag is False:
            return WorkplaceType.ON_SITE, False

        return WorkplaceType.UNKNOWN, False

    @staticmethod
    def classify_employment_type(title: str, description: Optional[str] = None) -> EmploymentType:
        """Infers employment type from title or content."""
        combined = f"{title} {(description or '')[:300]}".lower()

        if any(term in combined for term in ("contract", "contractor", "freelance", "temp")):
            return EmploymentType.CONTRACT
        if any(term in combined for term in ("intern", "internship", "co-op", "trainee")):
            return EmploymentType.INTERNSHIP
        if any(term in combined for term in ("part-time", "part time")):
            return EmploymentType.PART_TIME
        if any(term in combined for term in ("full-time", "full time", "permanent")):
            return EmploymentType.FULL_TIME

        return EmploymentType.FULL_TIME

    @staticmethod
    def parse_location(location_str: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Parses location string into (city, state, country)."""
        if not location_str:
            return None, None, None

        # Clean string
        clean = re.sub(r"\(.*?\)", "", location_str).strip()
        parts = [p.strip() for p in clean.split(",") if p.strip()]

        if len(parts) == 1:
            return parts[0], None, None
        if len(parts) == 2:
            return parts[0], parts[1], None
        if len(parts) >= 3:
            return parts[0], parts[1], parts[2]

        return None, None, None

    @classmethod
    def extract_skills(cls, title: str, description: str) -> List[str]:
        """Identifies mentioned technical skills in title and job text."""
        combined = f" {title} {description} ".lower()
        found: List[str] = []

        for skill in KNOWN_SKILLS:
            # Word boundary search
            pattern = rf"(?:\b|_){re.escape(skill.lower())}(?:\b|_)"
            if re.search(pattern, combined):
                found.append(skill)

        return sorted(found)

    @classmethod
    def normalize_record(
        cls,
        raw_job: RawJobPayload,
        source: JobSourceRecord
    ) -> Dict[str, Any]:
        """Transforms a raw provider payload into canonical schema attributes."""
        raw = raw_job.raw_payload
        provider = source.provider.lower()

        # Provider-specific extraction
        title = ""
        description_raw = ""
        location_raw: Optional[str] = None
        department: Optional[str] = None
        company_name: Optional[str] = None
        is_remote_flag: Optional[bool] = None
        min_salary: Optional[float] = None
        max_salary: Optional[float] = None
        currency: Optional[str] = None
        salary_period: Optional[str] = None

        if provider == "greenhouse":
            title = raw.get("title", "Untitled Position")
            description_raw = raw.get("content", "")
            loc_data = raw.get("location")
            if isinstance(loc_data, dict):
                location_raw = loc_data.get("name")
            elif isinstance(loc_data, str):
                location_raw = loc_data

            depts = raw.get("departments", [])
            if depts and isinstance(depts, list) and isinstance(depts[0], dict):
                department = depts[0].get("name")

        elif provider == "ashby":
            title = raw.get("title", "Untitled Position")
            description_raw = raw.get("descriptionHtml") or raw.get("descriptionPlain") or ""
            location_raw = raw.get("location")
            department = raw.get("department")
            is_remote_flag = raw.get("isRemote")

            comp = raw.get("compensation")
            if isinstance(comp, dict):
                min_salary = comp.get("minSalary") or comp.get("minValue")
                max_salary = comp.get("maxSalary") or comp.get("maxValue")
                currency = comp.get("currency")
                salary_period = comp.get("interval")

        elif provider == "synthetic":
            title = raw.get("title", "Untitled Position")
            description_raw = raw.get("content", "")
            location_raw = raw.get("location")
            department = raw.get("department")
            is_remote_flag = raw.get("is_remote")

            salary_data = raw.get("salary")
            if isinstance(salary_data, dict):
                min_salary = salary_data.get("min")
                max_salary = salary_data.get("max")
                currency = salary_data.get("currency")
                salary_period = salary_data.get("period")

        elif provider == "adzuna":
            title = raw.get("title", "Untitled Position")
            description_raw = raw.get("description", "")
            loc_data = raw.get("location")
            if isinstance(loc_data, dict):
                location_raw = loc_data.get("display_name")
            elif isinstance(loc_data, str):
                location_raw = loc_data

            comp_data = raw.get("company")
            if isinstance(comp_data, dict) and comp_data.get("display_name"):
                company_name = comp_data.get("display_name")

            min_salary = raw.get("salary_min")
            max_salary = raw.get("salary_max")
            currency = "INR" if ("in" in source.base_url.lower()) else "USD"
            salary_period = "YEAR"

        elif provider == "jooble":
            title = raw.get("title", "Untitled Position")
            description_raw = raw.get("snippet", "")
            location_raw = raw.get("location")
            if raw.get("company"):
                company_name = str(raw.get("company"))

            sal_raw = str(raw.get("salary") or "")
            if sal_raw:
                nums = re.findall(r"[\d,]+", sal_raw)
                if nums:
                    parsed_nums = [float(n.replace(",", "")) for n in nums if len(n.replace(",", "")) >= 3]
                    if len(parsed_nums) == 1:
                        min_salary = parsed_nums[0]
                    elif len(parsed_nums) >= 2:
                        min_salary = min(parsed_nums[0], parsed_nums[1])
                        max_salary = max(parsed_nums[0], parsed_nums[1])
                    currency = "USD"
                    salary_period = "YEAR"

        elif provider == "lever":
            title = raw.get("text") or raw.get("title") or "Untitled Position"
            description_raw = raw.get("descriptionPlain") or raw.get("description") or ""
            cats = raw.get("categories")
            if isinstance(cats, dict):
                location_raw = cats.get("location")
                department = cats.get("department") or cats.get("team")
                commitment = cats.get("commitment")
                if commitment and ("remote" in str(commitment).lower()):
                    is_remote_flag = True
            comp_data = raw.get("company")
            if isinstance(comp_data, str) and comp_data:
                company_name = comp_data

        elif provider == "remoteok":
            title = raw.get("position") or raw.get("title") or "Untitled Position"
            description_raw = raw.get("description") or ""
            location_raw = raw.get("location") or "Remote"
            company_name = raw.get("company")
            is_remote_flag = True

        else:
            # Generic fallback
            title = raw.get("title") or raw.get("job_title") or "Untitled Position"
            description_raw = raw.get("description") or raw.get("content") or ""
            location_raw = raw.get("location") or raw.get("city")
            department = raw.get("department")
            is_remote_flag = raw.get("is_remote")

        # Company derivation
        if not company_name:
            company_name = source.display_name
            if " - " in company_name:
                company_name = company_name.split(" - ")[0].strip()
            elif " Board" in company_name:
                company_name = company_name.replace(" Board", "").strip()

        # Clean description
        description_clean = cls.clean_html(description_raw)

        # Classify attributes
        workplace_type, is_remote = cls.classify_workplace(
            title=title,
            location=location_raw,
            is_remote_flag=is_remote_flag,
            description=description_clean
        )
        employment_type = cls.classify_employment_type(title, description_clean)
        city, state, country = cls.parse_location(location_raw)
        skills = cls.extract_skills(title, description_clean)

        # Deduplication keys
        dedup_key = cls.compute_dedup_key(company_name, title, location_raw)

        # Provenance envelope
        # Ensure application URL is direct and not blocked by aggregator bot walls
        clean_app_url = raw_job.listing_url
        if not clean_app_url or "jooble.org" in clean_app_url.lower():
            clean_app_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(f'{company_name.strip()} {title.strip()} job apply')}"

        provenance = {
            "source_id": source.id,
            "source_key": source.source_key,
            "provider": source.provider,
            "normalizer_version": NORMALIZER_VERSION,
            "normalized_at": datetime.now(timezone.utc).isoformat(),
            "original_listing_url": raw_job.listing_url,
        }

        return {
            "source_id": source.id,
            "external_job_id": raw_job.external_job_id,
            "dedup_key_sha256": dedup_key,
            "title": title.strip(),
            "company_name": company_name.strip(),
            "description_clean": description_clean,
            "employment_type": employment_type.value,
            "workplace_type": workplace_type.value,
            "department": department.strip() if department else None,
            "city": city,
            "state": state,
            "country": country,
            "is_remote": is_remote,
            "min_salary": float(min_salary) if min_salary is not None else None,
            "max_salary": float(max_salary) if max_salary is not None else None,
            "currency": currency,
            "salary_period": salary_period,
            "is_salary_estimated": False,  # Strict: Never claim estimated numbers
            "required_skills_json": skills,
            "application_url": clean_app_url,
            "source_published_at": raw_job.source_published_at,
            "provenance_json": provenance,
        }
