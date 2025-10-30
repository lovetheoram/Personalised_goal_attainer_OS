# services/intents.py

INTENT_KEYWORDS = {
    "get_targets": ["target", "study plan", "today to study"],
    "start_quiz": ["quiz", "test me", "check me"],
    "get_progress": ["progress", "mastery", "readiness"],
    "list_subjects": ["subjects", "list subjects"],
    "list_subtopics": ["subtopics in", "subtopics for"],
    "list_topics": ["topics in", "topics for"],
    "list_concepts": ["concepts in", "concepts for"],
    "concept_detail": ["details of concept", "concept info"],
    "get_mindstate": ["my mindstate", "how am i doing", "my focus", "my motivation"],
    "mindstate_history": ["mindstate history", "focus history", "motivation trend"],
    "improve_mindstate": ["improve focus", "boost motivation", "increase energy"],
    "diary_reflection": ["diary insights", "mood pattern", "emotion trend"],
    "start_diary": ["write diary", "new diary", "diary entry"],
    "greeting": ["hello", "hi", "hey", "good morning", "good evening", "what’s up"],
    "small_talk": ["how are you", "who are you", "tell me a joke", "what do you do"],
    "command": ["open", "start", "stop", "play", "show"],
}

# Intent → category mapping
INTENT_CATEGORY = {
    # Action intents (fast, functional)
    "get_targets": "action",
    "start_quiz": "action",
    "get_progress": "action",
    "list_subjects": "action",
    "list_topics": "action",
    "list_subtopics": "action",
    "list_concepts": "action",
    "concept_detail": "action",
    "get_mindstate": "action",
    "mindstate_history": "action",
    "improve_mindstate": "action",

    # Reflective (goes into Diary + AI reasoning)
    "diary_reflection": "reflective",
    "start_diary": "reflective",

    # Informational or small-talk (no heavy processing)
    "greeting": "informational",
    "small_talk": "informational",
    "command": "action",
}


def detect_intent(message: str) -> dict:
    """
    Detect user intent and classify it into a category.
    Returns: {"intent": <str>, "category": <str>}
    """
    if not message:
        return {"intent": "chat", "category": "informational"}

    m = message.lower()

    # Exact keyword-based match
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in m for k in keywords):
            return {"intent": intent, "category": INTENT_CATEGORY.get(intent, "action")}

    # Heuristic fallback — detect reflective / emotional content
    reflective_triggers = ["i feel", "i am", "today", "yesterday", "i did", "i failed", "i want", "i wish"]
    if any(t in m for t in reflective_triggers):
        return {"intent": "reflective_journal", "category": "reflective"}

    # Default: simple chat
    return {"intent": "chat", "category": "informational"}
