"""
RIGHT FIT Core — Evidence-Based Job-Specific Resume Matcher
Compares candidate resume against specific job descriptions across required skills,
preferred skills, experience levels, and project-theme alignment without hallucination.
Migrates PortfolioProjectMatcher and AtsKeywordCoverageScorer from agentic-career-search.
Phase: Resume Intelligence Deep Enhancement (Phase 5)
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

from contracts.resume.schemas import ResumeJobMatchResponse

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9+.#/-]*", re.IGNORECASE)

_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "our", "that", "the", "their", "this",
    "to", "we", "with", "you", "your", "will", "can", "able", "about", "into", "over",
    "such", "than", "then", "them", "they", "was", "were", "what", "when", "who",
    "which", "while", "also", "both", "each", "more", "most", "other", "some", "team",
    "work", "role", "job", "years", "year", "experience", "including", "using", "across",
    "within", "required", "requirements", "preferred", "responsibilities", "opportunity",
    "position", "candidate", "candidates", "strong", "good", "great", "well", "must",
    "should", "may", "etc", "seeking", "looking", "apply", "applicant", "plus", "bonus",
    "minimum", "qualifications", "proficiency", "skills", "ability", "knowledge", "understanding"
})

_YEARS_EXP_RE = re.compile(
    r"(\d{1,2})\+?\s*(?:-\s*(\d{1,2}))?\s*years?(?:\s+of)?(?:\s+[a-z]{1,25}){0,3}\s+experience",
    re.IGNORECASE
)

_CANDIDATE_YEARS_RE = re.compile(
    r"(\d{1,2})\+?\s*years?(?:\s+of)?(?:\s+[a-z]{1,25}){0,3}(?:\s+experience|\s+building|\s+designing|\s+developing|\s+working|\s+in)",
    re.IGNORECASE
)


@dataclass(slots=True, frozen=True)
class PortfolioMatchResult:
    """Human-reviewable portfolio bullet match for one JD theme."""
    jd_theme: str
    matched_bullets: list[str]
    score: float
    requires_human_review: bool = True


def _require_nonblank_list(values: list[str] | None, *, field: str) -> list[str]:
    if values is None:
        raise ValueError(f"{field} must contain at least one non-empty string")
    cleaned = [item.strip() for item in values if item and str(item).strip()]
    if not cleaned:
        raise ValueError(f"{field} must contain at least one non-empty string")
    return cleaned


def _tokenize_theme(text: str) -> set[str]:
    return {token.lower() for token in _WORD_RE.findall(text or "")}


class PortfolioProjectMatcher:
    """Map portfolio bullets to JD theme keywords via offline token overlap."""

    def match(
        self,
        *,
        portfolio_bullets: list[str],
        jd_themes: list[str],
    ) -> list[PortfolioMatchResult]:
        """Score portfolio bullets against each JD theme (HITL; no network)."""
        cleaned_bullets = _require_nonblank_list(
            portfolio_bullets,
            field="portfolio_bullets",
        )
        cleaned_themes = _require_nonblank_list(jd_themes, field="jd_themes")

        results: list[PortfolioMatchResult] = []
        for theme in cleaned_themes:
            theme_tokens = _tokenize_theme(theme)
            if not theme_tokens:
                raise ValueError("jd_themes must contain at least one tokenizable theme")

            matched: list[str] = []
            best = 0.0
            for bullet in cleaned_bullets:
                bullet_tokens = _tokenize_theme(bullet)
                if not bullet_tokens:
                    continue
                overlap = theme_tokens & bullet_tokens
                if not overlap:
                    continue
                bullet_score = len(overlap) / len(theme_tokens)
                matched.append(bullet)
                if bullet_score > best:
                    best = bullet_score

            results.append(
                PortfolioMatchResult(
                    jd_theme=theme,
                    matched_bullets=matched,
                    score=round(best, 4),
                    requires_human_review=True,
                )
            )
        return results


class ResumeJobMatcher:
    """Matches candidate resume evidence against specific job requirements."""

    def __init__(self) -> None:
        self.portfolio_matcher = PortfolioProjectMatcher()

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Extracts normalized content tokens (stopwords and pure numbers removed)."""
        tokens = [match.group(0).lower().strip("+-.,#") for match in _WORD_RE.finditer(text or "")]
        return [
            token for token in tokens
            if token not in _STOPWORDS and len(token) > 1 and any(c.isalpha() for c in token)
        ]

    @classmethod
    def extract_keywords_ranked(cls, text: str, top_k: int = 30) -> List[str]:
        """Extracts ranked keywords using term-frequency and first-seen tie-breaking."""
        tokens = cls.tokenize(text)
        if not tokens:
            return []
        counts = Counter(tokens)
        seen: Dict[str, int] = {}
        for idx, token in enumerate(tokens):
            if token not in seen:
                seen[token] = idx
        ranked = sorted(counts.keys(), key=lambda t: (-counts[t], seen[t]))
        return ranked[:top_k]

    @classmethod
    def segment_jd_requirements(cls, jd_text: str) -> Tuple[List[str], List[str]]:
        """
        Heuristically partitions job description text into required vs preferred skills/tokens.
        """
        lines = [line.strip() for line in jd_text.splitlines() if line.strip()]
        required_text_parts: List[str] = []
        preferred_text_parts: List[str] = []

        current_mode = "REQUIRED"  # default
        for line in lines:
            lower = line.lower()
            if any(k in lower for k in ["preferred", "nice to have", "plus", "bonus", "desirable"]):
                current_mode = "PREFERRED"
            elif any(k in lower for k in ["required", "must have", "minimum qualifications", "requirements", "what you need"]):
                current_mode = "REQUIRED"

            if current_mode == "PREFERRED":
                preferred_text_parts.append(line)
            else:
                required_text_parts.append(line)

        req_text = " ".join(required_text_parts)
        pref_text = " ".join(preferred_text_parts)

        required_keywords = cls.extract_keywords_ranked(req_text, top_k=20)
        preferred_keywords = cls.extract_keywords_ranked(pref_text, top_k=15)

        # Ensure no duplicates in preferred that are already in required
        req_set = set(required_keywords)
        preferred_keywords = [k for k in preferred_keywords if k not in req_set]

        return required_keywords, preferred_keywords

    def align_portfolio_themes(
        self,
        portfolio_bullets: List[str],
        jd_themes: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Maps project/portfolio bullets to job posting themes via token overlap using PortfolioProjectMatcher.
        Always flags requires_human_review=True.
        """
        if not portfolio_bullets or not jd_themes:
            return []

        clean_bullets = [b.strip() for b in portfolio_bullets if b and b.strip()]
        clean_themes = [t.strip() for t in jd_themes if t and t.strip()]
        if not clean_bullets or not clean_themes:
            return []

        try:
            match_results = self.portfolio_matcher.match(
                portfolio_bullets=clean_bullets,
                jd_themes=clean_themes
            )
            return [
                {
                    "jd_theme": r.jd_theme,
                    "matched_bullets": r.matched_bullets,
                    "score": r.score,
                    "match_score": r.score,
                    "overlap_count": len(r.matched_bullets),
                    "requires_human_review": r.requires_human_review
                }
                for r in match_results
                if r.matched_bullets
            ]
        except ValueError:
            return []

    def match_resume_to_job(
        self,
        resume_id: str,
        version_id: str,
        target_job_title: str,
        target_job_description: str,
        raw_resume_text: str,
        extractions: Dict[str, Any],
        match_id: Optional[str] = None
    ) -> ResumeJobMatchResponse:
        """
        Executes full evidence-backed resume-to-job matching.
        """
        combined_jd = f"{target_job_title}\n\n{target_job_description}"
        resume_tokens = set(self.tokenize(raw_resume_text))

        # 1. Keyword coverage across entire JD
        top_jd_keywords = self.extract_keywords_ranked(combined_jd, top_k=30)
        all_matched_kws = [k for k in top_jd_keywords if k in resume_tokens]
        coverage_score = round(len(all_matched_kws) / len(top_jd_keywords), 4) if top_jd_keywords else 0.0

        # 2. Required vs Preferred segmentation
        req_keywords, pref_keywords = self.segment_jd_requirements(combined_jd)

        matched_req = [k for k in req_keywords if k in resume_tokens]
        missing_req = [k for k in req_keywords if k not in resume_tokens]
        req_match_pct = round((len(matched_req) / len(req_keywords)) * 100, 1) if req_keywords else 100.0

        matched_pref = [k for k in pref_keywords if k in resume_tokens]
        missing_pref = [k for k in pref_keywords if k not in resume_tokens]
        pref_match_pct = round((len(matched_pref) / len(pref_keywords)) * 100, 1) if pref_keywords else 100.0

        # 3. Experience level detection
        jd_exp_match = _YEARS_EXP_RE.search(combined_jd)
        required_years = None
        if jd_exp_match:
            required_years = float(jd_exp_match.group(1))

        # Detect candidate years from text and experience entries
        detected_years = 0.0
        experience_items = extractions.get("experience", [])
        resume_exp_match = _YEARS_EXP_RE.search(raw_resume_text) or _CANDIDATE_YEARS_RE.search(raw_resume_text)
        if resume_exp_match:
            detected_years = float(resume_exp_match.group(1))
        else:
            for exp in experience_items:
                # Estimate roughly 1.5 - 2 years per distinct recorded experience block if dates not parsed
                detected_years += 1.5
        detected_years = min(25.0, round(detected_years, 1))

        exp_assessment = "MEETS_OR_EXCEEDS"
        if required_years:
            if detected_years >= required_years:
                exp_assessment = "MEETS_REQUIREMENT"
                exp_score = 100.0
            elif detected_years >= (required_years - 1):
                exp_assessment = "BORDERLINE"
                exp_score = 75.0
            else:
                exp_assessment = "POTENTIALLY_UNDER_REQUIREMENT"
                exp_score = 50.0
        else:
            exp_score = 90.0

        # 4. Project bullet alignment to JD themes (PortfolioMatcher algorithm)
        project_bullets: List[str] = []
        for p in extractions.get("projects", []):
            if isinstance(p, dict) and p.get("description"):
                project_bullets.append(p["description"])
        for exp in experience_items:
            if isinstance(exp, dict):
                for resp in exp.get("responsibilities", []):
                    if isinstance(resp, str) and resp.strip():
                        project_bullets.append(resp)

        theme_candidates = req_keywords[:8]
        theme_alignments = self.align_portfolio_themes(project_bullets, theme_candidates)
        theme_score = round(min(100.0, (len(theme_alignments) / max(1, len(theme_candidates))) * 100), 1)

        # 5. Distinguish unverified / inferred matches
        inferred_skills = [
            s.get("name", "").lower() for s in extractions.get("inferred_skills", [])
            if isinstance(s, dict)
        ]
        unverified = [k for k in matched_req if k in inferred_skills]

        # 6. Overall Weighted Match Score
        # Required skills: 45%, Preferred skills: 20%, Experience level: 20%, Project alignment: 15%
        overall_score = round(
            (req_match_pct * 0.45) +
            (pref_match_pct * 0.20) +
            (exp_score * 0.20) +
            (theme_score * 0.15),
            1
        )

        # 7. Actionable job-specific suggestions
        suggestions: List[Dict[str, Any]] = []
        if missing_req:
            suggestions.append({
                "type": "CRITICAL_KEYWORD_GAP",
                "title": "Address High-Priority Job Requirements",
                "message": (
                    f"The role heavily emphasizes requirements: {', '.join(missing_req[:4])}. "
                    "If you have verified experience with any of these, state them clearly in your experience or skills list."
                ),
                "keywords": missing_req[:4]
            })

        if missing_pref:
            suggestions.append({
                "type": "PREFERRED_SKILL_ENHANCEMENT",
                "title": "Highlight Preferred Skills",
                "message": (
                    f"The posting lists nice-to-have capabilities: {', '.join(missing_pref[:3])}. "
                    "Featuring these can distinguish your profile from other applicants."
                ),
                "keywords": missing_pref[:3]
            })

        return ResumeJobMatchResponse(
            match_id=match_id,
            resume_id=resume_id,
            version_id=version_id,
            target_job_title=target_job_title,
            overall_match_score=overall_score,
            keyword_coverage_score=coverage_score,
            required_skills_match={
                "target_count": len(req_keywords),
                "matched_count": len(matched_req),
                "match_percentage": req_match_pct,
                "matched": matched_req,
                "missing": missing_req,
            },
            preferred_skills_match={
                "target_count": len(pref_keywords),
                "matched_count": len(matched_pref),
                "match_percentage": pref_match_pct,
                "matched": matched_pref,
                "missing": missing_pref,
            },
            experience_level_match={
                "required_years": required_years,
                "detected_years": detected_years,
                "estimated_candidate_years": detected_years,
                "assessment": exp_assessment,
                "score": exp_score,
            },
            project_theme_alignments=theme_alignments,
            unverified_matches=unverified,
            job_specific_suggestions=suggestions
        )


# Singleton
resume_job_matcher = ResumeJobMatcher()
