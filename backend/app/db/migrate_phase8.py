"""
RIGHT FIT Core — Phase 8 Database Migration Helper
Creates Phase 8 tables (applications, application_status_history, application_notes,
reminders, interview_plans, interview_rounds, star_answers, mock_interview_sessions,
mock_interview_questions, interview_debriefs, notifications, notification_preferences)
in the active database.
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.db.models import (
    Base,
    ApplicationRecord,
    ApplicationStatusHistoryRecord,
    ApplicationNoteRecord,
    ReminderRecord,
    InterviewPlanRecord,
    InterviewRoundRecord,
    STARAnswerRecord,
    MockInterviewSessionRecord,
    MockInterviewQuestionRecord,
    InterviewDebriefRecord,
    NotificationRecord,
    NotificationPreferencesRecord,
)


def run_migration():
    sync_url = settings.DATABASE_URL.replace("sqlite+aiosqlite:", "sqlite:")
    sync_url = sync_url.replace("postgresql+asyncpg:", "postgresql:")
    print(f"Connecting to {sync_url} to create Phase 8 tables...")
    engine = create_engine(sync_url)
    
    tables_to_create = [
        ApplicationRecord.__table__,
        ApplicationStatusHistoryRecord.__table__,
        ApplicationNoteRecord.__table__,
        ReminderRecord.__table__,
        InterviewPlanRecord.__table__,
        InterviewRoundRecord.__table__,
        STARAnswerRecord.__table__,
        MockInterviewSessionRecord.__table__,
        MockInterviewQuestionRecord.__table__,
        InterviewDebriefRecord.__table__,
        NotificationRecord.__table__,
        NotificationPreferencesRecord.__table__,
    ]

    Base.metadata.create_all(bind=engine, tables=tables_to_create)
    print("Phase 8 tables created successfully (12 tables).")


if __name__ == "__main__":
    run_migration()

