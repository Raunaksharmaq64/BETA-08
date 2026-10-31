"""
RIGHT FIT Core — Resume Parser & Extraction Engine
Extracts text, sections, structured entities, and traceable evidence from PDF and DOCX documents.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

import io
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import docx

from contracts.resume.schemas import ConfidenceLevel, EvidenceDTO, ReviewStatus


class ParsingError(Exception):
    """Raised when parsing fails due to corrupted, encrypted, or invalid document structure."""
    pass


# =============================================================================
# Document Section Header Patterns
# =============================================================================

_SECTION_PATTERNS: Dict[str, re.Pattern] = {
    "SUMMARY": re.compile(
        r"^(?:professional\s+summary|executive\s+summary|summary|profile|about\s+me|career\s+objective|objective)\b",
        re.IGNORECASE
    ),
    "EXPERIENCE": re.compile(
        r"^(?:(?:relevant|selected|professional|work|industry|software)\s+)*(?:experience|employment\s+history|work\s+history|career\s+history)\b",
        re.IGNORECASE
    ),
    "EDUCATION": re.compile(
        r"^(?:education|academic\s+background|academics|educational\s+background|degrees|qualifications)\b",
        re.IGNORECASE
    ),
    "SKILLS": re.compile(
        r"^(?:technical\s+skills|skills\s*&?\s*competencies|core\s+competencies|skills|technologies|tools\s*&?\s*technologies)\b",
        re.IGNORECASE
    ),
    "INTERNSHIPS": re.compile(
        r"^(?:internships?|internship\s+experience|summer\s+internships?)\b",
        re.IGNORECASE
    ),
    "PROJECTS": re.compile(
        r"^(?:(?:selected|featured|key|personal|academic|technical|industry|ai\s*&?\s*automation|software|notable)\s+)*(?:projects|automations?|portfolio)\b",
        re.IGNORECASE
    ),
    "CERTIFICATIONS": re.compile(
        r"^(?:certifications|certifications\s*&?\s*industry\s+simulations|licenses\s*&?\s*certifications|certificates|credentials|professional\s+certifications)\b",
        re.IGNORECASE
    ),
    "AWARDS": re.compile(
        r"^(?:honors\s*&?\s*awards|awards|achievements|recognition)\b",
        re.IGNORECASE
    ),
    "PUBLICATIONS": re.compile(
        r"^(?:publications|research|papers)\b",
        re.IGNORECASE
    ),
    "LANGUAGES": re.compile(
        r"^(?:spoken\s+languages|languages\s+spoken|language\s+proficiency)\b|^(?:languages)\s*[:\-]?\s*$",
        re.IGNORECASE
    ),
}

# =============================================================================
# Skills Taxonomy
# =============================================================================

_KNOWN_SKILLS: Dict[str, List[str]] = {
    "languages": [
        "python", "javascript", "typescript", "golang", "go", "rust", "java", "c++", "c#",
        "ruby", "php", "swift", "kotlin", "scala", "sql", "html", "html5", "css", "css3", "r", "julia"
    ],
    "frameworks": [
        "fastapi", "react", "react.js", "next.js", "nextjs", "vue", "vue.js", "angular",
        "django", "flask", "node.js", "nodejs", "express", "express.js", "spring boot",
        "spring", "ruby on rails", "rails", "asp.net", "tailwind", "tailwindcss", "bootstrap",
        "restful apis", "rest api", "web audio api", "jwt authentication", "whatsapp protocol"
    ],
    "databases": [
        "postgresql", "postgres", "mysql", "redis", "mongodb", "sqlite", "elasticsearch",
        "cassandra", "dynamodb", "mariadb", "oracle", "neo4j", "supabase"
    ],
    "cloud": [
        "aws", "amazon web services", "gcp", "google cloud", "azure", "docker", "docker compose",
        "kubernetes", "k8s", "terraform", "ansible", "cloudflare", "linux", "nginx", "render",
        "vercel", "ec2", "s3", "vpc networking"
    ],
    "tools": [
        "git", "github", "gitlab", "jira", "ci/cd", "postman", "celery", "rabbitmq",
        "kafka", "pytest", "jest", "webpack", "vite", "argocd", "datadog", "prometheus",
        "playwright", "selenium", "serpapi", "webhooks"
    ],
    "ai_agentic": [
        "ai agent workflows", "ai agents", "llm apis", "llm integrations", "large language models",
        "gemini", "claude", "gpt", "rag", "document rag", "bolna", "prompt engineering",
        "langchain", "llamaindex", "autogen", "crewai"
    ],
    "soft_skills": [
        "leadership", "mentorship", "agile", "scrum", "communication", "collaboration",
        "problem solving", "critical thinking", "project management"
    ]
}

# Regex for common contact elements
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
_PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
_LINKEDIN_RE = re.compile(r"\b(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_-]+)\b", re.IGNORECASE)
_GITHUB_RE = re.compile(r"\b(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_-]+)\b", re.IGNORECASE)
_URL_RE = re.compile(r"\bhttps?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[A-Za-z0-9_#?&/=-]*)?\b", re.IGNORECASE)

_DEGREE_KEYWORDS = [
    "bachelor of science", "bachelor of arts", "bachelor of engineering", "bachelor of technology",
    "b.s.", "b.a.", "b.e.", "b.tech", "btech", "bs", "ba",
    "master of science", "master of arts", "master of engineering", "master of technology",
    "m.s.", "m.a.", "m.tech", "mtech", "ms", "mba", "ph.d.", "phd", "doctor of philosophy"
]

_INSTITUTION_KEYWORDS = [
    "university", "college", "institute", "school", "academy", "polytechnic"
]

_DATE_RANGE_RE = re.compile(
    r"\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)?\s*\d{4})\s*[-–—to]+\s*((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)?\s*\d{4}|present|current)\b",
    re.IGNORECASE
)


class ResumeParserService:
    """Core extraction pipeline converting binary resumes into structured evidenced entities."""

    def extract_document_text_and_pages(
        self,
        file_bytes: bytes,
        file_type: str
    ) -> List[Dict[str, Any]]:
        """
        Extracts text partitioned by page number.
        Returns: list of dicts: [{"page_number": int, "text": str, "lines": List[str]}]
        """
        pages: List[Dict[str, Any]] = []

        if file_type == "pdf":
            try:
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                if doc.is_encrypted:
                    raise ParsingError("Password-protected PDF cannot be parsed. Please remove password encryption.")

                if doc.page_count == 0:
                    raise ParsingError("PDF document is empty (0 pages).")

                for page_idx in range(doc.page_count):
                    page = doc.load_page(page_idx)
                    page_text = page.get_text("text") or ""
                    lines = [line.strip() for line in page_text.splitlines() if line.strip()]
                    pages.append({
                        "page_number": page_idx + 1,
                        "text": page_text,
                        "lines": lines
                    })
                doc.close()

            except fitz.FileDataError as e:
                raise ParsingError(f"Corrupted or invalid PDF structure: {str(e)}")
            except Exception as e:
                if isinstance(e, ParsingError):
                    raise
                raise ParsingError(f"Failed to read PDF document: {str(e)}")

        elif file_type == "docx":
            try:
                docx_file = io.BytesIO(file_bytes)
                doc = docx.Document(docx_file)
                all_lines: List[str] = []

                for para in doc.paragraphs:
                    text = para.text.strip()
                    if text:
                        all_lines.append(text)

                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_text:
                            all_lines.append(row_text)

                if not all_lines:
                    raise ParsingError("DOCX document is empty.")

                full_text = "\n".join(all_lines)
                pages.append({
                    "page_number": 1,
                    "text": full_text,
                    "lines": all_lines
                })

            except Exception as e:
                if isinstance(e, ParsingError):
                    raise
                raise ParsingError(f"Failed to read DOCX document: {str(e)}")

        else:
            raise ParsingError(f"Unsupported document format: {file_type}")

        # Check total extracted text
        total_text = "".join(p["text"] for p in pages).strip()
        if not total_text:
            raise ParsingError("No extractable text found in document (may be scanned image or empty).")

        return pages

    def detect_sections(self, pages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Segments lines into recognized sections based on header patterns.
        Returns: {section_name: [{"page": int, "line": str}]}
        """
        sections: Dict[str, List[Dict[str, Any]]] = {
            "HEADER": [],
            "SUMMARY": [],
            "EXPERIENCE": [],
            "INTERNSHIPS": [],
            "EDUCATION": [],
            "SKILLS": [],
            "PROJECTS": [],
            "CERTIFICATIONS": [],
            "AWARDS": [],
            "PUBLICATIONS": [],
            "LANGUAGES": [],
            "OTHER": []
        }

        current_section = "HEADER"

        for page in pages:
            page_num = page["page_number"]
            for line in page["lines"]:
                trimmed = line.strip()
                if not trimmed:
                    continue

                # Test if line matches a known section header
                # Headers are typically short (< 50 chars)
                is_header = False
                if len(trimmed) < 55:
                    cleaned_header = re.sub(r"^[#*•\-\s]+", "", trimmed).strip()
                    
                    # If currently inside SKILLS, subcategory markers like "Languages: ...", "Languages | ..."
                    # should not break into a new section.
                    if current_section == "SKILLS" and re.match(
                        r"^(?:languages?|programming\s+languages?|frameworks?|databases?|cloud|tools|technologies)\b(?:\s*[:|])",
                        cleaned_header,
                        re.IGNORECASE
                    ):
                        is_header = False
                    else:
                        for sec_name, pattern in _SECTION_PATTERNS.items():
                            if pattern.match(cleaned_header):
                                current_section = sec_name
                                is_header = True
                                break

                if not is_header:
                    sections[current_section].append({
                        "page": page_num,
                        "line": trimmed
                    })

        return sections

    def extract_personal_info(
        self,
        pages: List[Dict[str, Any]],
        evidence_list: List[EvidenceDTO]
    ) -> Dict[str, Any]:
        """Extracts candidate contact details with exact evidence citations."""
        first_page = pages[0]
        text = first_page["text"]
        lines = first_page["lines"]
        page_num = 1

        info: Dict[str, Any] = {
            "full_name": None,
            "headline": None,
            "email": None,
            "phone": None,
            "city": None,
            "state": None,
            "country": None,
            "linkedin_url": None,
            "github_url": None,
            "portfolio_url": None
        }

        # Candidate name: First prominent line of document
        if lines:
            candidate_name = lines[0].strip()
            # Clean common label prefixes
            candidate_name = re.sub(r"^(?:name[:\s]+|resume[:\s]+)", "", candidate_name, flags=re.IGNORECASE).strip()
            if candidate_name and len(candidate_name) < 60 and not _EMAIL_RE.search(candidate_name):
                info["full_name"] = candidate_name
                evidence_list.append(EvidenceDTO(
                    field_id=str(uuid.uuid4()),
                    field_name="personal_info.full_name",
                    extracted_value=candidate_name,
                    source_section="HEADER",
                    excerpt=candidate_name,
                    page_number=page_num,
                    extraction_method="DOCUMENT_HEADER",
                    confidence_score=0.90,
                    confidence_level=ConfidenceLevel.HIGH,
                    review_status=ReviewStatus.PENDING
                ))

        # Headline / Professional Title: typically the line right after name
        if len(lines) > 1:
            headline_candidate = lines[1].strip()
            if (
                headline_candidate
                and len(headline_candidate) < 140
                and not _EMAIL_RE.search(headline_candidate)
                and not _PHONE_RE.search(headline_candidate)
                and "http" not in headline_candidate.lower()
                and "github" not in headline_candidate.lower()
                and "linkedin" not in headline_candidate.lower()
            ):
                info["headline"] = headline_candidate
                evidence_list.append(EvidenceDTO(
                    field_id=str(uuid.uuid4()),
                    field_name="personal_info.headline",
                    extracted_value=headline_candidate,
                    source_section="HEADER",
                    excerpt=headline_candidate,
                    page_number=page_num,
                    extraction_method="DOCUMENT_HEADER",
                    confidence_score=0.92,
                    confidence_level=ConfidenceLevel.HIGH,
                    review_status=ReviewStatus.PENDING
                ))

        # Location extraction (City, State, Country)
        loc_match = re.search(r"(?:📍|location[:\s]+)?\s*([A-Za-z\s]+),\s*([A-Za-z\s]+),\s*(India|United States|USA|UK|Canada|Germany|Singapore|[A-Za-z\s]+)", text)
        if loc_match:
            c = loc_match.group(1).strip()
            s = loc_match.group(2).strip()
            co = loc_match.group(3).strip()
            if c and len(c) < 50:
                info["city"] = c
            if s and len(s) < 50:
                info["state"] = s
            if co and len(co) < 50:
                info["country"] = co
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name="personal_info.location",
                extracted_value=f"{info.get('city')}, {info.get('state')}, {info.get('country')}",
                source_section="HEADER",
                excerpt=loc_match.group(0).strip(),
                page_number=page_num,
                extraction_method="REGEX",
                confidence_score=0.92,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        # Email
        email_match = _EMAIL_RE.search(text)
        if email_match:
            email = email_match.group(0).strip()
            info["email"] = email
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name="personal_info.email",
                extracted_value=email,
                source_section="HEADER",
                excerpt=email_match.group(0),
                page_number=page_num,
                extraction_method="REGEX",
                confidence_score=0.99,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        # Phone
        phone_match = _PHONE_RE.search(text)
        if phone_match:
            phone = phone_match.group(0).strip()
            info["phone"] = phone
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name="personal_info.phone",
                extracted_value=phone,
                source_section="HEADER",
                excerpt=phone_match.group(0),
                page_number=page_num,
                extraction_method="REGEX",
                confidence_score=0.95,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        # LinkedIn
        li_match = _LINKEDIN_RE.search(text)
        if li_match:
            li_url = f"https://linkedin.com/in/{li_match.group(1)}"
            info["linkedin_url"] = li_url
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name="personal_info.linkedin_url",
                extracted_value=li_url,
                source_section="HEADER",
                excerpt=li_match.group(0),
                page_number=page_num,
                extraction_method="REGEX",
                confidence_score=0.98,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        # GitHub
        gh_match = _GITHUB_RE.search(text)
        if gh_match:
            username = gh_match.group(1)
            # Avoid matching common paths
            if username.lower() not in ("about", "features", "pricing", "security"):
                gh_url = f"https://github.com/{username}"
                info["github_url"] = gh_url
                evidence_list.append(EvidenceDTO(
                    field_id=str(uuid.uuid4()),
                    field_name="personal_info.github_url",
                    extracted_value=gh_url,
                    source_section="HEADER",
                    excerpt=gh_match.group(0),
                    page_number=page_num,
                    extraction_method="REGEX",
                    confidence_score=0.98,
                    confidence_level=ConfidenceLevel.HIGH,
                    review_status=ReviewStatus.PENDING
                ))

        # Portfolio URL (other URLs)
        all_urls = _URL_RE.findall(text)
        for url in all_urls:
            lower = url.lower()
            if "linkedin.com" not in lower and "github.com" not in lower:
                info["portfolio_url"] = url
                evidence_list.append(EvidenceDTO(
                    field_id=str(uuid.uuid4()),
                    field_name="personal_info.portfolio_url",
                    extracted_value=url,
                    source_section="HEADER",
                    excerpt=url,
                    page_number=page_num,
                    extraction_method="REGEX",
                    confidence_score=0.90,
                    confidence_level=ConfidenceLevel.HIGH,
                    review_status=ReviewStatus.PENDING
                ))
                break

        return info

    def extract_summary(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> Optional[Dict[str, Any]]:
        """Extracts professional summary text if explicitly present in document."""
        summary_lines = sections.get("SUMMARY", [])
        if not summary_lines:
            return None

        combined_text = " ".join(item["line"] for item in summary_lines).strip()
        if not combined_text:
            return None

        page_num = summary_lines[0]["page"] if summary_lines else 1
        excerpt = combined_text[:200] + ("..." if len(combined_text) > 200 else "")

        evidence_list.append(EvidenceDTO(
            field_id=str(uuid.uuid4()),
            field_name="summary.text",
            extracted_value=combined_text,
            source_section="SUMMARY",
            excerpt=excerpt,
            page_number=page_num,
            extraction_method="SECTION_PARSER",
            confidence_score=0.92,
            confidence_level=ConfidenceLevel.HIGH,
            review_status=ReviewStatus.PENDING
        ))

        return {
            "text": combined_text,
            "headline": summary_lines[0]["line"] if summary_lines else None
        }

    def extract_education(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts education records supported by document evidence."""
        edu_lines = sections.get("EDUCATION", [])
        if not edu_lines:
            return []

        education_records: List[Dict[str, Any]] = []
        current_record: Optional[Dict[str, Any]] = None

        for item in edu_lines:
            line = item["line"]
            page_num = item["page"]
            lower_line = line.lower()

            # Check if line contains an institution keyword
            has_institution = any(kw in lower_line for kw in _INSTITUTION_KEYWORDS)
            # Check if line contains degree keyword
            has_degree = any(kw in lower_line for kw in _DEGREE_KEYWORDS)

            if has_institution or has_degree:
                if current_record and (current_record.get("institution") or current_record.get("degree")):
                    education_records.append(current_record)

                current_record = {
                    "institution": line if has_institution else "Higher Education Institution",
                    "degree": line if has_degree else None,
                    "field_of_study": None,
                    "start_date": None,
                    "end_date": None,
                    "grade": None,
                    "source_excerpt": line,
                    "page_number": page_num
                }

                # Date extraction
                date_match = _DATE_RANGE_RE.search(line)
                if date_match:
                    current_record["start_date"] = date_match.group(1).strip()
                    current_record["end_date"] = date_match.group(2).strip()

            elif current_record:
                # Supplementary line (e.g. GPA or dates)
                date_match = _DATE_RANGE_RE.search(line)
                if date_match and not current_record["end_date"]:
                    current_record["start_date"] = date_match.group(1).strip()
                    current_record["end_date"] = date_match.group(2).strip()

                if "gpa" in lower_line or "cgpa" in lower_line:
                    current_record["grade"] = line.strip()

        if current_record and (current_record.get("institution") or current_record.get("degree")):
            education_records.append(current_record)

        # Attach evidence items
        for idx, edu in enumerate(education_records):
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"education[{idx}].institution",
                extracted_value=edu["institution"],
                source_section="EDUCATION",
                excerpt=edu["source_excerpt"],
                page_number=edu["page_number"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return education_records

    def extract_experience(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts work experience roles and bullet points supported by evidence."""
        exp_lines = sections.get("EXPERIENCE", [])
        if not exp_lines:
            return []

        experiences: List[Dict[str, Any]] = []
        current_exp: Optional[Dict[str, Any]] = None

        for item in exp_lines:
            line = item["line"]
            page_num = item["page"]

            # Date ranges often signify a new role header
            date_match = _DATE_RANGE_RE.search(line)
            is_bullet = line.startswith(("-", "•", "*", "–", "—")) or len(line) > 100

            if date_match and not is_bullet:
                if current_exp and current_exp.get("company"):
                    experiences.append(current_exp)

                # Split title/company around separator or date
                header_text = _DATE_RANGE_RE.sub("", line).strip()
                parts = [p.strip() for p in re.split(r"[,|–—\t]", header_text) if p.strip()]

                company = parts[0] if parts else "Organization"
                title = parts[1] if len(parts) > 1 else "Professional Role"

                current_exp = {
                    "company": company,
                    "title": title,
                    "start_date": date_match.group(1).strip(),
                    "end_date": date_match.group(2).strip(),
                    "responsibilities": [],
                    "technologies": [],
                    "source_excerpt": line,
                    "page_number": page_num
                }
            elif current_exp:
                # Add responsibility bullet point
                cleaned_bullet = re.sub(r"^[-•*–—\s]+", "", line).strip()
                if cleaned_bullet:
                    current_exp["responsibilities"].append(cleaned_bullet)

        if current_exp and current_exp.get("company"):
            experiences.append(current_exp)

        # Attach evidence items
        for idx, exp in enumerate(experiences):
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"experience[{idx}].company",
                extracted_value=exp["company"],
                source_section="EXPERIENCE",
                excerpt=exp["source_excerpt"],
                page_number=exp["page_number"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.86,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return experiences

    def extract_skills(
        self,
        full_text: str,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], List[Dict[str, Any]]]:
        """
        Extracts categorized skills with boundary matching.
        Distinguishes between explicit skills (in SKILLS section) and inferred skills (in project/experience text).
        """
        categorized_skills: Dict[str, List[Dict[str, Any]]] = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "tools": [],
            "ai_agentic": [],
            "soft_skills": []
        }
        inferred_skills: List[Dict[str, Any]] = []

        skills_section_text = " ".join(item["line"] for item in sections.get("SKILLS", [])).lower()
        skills_section_page = sections["SKILLS"][0]["page"] if sections.get("SKILLS") else 1
        lower_full_text = full_text.lower()

        for category, skill_list in _KNOWN_SKILLS.items():
            for skill in skill_list:
                # Enforce boundary word matching to avoid false positives (e.g. 'c' in 'cat')
                pattern = rf"\b{re.escape(skill)}\b"
                in_skills_section = bool(re.search(pattern, skills_section_text))
                in_document = in_skills_section or bool(re.search(pattern, lower_full_text))

                if in_document:
                    confidence = 0.95 if in_skills_section else 0.80
                    confidence_lvl = ConfidenceLevel.HIGH if in_skills_section else ConfidenceLevel.MEDIUM
                    source_sec = "SKILLS" if in_skills_section else "BODY_TEXT"

                    # Generate excerpt snippet
                    match = re.search(pattern, skills_section_text if in_skills_section else lower_full_text)
                    start = max(0, match.start() - 25)
                    end = min(len(full_text), match.end() + 25)
                    excerpt_snippet = full_text[start:end].strip()

                    skill_item = {
                        "name": skill.title() if len(skill) > 3 else skill.upper(),
                        "category": category,
                        "source_section": source_sec,
                        "confidence_score": confidence,
                        "is_inferred": not in_skills_section
                    }

                    if in_skills_section:
                        categorized_skills[category].append(skill_item)
                        evidence_list.append(EvidenceDTO(
                            field_id=str(uuid.uuid4()),
                            field_name=f"skills.{category}.{skill}",
                            extracted_value=skill_item["name"],
                            source_section=source_sec,
                            excerpt=excerpt_snippet or skill,
                            page_number=skills_section_page,
                            extraction_method="KEYWORD_MATCHER",
                            confidence_score=confidence,
                            confidence_level=confidence_lvl,
                            review_status=ReviewStatus.PENDING
                        ))
                    else:
                        inferred_skills.append({
                            "name": skill_item["name"],
                            "category": category,
                            "source_section": source_sec,
                            "excerpt": excerpt_snippet or skill,
                            "confidence_score": confidence
                        })
                        evidence_list.append(EvidenceDTO(
                            field_id=str(uuid.uuid4()),
                            field_name=f"inferred_skills.{category}.{skill}",
                            extracted_value=skill_item["name"],
                            source_section=source_sec,
                            excerpt=excerpt_snippet or skill,
                            page_number=skills_section_page,
                            extraction_method="CONTEXT_INFERENCE",
                            confidence_score=confidence,
                            confidence_level=confidence_lvl,
                            review_status=ReviewStatus.PENDING
                        ))

        return categorized_skills, inferred_skills

    def extract_internships(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts internships explicitly documented in resume."""
        internship_lines = sections.get("INTERNSHIPS", [])
        internships: List[Dict[str, Any]] = []

        for idx, item in enumerate(internship_lines):
            line = item["line"].strip()
            if not line:
                continue
            cleaned = re.sub(r"^[-•*–—\s]+", "", line).strip()
            internship_item = {
                "title": cleaned,
                "page_number": item["page"],
                "excerpt": line
            }
            internships.append(internship_item)
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"internships[{idx}].title",
                extracted_value=cleaned,
                source_section="INTERNSHIPS",
                excerpt=line,
                page_number=item["page"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return internships

    def extract_publications(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts research papers and publications."""
        pub_lines = sections.get("PUBLICATIONS", [])
        if not pub_lines:
            return []

        publications: List[Dict[str, Any]] = []
        for idx, item in enumerate(pub_lines):
            line = item["line"].strip()
            if not line:
                continue
            cleaned = re.sub(r"^[-•*–—\s]+", "", line).strip()
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", cleaned)
            year = year_match.group(0) if year_match else None
            pub_item = {
                "title": cleaned,
                "year": year,
                "page_number": item["page"],
                "excerpt": line
            }
            publications.append(pub_item)
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"publications[{idx}].title",
                extracted_value=cleaned,
                source_section="PUBLICATIONS",
                excerpt=line,
                page_number=item["page"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return publications

    def extract_languages(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts natural spoken/written languages and proficiencies."""
        lang_lines = sections.get("LANGUAGES", [])
        if not lang_lines:
            return []

        _COMMON_LANGUAGES = [
            "english", "spanish", "french", "german", "mandarin", "cantonese",
            "hindi", "japanese", "russian", "arabic", "portuguese", "italian",
            "korean", "dutch", "polish", "turkish", "vietnamese", "swedish", "tamil", "bengali"
        ]
        _PROFICIENCY_PATTERNS = {
            "NATIVE": r"\b(native|bilingual|mother\s+tongue)\b",
            "FLUENT": r"\b(fluent|full\s+professional)\b",
            "PROFESSIONAL": r"\b(professional|working\s+proficiency)\b",
            "INTERMEDIATE": r"\b(intermediate|conversational)\b",
            "ELEMENTARY": r"\b(basic|elementary|beginner)\b",
        }

        languages: List[Dict[str, Any]] = []
        for item in lang_lines:
            line = item["line"].strip()
            if not line:
                continue
            lower_line = line.lower()
            for lang in _COMMON_LANGUAGES:
                if re.search(rf"\b{re.escape(lang)}\b", lower_line):
                    prof = "PROFESSIONAL"
                    for p_name, pat in _PROFICIENCY_PATTERNS.items():
                        if re.search(pat, lower_line):
                            prof = p_name
                            break
                    lang_item = {
                        "language": lang.capitalize(),
                        "proficiency": prof,
                        "page_number": item["page"],
                        "excerpt": line
                    }
                    languages.append(lang_item)
                    evidence_list.append(EvidenceDTO(
                        field_id=str(uuid.uuid4()),
                        field_name=f"languages[{len(languages)-1}].language",
                        extracted_value=lang.capitalize(),
                        source_section="LANGUAGES",
                        excerpt=line,
                        page_number=item["page"],
                        extraction_method="SECTION_PARSER",
                        confidence_score=0.90,
                        confidence_level=ConfidenceLevel.HIGH,
                        review_status=ReviewStatus.PENDING
                    ))

        return languages

    def extract_awards(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts awards, honors, and recognition."""
        award_lines = sections.get("AWARDS", [])
        if not award_lines:
            return []

        awards: List[Dict[str, Any]] = []
        for idx, item in enumerate(award_lines):
            line = item["line"].strip()
            if not line:
                continue
            cleaned = re.sub(r"^[-•*–—\s]+", "", line).strip()
            year_match = re.search(r"\b(19\d{2}|20\d{2})\b", cleaned)
            year = year_match.group(0) if year_match else None
            award_item = {
                "title": cleaned,
                "year": year,
                "page_number": item["page"],
                "excerpt": line
            }
            awards.append(award_item)
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"awards[{idx}].title",
                extracted_value=cleaned,
                source_section="AWARDS",
                excerpt=line,
                page_number=item["page"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.85,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return awards

    def extract_projects(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts projects explicitly documented in resume."""
        proj_lines = sections.get("PROJECTS", [])
        if not proj_lines:
            return []

        projects: List[Dict[str, Any]] = []
        current_proj: Optional[Dict[str, Any]] = None

        for item in proj_lines:
            line = item["line"].strip()
            page_num = item["page"]
            if not line:
                continue

            # Detect tech stack lines like "React • FastAPI • PostgreSQL • Redis"
            if current_proj and ("•" in line or "|" in line) and any(
                kw in line.lower() for kw in ("react", "fastapi", "python", "node", "express", "postgres", "redis", "mongodb", "docker", "gemini", "aws", "bolna", "rag", "sql")
            ):
                techs = [t.strip() for t in re.split(r"[•|]", line) if t.strip()]
                current_proj["technologies"].extend(techs)
                continue

            # Check if this line is a project title: short, not starting with bullet point
            is_bullet = line.startswith(("-", "•", "*", "–", "—"))
            is_title = (not is_bullet) and (
                "—" in line or " - " in line or ":" in line or "(" in line or len(line) < 65
            ) and not any(line.lower().startswith(b) for b in ("architected", "engineered", "integrated", "built", "developed", "implemented"))

            if is_title:
                if current_proj:
                    projects.append(current_proj)
                current_proj = {
                    "name": line.strip(),
                    "description": "",
                    "technologies": [],
                    "bullets": [],
                    "page_number": page_num,
                    "excerpt": line
                }
            elif current_proj:
                cleaned = re.sub(r"^[-•*–—\s]+", "", line).strip()
                if cleaned:
                    current_proj.setdefault("bullets", []).append(cleaned)
                    if current_proj["description"]:
                        current_proj["description"] += "\n" + cleaned
                    else:
                        current_proj["description"] = cleaned

        if current_proj:
            projects.append(current_proj)

        # Clean duplicates or fragment titles (filter out orphan bullets)
        final_projects = []
        for p in projects:
            name = p["name"].strip()
            if (
                len(name) >= 6
                and not name[0].islower()
                and not name.lower().startswith(("and ", "architecture", "dynamic", "fees", "spoken", "technical audits", "recognition"))
            ):
                final_projects.append(p)

        for idx, proj in enumerate(final_projects):
            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"projects[{idx}].name",
                extracted_value=proj["name"],
                source_section="PROJECTS",
                excerpt=proj["excerpt"],
                page_number=proj["page_number"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.88,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return final_projects

    def extract_certifications(
        self,
        sections: Dict[str, List[Dict[str, Any]]],
        evidence_list: List[EvidenceDTO]
    ) -> List[Dict[str, Any]]:
        """Extracts certifications explicitly documented in resume."""
        cert_lines = sections.get("CERTIFICATIONS", [])
        if not cert_lines:
            return []

        # Merge wrapped lines (e.g., "(EC2, S3, VPC Networking," followed by "Cloud Architecture)")
        merged_lines: List[Dict[str, Any]] = []
        for item in cert_lines:
            raw_line = item["line"].strip()
            if not raw_line:
                continue
            if merged_lines and (
                merged_lines[-1]["line"].count("(") > merged_lines[-1]["line"].count(")")
                or merged_lines[-1]["line"].endswith(",")
            ):
                merged_lines[-1]["line"] += " " + raw_line
            else:
                merged_lines.append({"line": raw_line, "page": item["page"]})

        certifications: List[Dict[str, Any]] = []
        for idx, item in enumerate(merged_lines):
            line = item["line"].strip()
            if not line:
                continue
            cleaned = re.sub(r"^[-•*–—\s]+", "", line).strip()
            issuer = None
            if ":" in cleaned:
                parts = cleaned.split(":", 1)
                issuer = parts[0].strip()

            cert_item = {
                "name": cleaned,
                "issuer": issuer,
                "page_number": item["page"],
                "excerpt": line
            }
            certifications.append(cert_item)

            evidence_list.append(EvidenceDTO(
                field_id=str(uuid.uuid4()),
                field_name=f"certifications[{idx}].name",
                extracted_value=cleaned,
                source_section="CERTIFICATIONS",
                excerpt=line,
                page_number=item["page"],
                extraction_method="SECTION_PARSER",
                confidence_score=0.90,
                confidence_level=ConfidenceLevel.HIGH,
                review_status=ReviewStatus.PENDING
            ))

        return certifications

    def parse_document(
        self,
        file_bytes: bytes,
        file_type: str
    ) -> Tuple[str, Dict[str, Any], List[EvidenceDTO]]:
        """
        Complete parsing and entity extraction pipeline.
        Returns: (raw_text, structured_extractions_dict, evidence_list)
        """
        # 1. Page & Text Extraction
        pages = self.extract_document_text_and_pages(file_bytes, file_type)
        raw_text = "\n\n".join(f"--- Page {p['page_number']} ---\n{p['text']}" for p in pages)

        # Scanned document & mixed-content diagnostics (per-page threshold < 50 extractable characters)
        extraction_notes: List[str] = []
        low_text_pages: List[int] = []
        normal_text_pages: List[int] = []
        is_scanned_pdf = False
        is_mixed_content = False
        ocr_required = False

        if file_type == "pdf" and pages:
            for p in pages:
                page_chars = len(p["text"].strip())
                if page_chars < 50:
                    low_text_pages.append(p["page_number"])
                else:
                    normal_text_pages.append(p["page_number"])

            if len(low_text_pages) == len(pages):
                # All pages have fewer than 50 characters -> Scanned physical document
                is_scanned_pdf = True
                is_mixed_content = False
                ocr_required = True
                extraction_notes.append(
                    "Notice: Scanned PDF detected (all pages contain fewer than 50 extractable characters). "
                    "Optical Character Recognition (OCR) is required to accurately extract structured text."
                )
            elif len(low_text_pages) > 0:
                # Some pages have < 50 characters while others have normal text -> Mixed-content document
                is_scanned_pdf = False
                is_mixed_content = True
                ocr_required = True
                low_pages_str = ", ".join(map(str, low_text_pages))
                extraction_notes.append(
                    f"Notice: Mixed-content PDF detected. Page(s) {low_pages_str} contain fewer than 50 characters "
                    "(scanned images, portfolio inserts, or attachments). Portions of this resume require OCR."
                )
            else:
                is_scanned_pdf = False
                is_mixed_content = False
                ocr_required = False

        # 2. Section Segmentation
        sections = self.detect_sections(pages)

        # 3. Entity & Evidence Extraction
        evidence_list: List[EvidenceDTO] = []

        personal_info = self.extract_personal_info(pages, evidence_list)
        summary = self.extract_summary(sections, evidence_list)
        education = self.extract_education(sections, evidence_list)
        experience = self.extract_experience(sections, evidence_list)
        internships = self.extract_internships(sections, evidence_list)
        explicit_skills, inferred_skills = self.extract_skills(raw_text, sections, evidence_list)
        projects = self.extract_projects(sections, evidence_list)
        certifications = self.extract_certifications(sections, evidence_list)
        publications = self.extract_publications(sections, evidence_list)
        languages = self.extract_languages(sections, evidence_list)
        awards = self.extract_awards(sections, evidence_list)

        structured_extractions = {
            "sections": {k: [i["line"] for i in v] for k, v in sections.items() if v},
            "personal_info": personal_info,
            "summary": summary,
            "education": education,
            "experience": experience,
            "internships": internships,
            "skills": explicit_skills,  # Backward compatible alias
            "explicit_skills": explicit_skills,
            "inferred_skills": inferred_skills,
            "projects": projects,
            "certifications": certifications,
            "publications": publications,
            "languages": languages,
            "awards": awards,
            "is_scanned_pdf": is_scanned_pdf,
            "is_mixed_content": is_mixed_content,
            "ocr_required": ocr_required,
            "low_text_pages": low_text_pages,
            "extraction_notes": extraction_notes,
        }

        return raw_text, structured_extractions, evidence_list


# Singleton instance
resume_parser_service = ResumeParserService()

