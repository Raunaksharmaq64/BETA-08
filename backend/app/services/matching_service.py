"""
RIGHT FIT — Evidence-Based Candidate Matching & Eligibility Engine
Phase: 7 — Job Search, Candidate Matching & Personalized Discovery

Implements:
1. Evidence-Based Skill Fit Engine (Exact/alias matches, required vs preferred, candidate review evidence)
2. Mandatory Eligibility Engine (Hard constraints evaluated independently from skill fit)
3. Transparent Multi-Dimensional Ranking
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from contracts.matching.schemas import (
    CriterionEvaluation,
    CriterionEvaluationStatus,
    EligibilityBreakdown,
    EligibilityStatus,
    MatchedSkillEvidence,
    MatchExplanationResponse,
    SkillFitBreakdown,
)
from app.services.verification_service import VerificationService


# Common skill normalization aliases
SKILL_ALIASES: Dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "postgres": "postgresql",
    "psql": "postgresql",
    "k8s": "kubernetes",
    "docker": "docker",
    "react.js": "react",
    "reactjs": "react",
    "nextjs": "next.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "node": "node.js",
    "nodejs": "node.js",
    "aws": "amazon web services",
    "gcp": "google cloud platform",
    "rest": "restful api",
    "rest api": "restful api",
    "rest apis": "restful api",
}


def normalize_skill(name: str) -> str:
    """Canonicalizes a skill name for robust matching."""
    cleaned = re.sub(r"[^\w\s\.\+#]", "", name.strip().lower())
    cleaned = re.sub(r"\s+", " ", cleaned)
    return SKILL_ALIASES.get(cleaned, cleaned)


class MatchingService:
    """Core matching and eligibility evaluation engine."""

    @classmethod
    def compute_skill_fit(
        cls,
        candidate_skills: List[Dict[str, Any]],
        job_required_skills: List[str],
        job_preferred_skills: Optional[List[str]] = None,
        resume_evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> SkillFitBreakdown:
        """
        Computes evidence-based skill fit breakdown without hallucinations.
        
        candidate_skills: list of dicts with keys:
            - skill_name (str)
            - proficiency (optional str)
            - years_experience (optional float)
            - provenance (optional str)
            - is_confirmed (optional bool, default True)
        """
        job_preferred_skills = job_preferred_skills or []
        resume_evidence = resume_evidence or []

        # Map normalized candidate skills
        candidate_map: Dict[str, Dict[str, Any]] = {}
        for s in candidate_skills:
            raw_name = s.get("skill_name", "")
            norm = normalize_skill(raw_name)
            if norm:
                candidate_map[norm] = s

        # Index resume evidence
        evidence_by_norm: Dict[str, Dict[str, Any]] = {}
        for ev in resume_evidence:
            val = ev.get("extracted_value")
            if isinstance(val, str):
                evidence_by_norm[normalize_skill(val)] = ev
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        evidence_by_norm[normalize_skill(item)] = ev

        matched_required: List[str] = []
        missing_required: List[str] = []
        matched_preferred: List[str] = []
        missing_preferred: List[str] = []
        unconfirmed_skills: List[str] = []
        evidence_list: List[MatchedSkillEvidence] = []

        # Process Required Skills
        for raw_req in job_required_skills:
            norm_req = normalize_skill(raw_req)
            if not norm_req:
                continue

            if norm_req in candidate_map:
                matched_required.append(raw_req)
                cand_info = candidate_map[norm_req]
                is_conf = cand_info.get("is_confirmed", True)
                if not is_conf:
                    unconfirmed_skills.append(raw_req)

                # Find excerpt
                excerpt = None
                ev = evidence_by_norm.get(norm_req)
                if ev:
                    excerpt = ev.get("excerpt")

                evidence_list.append(
                    MatchedSkillEvidence(
                        skill=raw_req,
                        source_type=cand_info.get("provenance", "PROFILE_SKILL"),
                        confidence=cand_info.get("confidence", 1.0),
                        evidence_excerpt=excerpt,
                        years_experience=cand_info.get("years_experience"),
                        is_confirmed=is_conf,
                    )
                )
            else:
                missing_required.append(raw_req)

        # Process Preferred Skills
        for raw_pref in job_preferred_skills:
            norm_pref = normalize_skill(raw_pref)
            if not norm_pref:
                continue

            if norm_pref in candidate_map:
                matched_preferred.append(raw_pref)
                cand_info = candidate_map[norm_pref]
                is_conf = cand_info.get("is_confirmed", True)
                if not is_conf and raw_pref not in unconfirmed_skills:
                    unconfirmed_skills.append(raw_pref)

                excerpt = None
                ev = evidence_by_norm.get(norm_pref)
                if ev:
                    excerpt = ev.get("excerpt")

                evidence_list.append(
                    MatchedSkillEvidence(
                        skill=raw_pref,
                        source_type=cand_info.get("provenance", "PROFILE_SKILL"),
                        confidence=cand_info.get("confidence", 0.9),
                        evidence_excerpt=excerpt,
                        years_experience=cand_info.get("years_experience"),
                        is_confirmed=is_conf,
                    )
                )
            else:
                missing_preferred.append(raw_pref)

        # Calculate Fit Score
        tot_req = len(job_required_skills)
        tot_pref = len(job_preferred_skills)

        if tot_req == 0 and tot_pref == 0:
            score = 100.0
        elif tot_req > 0 and tot_pref > 0:
            req_part = (len(matched_required) / tot_req) * 80.0
            pref_part = (len(matched_preferred) / tot_pref) * 20.0
            score = round(req_part + pref_part, 1)
        elif tot_req > 0:
            score = round((len(matched_required) / tot_req) * 100.0, 1)
        else:
            score = round((len(matched_preferred) / tot_pref) * 100.0, 1)

        return SkillFitBreakdown(
            fit_score=score,
            total_required_skills=tot_req,
            matched_required_count=len(matched_required),
            matched_required_skills=matched_required,
            missing_required_skills=missing_required,
            total_preferred_skills=tot_pref,
            matched_preferred_count=len(matched_preferred),
            matched_preferred_skills=matched_preferred,
            missing_preferred_skills=missing_preferred,
            unconfirmed_skills=unconfirmed_skills,
            skill_evidence=evidence_list,
        )

    @classmethod
    def evaluate_eligibility(
        cls,
        candidate_profile: Optional[Dict[str, Any]],
        opportunity: Dict[str, Any],
    ) -> EligibilityBreakdown:
        """
        Evaluates hard constraints independently from skill fit.
        When candidate information is missing, marks status as UNKNOWN (never false rejection).
        """
        criteria: List[CriterionEvaluation] = []
        has_missing_data = False

        if not candidate_profile:
            return EligibilityBreakdown(
                status=EligibilityStatus.UNKNOWN,
                summary="Candidate profile is empty or unavailable; mandatory eligibility cannot be verified.",
                criteria=[
                    CriterionEvaluation(
                        criterion_name="Profile Data Availability",
                        required_value="Completed Candidate Profile",
                        candidate_value="No Profile",
                        status=CriterionEvaluationStatus.UNKNOWN,
                        explanation="Complete your profile with education, location, and experience to evaluate mandatory eligibility.",
                    )
                ],
                has_missing_candidate_data=True,
            )

        # 1. Location / Work Mode Eligibility
        workplace_type = (opportunity.get("workplace_type") or "UNKNOWN").upper()
        is_remote = opportunity.get("is_remote", False)
        cand_country = candidate_profile.get("country")
        cand_city = candidate_profile.get("city")
        job_country = opportunity.get("country")
        job_city = opportunity.get("city")

        if is_remote or workplace_type == "REMOTE":
            criteria.append(
                CriterionEvaluation(
                    criterion_name="Remote Work Arrangement",
                    required_value="Remote",
                    candidate_value=f"{cand_city or 'Unknown'}, {cand_country or 'Unknown'}",
                    status=CriterionEvaluationStatus.SATISFIED,
                    explanation="Position is fully remote; location arrangement is satisfied.",
                )
            )
        elif workplace_type in ("ON_SITE", "HYBRID"):
            req_loc = f"{job_city or ''}, {job_country or ''}".strip(", ")
            if not cand_city and not cand_country:
                has_missing_data = True
                criteria.append(
                    CriterionEvaluation(
                        criterion_name="Geographic Location",
                        required_value=req_loc or "On-site / Hybrid location",
                        candidate_value="Location not specified in profile",
                        status=CriterionEvaluationStatus.UNKNOWN,
                        explanation="Add your city and country to profile to check commute / residency eligibility.",
                    )
                )
            else:
                same_country = (
                    cand_country and job_country and cand_country.strip().lower() == job_country.strip().lower()
                )
                if same_country or (cand_city and job_city and cand_city.strip().lower() == job_city.strip().lower()):
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Geographic Location",
                            required_value=req_loc,
                            candidate_value=f"{cand_city or ''}, {cand_country or ''}".strip(", "),
                            status=CriterionEvaluationStatus.SATISFIED,
                            explanation="Candidate location matches job location requirements.",
                        )
                    )
                else:
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Geographic Location",
                            required_value=req_loc,
                            candidate_value=f"{cand_city or ''}, {cand_country or ''}".strip(", "),
                            status=CriterionEvaluationStatus.NOT_SATISFIED,
                            explanation=f"On-site role requires presence in {req_loc}.",
                        )
                    )

        # 2. Minimum Experience Years Eligibility
        # Extract required years from title or description
        title = opportunity.get("title", "")
        desc = opportunity.get("description_clean", "")
        required_years: Optional[float] = None

        match = re.search(r"(\d+)\+?\s*years?(?:\s+of)?\s+experience", f"{title} {desc}", re.IGNORECASE)
        if match:
            required_years = float(match.group(1))
        elif "senior" in title.lower():
            required_years = 5.0
        elif "lead" in title.lower() or "principal" in title.lower():
            required_years = 7.0
        elif "mid-level" in title.lower() or "mid level" in title.lower():
            required_years = 3.0

        if required_years is not None:
            # Calculate candidate experience years
            exp_list = candidate_profile.get("experience", [])
            if not exp_list:
                has_missing_data = True
                criteria.append(
                    CriterionEvaluation(
                        criterion_name="Minimum Experience",
                        required_value=f"{int(required_years)}+ years",
                        candidate_value="No experience records in profile",
                        status=CriterionEvaluationStatus.UNKNOWN,
                        explanation="Candidate profile contains no work experience entries to verify tenure.",
                    )
                )
            else:
                # Approximate years from experience entries count or duration
                # Conservative estimate: count number of positions or years if recorded
                total_cand_years = 0.0
                for exp in exp_list:
                    # If years_experience recorded directly on skill or calculate duration
                    total_cand_years += exp.get("years_experience", 2.0)

                if total_cand_years >= required_years:
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Minimum Experience",
                            required_value=f"{int(required_years)}+ years",
                            candidate_value=f"~{int(total_cand_years)} years documented",
                            status=CriterionEvaluationStatus.SATISFIED,
                            explanation=f"Candidate meets or exceeds {int(required_years)} years of professional experience.",
                        )
                    )
                else:
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Minimum Experience",
                            required_value=f"{int(required_years)}+ years",
                            candidate_value=f"~{int(total_cand_years)} years documented",
                            status=CriterionEvaluationStatus.NOT_SATISFIED,
                            explanation=f"Job specifies {int(required_years)}+ years; candidate records indicate ~{int(total_cand_years)} years.",
                        )
                    )

        # 3. Education / Degree Requirement
        desc_lower = desc.lower()
        required_degree = None
        if "bachelor" in desc_lower or "bs in " in desc_lower or "ba in " in desc_lower:
            required_degree = "Bachelor's Degree"
        elif "master" in desc_lower or "ms in " in desc_lower:
            required_degree = "Master's Degree"
        elif "phd" in desc_lower or "doctorate" in desc_lower:
            required_degree = "PhD / Doctorate"

        if required_degree:
            edu_list = candidate_profile.get("education", [])
            if not edu_list:
                has_missing_data = True
                criteria.append(
                    CriterionEvaluation(
                        criterion_name="Education",
                        required_value=required_degree,
                        candidate_value="No education records in profile",
                        status=CriterionEvaluationStatus.UNKNOWN,
                        explanation="Add education details to your profile to confirm qualification.",
                    )
                )
            else:
                degrees_held = [e.get("degree", "").lower() for e in edu_list]
                satisfied = any(
                    "bachelor" in d or "master" in d or "phd" in d or "b." in d or "m." in d
                    for d in degrees_held
                )
                if satisfied:
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Education",
                            required_value=required_degree,
                            candidate_value=edu_list[0].get("degree", "Degree"),
                            status=CriterionEvaluationStatus.SATISFIED,
                            explanation="Candidate holds required post-secondary degree.",
                        )
                    )
                else:
                    criteria.append(
                        CriterionEvaluation(
                            criterion_name="Education",
                            required_value=required_degree,
                            candidate_value=edu_list[0].get("degree", "Other"),
                            status=CriterionEvaluationStatus.NOT_SATISFIED,
                            explanation=f"Requires {required_degree}.",
                        )
                    )

        # Synthesize Overall Status
        has_not_satisfied = any(c.status == CriterionEvaluationStatus.NOT_SATISFIED for c in criteria)
        has_unknown = any(c.status == CriterionEvaluationStatus.UNKNOWN for c in criteria)

        if has_not_satisfied:
            overall_status = EligibilityStatus.DOES_NOT_MEET_REQUIREMENTS
            summary = "Candidate does not meet one or more mandatory job criteria."
        elif has_unknown:
            overall_status = EligibilityStatus.UNKNOWN
            summary = "Certain mandatory eligibility criteria cannot be verified because relevant profile sections are incomplete."
        else:
            overall_status = EligibilityStatus.MEETS_REQUIREMENTS
            summary = "Candidate meets all documented mandatory eligibility requirements."

        return EligibilityBreakdown(
            status=overall_status,
            summary=summary,
            criteria=criteria,
            has_missing_candidate_data=has_missing_data,
        )

    @classmethod
    def calculate_ranking_score(
        cls,
        skill_fit_score: float,
        eligibility_status: EligibilityStatus,
        verification_status: str,
        freshness_state: str,
        preference_alignment_score: float = 100.0,
    ) -> float:
        """
        Calculates an explainable multi-dimensional sort score [0.0 - 100.0].
        
        Weights:
        - Skill Fit: 40%
        - Eligibility: 25% (MEETS=25, UNKNOWN=15, NEEDS_REVIEW=10, DOES_NOT_MEET=0)
        - Verification Trust: 15% (OPEN_CONFIRMED/VERIFIED=15, UNVERIFIED=8, others=0)
        - Freshness: 10% (FRESH=10, RECENT=7, STALE=2, others=0)
        - Preference Alignment: 10%
        """
        # Skill part
        skill_part = (max(0.0, min(100.0, skill_fit_score))) * 0.40

        # Eligibility part
        if eligibility_status == EligibilityStatus.MEETS_REQUIREMENTS:
            elig_part = 25.0
        elif eligibility_status == EligibilityStatus.UNKNOWN:
            elig_part = 15.0
        elif eligibility_status == EligibilityStatus.NEEDS_REVIEW:
            elig_part = 10.0
        else:
            elig_part = 0.0

        # Verification part
        verif_upper = (verification_status or "").upper()
        if verif_upper in ("OPEN_CONFIRMED", "VERIFIED"):
            verif_part = 15.0
        elif verif_upper == "UNVERIFIED":
            verif_part = 8.0
        else:
            verif_part = 0.0

        # Freshness part
        fresh_upper = (freshness_state or "").upper()
        if fresh_upper == "FRESH":
            fresh_part = 10.0
        elif fresh_upper == "RECENT":
            fresh_part = 7.0
        elif fresh_upper == "STALE":
            fresh_part = 2.0
        else:
            fresh_part = 0.0

        # Preference part
        pref_part = (max(0.0, min(100.0, preference_alignment_score))) * 0.10

        composite = skill_part + elig_part + verif_part + fresh_part + pref_part
        return round(max(0.0, min(100.0, composite)), 2)

    @classmethod
    def build_match_explanation(
        cls,
        opportunity_id: str,
        candidate_id: str,
        opportunity: Dict[str, Any],
        candidate_profile: Optional[Dict[str, Any]],
        candidate_skills: List[Dict[str, Any]],
        candidate_preferences: Optional[Dict[str, Any]] = None,
        resume_evidence: Optional[List[Dict[str, Any]]] = None,
    ) -> MatchExplanationResponse:
        """Assembles the complete transparent match explanation object."""
        job_req_skills = opportunity.get("required_skills_json") or []
        job_pref_skills = opportunity.get("preferred_skills_json") or []

        skill_fit = cls.compute_skill_fit(
            candidate_skills=candidate_skills,
            job_required_skills=job_req_skills,
            job_preferred_skills=job_pref_skills,
            resume_evidence=resume_evidence,
        )

        eligibility = cls.evaluate_eligibility(
            candidate_profile=candidate_profile,
            opportunity=opportunity,
        )

        verif_status = opportunity.get("verification_status", "UNVERIFIED")
        freshness_state = opportunity.get("freshness_state", "UNKNOWN")

        verif_expl = VerificationService.get_user_explanation(
            status=verif_status,
            freshness=freshness_state,
        )

        # Preference alignment computation
        pref_score = 100.0
        pref_match_details: Dict[str, Any] = {}
        if candidate_preferences:
            cand_rem = candidate_preferences.get("remote_preference", "ANY")
            job_rem = opportunity.get("is_remote", False)
            if cand_rem == "REMOTE" and not job_rem:
                pref_score -= 30.0
                pref_match_details["remote_alignment"] = "Job is on-site but preference is Remote"
            else:
                pref_match_details["remote_alignment"] = "Matches remote preference"

            cand_min_sal = candidate_preferences.get("min_salary")
            job_max_sal = opportunity.get("max_salary")
            if cand_min_sal and job_max_sal and job_max_sal < cand_min_sal:
                pref_score -= 20.0
                pref_match_details["salary_alignment"] = "Job max salary is below candidate minimum target"
            else:
                pref_match_details["salary_alignment"] = "Compensation is within target range"

        ranking_score = cls.calculate_ranking_score(
            skill_fit_score=skill_fit.fit_score,
            eligibility_status=eligibility.status,
            verification_status=verif_status,
            freshness_state=freshness_state,
            preference_alignment_score=pref_score,
        )

        return MatchExplanationResponse(
            opportunity_id=opportunity_id,
            candidate_id=candidate_id,
            skill_fit=skill_fit,
            eligibility=eligibility,
            verification_status=verif_status,
            verification_explanation=verif_expl,
            freshness_state=freshness_state,
            freshness_explanation=f"Freshness status is currently {freshness_state}.",
            preference_match=pref_match_details,
            ranking_score=ranking_score,
            computed_at=datetime.now(timezone.utc),
        )

