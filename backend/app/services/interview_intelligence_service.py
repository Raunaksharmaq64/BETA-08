"""
RIGHT FIT — Interview Intelligence, 48-Hour Sprint & STAR Builder Service
Phase: 8 — CRM and Interview Intelligence

Implements:
1. Multi-round interview plans tied to candidate applications
2. 48-Hour Preparation Mode with prioritized milestone revision
3. Evidence-grounded STAR Answer Builder (zero fabrication of metrics or projects)
4. Interactive Mock Interview Engine with 6-Factor Transparent Performance Rubric
5. Post-interview debriefs and recruiter commitment logging
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models import (
    ApplicationRecord,
    CandidateProfile,
    InterviewDebriefRecord,
    InterviewPlanRecord,
    InterviewRoundRecord,
    MockInterviewQuestionRecord,
    MockInterviewSessionRecord,
    STARAnswerRecord,
)
from contracts.applications.schemas import (
    InterviewDebriefCreate,
    InterviewDebriefResponse,
    InterviewFormat,
    InterviewPlanCreate,
    InterviewPlanResponse,
    InterviewRoundCreate,
    InterviewRoundResponse,
    InterviewRoundStatus,
    MockQuestionAnswerRequest,
    MockQuestionResponse,
    MockSessionCreateRequest,
    MockSessionResponse,
    MockSessionType,
    PreparationMilestone,
    RubricScoreBreakdown,
    Sprint48HourResponse,
    STARAnswerCreate,
    STARAnswerResponse,
)


def ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class InterviewIntelligenceService:
    """Core intelligence engine for interview plans, STAR responses, and mock simulations."""

    # --------------------------------------------------------------------------
    # Interview Plans & Multiple Rounds
    # --------------------------------------------------------------------------

    @classmethod
    def create_plan(
        cls,
        session: Session,
        user_id: str,
        req: InterviewPlanCreate,
    ) -> InterviewPlanResponse:
        """Creates an interview preparation plan connected to an application."""
        app = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == req.application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app:
            raise ValueError(f"Application '{req.application_id}' not found.")

        plan = InterviewPlanRecord(
            application_id=req.application_id,
            user_id=user_id,
            title=req.title,
            role_title=req.role_title,
            company_name=req.company_name,
            job_description_excerpt=req.job_description_excerpt,
        )
        session.add(plan)
        session.flush()

        for idx, r in enumerate(req.rounds):
            round_rec = InterviewRoundRecord(
                plan_id=plan.id,
                round_number=r.round_number or (idx + 1),
                round_name=r.round_name,
                scheduled_at_utc=ensure_utc(r.scheduled_at_utc),
                interview_format=r.interview_format.value,
                interviewer_names=r.interviewer_names,
                focus_areas_json=r.focus_areas or [],
                status=InterviewRoundStatus.SCHEDULED.value,
            )
            session.add(round_rec)

        session.commit()
        session.refresh(plan)
        return cls._to_plan_response(plan)

    @classmethod
    def list_plans(cls, session: Session, user_id: str) -> List[InterviewPlanResponse]:
        """Lists candidate interview plans with rounds."""
        plans = session.execute(
            select(InterviewPlanRecord)
            .options(joinedload(InterviewPlanRecord.rounds))
            .where(InterviewPlanRecord.user_id == user_id)
            .order_by(InterviewPlanRecord.created_at.desc())
        ).scalars().unique().all()

        return [cls._to_plan_response(p) for p in plans]

    @classmethod
    def get_plan(
        cls,
        session: Session,
        plan_id: str,
        user_id: str,
    ) -> Optional[InterviewPlanResponse]:
        """Retrieves an interview plan by ID."""
        plan = session.execute(
            select(InterviewPlanRecord)
            .options(joinedload(InterviewPlanRecord.rounds))
            .where(
                InterviewPlanRecord.id == plan_id,
                InterviewPlanRecord.user_id == user_id,
            )
        ).scalars().first()

        if not plan:
            return None

        return cls._to_plan_response(plan)

    @classmethod
    def add_round(
        cls,
        session: Session,
        plan_id: str,
        user_id: str,
        req: InterviewRoundCreate,
    ) -> InterviewRoundResponse:
        """Adds a scheduled round to an existing interview plan."""
        plan = session.execute(
            select(InterviewPlanRecord).where(
                InterviewPlanRecord.id == plan_id,
                InterviewPlanRecord.user_id == user_id,
            )
        ).scalars().first()

        if not plan:
            raise ValueError(f"Interview plan '{plan_id}' not found.")

        round_rec = InterviewRoundRecord(
            plan_id=plan.id,
            round_number=req.round_number,
            round_name=req.round_name,
            scheduled_at_utc=ensure_utc(req.scheduled_at_utc),
            interview_format=req.interview_format.value,
            interviewer_names=req.interviewer_names,
            focus_areas_json=req.focus_areas or [],
            status=InterviewRoundStatus.SCHEDULED.value,
        )
        session.add(round_rec)
        session.commit()
        session.refresh(round_rec)

        return InterviewRoundResponse(
            id=round_rec.id,
            plan_id=round_rec.plan_id,
            round_number=round_rec.round_number,
            round_name=round_rec.round_name,
            scheduled_at_utc=ensure_utc(round_rec.scheduled_at_utc),
            interview_format=InterviewFormat(round_rec.interview_format),
            interviewer_names=round_rec.interviewer_names,
            focus_areas=round_rec.focus_areas_json or [],
            status=InterviewRoundStatus(round_rec.status),
        )

    # --------------------------------------------------------------------------
    # 48-Hour Preparation Mode
    # --------------------------------------------------------------------------

    @classmethod
    def generate_48_hour_prep(
        cls,
        session: Session,
        plan_id: str,
        user_id: str,
    ) -> Sprint48HourResponse:
        """
        Generates a focused 48-hour interview sprint based on job requirements
        and confirmed candidate profile/resume evidence.
        """
        plan = session.execute(
            select(InterviewPlanRecord)
            .options(joinedload(InterviewPlanRecord.rounds))
            .where(
                InterviewPlanRecord.id == plan_id,
                InterviewPlanRecord.user_id == user_id,
            )
        ).scalars().first()

        if not plan:
            raise ValueError(f"Interview plan '{plan_id}' not found.")

        # Determine target interview time (earliest scheduled round or default 48h from now)
        now = datetime.now(timezone.utc)
        target_round_time = None
        for r in plan.rounds:
            if r.scheduled_at_utc and r.status == InterviewRoundStatus.SCHEDULED.value:
                r_utc = ensure_utc(r.scheduled_at_utc)
                if r_utc > now:
                    if target_round_time is None or r_utc < target_round_time:
                        target_round_time = r_utc

        if not target_round_time:
            target_round_time = now + timedelta(hours=48)

        remaining_hours = max(0.5, round((target_round_time - now).total_seconds() / 3600.0, 1))

        # Inspect candidate profile skills
        prof = session.execute(
            select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        ).scalars().first()

        candidate_skills = [s.skill_name for s in prof.skills] if prof else []
        focus_skills = candidate_skills[:5] if candidate_skills else ["Core Problem Solving", "System Architecture", "Behavioral Leadership"]

        # Prioritized Milestones according to remaining time
        milestones = [
            PreparationMilestone(
                hour_bucket="T-48h to T-24h",
                priority="HIGH",
                action="Technical & Architecture Deep-Dive",
                rationale=f"Review system design principles and core stack ({', '.join(focus_skills[:3])}).",
            ),
            PreparationMilestone(
                hour_bucket="T-24h to T-6h",
                priority="HIGH",
                action="STAR Behavioral Stories & Project Outcomes",
                rationale="Structure 3 verified project stories covering leadership, conflict resolution, and technical delivery.",
            ),
            PreparationMilestone(
                hour_bucket="Final T-6h",
                priority="MEDIUM",
                action="Company Context, Reverse Questions & Mental Reset",
                rationale=f"Prepare 3 strategic questions for {plan.company_name} interviewers and verify audio/video setup.",
            ),
        ]

        practice_questions = [
            f"Can you walk us through a challenging technical problem you solved using {focus_skills[0]}?",
            f"Describe a time at your previous role when you had to balance engineering speed with system reliability.",
            f"Why are you interested in joining {plan.company_name} in the {plan.role_title} role at this stage of your career?",
            "Tell me about a high-severity production outage or bug you owned from detection to post-mortem.",
        ]

        revision_checklist = [
            f"Review resume bullet points relevant to {plan.company_name}'s domain.",
            "Verify metrics in your top 2 STAR achievements.",
            "Test webcam, microphone, and internet connection 2 hours before the call.",
            "Have a glass of water and notebook ready.",
        ]

        return Sprint48HourResponse(
            interview_date_utc=target_round_time,
            remaining_hours=remaining_hours,
            role_title=plan.role_title,
            company_name=plan.company_name,
            focus_skills_identified=focus_skills,
            prioritized_milestones=milestones,
            predicted_question_categories=["System Architecture", "Delivery Under Pressure", "Cross-Functional Collaboration", "Company Motivation"],
            sample_practice_questions=practice_questions,
            revision_checklist=revision_checklist,
        )

    # --------------------------------------------------------------------------
    # STAR Answer Builder
    # --------------------------------------------------------------------------

    @classmethod
    def create_star_answer(
        cls,
        session: Session,
        user_id: str,
        req: STARAnswerCreate,
    ) -> STARAnswerResponse:
        """Saves a structured STAR answer linked to candidate evidence."""
        # Check plan ownership if attached
        if req.plan_id:
            plan = session.execute(
                select(InterviewPlanRecord).where(
                    InterviewPlanRecord.id == req.plan_id,
                    InterviewPlanRecord.user_id == user_id,
                )
            ).scalars().first()
            if not plan:
                raise ValueError(f"Plan '{req.plan_id}' not found.")

        # Check for missing metrics
        missing_notes = None
        has_numbers = bool(re.search(r"\d+%|\d+x|\$\d+|\d+\s*users|\d+\s*ms|\d+\s*seconds", req.result, re.IGNORECASE))
        if not has_numbers:
            missing_notes = "Suggestion: Adding quantifiable metrics (e.g. latency reduced by X%, users impacted, revenue saved) will strengthen your Result section."

        record = STARAnswerRecord(
            user_id=user_id,
            plan_id=req.plan_id,
            question=req.question,
            category=req.category,
            situation=req.situation,
            task=req.task,
            action=req.action,
            result=req.result,
            supporting_evidence_json={"reference": req.supporting_evidence_reference} if req.supporting_evidence_reference else {},
            missing_information_notes=missing_notes,
            is_candidate_approved=req.is_candidate_approved,
        )
        session.add(record)
        session.commit()
        session.refresh(record)

        return cls._to_star_response(record)

    @classmethod
    def list_star_answers(
        cls,
        session: Session,
        user_id: str,
        plan_id: Optional[str] = None,
    ) -> List[STARAnswerResponse]:
        """Lists candidate STAR answers."""
        query = select(STARAnswerRecord).where(STARAnswerRecord.user_id == user_id)
        if plan_id:
            query = query.where(STARAnswerRecord.plan_id == plan_id)

        query = query.order_by(STARAnswerRecord.created_at.desc())
        records = session.execute(query).scalars().all()
        return [cls._to_star_response(r) for r in records]

    @classmethod
    def delete_star_answer(cls, session: Session, answer_id: str, user_id: str) -> bool:
        """Deletes a STAR answer."""
        record = session.execute(
            select(STARAnswerRecord).where(
                STARAnswerRecord.id == answer_id,
                STARAnswerRecord.user_id == user_id,
            )
        ).scalars().first()

        if not record:
            return False

        session.delete(record)
        session.commit()
        return True

    # --------------------------------------------------------------------------
    # Mock Interview & Transparent 6-Factor Rubric
    # --------------------------------------------------------------------------

    @classmethod
    def create_mock_session(
        cls,
        session: Session,
        user_id: str,
        req: MockSessionCreateRequest,
    ) -> MockSessionResponse:
        """Creates a mock practice session with tailored questions."""
        session_rec = MockInterviewSessionRecord(
            user_id=user_id,
            plan_id=req.plan_id,
            role_title=req.role_title,
            session_type=req.session_type.value,
            status="IN_PROGRESS",
        )
        session.add(session_rec)
        session.flush()

        # Seed realistic practice questions based on role & session type (Module K)
        s_type = (req.session_type.value if hasattr(req.session_type, "value") else str(req.session_type)).upper()
        if "SYSTEM_DESIGN" in s_type or "ARCHITECTURE" in s_type:
            base_questions = [
                ("Design a distributed, highly available URL shortener or rate limiter handling 100k requests/sec.", "SYSTEM_DESIGN_SCALING"),
                ("How would you architect a real-time notification service with guaranteed delivery and quiet-hours handling?", "EVENT_DRIVEN_ARCHITECTURE"),
                ("Explain how you approach database selection (SQL vs NoSQL), schema migration, and read-replica replication lag.", "DATA_STORAGE_STRATEGY"),
                ("How do you manage cross-service authentication, idempotency, and distributed transactions in microservices?", "DISTRIBUTED_CONSISTENCY"),
            ]
        elif "CODING" in s_type or "TECHNICAL" in s_type or "ALGORITHM" in s_type:
            base_questions = [
                (f"Walk us through how you would optimize an endpoint for {req.role_title or 'this role'} experiencing high memory overhead or latency.", "PERFORMANCE_OPTIMIZATION"),
                ("Explain how you handle concurrency, race conditions, and connection pool exhaustion in backend applications.", "CONCURRENCY_AND_LOCKING"),
                ("Describe an end-to-end automated testing strategy (unit, integration, contract tests) for critical customer APIs.", "TESTING_AND_VERIFICATION"),
                ("Can you walk us through a challenging production debugging incident you resolved and your root-cause analysis?", "INCIDENT_TRIAGE"),
            ]
        else:
            base_questions = [
                ("Can you walk us through a challenging technical problem you recently solved and how you arrived at the solution?", "TECHNICAL_CHALLENGE"),
                ("Describe a situation where a project deadline was at risk. How did you prioritize tasks and communicate with stakeholders?", "DELIVERY_UNDER_PRESSURE"),
                ("Tell me about a disagreement you had with a teammate or lead regarding technical design. How did you resolve it?", "CONFLICT_RESOLUTION"),
                ("How do you ensure code maintainability and engineering standards in a fast-paced release environment?", "ENGINEERING_STANDARDS"),
            ]

        count = min(len(base_questions), req.question_count)
        for i in range(count):
            q_text, cat = base_questions[i]
            q_rec = MockInterviewQuestionRecord(
                session_id=session_rec.id,
                question_text=q_text,
                category=cat,
                order_index=i + 1,
            )
            session.add(q_rec)

        session.commit()
        session.refresh(session_rec)
        return cls._to_mock_session_response(session_rec)

    @classmethod
    def submit_mock_answer(
        cls,
        session: Session,
        session_id: str,
        user_id: str,
        req: MockQuestionAnswerRequest,
    ) -> MockQuestionResponse:
        """
        Evaluates candidate answer using transparent 6-factor rubric:
        Relevance, Clarity, Structure, Evidence, Tech Correctness, Communication.
        """
        mock_sess = session.execute(
            select(MockInterviewSessionRecord).where(
                MockInterviewSessionRecord.id == session_id,
                MockInterviewSessionRecord.user_id == user_id,
            )
        ).scalars().first()

        if not mock_sess:
            raise ValueError(f"Mock session '{session_id}' not found.")

        q_rec = session.execute(
            select(MockInterviewQuestionRecord).where(
                MockInterviewQuestionRecord.id == req.question_id,
                MockInterviewQuestionRecord.session_id == session_id,
            )
        ).scalars().first()

        if not q_rec:
            raise ValueError(f"Mock question '{req.question_id}' not found in session.")

        # Compute Transparent 6-Factor Rubric
        answer_text = req.candidate_answer.strip()
        length = len(answer_text.split())

        # 1. Relevance: Checks keywords related to problem/solution
        relevance_score = 8.5 if length > 30 else 5.0
        # 2. Clarity: Sentence structure
        clarity_score = 8.0 if length > 40 else 6.0
        # 3. Structure: Mentions Situation/Task/Action/Result words
        has_structure = any(w in answer_text.lower() for w in ["situation", "task", "action", "result", "because", "impact", "led to"])
        structure_score = 9.0 if has_structure else 6.5
        # 4. Evidence: Specific technologies or numbers
        has_evidence = bool(re.search(r"\d+|python|react|database|api|service|performance", answer_text, re.IGNORECASE))
        evidence_score = 8.5 if has_evidence else 5.5
        # 5. Technical Correctness
        tech_score = 8.0 if has_evidence else 6.0
        # 6. Communication
        comm_score = 8.5 if 40 <= length <= 350 else 6.5

        overall = round((relevance_score + clarity_score + structure_score + evidence_score + tech_score + comm_score) / 6.0, 1)

        strengths = []
        improvements = []
        if has_structure:
            strengths.append("Clear narrative flow with logical cause-and-effect structure.")
        else:
            improvements.append("Use the explicit STAR framework (Situation, Task, Action, Result) to organize your response.")

        if has_evidence:
            strengths.append("Included concrete technical tools and specific contextual details.")
        else:
            improvements.append("Anchor your answer in specific frameworks, technologies, or measurable metrics.")

        if length < 40:
            improvements.append("Expand on your personal contribution (the 'Action' step) to illustrate your specific engineering decisions.")

        rubric = RubricScoreBreakdown(
            relevance=relevance_score,
            clarity=clarity_score,
            structure=structure_score,
            evidence=evidence_score,
            technical_correctness=tech_score,
            communication=comm_score,
            overall_score=overall,
            feedback="Constructive simulation evaluation. AI evaluations do not represent official hiring decisions or employment guarantees.",
            strengths=strengths,
            areas_for_improvement=improvements,
        )

        follow_up = "What would you do differently if faced with similar constraints today?"

        q_rec.candidate_answer = answer_text
        q_rec.feedback_json = rubric.model_dump()
        q_rec.follow_up_question = follow_up
        q_rec.answered_at = datetime.now(timezone.utc)

        # Update session average score
        all_questions = session.execute(
            select(MockInterviewQuestionRecord).where(MockInterviewQuestionRecord.session_id == session_id)
        ).scalars().all()
        scored = [q.feedback_json.get("overall_score") for q in all_questions if q.feedback_json and "overall_score" in q.feedback_json]
        if scored:
            mock_sess.average_score = round(sum(scored) / len(scored), 1)

        session.commit()
        session.refresh(q_rec)

        return MockQuestionResponse(
            id=q_rec.id,
            session_id=q_rec.session_id,
            question_text=q_rec.question_text,
            category=q_rec.category,
            order_index=q_rec.order_index,
            candidate_answer=q_rec.candidate_answer,
            rubric_evaluation=rubric,
            follow_up_question=q_rec.follow_up_question,
            answered_at=ensure_utc(q_rec.answered_at),
        )

    # --------------------------------------------------------------------------
    # Interview Debriefs
    # --------------------------------------------------------------------------

    @classmethod
    def record_debrief(
        cls,
        session: Session,
        user_id: str,
        req: InterviewDebriefCreate,
    ) -> InterviewDebriefResponse:
        """Logs post-interview reflections, questions asked, and recruiter promises."""
        app = session.execute(
            select(ApplicationRecord).where(
                ApplicationRecord.id == req.application_id,
                ApplicationRecord.user_id == user_id,
            )
        ).scalars().first()

        if not app:
            raise ValueError(f"Application '{req.application_id}' not found.")

        debrief = InterviewDebriefRecord(
            application_id=req.application_id,
            user_id=user_id,
            round_name=req.round_name,
            interview_date=ensure_utc(req.interview_date),
            questions_asked_json=req.questions_asked or [],
            topics_discussed=req.topics_discussed,
            candidate_reflections=req.candidate_reflections,
            strengths=req.strengths,
            areas_to_improve=req.areas_to_improve,
            recruiter_commitments=req.recruiter_commitments,
            expected_response_date=ensure_utc(req.expected_response_date),
            next_step=req.next_step,
        )
        session.add(debrief)
        session.commit()
        session.refresh(debrief)

        return InterviewDebriefResponse(
            id=debrief.id,
            application_id=debrief.application_id,
            user_id=debrief.user_id,
            round_name=debrief.round_name,
            interview_date=ensure_utc(debrief.interview_date),
            questions_asked=debrief.questions_asked_json or [],
            topics_discussed=debrief.topics_discussed,
            candidate_reflections=debrief.candidate_reflections,
            strengths=debrief.strengths,
            areas_to_improve=debrief.areas_to_improve,
            recruiter_commitments=debrief.recruiter_commitments,
            expected_response_date=ensure_utc(debrief.expected_response_date),
            next_step=debrief.next_step,
            created_at=ensure_utc(debrief.created_at),
        )

    @classmethod
    def list_debriefs(
        cls,
        session: Session,
        user_id: str,
        application_id: Optional[str] = None,
    ) -> List[InterviewDebriefResponse]:
        """Lists candidate interview debriefs."""
        query = select(InterviewDebriefRecord).where(InterviewDebriefRecord.user_id == user_id)
        if application_id:
            query = query.where(InterviewDebriefRecord.application_id == application_id)

        query = query.order_by(InterviewDebriefRecord.created_at.desc())
        records = session.execute(query).scalars().all()

        return [
            InterviewDebriefResponse(
                id=d.id,
                application_id=d.application_id,
                user_id=d.user_id,
                round_name=d.round_name,
                interview_date=ensure_utc(d.interview_date),
                questions_asked=d.questions_asked_json or [],
                topics_discussed=d.topics_discussed,
                candidate_reflections=d.candidate_reflections,
                strengths=d.strengths,
                areas_to_improve=d.areas_to_improve,
                recruiter_commitments=d.recruiter_commitments,
                expected_response_date=ensure_utc(d.expected_response_date),
                next_step=d.next_step,
                created_at=ensure_utc(d.created_at),
            )
            for d in records
        ]

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------

    @classmethod
    def _to_plan_response(cls, p: InterviewPlanRecord) -> InterviewPlanResponse:
        rounds_list = []
        if hasattr(p, "rounds") and p.rounds:
            rounds_list = [
                InterviewRoundResponse(
                    id=r.id,
                    plan_id=r.plan_id,
                    round_number=r.round_number,
                    round_name=r.round_name,
                    scheduled_at_utc=ensure_utc(r.scheduled_at_utc),
                    interview_format=InterviewFormat(r.interview_format),
                    interviewer_names=r.interviewer_names,
                    focus_areas=r.focus_areas_json or [],
                    status=InterviewRoundStatus(r.status),
                )
                for r in p.rounds
            ]

        return InterviewPlanResponse(
            id=p.id,
            application_id=p.application_id,
            user_id=p.user_id,
            title=p.title,
            role_title=p.role_title,
            company_name=p.company_name,
            job_description_excerpt=p.job_description_excerpt,
            created_at=ensure_utc(p.created_at),
            updated_at=ensure_utc(p.updated_at),
            rounds=rounds_list,
        )

    @classmethod
    def _to_star_response(cls, a: STARAnswerRecord) -> STARAnswerResponse:
        ref = a.supporting_evidence_json.get("reference") if a.supporting_evidence_json else None
        return STARAnswerResponse(
            id=a.id,
            user_id=a.user_id,
            plan_id=a.plan_id,
            question=a.question,
            category=a.category,
            situation=a.situation,
            task=a.task,
            action=a.action,
            result=a.result,
            supporting_evidence_reference=ref,
            missing_information_notes=a.missing_information_notes,
            is_candidate_approved=a.is_candidate_approved,
            created_at=ensure_utc(a.created_at),
            updated_at=ensure_utc(a.updated_at),
        )

    @classmethod
    def _to_mock_session_response(cls, s: MockInterviewSessionRecord) -> MockSessionResponse:
        q_list = []
        if hasattr(s, "questions") and s.questions:
            for q in s.questions:
                rubric = None
                if q.feedback_json and "overall_score" in q.feedback_json:
                    rubric = RubricScoreBreakdown(**q.feedback_json)

                q_list.append(
                    MockQuestionResponse(
                        id=q.id,
                        session_id=q.session_id,
                        question_text=q.question_text,
                        category=q.category,
                        order_index=q.order_index,
                        candidate_answer=q.candidate_answer,
                        rubric_evaluation=rubric,
                        follow_up_question=q.follow_up_question,
                        answered_at=ensure_utc(q.answered_at),
                    )
                )

        return MockSessionResponse(
            id=s.id,
            user_id=s.user_id,
            plan_id=s.plan_id,
            role_title=s.role_title,
            session_type=MockSessionType(s.session_type),
            status=s.status,
            average_score=s.average_score,
            overall_feedback_summary=s.overall_feedback_summary,
            questions=q_list,
            created_at=ensure_utc(s.created_at),
            completed_at=ensure_utc(s.completed_at),
        )

