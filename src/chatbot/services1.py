from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from progress.models import UserConceptProgress
from syllabus.models import Subject, Topic, Subtopic, Concept
from target.models import PlanTask
from target.services import get_latest_plan_tasks
from quiz.services import generate_ai_quiz
from django.core.cache import cache
from ai_engine.services import infer_text, predict_mindstate, find_similar_entries
from diary.models import DiaryEntry
User = get_user_model()


# -----------------------------
# Intent Detection
# -----------------------------
INTENT_KEYWORDS = {
    "get_targets": ["target", "study plan", "today to study"],
    "start_quiz": ["quiz", "test me", "check me"],
    "get_progress": ["progress", "mastery", "readiness"],
    "list_subjects": ["subjects", "list subjects"],
    "list_subtopics": ["subtopics in", "subtopics for"],
    "list_topics": ["topics in", "topics for"],
    "list_concepts": ["concepts in", "concepts for"],
    "concept_detail": ["details of concept", "concept info"],
   
    # New mindstate-related intents
    "get_mindstate": ["my mindstate", "how am i doing", "my focus", "my motivation"],
    "mindstate_history": ["mindstate history", "focus history", "motivation trend"],
    "improve_mindstate": ["improve focus", "boost motivation", "increase energy"],
    # New diary-related intents
    "diary_reflection": ["diary insights", "mood pattern", "emotion trend"],
    "start_diary": ["write diary", "new diary", "diary entry"]
}


def detect_intent(message: str) -> str:
    m = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in m for k in keywords):
            return intent
    return "chat"


# -----------------------------
# User Progress Helper
# -----------------------------
def get_user_progress(user) -> list[dict]:
    """Return all concepts with user's progress details."""
    progress_qs = UserConceptProgress.objects.filter(user=user).select_related('concept')
    return [
        {
            "concept_id": p.concept.id,
            "concept_name": p.concept.name,
            "mastery": p.mastery,
            "last_studied": p.last_studied,
            "last_score": p.last_score,
        }
        for p in progress_qs
    ]


# -----------------------------
# MindState Handlers
# -----------------------------
def get_current_mindstate(user) -> dict:
    """Get user's current mindstate"""
    from planner.models import MindState
    from django.utils import timezone
    
    today = timezone.now().date()
    state = MindState.objects.filter(user=user, date=today).first()
    
    if not state:
        return {
            'status': 'not_recorded',
            'message': 'No mindstate recorded for today'
        }
    
    return {
        'status': 'recorded',
        'focus': state.focus,
        'energy': state.energy,
        'motivation': state.motivation,
        'emotion': state.emotion,
        'context': state.context
    }

def get_mindstate_trends(user, days=7) -> dict:
    """Get mindstate trends over time"""
    from planner.models import MindState
    from django.utils import timezone
    from django.db.models import Avg
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    states = MindState.objects.filter(
        user=user,
        date__range=(start_date, end_date)
    ).order_by('date')
    
    if not states.exists():
        return {
            'status': 'no_data',
            'message': f'No mindstate data available for the last {days} days'
        }
    
    averages = states.aggregate(
        avg_focus=Avg('focus'),
        avg_energy=Avg('energy'),
        avg_motivation=Avg('motivation')
    )
    
    return {
        'status': 'success',
        'days_analyzed': days,
        'averages': averages,
        'daily_states': [
            {
                'date': s.date,
                'focus': s.focus,
                'energy': s.energy,
                'motivation': s.motivation,
                'emotion': s.emotion
            } for s in states
        ]
    }

# -----------------------------
# Diary Handlers
# -----------------------------
def get_diary_insights(user, days=7) -> dict:
    """Get insights from diary entries"""
    from diary.models import DiaryEntry
    from django.utils import timezone
    
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=days)
    
    entries = DiaryEntry.objects.filter(
        user=user,
        created_at__date__range=(start_date, end_date)
    ).order_by('-created_at')
    
    if not entries.exists():
        return {
            'status': 'no_data',
            'message': f'No diary entries found for the last {days} days'
        }
    
    # Extract emotions and sentiments from processed data
    emotions = []
    sentiments = []
    
    for entry in entries:
        if entry.processed:
            if 'emotion' in entry.processed:
                emotions.append(entry.processed['emotion'])
            if 'sentiment' in entry.processed:
                sentiments.append(entry.processed['sentiment'])
    
    entry_count = entries.count()

    return {
        'status': 'success',
        'days_analyzed': days,
        'entry_count': entry_count,
        'common_emotions': list(set(emotions)),
        'average_sentiment': sum(sentiments) / len(sentiments) if sentiments else None,
        'entries': [
            {
                'date': e.created_at.date(),
                'type': e.input_type,
                'processed': e.processed
            } for e in entries
        ]
    }


# -----------------------------
# Syllabus Helpers
# -----------------------------
def fetch_subjects():
    return list(Subject.objects.all().values("id", "name", "weightage"))


def fetch_topics(subject_name: str):
    try:
        subject = Subject.objects.prefetch_related(
            Prefetch("topics", queryset=Topic.objects.all())
        ).get(name__iexact=subject_name)
        return list(subject.topics.all().values("id", "name", "weightage"))
    except Subject.DoesNotExist:
        return {"error": "Subject not found"}


def fetch_subtopics(topic_name: str):
    try:
        topic = Topic.objects.prefetch_related(
            Prefetch("subtopics", queryset=Subtopic.objects.all())
        ).get(name__iexact=topic_name)
        return list(topic.subtopics.all().values("id", "name", "weightage"))
    except Topic.DoesNotExist:
        return {"error": "Topic not found"}


def fetch_concepts(subtopic_name: str):
    try:
        subtopic = Subtopic.objects.prefetch_related(
            Prefetch("concepts", queryset=Concept.objects.all())
        ).get(name__iexact=subtopic_name)
        return list(subtopic.concepts.all().values(
            "id", "name", "description", "weightage", "difficulty"
        ))
    except Subtopic.DoesNotExist:
        return {"error": "Subtopic not found"}


def fetch_concept_detail(concept_name: str):
    try:
        concept = Concept.objects.get(name__iexact=concept_name)
        return {
            "name": concept.name,
            "description": concept.description,
            "estimated_time": concept.estimated_time,
            "weightage": concept.weightage,
            "difficulty": concept.difficulty,
            "resources": concept.resources
        }
    except Concept.DoesNotExist:
        return {"error": "Concept not found"}


# -----------------------------
# Daily Targets Helper
# -----------------------------
def fetch_daily_targets(user):
    today = date.today()
    targets=get_latest_plan_tasks(user, today)
    return list(targets.values(
        "id", "study_date", "concept", "allocated_time", "status", "created_at"
    ))


# -----------------------------
# AI Quiz Helper
# -----------------------------
def start_ai_quiz(user):
    try:
        today = date.today()
        return generate_ai_quiz(user, today)
    except Exception as e:
        return {"error": str(e)}


def ai_chat_reply(user, message: str) -> dict:
    if not message.strip():
        return {"message": "Please write something for me to respond."}

    # Step 1: Try to get processed data from DB
    diary_entry = DiaryEntry.objects.filter(user=user, raw_text=message).last()
    if diary_entry and diary_entry.processed:
        processed = diary_entry.processed
    else:
        processed = infer_text(message)

    mindstate = predict_mindstate(message, [])

    # Step 2: Retrieve memory of past diary entries
    cache_key = f"user_diary_embeddings:{user.id}"
    entry_embeddings = cache.get(cache_key, [])
    similar_entries = find_similar_entries(message, entry_embeddings)

    # Step 3: Generate reply based on emotion and sentiment
    primary_emotion = mindstate["primary_emotion"]
    sentiment_score = processed["sentiment"]

    reply_text = ""
    if primary_emotion in ["sadness", "fear"]:
        reply_text = "I hear you. It's okay to feel this way. Want to talk more?"
    elif primary_emotion == "joy":
        reply_text = "That’s great to hear! Keep up the positive energy!"
    elif sentiment_score < -0.3:
        reply_text = "It seems like a tough moment. How can I support you?"
    else:
        reply_text = "I understand. Can you tell me more?"

    if similar_entries:
        last_entry = similar_entries[0]
        reply_text += f" (You wrote something similar before: \"{last_entry['entry_id']}\")"

    return {"message": reply_text, "mindstate": mindstate, "processed": processed}



# -----------------------------
# Main Intent Handler
# -----------------------------
def handle_intent(user, intent: str, message: str = None) -> dict:
    if intent == "list_subjects":
        return {"intent": intent, "payload": fetch_subjects()}

    elif intent == "list_topics":
        subject_name = message.lower().split("topics for")[-1].strip()
        return {"intent": intent, "payload": fetch_topics(subject_name)}

    elif intent == "list_subtopics":
        topic_name = message.lower().split("subtopics for")[-1].strip()
        return {"intent": intent, "payload": fetch_subtopics(topic_name)}

    elif intent == "list_concepts":
        subtopic_name = message.lower().split("concepts for")[-1].strip()
        return {"intent": intent, "payload": fetch_concepts(subtopic_name)}

    elif intent == "concept_detail":
        concept_name = message.lower().split("concept info")[-1].strip()
        return {"intent": intent, "payload": fetch_concept_detail(concept_name)}

    elif intent == "get_targets":
        return {"intent": intent, "payload": fetch_daily_targets(user)}

    elif intent == "get_progress":
        return {"intent": intent, "payload": get_user_progress(user)}

    elif intent == "start_quiz":
        return {"intent": intent, "payload": start_ai_quiz(user)}

    # Fallback
    return {
        "intent": "chat",
        "payload": {
            "message": "I can show syllabus, topics, subtopics, targets, progress, and start AI quizzes."
        }
    }
