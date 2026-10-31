# Reminders, Scheduling & Timezone Intelligence

## Overview
Reminders in RIGHT FIT are mission-critical. A missed interview or follow-up deadline damages candidate trust. All reminders are strictly stored in UTC with explicit IANA timezone translation for local rendering and DST safety.

## Timezone Storage Standard
- **Database Storage**: Strict ISO 8601 UTC with timezone offset zero (`Z` or `+00:00`).
- **User Preference**: Candidates specify their active IANA Timezone (e.g. `America/New_York`, `Asia/Kolkata`, `Europe/London`).
- **Daylight Saving Time (DST) Handling**: Reminders scheduled across DST boundaries calculate the exact wall-clock instant in UTC without drifting 1 hour forward or backward.

## Schema (`ReminderRecord`)
```python
class ReminderRecord(Base):
    __tablename__ = "reminders"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = Column(String(36), ForeignKey("candidate_profiles.id"), nullable=False)
    application_id = Column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True)
    interview_plan_id = Column(String(36), ForeignKey("interview_plans.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=False)  # Always UTC
    user_timezone = Column(String(64), default="UTC", nullable=False)
    status = Column(String(32), default="PENDING", nullable=False)  # PENDING, COMPLETED, DISMISSED, CANCELLED
    recurrence_rule = Column(String(128), nullable=True)
```

## Calendar Integration
- Supports standard iCalendar / ICS export for Google Calendar, Apple Calendar, and Outlook.
- Timezone rules are bundled in the VTIMEZONE calendar block.

