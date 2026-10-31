"""
RIGHT FIT Core — Resume Quality & Semantic Understanding Engine
Evaluates resume completeness, readability, action verb usage,
quantifiable impact density, and formatting hygiene without black-box ATS claims.
Phase: Resume Intelligence Deep Enhancement (Phase 2)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from contracts.resume.schemas import QualityDimensionEvaluation, ResumeQualityReportResponse

# Regex cues for quantified impact migrated from source bullet_impact.py
_PERCENT_RE = re.compile(r"(?<!\w)\d{1,3}(?:\.\d+)?%")
_MONEY_RE = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?\s?[kKmMbB]?\b")
_MULTIPLIER_RE = re.compile(r"\b\d+(?:\.\d+)?\s?x\b", re.IGNORECASE)
_SCALE_RE = re.compile(
    r"\b\d[\d,]*(?:\.\d+)?\s*[kKmMbB]?\+?\s*"
    r"(?:users?|customers?|requests?|qps|rps|devices?|"
    r"merchants?|transactions?|seats?|employees?|engineers?|queries)\b",
    re.IGNORECASE,
)

_STRONG_ACTION_VERBS: frozenset[str] = frozenset({
    "led", "owned", "shipped", "launched", "reduced", "increased", "improved",
    "cut", "grew", "built", "designed", "automated", "architected", "delivered",
    "scaled", "spearheaded", "accelerated", "transformed", "engineered",
    "optimized", "deployed", "orchestrated", "mentored", "implemented", "established",
    "pioneered", "refactored", "formulated", "created", "constructed", "integrated"
})

_PASSIVE_WEAK_PHRASES: tuple[str, ...] = (
    "responsible for",
    "helped with",
    "worked on",
    "assisted in",
    "participated in",
    "handled duties",
    "duties included",
    "tasked with",
    "involved in",
)


class ResumeQualityAnalyzer:
    """
    Multi-dimensional deterministic resume quality evaluation.
    Measures 5 dimensions:
    1. Structure Completeness (25%)
    2. Quantifiable Impact Density (25%)
    3. Action Verb Usage (20%)
    4. Readability (15%)
    5. Formatting Hygiene (15%)
    """

    @classmethod
    def evaluate_bullet(cls, bullet: str) -> Dict[str, Any]:
        """Scores a single bullet for action verbs, quantified metrics, and weakness cues."""
        trimmed = bullet.strip()
        cues: List[str] = []
        score = 0.0

        # Action verb check
        first_word = trimmed.split()[0].lower() if trimmed.split() else ""
        has_action_verb = any(first_word.startswith(verb) for verb in _STRONG_ACTION_VERBS)
        if has_action_verb:
            cues.append("action_verb")
            score += 0.35

        # Passive/weak phrase penalty check
        lowered = trimmed.lower()
        has_passive = any(phrase in lowered for phrase in _PASSIVE_WEAK_PHRASES)
        if has_passive:
            cues.append("passive_phrase")

        # Metric detection
        has_metric = False
        if _PERCENT_RE.search(trimmed):
            cues.append("percentage")
            score += 0.35
            has_metric = True
        if _MONEY_RE.search(trimmed):
            cues.append("financial")
            score += 0.35
            has_metric = True
        if _MULTIPLIER_RE.search(trimmed):
            cues.append("multiplier")
            score += 0.25
            has_metric = True
        if _SCALE_RE.search(trimmed):
            cues.append("scale")
            score += 0.30
            has_metric = True

        score = min(1.0, round(score, 2))
        band = "strong" if score >= 0.50 else ("moderate" if score >= 0.25 else "weak")

        return {
            "bullet": trimmed,
            "score": score,
            "band": band,
            "cues": cues,
            "has_action_verb": has_action_verb,
            "has_metric": has_metric,
            "has_passive_phrase": has_passive,
        }

    @classmethod
    def analyze_quality(
        cls,
        resume_id: str,
        version_id: str,
        raw_text: str,
        extractions: Dict[str, Any]
    ) -> ResumeQualityReportResponse:
        """
        Calculates deterministic, explainable quality metrics across 5 dimensions.
        Includes career-stage fairness adjustments (students/entry-level credited for projects/internships).
        """
        dimension_evaluations: Dict[str, QualityDimensionEvaluation] = {}
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        critical_issues: List[str] = []
        all_priorities: List[str] = []

        personal_info = extractions.get("personal_info") or {}
        summary = extractions.get("summary")
        experience = extractions.get("experience") or []
        internships = extractions.get("internships") or []
        education = extractions.get("education") or []
        skills = extractions.get("explicit_skills") or extractions.get("skills") or {}
        projects = extractions.get("projects") or []
        certifications = extractions.get("certifications") or []

        # ==================================================================
        # 1. Structure Completeness (Weight: 25%)
        # ==================================================================
        struct_pos: List[str] = []
        struct_neg: List[str] = []
        struct_recs: List[str] = []
        struct_points = 0.0
        max_struct = 100.0

        # Contact info (25 pts)
        if personal_info.get("email") and personal_info.get("phone"):
            struct_points += 20.0
            struct_pos.append("Complete contact essentials: both email and telephone number are documented.")
        elif personal_info.get("email") or personal_info.get("phone"):
            struct_points += 10.0
            struct_neg.append("Partial contact information provided (missing either phone or email).")
            struct_recs.append("Ensure both your email address and primary contact phone number are clearly visible.")
        else:
            critical_issues.append("Missing primary contact details (neither email nor phone detected).")
            struct_neg.append("No primary contact details found.")

        if personal_info.get("linkedin_url") or personal_info.get("github_url"):
            struct_points += 5.0
            struct_pos.append("Professional profile link (LinkedIn or GitHub) included for identity verification.")

        # Summary statement (15 pts)
        if summary and summary.get("text") and len(summary.get("text", "").strip()) >= 40:
            struct_points += 15.0
            struct_pos.append("Professional headline summary clearly articulates candidate domain focus.")
        else:
            struct_neg.append("Resume lacks a concise professional summary header.")
            struct_recs.append("Add a 2–3 sentence executive summary highlighting your domain specialty and career scope.")

        # Experience & Career Stage Fairness (30 pts)
        # If corporate experience is absent, credit projects or internships fairly
        if experience:
            struct_points += 30.0
            struct_pos.append(f"Work experience section documents {len(experience)} distinct professional role(s).")
        elif internships:
            struct_points += 25.0
            struct_pos.append(f"Internship section documents {len(internships)} practical placement(s) (career-stage adjusted).")
        elif projects:
            struct_points += 20.0
            struct_pos.append(f"Technical projects section documents {len(projects)} system(s) (entry-level stage adjusted).")
        else:
            critical_issues.append("No work experience, internships, or technical projects detected.")
            struct_neg.append("Document lacks any record of practical employment, internships, or engineering projects.")
            struct_recs.append("Add detailed work experience, internships, or academic/personal technical projects.")

        # Education (15 pts)
        if education:
            struct_points += 15.0
            struct_pos.append(f"Education section identifies {len(education)} academic degree(s) / credential(s).")
        else:
            struct_neg.append("No academic degrees or university credentials detected.")
            struct_recs.append("Include degree, institution name, and graduation year in an Education section.")

        # Skills section (15 pts)
        total_skills_count = sum(len(v) for v in skills.values()) if isinstance(skills, dict) else len(skills)
        if total_skills_count >= 6:
            struct_points += 15.0
            struct_pos.append(f"Dedicated skills section categorizes {total_skills_count} explicit technologies.")
        elif total_skills_count >= 2:
            struct_points += 8.0
            struct_neg.append("Skills section contains few explicit keywords.")
        else:
            struct_neg.append("Missing dedicated technical skills section.")
            struct_recs.append("Add a structured Skills section grouped into Languages, Frameworks, Databases, and Tools.")

        structure_score = min(100.0, round(struct_points, 1))
        dimension_evaluations["structure_completeness"] = QualityDimensionEvaluation(
            dimension_name="Structure Completeness",
            score=structure_score,
            positive_observations=struct_pos,
            negative_observations=struct_neg,
            actionable_recommendations=struct_recs
        )

        # ==================================================================
        # Collect All Accomplishment Bullets
        # ==================================================================
        all_bullets: List[str] = []
        for exp in experience:
            all_bullets.extend(exp.get("responsibilities", []))
        for intern in internships:
            if isinstance(intern, dict) and intern.get("responsibilities"):
                all_bullets.append(intern["responsibilities"])
        for proj in projects:
            if proj.get("description"):
                all_bullets.append(proj["description"])

        scored_bullets = [cls.evaluate_bullet(b) for b in all_bullets if b.strip()]

        # ==================================================================
        # 2. Quantifiable Impact Density (Weight: 25%)
        # ==================================================================
        impact_pos: List[str] = []
        impact_neg: List[str] = []
        impact_recs: List[str] = []

        if scored_bullets:
            metric_bullets = [b for b in scored_bullets if b["has_metric"]]
            metric_ratio = len(metric_bullets) / len(scored_bullets)

            # Score scales from 40 (purely qualitative) to 100 (50%+ bullets quantified)
            impact_score = min(100.0, round(40.0 + (metric_ratio * 120.0), 1))

            if metric_ratio >= 0.40:
                impact_pos.append(f"High metric density: {len(metric_bullets)} of {len(scored_bullets)} bullets highlight measurable outcomes (%, $, scale, or speed).")
            elif metric_ratio > 0:
                impact_pos.append(f"{len(metric_bullets)} accomplishment bullet(s) contain concrete quantitative proof.")
                impact_neg.append(f"Low metric density: {len(scored_bullets) - len(metric_bullets)} bullets are qualitative task descriptions lacking quantified results.")
                impact_recs.append("Quantify accomplishments with concrete figures: throughput improvement %, cost saved, scale handled, or latency reduced.")
            else:
                impact_neg.append("Zero bullets contain quantifiable numbers (%, $, latency, or scale figures).")
                impact_recs.append("Incorporate measurable results into responsibility statements (e.g. 'reduced latency by 35%', 'scaled to 10k users').")
        else:
            impact_score = 50.0  # Fair baseline if minimal bullets present
            impact_neg.append("Insufficient bullet points found to evaluate quantifiable metrics.")
            impact_recs.append("Add structured bullet points under each experience and project entry.")

        dimension_evaluations["quantifiable_impact_density"] = QualityDimensionEvaluation(
            dimension_name="Quantifiable Impact Density",
            score=impact_score,
            positive_observations=impact_pos,
            negative_observations=impact_neg,
            actionable_recommendations=impact_recs
        )

        # ==================================================================
        # 3. Action Verb Usage (Weight: 20%)
        # ==================================================================
        action_pos: List[str] = []
        action_neg: List[str] = []
        action_recs: List[str] = []

        if scored_bullets:
            action_bullets = [b for b in scored_bullets if b["has_action_verb"]]
            passive_bullets = [b for b in scored_bullets if b["has_passive_phrase"]]
            action_ratio = len(action_bullets) / len(scored_bullets)

            # Base score from strong verb ratio, penalize for passive phrases
            action_score = min(100.0, round(action_ratio * 100.0, 1))
            if passive_bullets:
                action_score = max(20.0, round(action_score - (len(passive_bullets) * 8.0), 1))

            if action_ratio >= 0.65:
                action_pos.append(f"Strong verb leadership: {len(action_bullets)} of {len(scored_bullets)} bullets open with dynamic, decisive action verbs.")
            else:
                action_neg.append(f"Only {len(action_bullets)} of {len(scored_bullets)} bullets begin with recognized strong action verbs.")
                action_recs.append("Begin every bullet point with a decisive power verb (e.g. 'Architected', 'Spearheaded', 'Optimized', 'Automated').")

            if passive_bullets:
                action_neg.append(f"Detected {len(passive_bullets)} passive/weak opening phrases ('responsible for', 'helped with', 'worked on').")
                action_recs.append("Eliminate passive openers like 'responsible for' and directly state your leadership contribution.")
        else:
            action_score = 60.0
            action_neg.append("No bullet points available to assess action verb density.")
            action_recs.append("Format roles using bulleted accomplishment statements rather than prose paragraphs.")

        dimension_evaluations["action_verb_usage"] = QualityDimensionEvaluation(
            dimension_name="Action Verb Usage",
            score=action_score,
            positive_observations=action_pos,
            negative_observations=action_neg,
            actionable_recommendations=action_recs
        )

        # ==================================================================
        # 4. Readability & Scannability (Weight: 15%)
        # ==================================================================
        read_pos: List[str] = []
        read_neg: List[str] = []
        read_recs: List[str] = []
        read_points = 100.0

        if scored_bullets:
            bullet_lengths = [len(b["bullet"].split()) for b in scored_bullets]
            avg_words = sum(bullet_lengths) / len(bullet_lengths)
            run_on_count = sum(1 for length in bullet_lengths if length > 40)
            sparse_count = sum(1 for length in bullet_lengths if length < 6)

            if 10 <= avg_words <= 26:
                read_pos.append(f"Optimal bullet length: Average of {round(avg_words, 1)} words per statement enables rapid recruiter scanning.")
            elif avg_words > 26:
                read_points -= 20.0
                read_neg.append(f"Bullets are overly verbose (average {round(avg_words, 1)} words). Long text blocks decrease scannability.")
                read_recs.append("Tighten bullet statements to between 12 and 24 words for optimal visual scanning.")
            else:
                read_points -= 15.0
                read_neg.append(f"Bullets are terse (average {round(avg_words, 1)} words) and may lack adequate technical context.")

            if run_on_count > 0:
                read_points -= min(25.0, run_on_count * 8.0)
                read_neg.append(f"Found {run_on_count} dense, run-on bullet(s) exceeding 40 words.")
                read_recs.append("Split lengthy compound bullets into 2 separate focused accomplishment points.")
            else:
                read_pos.append("Zero run-on bullets exceeding 40 words detected.")
        else:
            read_points = 65.0
            read_neg.append("Limited structured text available to evaluate scannability.")

        readability_score = max(0.0, min(100.0, round(read_points, 1)))
        dimension_evaluations["readability"] = QualityDimensionEvaluation(
            dimension_name="Readability & Scannability",
            score=readability_score,
            positive_observations=read_pos,
            negative_observations=read_neg,
            actionable_recommendations=read_recs
        )

        # ==================================================================
        # 5. Formatting Hygiene & Length (Weight: 15%)
        # ==================================================================
        form_pos: List[str] = []
        form_neg: List[str] = []
        form_recs: List[str] = []
        form_points = 100.0

        words = raw_text.split()
        word_count = len(words)

        if 350 <= word_count <= 950:
            form_pos.append(f"Ideal document density ({word_count} words), conforming to the standard 1–2 page hiring guideline.")
        elif word_count > 1200:
            form_points -= 30.0
            form_neg.append(f"Document is lengthy ({word_count} words). Recruiters spend only 6–10 seconds on initial triage.")
            form_recs.append("Prune older roles and condense bullet descriptions to keep document length under 900 words.")
        elif word_count < 220:
            form_points -= 35.0
            critical_issues.append(f"Document text is sparse ({word_count} words). Expand on technologies and key project milestones.")
            form_neg.append(f"Document text is very short ({word_count} words).")
            form_recs.append("Expand descriptions of key technical projects, architectural trade-offs, and responsibilities.")
        else:
            # 220-350 or 950-1200
            form_points -= 10.0
            form_pos.append(f"Acceptable document length ({word_count} words).")

        # Punctuation consistency check
        if scored_bullets:
            period_endings = sum(1 for b in scored_bullets if b["bullet"].endswith("."))
            period_ratio = period_endings / len(scored_bullets)
            if 0.15 < period_ratio < 0.85:
                form_points -= 10.0
                form_neg.append("Inconsistent bullet punctuation: some statements end with periods while others do not.")
                form_recs.append("Standardize punctuation: either terminate every bullet point with a period or omit periods consistently.")
            else:
                form_pos.append("Consistent punctuation across bullet statements.")

        formatting_score = max(0.0, min(100.0, round(form_points, 1)))
        dimension_evaluations["formatting_hygiene"] = QualityDimensionEvaluation(
            dimension_name="Formatting Hygiene & Length",
            score=formatting_score,
            positive_observations=form_pos,
            negative_observations=form_neg,
            actionable_recommendations=form_recs
        )

        # ==================================================================
        # Overall Weighted Resume Quality Index
        # Weights: Structure (25%), Impact (25%), Action Verbs (20%), Readability (15%), Formatting (15%)
        # ==================================================================
        overall = round(
            (structure_score * 0.25) +
            (impact_score * 0.25) +
            (action_score * 0.20) +
            (readability_score * 0.15) +
            (formatting_score * 0.15),
            1
        )

        quality_band = "STRONG" if overall >= 80.0 else ("MODERATE" if overall >= 60.0 else "NEEDS_IMPROVEMENT")

        # Compile consolidated strengths, weaknesses, and priorities
        for de in dimension_evaluations.values():
            all_strengths.extend(de.positive_observations)
            all_weaknesses.extend(de.negative_observations)
            all_priorities.extend(de.actionable_recommendations)

        methodology = (
            "Deterministic 5-dimensional evaluation: Structure Completeness (25%), Quantified Impact Density (25%), "
            "Action Verb Usage (20%), Readability & Scannability (15%), and Formatting Hygiene (15%). "
            "Includes career-stage fairness normalization. Does not rely on black-box or non-deterministic AI generation."
        )

        # Section scores with backward-compatible aliases
        section_scores = {
            "structure_completeness": structure_score,
            "quantifiable_impact_density": impact_score,
            "action_verb_usage": action_score,
            "readability": readability_score,
            "formatting_hygiene": formatting_score,
            # Backward compatibility aliases
            "structure": structure_score,
            "impact_quantification": impact_score,
            "skills_depth": structure_score,
            "formatting_and_length": formatting_score,
        }

        return ResumeQualityReportResponse(
            resume_id=resume_id,
            version_id=version_id,
            overall_quality_score=overall,
            quality_band=quality_band,
            section_scores=section_scores,
            dimension_evaluations=dimension_evaluations,
            strengths=all_strengths,
            weaknesses=all_weaknesses,
            critical_issues=critical_issues,
            improvement_priorities=all_priorities[:5],
            methodology=methodology
        )


# Singleton
resume_quality_analyzer = ResumeQualityAnalyzer()
