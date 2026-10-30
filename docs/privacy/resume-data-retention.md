# Resume Privacy, Retention & Deletion Standards

## 1. Regulatory Context (GDPR / CCPA)

Under GDPR (Art. 5, 17, 20) and CCPA/CPRA, resume documents and the personal identifiable information (PII) extracted from them are subject to strict data minimization, purpose limitation, and erasure requirements.

In **RIGHT FIT**, candidates retain the right to delete individual resumes or initiate complete account erasure at any time.

---

## 2. Retention Policies

| Entity / Asset | Storage Location | Retention Lifetime | Deletion Trigger |
|---|---|---|---|
| **Original Resume File** | Private local storage (`storage/resumes/{user_id}/`) | Retained while candidate maintains version | Explicit resume deletion or account deletion |
| **Extracted Raw Text** | Database column `raw_text` | Retained during active candidate review | Purged upon resume deletion |
| **Evidenced Fact Records** | Database column `evidence_items_json` | Retained while version exists | Purged upon resume deletion |
| **Temporary Parse Buffers** | In-memory `io.BytesIO` | Discarded immediately after parsing | Destroyed upon request completion |

---

## 3. Deletion Behavior & Execution

### 3.1 Individual Resume Deletion (`DELETE /api/v1/resumes/{resume_id}`)
1. **Ownership Validation**: Validates that `ResumeRecord.user_id == current_user.id`.
2. **File System Cleanup**: Iterates over all `ResumeVersionRecord` items under the resume and invokes `storage_service.delete_resume_file` to physically remove private disk files.
3. **Database Cascade**: Deletes the `ResumeRecord`, cascade-deleting associated `ResumeVersionRecord`, `ResumeExtractionRecord`, `ResumeReviewRecord`, and `ATSAnalysisRecord` entities.
4. **Audit Logging**: Emits `RESUME_DELETED` security audit event with sanitized IDs (no resume text logged).

### 3.2 Account Deletion Integration (`POST /api/v1/privacy/account/delete`)
When a candidate requests full account deletion:
- Account enters `DELETION_PENDING` with a 30-day statutory grace period.
- Active refresh tokens are revoked across all devices.
- Upon grace period expiration, `storage_service.purge_user_storage(user_id)` recursively removes the candidate's entire storage directory, leaving zero orphaned files.

---

## 4. GDPR / CCPA Machine-Readable Data Export

Resume metadata is fully integrated into the candidate data export pipeline (`export_service.py`):
- Includes: Resume titles, version counts, active version IDs, and creation timestamps.
- **Strictly Excluded**: Raw binary bytes, internal storage file system paths, and cryptographic secret keys.

