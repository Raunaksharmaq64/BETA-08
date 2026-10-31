"""
RIGHT FIT Core — ATS Keyword Coverage & Bullet Impact Scorer (Phase 3)
Integrates algorithms from ats_keyword_coverage.py and bullet_impact.py.
Provides transparent keyword alignment (with required vs preferred separation),
first-seen tie-breaking, and contextual bullet impact scoring without fake black-box claims.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

# Word matching regex matching letters, digits, and technical symbols (+, #, ., -, /)
_WORD_RE = re.compile(r"[a-z][a-z0-9+.#/-]{1,}", re.IGNORECASE)

# Comprehensive stopword list: 140+ common English words, prepositions, and domain-generic terms
# Generic recruitment words are filtered out so they are not counted as meaningful technical skills.
_STOPWORDS: frozenset[str] = frozenset({
    # Common English grammar stopwords
    "a", "about", "above", "across", "after", "again", "against", "all", "almost", "also",
    "am", "an", "and", "any", "are", "aren't", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "cannot", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has",
    "have", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "isn't", "it", "its", "itself", "let", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    # Domain-generic recruitment words (not meaningful skills)
    "team", "teams", "work", "working", "worker", "role", "roles", "job", "jobs", "years",
    "year", "experience", "experienced", "including", "using", "across", "within", "required",
    "require", "requires", "requiring", "requirements", "requirement", "preferred", "preference",
    "responsibilities", "responsibility", "opportunity", "opportunities", "position", "positions",
    "candidate", "candidates", "applicant", "applicants", "strong", "good", "great", "well", "must",
    "should", "may", "etc", "seeking", "looking", "ideal", "successful", "environment", "company",
    "companies", "fast-paced", "dynamic", "excellent", "skills", "skill", "ability", "abilities",
    "track", "record", "day-to-day", "daily", "tasks", "task", "duties", "duty", "hands-on", "high",
    "level", "full-time", "part-time", "remote", "hybrid", "office", "location", "plus",
    "bonus", "minimum", "qualifications", "qualification", "degree", "field", "related",
    "demonstrated", "proven", "proficient", "proficiency", "familiarity", "knowledge",
    "understanding", "willingness", "passion", "passionate", "drive", "driven"
})

# Quantifiable metric patterns from bullet_impact.py
_PERCENT_RE = re.compile(r"(?<!\w)\d{1,3}(?:\.\d+)?%")
_MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmMbB]?\b")
_MULTIPLIER_RE = re.compile(r"\b\d+(?:\.\d+)?\s?x\b", re.IGNORECASE)
_SCALE_RE = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?\s*[kKmMbB]?\+?\s*"
    r"(?:users?|customers?|requests?|qps|rps|devices?|"
    r"merchants?|transactions?|seats?|employees?|engineers?|queries|records|events|messages)\b",
    re.IGNORECASE,
)

# Strong active verbs
_ACTION_VERBS: frozenset[str] = frozenset({
    "led", "owned", "shipped", "launched", "reduced", "increased", "improved",
    "cut", "grew", "built", "designed", "automated", "architected", "delivered",
    "scaled", "spearheaded", "accelerated", "transformed", "engineered",
    "optimized", "deployed", "orchestrated", "mentored", "implemented", "established",
    "authored", "refactored", "migrated", "centralized", "streamlined", "standardized",
    "debugged", "resolved", "devised", "constructed", "pioneered", "negotiated"
})

# Passive or weak phrases to flag
_PASSIVE_WEAK_PHRASES: tuple[str, ...] = (
    "responsible for",
    "helped with",
    "worked on",
    "assisted in",
    "assisted with",
    "participated in",
    "handled duties",
    "duties included",
    "tasked with",
    "involved in",
    "helped the team",
)

# Technical complexity indicators (give contextual credit to bullets without raw numbers)
_TECH_COMPLEXITY_CUES: tuple[str, ...] = (
    "distributed", "microservices", "scalable", "high-throughput", "low-latency",
    "ci/cd", "concurrency", "fault-tolerant", "monolith", "oauth2", "oidc", "pipeline",
    "etl", "real-time", "asynchronous", "clustering", "sharding", "replication",
    "zero-downtime", "idempotent", "load balancer", "caching", "containerization"
)

_REQUIRED_SECTION_RE = re.compile(
    r"(?:(?:required|minimum|basic|must\s+have)\s+(?:qualifications|requirements|skills|criteria)?)(.*?)(?=(?:preferred|nice\s+to\s+have|bonus|desired|benefits|what\s+we\s+offer|\Z))",
    re.IGNORECASE | re.DOTALL
)

_PREFERRED_SECTION_RE = re.compile(
    r"(?:(?:preferred|nice\s+to\s+have|bonus|desired|additional)\s+(?:qualifications|requirements|skills|criteria)?)(.*?)(?=(?:required|minimum|benefits|what\s+we\s+offer|\Z))",
    re.IGNORECASE | re.DOTALL
)


@dataclass(slots=True, frozen=True)
class KeywordCoverageOutcome:
    """ATS keyword coverage outcome conforming to source library API."""
    coverage_score: float
    jd_keywords: list[str]
    present_keywords: list[str]
    missing_keywords: list[str]
    required_keywords: list[str]
    required_matched: list[str]
    required_missing: list[str]
    preferred_keywords: list[str]
    preferred_matched: list[str]
    preferred_missing: list[str]
    keyword_frequency: dict[str, int]
    keyword_relevance: dict[str, str]
    ranking_and_explanation: list[dict[str, Any]]

    def __iter__(self):
        """Allows unpacking as (coverage_score, present_keywords, missing_keywords)."""
        yield self.coverage_score
        yield self.present_keywords
        yield self.missing_keywords


@dataclass(slots=True, frozen=True)
class BulletImpactItem:
    """Impact evaluation for a single resume bullet."""
    original_bullet: str
    detected_action_verbs: list[str]
    quantifiable_evidence: list[str]
    impact_band: str  # STRONG, MODERATE, WEAK
    score: float
    explanation: str
    improvement_opportunity: str
    has_passive_phrase: bool


@dataclass(slots=True, frozen=True)
class BulletImpactReport:
    """Complete resume bullet impact report."""
    bullets_scored: list[BulletImpactItem]
    average_score: float
    strong_bullets_count: int
    moderate_bullets_count: int
    weak_bullets_count: int
    weak_bullets: list[str]
    guidance: list[str]
    requires_human_review: bool
    auto_rewrite: bool

    def __getitem__(self, item: str):
        """Allows dictionary-style subscripting for backward-compatibility."""
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)


class ATSAnalysisService:
    """
    ATS Keyword Coverage & Bullet Impact Scorer.
    Integrates source algorithms from ats_keyword_coverage.py and bullet_impact.py.
    """

    @staticmethod
    def clean_token(token: str) -> str:
        """Strips leading and trailing punctuation while preserving internal dots/hyphens."""
        return token.strip(".,;:!?()[]{}\"'`~").lower()

    @classmethod
    def tokenize(cls, text: str) -> list[str]:
        """
        Extracts lowercased content tokens from free-form text.
        Removes stopwords and short non-substantive tokens.
        """
        if not text:
            return []
        raw_matches = _WORD_RE.findall(text)
        tokens: list[str] = []
        for match in raw_matches:
            cleaned = cls.clean_token(match)
            if cleaned and cleaned not in _STOPWORDS and len(cleaned) > 1:
                # Filter out pure numbers
                if not re.fullmatch(r"\d+", cleaned):
                    tokens.append(cleaned)
        return tokens

    @classmethod
    def extract_job_keywords(
        cls,
        job_text: str,
        *,
        top_k: int = 25
    ) -> list[str]:
        """
        Extracts ranked keywords from a job description.
        Ranking is by term frequency; ties break using stable first-seen order.
        """
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")
        tokens = cls.tokenize(job_text)
        if not tokens:
            return []

        counts = Counter(tokens)
        seen: dict[str, int] = {}
        for index, token in enumerate(tokens):
            if token not in seen:
                seen[token] = index

        # Stable sort: (-frequency, first-seen index)
        ranked = sorted(counts.keys(), key=lambda t: (-counts[t], seen[t]))
        return ranked[:top_k]

    @classmethod
    def segment_jd_requirements(cls, job_text: str) -> Tuple[str, str, str]:
        """
        Separates job text into (required_text, preferred_text, general_text).
        """
        if not job_text:
            return "", "", ""

        req_match = _REQUIRED_SECTION_RE.search(job_text)
        required_text = req_match.group(1).strip() if req_match else ""

        pref_match = _PREFERRED_SECTION_RE.search(job_text)
        preferred_text = pref_match.group(1).strip() if pref_match else ""

        return required_text, preferred_text, job_text

    @classmethod
    def score_keyword_coverage(
        cls,
        resume_text: str | None,
        job_text: str | None,
        *,
        top_k: int = 25
    ) -> KeywordCoverageOutcome:
        """
        Scores ATS keyword coverage of resume against job description.
        Includes required vs. preferred segregation, frequency ranking, and explanations.
        """
        if top_k < 1:
            raise ValueError(f"top_k must be >= 1, got {top_k}")

        clean_jd = (job_text or "").strip()
        clean_resume = (resume_text or "").strip()

        if not clean_jd:
            return KeywordCoverageOutcome(
                coverage_score=0.0,
                jd_keywords=[],
                present_keywords=[],
                missing_keywords=[],
                required_keywords=[],
                required_matched=[],
                required_missing=[],
                preferred_keywords=[],
                preferred_matched=[],
                preferred_missing=[],
                keyword_frequency={},
                keyword_relevance={},
                ranking_and_explanation=[]
            )

        # 1. Extract all JD keywords with tie-breaking
        jd_keywords = cls.extract_job_keywords(clean_jd, top_k=top_k)
        if not jd_keywords:
            return KeywordCoverageOutcome(
                coverage_score=0.0,
                jd_keywords=[],
                present_keywords=[],
                missing_keywords=[],
                required_keywords=[],
                required_matched=[],
                required_missing=[],
                preferred_keywords=[],
                preferred_matched=[],
                preferred_missing=[],
                keyword_frequency={},
                keyword_relevance={},
                ranking_and_explanation=[]
            )

        # 2. Extract tokens from resume
        resume_tokens: Set[str] = set(cls.tokenize(clean_resume))

        # 3. Frequency counter for JD tokens
        all_jd_tokens = cls.tokenize(clean_jd)
        jd_counts = Counter(all_jd_tokens)

        # 4. Required vs Preferred segmentation
        req_text, pref_text, _ = cls.segment_jd_requirements(clean_jd)
        req_tokens_set = set(cls.tokenize(req_text)) if req_text else set()
        pref_tokens_set = set(cls.tokenize(pref_text)) if pref_text else set()

        present_kws: list[str] = []
        missing_kws: list[str] = []
        required_kws: list[str] = []
        required_matched: list[str] = []
        required_missing: list[str] = []
        preferred_kws: list[str] = []
        preferred_matched: list[str] = []
        preferred_missing: list[str] = []
        keyword_relevance: dict[str, str] = {}
        rankings: list[dict[str, Any]] = []

        for rank, kw in enumerate(jd_keywords, start=1):
            is_present = kw in resume_tokens
            if is_present:
                present_kws.append(kw)
            else:
                missing_kws.append(kw)

            # Determine relevance
            if kw in req_tokens_set:
                rel = "REQUIRED"
                required_kws.append(kw)
                if is_present:
                    required_matched.append(kw)
                else:
                    required_missing.append(kw)
            elif kw in pref_tokens_set:
                rel = "PREFERRED"
                preferred_kws.append(kw)
                if is_present:
                    preferred_matched.append(kw)
                else:
                    preferred_missing.append(kw)
            else:
                rel = "GENERAL"

            keyword_relevance[kw] = rel
            freq = jd_counts.get(kw, 1)

            # Construct explainable ranking entry
            status_text = "MATCHED" if is_present else "MISSING"
            explanation = (
                f"Appears {freq} time(s) in job description ({rel.lower()} qualification). "
                f"{'Verified in resume text.' if is_present else 'Not found in candidate resume.'}"
            )
            rankings.append({
                "rank": rank,
                "keyword": kw,
                "frequency": freq,
                "status": status_text,
                "relevance": rel,
                "explanation": explanation
            })

        coverage = round(len(present_kws) / len(jd_keywords), 4)

        return KeywordCoverageOutcome(
            coverage_score=coverage,
            jd_keywords=jd_keywords,
            present_keywords=present_kws,
            missing_keywords=missing_kws,
            required_keywords=required_kws,
            required_matched=required_matched,
            required_missing=required_missing,
            preferred_keywords=preferred_kws,
            preferred_matched=preferred_matched,
            preferred_missing=preferred_missing,
            keyword_frequency={kw: jd_counts[kw] for kw in jd_keywords},
            keyword_relevance=keyword_relevance,
            ranking_and_explanation=rankings
        )

    @classmethod
    def evaluate_bullet(cls, bullet: str) -> BulletImpactItem:
        """
        Scores an individual resume bullet point for action verbs, quantifiable metrics,
        and meaningful architectural/technical complexity.
        """
        trimmed = bullet.strip()
        cues: list[str] = []
        action_verbs_found: list[str] = []
        points = 0.0

        # 1. Action verb detection
        first_word = trimmed.split()[0].lower() if trimmed.split() else ""
        lowered = trimmed.lower()

        for verb in _ACTION_VERBS:
            if first_word.startswith(verb) or re.search(rf"\b{re.escape(verb)}\b", lowered[:30]):
                if verb not in action_verbs_found:
                    action_verbs_found.append(verb)

        if action_verbs_found:
            cues.append("action_verb")
            points += 0.25

        # 2. Passive opening check
        has_passive = any(phrase in lowered for phrase in _PASSIVE_WEAK_PHRASES)

        # 3. Quantifiable metric detection
        if _PERCENT_RE.search(trimmed):
            cues.append("percentage")
            points += 0.35
        if _MONEY_RE.search(trimmed):
            cues.append("financial")
            points += 0.35
        if _MULTIPLIER_RE.search(trimmed):
            cues.append("multiplier")
            points += 0.25
        if _SCALE_RE.search(trimmed):
            cues.append("scale")
            points += 0.30

        # 4. Contextual complexity (do not penalize bullets without raw numbers if technically rich)
        has_tech_complexity = any(t in lowered for t in _TECH_COMPLEXITY_CUES)
        if has_tech_complexity:
            cues.append("technical_complexity")
            points += 0.20

        # Passive phrase penalty
        if has_passive:
            cues.append("passive_phrase")
            points = max(0.10, points - 0.20)

        # Boost for combining active leadership with concrete financial/percentage/scale outcome
        if action_verbs_found and any(m in cues for m in ("percentage", "financial", "scale", "multiplier")):
            points = max(points, 0.75)

        score = min(1.0, round(points, 2))

        # Determine band:
        # STRONG: score >= 0.70 with metrics and action verbs
        # MODERATE: 0.35 to 0.70, or strong technical complexity even without numerical metrics
        # WEAK: < 0.35, passive opening or lacks both numbers and technical depth
        if score >= 0.70:
            band = "STRONG"
            explanation = "Strong bullet: Opens with an active ownership verb and demonstrates measurable impact or scale."
            opportunity = "Maintain this standard. Verify metrics can be substantiated in technical interviews."
        elif score >= 0.35 or (action_verbs_found and has_tech_complexity):
            band = "MODERATE"
            if not any(m in cues for m in ("percentage", "financial", "scale", "multiplier")):
                explanation = "Moderate bullet: Strong technical contribution, but lacks quantifiable business or engineering metrics."
                opportunity = "Consider adding verifiable, quantifiable figures (e.g. throughput improvement %, user count, latency reduction)."
            else:
                explanation = "Moderate bullet: Contains quantifiable evidence; strengthen opening verb for maximum impact."
                opportunity = "Lead with a decisive action verb (e.g. 'Architected', 'Spearheaded') rather than generic verbs."
        else:
            band = "WEAK"
            if has_passive:
                explanation = "Weak bullet: Begins with passive language ('responsible for', 'assisted with') that dilutes candidate ownership."
                opportunity = "Rewrite using active power verbs and articulate the concrete outcome of the effort."
            else:
                explanation = "Weak bullet: Lacks quantifiable metrics and authoritative action verbs."
                opportunity = "State the technical challenge solved, the technologies used, and the measurable outcome achieved."

        return BulletImpactItem(
            original_bullet=trimmed,
            detected_action_verbs=action_verbs_found,
            quantifiable_evidence=[c for c in cues if c in ("percentage", "financial", "multiplier", "scale")],
            impact_band=band,
            score=score,
            explanation=explanation,
            improvement_opportunity=opportunity,
            has_passive_phrase=has_passive
        )

    @classmethod
    def score_bullet_impact(cls, bullets: list[str] | None) -> Tuple[float, BulletImpactReport]:
        """
        Evaluates a collection of resume bullets.
        Returns: (overall_impact_score_0_to_100, BulletImpactReport)
        """
        cleaned = [b.strip() for b in (bullets or []) if b and b.strip()]
        if not cleaned:
            empty_report = BulletImpactReport(
                bullets_scored=[],
                average_score=0.0,
                strong_bullets_count=0,
                moderate_bullets_count=0,
                weak_bullets_count=0,
                weak_bullets=[],
                guidance=["No non-empty bullet points were provided for analysis."],
                requires_human_review=True,
                auto_rewrite=False
            )
            return 0.0, empty_report

        scored = [cls.evaluate_bullet(b) for b in cleaned]
        strong_count = sum(1 for b in scored if b.impact_band == "STRONG")
        moderate_count = sum(1 for b in scored if b.impact_band == "MODERATE")
        weak_count = sum(1 for b in scored if b.impact_band == "WEAK")
        weak_bullets = [b.original_bullet for b in scored if b.impact_band == "WEAK"]

        average_score = round(sum(b.score for b in scored) / len(scored), 2)
        overall_impact_score = round(((strong_count + 0.5 * moderate_count) / len(scored)) * 100, 1)

        guidance = [
            f"Evaluated {len(scored)} bullet(s): {strong_count} strong, {moderate_count} moderate, {weak_count} weak.",
            "requires_human_review=True; auto_rewrite=False — suggestions are advisory only and never alter raw text.",
            "Bullets without numerical metrics receive moderate credit if they articulate technical complexity."
        ]
        if weak_bullets:
            guidance.append(f"{len(weak_bullets)} bullet(s) scored in the weak band due to passive verbs or missing outcomes.")

        report = BulletImpactReport(
            bullets_scored=scored,
            average_score=average_score,
            strong_bullets_count=strong_count,
            moderate_bullets_count=moderate_count,
            weak_bullets_count=weak_count,
            weak_bullets=weak_bullets,
            guidance=guidance,
            requires_human_review=True,
            auto_rewrite=False
        )
        return overall_impact_score, report

    @classmethod
    def generate_grounded_suggestions(
        cls,
        missing_keywords: list[str],
        bullet_report: Any,
        extractions: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Generates ethical, grounded suggestions based on document evidence.
        Never fabricates candidate metrics or claims.
        """
        suggestions: list[dict[str, Any]] = []

        # Extract weak bullets whether bullet_report is BulletImpactReport or dict
        weak_bullets: list[str] = []
        if isinstance(bullet_report, dict):
            weak_bullets = bullet_report.get("weak_bullets", [])
            if not weak_bullets and "scored_bullets" in bullet_report:
                weak_bullets = [
                    b["bullet"] for b in bullet_report["scored_bullets"]
                    if not b.get("is_strong") or b.get("impact_band") == "WEAK"
                ]
        elif hasattr(bullet_report, "weak_bullets"):
            weak_bullets = bullet_report.weak_bullets

        # 1. Missing Keyword Guidance (HITL)
        if missing_keywords:
            high_priority_missing = missing_keywords[:6]
            suggestions.append({
                "category": "KEYWORD_ALIGNMENT",
                "title": "Incorporate Relevant Target Role Keywords",
                "message": (
                    f"The job description emphasizes high-signal keywords: {', '.join(high_priority_missing)}. "
                    "If you have genuine, verifiable experience with these technologies or concepts, consider "
                    "explicitly highlighting them in your project or experience descriptions. "
                    "(Do not add skills you have not used; never invent unverified experience)."
                ),
                "is_advisory": True
            })

        # 2. Bullet Quantification Guidance (HITL)
        if weak_bullets:
            sample_weak = weak_bullets[0]
            suggestions.append({
                "category": "IMPACT_QUANTIFICATION",
                "title": "Add Measurable Business or Engineering Outcomes",
                "message": (
                    f"The bullet statement: \"{sample_weak[:90]}...\" describes a routine task without a measurable outcome. "
                    "If you possess verified metrics (e.g. latency improvement, user adoption %, cost savings), "
                    "state the concrete result. Use placeholders like [X]% if metrics require checking your records. "
                    "Never invent numbers that cannot be verified."
                ),
                "is_advisory": True
            })

        # 3. Summary Check
        sections_dict = extractions.get("sections") if isinstance(extractions, dict) else None
        summary = extractions.get("summary") if isinstance(extractions, dict) else None
        if not summary or not summary.get("text"):
            suggestions.append({
                "category": "STRUCTURE",
                "title": "Add a Professional Summary",
                "message": (
                    "A concise 2-3 sentence professional summary at the top helps recruiters immediately understand "
                    "your target specialization, primary stack, and years of relevant background."
                ),
                "is_advisory": True
            })

        return suggestions

    def analyze_resume_for_ats(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        bullets: list[str],
        extractions: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Executes complete ATS keyword coverage and impact evaluation.
        Keeps ATS Keyword Coverage and Bullet Impact separate and explainable.
        """
        combined_job_text = f"{job_title}\n\n{job_description}"
        coverage_outcome = self.score_keyword_coverage(resume_text, combined_job_text)

        impact_score, bullet_report = self.score_bullet_impact(bullets)

        suggestions = self.generate_grounded_suggestions(
            coverage_outcome.missing_keywords, bullet_report, extractions
        )

        formatting_observations: list[str] = []
        words = resume_text.split()
        if len(words) > 1200:
            formatting_observations.append("Document text exceeds 1,200 words. Consider condensing to 1-2 pages.")
        if len(words) < 200:
            formatting_observations.append("Document text is brief (<200 words). Ensure all relevant experiences are detailed.")
        if extractions.get("personal_info", {}).get("email") is None:
            formatting_observations.append("Warning: No candidate email address was detected on page 1.")
        if extractions.get("personal_info", {}).get("phone") is None:
            formatting_observations.append("Notice: No telephone contact number was detected.")

        methodology = (
            "ATS keyword coverage measures exact term frequency overlap between normalized job description tokens "
            "and resume text, with first-seen tie breaking. Bullet impact analysis scores action verbs, quantitative metrics, "
            "and technical complexity. These are objective alignment metrics that do not represent proprietary black-box algorithms. "
            "High keyword coverage improves discoverability but does not guarantee interview invitations."
        )

        # Convert bullet report to serializable dict
        bullet_analysis_dict = {
            "total_bullets": len(bullet_report.bullets_scored),
            "strong_bullets_count": bullet_report.strong_bullets_count,
            "moderate_bullets_count": bullet_report.moderate_bullets_count,
            "weak_bullets_count": bullet_report.weak_bullets_count,
            "average_score": bullet_report.average_score,
            "scored_bullets": [
                {
                    "bullet": b.original_bullet,
                    "score": b.score,
                    "impact_band": b.impact_band,
                    "is_strong": b.impact_band == "STRONG",
                    "cues": b.quantifiable_evidence + b.detected_action_verbs,
                    "detected_action_verbs": b.detected_action_verbs,
                    "quantifiable_evidence": b.quantifiable_evidence,
                    "explanation": b.explanation,
                    "improvement_opportunity": b.improvement_opportunity
                }
                for b in bullet_report.bullets_scored
            ],
            "guidance": bullet_report.guidance,
            "requires_human_review": bullet_report.requires_human_review,
            "auto_rewrite": bullet_report.auto_rewrite
        }

        return {
            "coverage_score": coverage_outcome.coverage_score,
            "matched_keywords": coverage_outcome.present_keywords,
            "missing_keywords": coverage_outcome.missing_keywords,
            "total_relevant_keywords": len(coverage_outcome.jd_keywords),
            "keyword_coverage_percentage": round(coverage_outcome.coverage_score * 100, 1),
            "required_keywords": coverage_outcome.required_keywords,
            "required_matched": coverage_outcome.required_matched,
            "required_missing": coverage_outcome.required_missing,
            "preferred_keywords": coverage_outcome.preferred_keywords,
            "preferred_matched": coverage_outcome.preferred_matched,
            "preferred_missing": coverage_outcome.preferred_missing,
            "keyword_details": {
                "frequencies": coverage_outcome.keyword_frequency,
                "relevance": coverage_outcome.keyword_relevance
            },
            "keyword_rankings": coverage_outcome.ranking_and_explanation,
            "bullet_impact_score": impact_score,
            "bullet_impact_analysis": bullet_analysis_dict,
            "actionable_suggestions": suggestions,
            "formatting_observations": formatting_observations,
            "methodology_and_limitations": methodology
        }


# Singleton instance
ats_service = ATSAnalysisService()
