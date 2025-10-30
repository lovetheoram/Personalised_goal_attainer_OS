# services/handler.py

from .chat import ai_chat_reply
from .syllabus import (
    fetch_subjects,
    fetch_topics,
    fetch_subtopics,
    fetch_concepts,
    fetch_concept_detail,
)
from .targets import fetch_daily_targets
from progress.services import get_user_progress


def handle_intent(user, intent_obj: dict, message: str = None) -> dict:
    """
    Handle the detected intent and return a structured response.
    intent_obj = {"intent": <str>, "category": <str>}
    """

    intent = intent_obj.get("intent")
    category = intent_obj.get("category")

    # ✅ Action Intents (fast, functional)
    if intent == "list_subjects":
        return {"intent": intent, "payload": fetch_subjects()}
    if intent == "list_topics":
        return {"intent": intent, "payload": fetch_topics(message)}
    if intent == "list_subtopics":
        return {"intent": intent, "payload": fetch_subtopics(message)}
    if intent == "list_concepts":
        return {"intent": intent, "payload": fetch_concepts(message)}
    if intent == "concept_detail":
        return {"intent": intent, "payload": fetch_concept_detail(message)}
    if intent == "get_targets":
        return {"intent": intent, "payload": fetch_daily_targets(user)}
    if intent == "get_progress":
        return {"intent": intent, "payload": get_user_progress(user)}

    # 🧠 Reflective intents (pass to diary/ML engine)
    if category == "reflective":
        # We don’t respond directly — diary pipeline will handle it
        return {
            "intent": intent,
            "category": category,
            "payload": "Reflective input logged for processing.",
        }
    

    # 💬 Informational / fallback → chat reply
    return {"intent": "chat", "payload": ai_chat_reply(user, message)}
