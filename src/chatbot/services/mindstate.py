from django.utils import timezone
from planner.models import MindState
from django.db.models import Avg
from datetime import timedelta

def get_current_mindstate(user) -> dict:
    today = timezone.now().date()
    state = MindState.objects.filter(user=user, date=today).first()
    if not state:
        return {"status": "not_recorded", "message": "No mindstate recorded for today"}
    return {"status": "recorded", **state.__dict__}

def get_mindstate_trends(user, days=7) -> dict:
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    states = MindState.objects.filter(user=user, date__range=(start_date, end_date)).order_by('date')

    if not states.exists():
        return {"status": "no_data", "message": f"No mindstate data for last {days} days"}

    averages = states.aggregate(avg_focus=Avg('focus'), avg_energy=Avg('energy'), avg_motivation=Avg('motivation'))
    return {"status": "success", "days_analyzed": days, "averages": averages,
            "daily_states": [{"date": s.date, "focus": s.focus, "energy": s.energy,
                              "motivation": s.motivation, "emotion": s.emotion} for s in states]}
