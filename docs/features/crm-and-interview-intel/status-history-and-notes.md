# Application Status History & Contextual Notes

## Overview
Every transition in an application's lifecycle is permanently archived into an append-only timeline. Candidates and agents can inspect audit logs and attach free-form or structured notes to any application.

## Application Status History

### Schema (`ApplicationStatusHistoryRecord`)
- `id`: UUID primary key
- `application_id`: Foreign key to `applications.id`
- `from_status`: Preceding state (`SAVED`, `APPLYING`, etc.)
- `to_status`: Succeeding state (`APPLIED`, `INTERVIEWING`, etc.)
- `reason`: Optional candidate or recruiter justification
- `changed_at`: UTC timestamp of transition

```python
class ApplicationStatusHistoryRecord(Base):
    __tablename__ = "application_status_history"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(String(32), nullable=True)
    to_status = Column(String(32), nullable=False)
    reason = Column(Text, nullable=True)
    changed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
```

## Contextual Notes Architecture

### Schema (`ApplicationNoteRecord`)
- `id`: UUID primary key
- `application_id`: Foreign key to `applications.id`
- `author_id`: Candidate identifier
- `category`: Note category (`GENERAL`, `CALL_SUMMARY`, `COMPENSATION_OFFER`, `REFERRAL_INFO`)
- `content`: Markdown text payload
- `created_at` / `updated_at`: UTC audit timestamps

### Security & Privacy
- Notes are strictly isolated to the authenticated candidate.
- Cross-tenant candidate notes are unreachable through cryptographic tenant isolation.
- Sensitive compensation details are protected under standard tenant-level encryption.

