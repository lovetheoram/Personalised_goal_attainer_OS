from datetime import date
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from progress.models import UserConceptProgress
from syllabus.models import Subject, Topic, Subtopic, Concept
from target.models import DailyTarget
from quiz.services import generate_ai_quiz

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
    "concept_detail": ["details of concept", "concept info"]
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
    targets = DailyTarget.objects.filter(user=user, study_date=today).select_related('concept')
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
