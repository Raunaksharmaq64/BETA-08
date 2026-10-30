"""
RIGHT FIT Core — ATS Keyword Coverage & Bullet Impact Analysis
Evaluates keyword overlap and quantified bullet impact without fabricating facts.
Phase: 4 — Resume Intelligence & Reviewed Candidate Evidence
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, List, Set, Tuple

_WORD_RE = re.compile(r"[a-z][a-z0-9+.#/-]{1,}", re.IGNORECASE)

_STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have",
    "in", "is", "it", "its", "of", "on", "or", "our", "that", "the", "their", "this",
    "to", "we", "with", "you", "your", "will", "can", "able", "about", "into", "over",
    "such", "than", "then", "them", "they", "was", "were", "what", "when", "who",
    "which", "while", "also", "both", "each", "more", "most", "other", "some", "team",
    "work", "role", "job", "years", "year", "experience", "including", "using", "across",
    "within", "required", "requirements", "preferred", "responsibilities", "opportunity",
    "position", "candidate", "candidates", "strong", "good", "great", "well", "must",
    "should", "may", "etc"
})

_PERCENT_RE = re.compile(r"(?<!\w)\d{1,3}(?:\.\d+)?%")
_MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmMbB]?\b")
_MULTIPLIER_RE = re.compile(r"\b\d+(?:\.\d+)?\s?x\b", re.IGNORECASE)
_SCALE_RE = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?\s*[kKmMbB]?\+?\s*"
    r"(?:users?|customers?|requests?|qps|rps|devices?|"
    r"merchants?|transactions?|seats?|employees?|engineers?|queries)\b",
    re.IGNORECASE,
)
_ACTION_VERBS: Tuple[str, ...] = (
    "led", "owned", "shipped", "launched", "reduced", "increased", "improved",
    "cut", "grew", "built", "designed", "automated", "architected", "delivered",
    "scaled", "spearheaded", "accelerated", "transformed"
)


class ATSAnalysisService:
    """Provides transparent ATS keyword coverage, bullet impact scoring, and ethical HITL guidance."""

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Extracts lowercased content tokens, removing stopwords."""
        tokens = [match.group(0).lower() for match in _WORD_RE.finditer(text or "")]
        return [token for token in tokens if token not in _STOPWORDS and len(token) > 1]

    def extract_job_keywords(self, job_text: str, top_k: int = 25) -> List[str]:
        """Extracts ranked keywords from a job description by term frequency."""
        tokens = self.tokenize(job_text)
        if not tokens:
            return []
        counts = Counter(tokens)
        seen: Dict[str, int] = {}
        for index, token in enumerate(tokens):
            if token not in seen:
                seen[token] = index
        # Sort by (-frequency, first-seen index)
        ranked = sorted(counts.keys(), key=lambda t: (-counts[t], seen[t]))
        return ranked[:top_k]

    def score_keyword_coverage(
        self,
        resume_text: str,
        job_text: str,
        top_k: int = 25
    ) -> Tuple[float, List[str], List[str]]:
        """
        Calculates fraction of high-signal JD keywords found in resume text.
        Returns: (coverage_score, matched_keywords, missing_keywords)
        """
        jd_keywords = self.extract_job_keywords(job_text, top_k=top_k)
        if not jd_keywords:
            return 0.0, [], []

        resume_tokens: Set[str] = set(self.tokenize(resume_text))
        matched = [kw for kw in jd_keywords if kw in resume_tokens]
        missing = [kw for kw in jd_keywords if kw not in resume_tokens]
        coverage = round(len(matched) / len(jd_keywords), 4)
        return coverage, matched, missing

    def score_bullet_impact(self, bullets: List[str]) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluates quantified impact cues (%, $, multipliers, scale, action verbs) in resume bullets.
        Returns: (impact_score_0_to_100, analysis_dict)
        """
        if not bullets:
            return 0.0, {
                "total_bullets": 0,
                "strong_bullets_count": 0,
                "weak_bullets_count": 0,
                "scored_bullets": []
            }

        scored_bullets: List[Dict[str, Any]] = []
        strong_count = 0

        for bullet in bullets:
            cues: List[str] = []
            score = 0.0

            # Check action verb start
            first_word = bullet.split()[0].lower() if bullet.split() else ""
            if any(first_word.startswith(verb) for verb in _ACTION_VERBS):
                cues.append("action_verb")
                score += 0.25

            # Check metrics
            if _PERCENT_RE.search(bullet):
                cues.append("percentage_metric")
                score += 0.35
            if _MONEY_RE.search(bullet):
                cues.append("financial_metric")
                score += 0.35
            if _MULTIPLIER_RE.search(bullet):
                cues.append("multiplier_metric")
                score += 0.25
            if _SCALE_RE.search(bullet):
                cues.append("scale_metric")
                score += 0.30

            score = min(1.0, round(score, 2))
            is_strong = score >= 0.50
            if is_strong:
                strong_count += 1

            scored_bullets.append({
                "bullet": bullet,
                "score": score,
                "is_strong": is_strong,
                "cues": cues
            })

        overall_impact = round((strong_count / len(bullets)) * 100, 1)

        analysis = {
            "total_bullets": len(bullets),
            "strong_bullets_count": strong_count,
            "weak_bullets_count": len(bullets) - strong_count,
            "scored_bullets": scored_bullets
        }
        return overall_impact, analysis

    def generate_grounded_suggestions(
        self,
        missing_keywords: List[str],
        bullet_analysis: Dict[str, Any],
        sections: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generates ethical, grounded suggestions.
        NEVER fabricates candidate metrics or claims.
        """
        suggestions: List[Dict[str, Any]] = []

        # 1. Missing Keyword Guidance (HITL)
        if missing_keywords:
            high_priority_missing = missing_keywords[:5]
            suggestions.append({
                "category": "KEYWORD_ALIGNMENT",
                "title": "Review Target Role Keywords",
                "message": (
                    f"The job description emphasizes keywords: {', '.join(high_priority_missing)}. "
                    "If you possess genuine experience with any of these concepts, consider referencing them "
                    "in your experience bullets or technical skills list. (Do not add skills you have not used)."
                ),
                "is_advisory": True
            })

        # 2. Bullet Quantification Guidance (HITL)
        weak_bullets = [
            b["bullet"] for b in bullet_analysis.get("scored_bullets", [])
            if not b["is_strong"]
        ]
        if weak_bullets:
            example_weak = weak_bullets[0]
            suggestions.append({
                "category": "IMPACT_QUANTIFICATION",
                "title": "Add Measurable Business Outcomes",
                "message": (
                    f"The bullet point: \"{example_weak[:90]}...\" describes a responsibility without measurable outcome. "
                    "If you have verified metrics (e.g. latency improvement, user adoption, transaction volume), "
                    "consider stating the specific result. Never invent estimated figures."
                ),
                "is_advisory": True
            })

        # 3. Section Completeness
        detected_sections = sections.get("sections", {})
        if "SUMMARY" not in detected_sections:
            suggestions.append({
                "category": "STRUCTURE",
                "title": "Add a Professional Summary",
                "message": (
                    "A concise 2-3 sentence professional summary at the top helps recruiters immediately understand "
                    "your target specialization and years of relevant background."
                ),
                "is_advisory": True
            })

        return suggestions

    def analyze_resume_for_ats(
        self,
        resume_text: str,
        job_title: str,
        job_description: str,
        bullets: List[str],
        extractions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes complete ATS keyword coverage and impact evaluation.
        """
        combined_job_text = f"{job_title}\n\n{job_description}"
        coverage_score, matched_kws, missing_kws = self.score_keyword_coverage(
            resume_text, combined_job_text
        )

        impact_score, bullet_analysis = self.score_bullet_impact(bullets)

        suggestions = self.generate_grounded_suggestions(
            missing_kws, bullet_analysis, extractions
        )

        formatting_observations: List[str] = []
        if len(resume_text.split()) > 1200:
            formatting_observations.append("Document text exceeds 1,200 words. Consider condensing to 1-2 pages.")
        if len(resume_text.split()) < 200:
            formatting_observations.append("Document text is brief (<200 words). Ensure all relevant experiences are detailed.")
        if extractions.get("personal_info", {}).get("email") is None:
            formatting_observations.append("Warning: No candidate email address was detected on page 1.")
        if extractions.get("personal_info", {}).get("phone") is None:
            formatting_observations.append("Notice: No telephone contact number was detected.")

        methodology = (
            "ATS keyword coverage measures exact term frequency overlap between normalized job description tokens "
            "and resume text. This is an objective alignment metric and does not represent proprietary ATS black-box algorithms. "
            "High keyword coverage improves search discoverability but does not guarantee interview invitations."
        )

        return {
            "coverage_score": coverage_score,
            "matched_keywords": matched_kws,
            "missing_keywords": missing_kws,
            "bullet_impact_score": impact_score,
            "bullet_impact_analysis": bullet_analysis,
            "actionable_suggestions": suggestions,
            "formatting_observations": formatting_observations,
            "methodology_and_limitations": methodology
        }


# Singleton instance
ats_service = ATSAnalysisService()

