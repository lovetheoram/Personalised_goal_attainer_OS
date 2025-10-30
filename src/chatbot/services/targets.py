from datetime import date
from target.services import get_latest_plan_tasks

def fetch_daily_targets(user):
    today = date.today()
    targets = get_latest_plan_tasks(user, today)
    return list(targets.values(
        "id", "study_date", "concept", "allocated_time", "status", "created_at"
    ))
