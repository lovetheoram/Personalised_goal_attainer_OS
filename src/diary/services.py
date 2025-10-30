import threading
from django.utils import timezone
from diary.models import DiaryEntry
from planner.services import ingest_mindstate_from_diary
from ai_engine.services import infer_text, predict_mindstate,cache_user_diary_embedding



def process_diary_entry(diary_entry: DiaryEntry):
    """
    Process a diary entry:
    
    2. Infer emotions, sentiment, topics.
    3. Predict mindstate.
    4. Update MindState table.
    5. Update AI memory (diary embeddings, context).
    """
   
    # --- Step 2: Text ---
    text = diary_entry.transcript or diary_entry.raw_text or ""
    if not text.strip():
        return

    # --- Step 3: AI Inference ---
    processed = infer_text(text)
    diary_entry.processed = processed
    diary_entry.processed_at = timezone.now()
    diary_entry.save()

    # --- Step 4: Mindstate Prediction & Update ---
    mindstate_dict = predict_mindstate(text, [])
    try:
        ingest_mindstate_from_diary(diary_entry.user, mindstate_dict)
    except Exception as e:
        print("Mindstate update failed:", e)

    # --- Step 5: Update AI Memory ---
    # Optionally cache embeddings for faster AI chat replies
    cache_user_diary_embedding(diary_entry.user, diary_entry.id, processed["context"]["embedding"])


def process_in_background(diary_entry: DiaryEntry):
    """Run diary processing in background"""
    thread = threading.Thread(target=process_diary_entry, args=(diary_entry,))
    thread.daemon = True
    thread.start()


def create_diary_entry(user, input_type, raw_text=None, audio_s3_key=None, privacy_flags=None):
    """Create diary entry and launch async processing"""
    diary = DiaryEntry.objects.create(
        user=user,
        input_type=input_type,
        raw_text=raw_text,
        audio_s3_key=audio_s3_key,
        privacy_flags=privacy_flags or {}
    )
    
    


    process_in_background(diary)
    return diary
