from diary.models import DiaryEntry
from django.utils import timezone
from datetime import timedelta

def get_diary_insights(user, days=7) -> dict:
    """Return diary insights for last `days` days"""
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    entries = DiaryEntry.objects.filter(
        user=user,
        created_at__date__range=(start_date, end_date)
    ).order_by('-created_at')

    if not entries.exists():
        return {"status": "no_data", "message": f"No diary entries in last {days} days"}

    emotions = [e.processed.get("emotion") for e in entries if e.processed and "emotion" in e.processed]
    sentiments = [e.processed.get("sentiment") for e in entries if e.processed and "sentiment" in e.processed]

    return {
        "status": "success",
        "days_analyzed": days,
        "entry_count": entries.count(),
        "common_emotions": list(set(emotions)),
        "average_sentiment": sum(sentiments) / len(sentiments) if sentiments else None,
        "entries": [
            {"date": e.created_at.date(), "type": e.input_type, "processed": e.processed} 
            for e in entries
        ]
    }

def get_last_processed_entry(user, text: str):
    """Return processed data for an existing diary entry with same raw_text"""
    entry = DiaryEntry.objects.filter(user=user, raw_text=text).last()
    return entry.processed if entry and entry.processed else None
