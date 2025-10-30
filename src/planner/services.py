from .models import MindState, Goal, DecisionLog
from diary.models import DiaryEntry
from ai_engine.services import predict_mindstate
from datetime import date
def ingest_mindstate_from_diary(user, mindset_dict:dict):
    """
    Simple logic: update or create MindState based on diary insights.
    """
    # date = diary_entry.created_at.date()
    data=data.today()
    processed = mindset_dict
    
    focus = processed.get('focus', 0.5)
    energy = processed.get('energy', 0.5)
    motivation = processed.get('motivation', 0.5)
    emotion = processed.get('emotion', 'neutral')

    mind, _ = MindState.objects.update_or_create(
        user=user,
        date=date,
        defaults={
            'focus': focus,
            'energy': energy,
            'motivation': motivation,
            'emotion': emotion,
            'context': processed.get('context', {})
        }
    )
    return mind







def log_decision(user, action: dict, rationale: str, diary_entry_id=None, plan_id=None):
    """
    Generic helper to log a decision/action for transparency.
    """
    return DecisionLog.objects.create(
        user=user,
        diary_entry_id=diary_entry_id,
        plan_id=plan_id,
        action=action,
        rationale=rationale
    )
