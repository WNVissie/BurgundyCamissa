from src.models.models import db, ActivityLog

def log_activity(user_id, action, details=None):
    """
    Helper function to log an activity.
    """
    try:
        log = ActivityLog(
            user_id=user_id,
            action=action,
            details=details
        )
        db.session.add(log)
        # The session will be committed by the calling route's final commit.
        # This ensures that the log is only saved if the main action succeeds.
    except Exception as e:
        # If logging fails, we don't want to crash the main operation.
        # In a production app, you might want to log this error to a file.
        print(f"Error logging activity: {e}")
