# Evaluation Dataset & Precision Benchmarks

## 1. Objective & Benchmark Methodology

To ensure algorithmic integrity and prevent hallucinations, Phase 7 includes an automated test and verification suite evaluating:
1. **Skill Normalization & Alias Accuracy**: 100% precision on canonical technical aliases (e.g. `py` -> `python`, `k8s` -> `kubernetes`, `postgres` -> `postgresql`).
2. **Missing Profile Data Semantics**: 100% adherence to `UNKNOWN` evaluation when candidate records are incomplete (zero false rejections).
3. **Multi-Dimensional Ranking Monotonicity**: Verifying that verified, fresh, high-match opportunities rank strictly above unverified, stale, low-match listings.
4. **Delivery Idempotency**: Zero duplicate notifications when background alert evaluation runs repeatedly.

---

## 2. Test Execution Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.1.0, pluggy-1.6.0
collecting ... collected 15 items

backend/tests/unit/test_skill_fit_engine.py::test_normalize_skill_aliases PASSED [  6%]
backend/tests/unit/test_skill_fit_engine.py::test_compute_skill_fit_exact_and_alias_matches PASSED [ 13%]
backend/tests/unit/test_skill_fit_engine.py::test_compute_skill_fit_no_hallucinations_or_invented_skills PASSED [ 20%]
backend/tests/unit/test_skill_fit_engine.py::test_compute_skill_fit_with_resume_evidence_excerpts PASSED [ 26%]
backend/tests/unit/test_eligibility_engine.py::test_missing_candidate_profile_returns_unknown_never_false_rejection PASSED [ 33%]
backend/tests/unit/test_eligibility_engine.py::test_missing_experience_and_education_evaluates_to_unknown PASSED [ 40%]
backend/tests/unit/test_eligibility_engine.py::test_satisfied_all_criteria_returns_meets_requirements PASSED [ 46%]
backend/tests/unit/test_eligibility_engine.py::test_unsatisfied_location_returns_does_not_meet PASSED [ 53%]
backend/tests/unit/test_explainable_ranking.py::test_ranking_score_deterministic_calculation PASSED [ 60%]
backend/tests/unit/test_explainable_ranking.py::test_ranking_relative_ordering PASSED [ 66%]
backend/tests/unit/test_saved_searches_and_alerts.py::test_saved_job_save_unsave_and_notes PASSED [ 73%]
backend/tests/unit/test_saved_searches_and_alerts.py::test_saved_search_create_and_alerts PASSED [ 80%]
backend/tests/integration/test_job_search_api.py::test_job_search_endpoint_with_filters_and_coverage PASSED [ 86%]
backend/tests/integration/test_job_search_api.py::test_saved_job_lifecycle PASSED [ 93%]
backend/tests/integration/test_job_search_api.py::test_saved_searches_lifecycle PASSED [100%]

============================= 15 passed in 23.92s =============================
```

---

## 3. Full Platform Suite Stability

Across all phases (Phases 1 through 7), the entire regression test suite of **135 automated tests** passed with zero failures:
```
======================= 135 passed in 172.64s (0:02:52) =======================
```
All 28 Next.js frontend routes compiled successfully in **711ms** with zero TypeScript or bundling errors.

