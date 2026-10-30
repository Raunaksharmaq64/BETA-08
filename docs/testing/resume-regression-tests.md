# Resume Intelligence Automated Regression Tests

## 1. Overview & Test Suite Structure

The Resume Intelligence automated test suite validates document parsing, evidence linking, candidate review, cross-candidate security isolation, and regression compatibility with Phase 2 and Phase 3 features.

All test documents utilize **synthetic, non-real-person fixtures** created specifically for testing purposes. Real candidate resumes and PII are strictly barred from the repository.

---

## 2. Test Suites Summary

| Test File | Type | Target System | Test Count | Status |
|---|---|---|---|---|
| `backend/tests/unit/test_resume_parser.py` | Unit | PDF/DOCX parsing, section detection, entity extraction, evidence linking | 8 | ✅ PASSED |
| `backend/tests/unit/test_ats_analysis.py` | Unit | Keyword coverage, bullet impact scoring, no-fabrication rule | 5 | ✅ PASSED |
| `backend/tests/unit/test_storage_security.py` | Unit | Path traversal defense, magic byte validation, size limits | 6 | ✅ PASSED |
| `backend/tests/integration/test_resume_api.py` | Integration | Upload, versioning, parsing, review workbench, profile sync, ATS analysis, download, delete | 1 (12 steps) | ✅ PASSED |
| `backend/tests/integration/test_resume_security_and_idor.py` | Security | Cross-candidate IDOR rejection, unauthenticated rejection, malicious file blocking | 3 | ✅ PASSED |
| **Total Phase 4 Tests** | | | **23** | **100% PASSED** |

---

## 3. Full Platform Regression Suite

The full test suite was executed across all contract, unit, integration, and security layers:
- **Contract Tests**: 31 passed
- **Phase 3 Auth & Privacy**: 28 passed
- **Phase 4 Resume Intelligence**: 23 passed
- **Grand Total**: **82 passed, 0 failed** in 99.66s.

---

## 4. Synthetic Fixture Inventory

Located in `backend/tests/fixtures/synthetic_resumes/`:

1. `standard_one_page.pdf`: 1-page PDF testing Jane Doe (Stanford, TechCorp, DataFlow, Python, Go, FastAPI, Docker).
2. `multi_page.pdf`: 2-page PDF testing Alex Smith (CloudScale, AlphaTech, BetaCorp, MIT, UC Berkeley, C++, Rust).
3. `standard_resume.docx`: DOCX testing Emily Davis with formatted tables and bullet runs.
4. `missing_sections.pdf`: Document missing summary, projects, and certifications (verifies no-fabrication rule).
5. `empty.pdf`: 0-text PDF testing graceful empty document rejection.
6. `corrupted.pdf`: Malformed binary payload starting with `%PDF-` testing parser fault tolerance.
7. `password_protected.pdf`: AES-256 encrypted PDF testing encrypted document rejection.
8. `corrupted_resume.docx`: Malformed ZIP archive testing DOCX error recovery.
9. `malicious.exe`: Executable header testing file type rejection.

