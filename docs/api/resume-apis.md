# Resume Intelligence REST API Reference

All endpoints are hosted by the **Core Career Engine** and prefixed with `/api/v1/resumes`.
Authentication is mandatory using standard PyJWT Bearer tokens or the `rightfit_session` HttpOnly cookie.

---

## 1. Resume Container Management

### `POST /api/v1/resumes`
Uploads an initial candidate resume (PDF or DOCX) and initializes version 1.
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `title` (string, optional, default: `"My Resume"`)
  - `file` (binary document, required, max 10MB)
- **Response**: `201 Created` with `ResumeUploadResponse`.

### `GET /api/v1/resumes`
Lists all resume containers owned by the authenticated candidate.
- **Response**: `200 OK` with `List[ResumeSummaryResponse]`.

### `GET /api/v1/resumes/{resume_id}`
Retrieves summary details and active version metadata for a specific resume.
- **Response**: `200 OK` with `ResumeSummaryResponse`.

### `DELETE /api/v1/resumes/{resume_id}`
Permanently deletes a resume, its versions, extractions, and physical disk files.
- **Response**: `200 OK` with `{"success": true, "message": "..."}`.

---

## 2. Version Management

### `POST /api/v1/resumes/{resume_id}/versions`
Uploads a new version to an existing resume container without overwriting past versions.
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `version_label` (string, optional, e.g. `"v2 - Backend Focus"`)
  - `file` (binary document, required)
- **Response**: `201 Created` with `ResumeUploadResponse`.

### `GET /api/v1/resumes/{resume_id}/versions`
Lists all versions belonging to the resume.
- **Response**: `200 OK` with `List[ResumeVersionResponse]`.

### `PATCH /api/v1/resumes/{resume_id}/active-version`
Sets a specific version as the active version for the candidate.
- **Query Parameters**:
  - `version_id` (string, required)
- **Response**: `200 OK` with updated `ResumeSummaryResponse`.

---

## 3. Parsing & Structured Extraction

### `POST /api/v1/resumes/{resume_id}/parse`
Executes document text extraction, section classification, and evidenced entity parsing.
- **Query Parameters**:
  - `version_id` (string, optional, defaults to active version)
- **Response**: `200 OK` with `ResumeExtractionResponse`.

### `GET /api/v1/resumes/{resume_id}/extraction`
Retrieves structured entities (contact, summary, education, experience, skills, projects, certifications) and evidence items.
- **Response**: `200 OK` with `ResumeExtractionResponse`.

---

## 4. Review Workbench & Profile Synchronization

### `GET /api/v1/resumes/{resume_id}/review`
Returns review workbench state, evidence items, and profile conflict diffs.
- **Response**: `200 OK` with `ResumeReviewResponse`.

### `PATCH /api/v1/resumes/{resume_id}/review`
Confirms, corrects, or rejects an evidenced candidate fact.
- **Body (`ResumeReviewFieldUpdate`)**:
  ```json
  {
    "field_id": "uuid",
    "action": "CONFIRM",
    "corrected_value": null
  }
  ```
- **Response**: `200 OK` with updated `ResumeReviewResponse`.

### `POST /api/v1/resumes/{resume_id}/confirm`
Synchronizes candidate-confirmed facts into canonical profile tables (`CandidateProfile`, `EducationRecord`, `ExperienceRecord`, `CandidateSkillRecord`).
- **Body (`ResumeConfirmSyncRequest`)**:
  ```json
  {
    "approved_field_ids": null,
    "overwrite_conflicts": false
  }
  ```
- **Response**: `200 OK` with `ResumeConfirmSyncResponse`.

---

## 5. ATS Keyword & Impact Analysis

### `POST /api/v1/resumes/{resume_id}/ats-analysis`
Evaluates keyword coverage, bullet impact strength, and non-fabricating advice against a target job description.
- **Body (`ATSAnalysisRequest`)**:
  ```json
  {
    "target_job_title": "Senior Backend Engineer",
    "target_job_description": "We are seeking a Python engineer..."
  }
  ```
- **Response**: `200 OK` with `ATSAnalysisResponse`.

### `GET /api/v1/resumes/{resume_id}/ats-analysis/{analysis_id}`
Retrieves a previously computed ATS analysis report.
- **Response**: `200 OK` with `ATSAnalysisResponse`.

---

## 6. Secure Document Download

### `GET /api/v1/resumes/{resume_id}/download`
Streams original candidate file bytes with ownership enforcement and Content-Disposition header.
- **Query Parameters**:
  - `version_id` (string, optional)
- **Response**: `200 OK` binary stream (`application/pdf` or `application/vnd.openxmlformats...`).

