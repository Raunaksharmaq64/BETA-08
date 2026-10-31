# Notifications & Candidate Preferences

## Overview
Candidates receive timely notifications regarding upcoming interview milestones, deadline reminders, application status updates, and new job match alerts. All deliveries honor candidate channel preferences and frequency limits.

## Notification Categories & Channels
- **Categories**:
  - `INTERVIEW_REMINDER`: Critical 24-hour and 1-hour interview alerts.
  - `APPLICATION_STATUS`: Confirmation of state transitions or employer responses.
  - `DEADLINE_ALERT`: Take-home exam or offer expiration countdown.
  - `JOB_MATCH`: High-confidence verified opportunity alerts.
  - `SYSTEM_ALERT`: Security, privacy, or policy notices.
- **Channels**:
  - `IN_APP`: Notification drawer and banner alerts.
  - `EMAIL`: Asynchronous transactional email.
  - `SMS`: High-priority time-sensitive reminders (opt-in).

## Schema (`NotificationRecord` & `NotificationPreferenceRecord`)
```python
class NotificationRecord(Base):
    __tablename__ = "notifications"
    id = Column(String(36), primary_key=True)
    candidate_id = Column(String(36), ForeignKey("candidate_profiles.id"), nullable=False)
    category = Column(String(64), nullable=False)
    channel = Column(String(32), default="IN_APP", nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    payload_json = Column(JSON, default=dict)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

class NotificationPreferenceRecord(Base):
    __tablename__ = "notification_preferences"
    id = Column(String(36), primary_key=True)
    candidate_id = Column(String(36), ForeignKey("candidate_profiles.id"), nullable=False)
    channel = Column(String(32), nullable=False)
    category = Column(String(64), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    quiet_hours_start = Column(String(5), nullable=True)  # e.g., "22:00"
    quiet_hours_end = Column(String(5), nullable=True)    # e.g., "08:00"
```

