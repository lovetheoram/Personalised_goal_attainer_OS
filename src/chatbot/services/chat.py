from django.core.cache import cache
from diary.models import DiaryEntry
from ai_engine.services import infer_text, predict_mindstate, find_similar_entries


def ai_chat_reply(user, message: str) -> dict:
    if not message.strip():
        return {"message": "Please write something for me to respond."}

    # --- Step 1: Process text ---
    diary_entry = DiaryEntry.objects.filter(user=user, raw_text=message).last()
    processed = diary_entry.processed if diary_entry and diary_entry.processed else infer_text(message)
    mindstate = predict_mindstate(message, [])

    # --- Step 2: Check for similar past entries (only if available) ---
    reply_text = ""
    cache_key = f"user_diary_embeddings:{user.id}"
    entry_embeddings = cache.get(cache_key)

    if entry_embeddings:
        similar_entries = find_similar_entries(message, entry_embeddings)
    else:
        similar_entries = []

    # --- Step 3: Generate emotion-based reply ---
    primary_emotion = mindstate.get("primary_emotion", "neutral")
    sentiment_score = processed.get("sentiment", 0)

    if primary_emotion in ["sadness", "fear"]:
        reply_text = "I hear you. It's okay to feel this way. Want to talk more?"
    elif primary_emotion == "joy":
        reply_text = "That’s great to hear! Keep up the positive energy!"
    elif sentiment_score < -0.3:
        reply_text = "It seems like a tough moment. How can I support you?"
    else:
        reply_text = "I understand. Can you tell me more?"

    # --- Step 4: Add contextual memory only if found ---
    if similar_entries:
        last_entry = similar_entries[0]
        reply_text += f" (You wrote something similar before: \"{last_entry['entry_id']}\")"

    return {
        "message": reply_text,
        "mindstate": mindstate,
        "processed": processed
    }
