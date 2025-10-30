from typing import Dict, List, Optional
from django.core.cache import cache
from .ml_models import EmotionAnalyzer, TextProcessor,  MindStatePredictor
import json

# Initialize ML models
_emotion_analyzer = None
_text_processor = None
_mindstate_predictor = None

def get_emotion_analyzer() -> EmotionAnalyzer:
    """Get or initialize emotion analyzer"""
    global _emotion_analyzer
    if _emotion_analyzer is None:
        _emotion_analyzer = EmotionAnalyzer()
    return _emotion_analyzer

def get_text_processor() -> TextProcessor:
    """Get or initialize text processor"""
    global _text_processor
    if _text_processor is None:
        _text_processor = TextProcessor()
    return _text_processor


def get_mindstate_predictor() -> MindStatePredictor:
    """Get or initialize mindstate predictor"""
    global _mindstate_predictor
    if _mindstate_predictor is None:
        _mindstate_predictor = MindStatePredictor()
    return _mindstate_predictor

def infer_text(text: str) -> Dict:
    """Analyze text using ML models"""
    if not text:
        return {
            'sentiment': 0.0,
            'emotion': 'neutral',
            'severity': 0.0,
            'topics': []
        }
    
    # Get cached result if available
    cache_key = f'text_inference:{hash(text)}'
    cached_result = cache.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    
    # Analyze text
    emotion_analyzer = get_emotion_analyzer()
    text_processor = get_text_processor()
    
    emotion_data = emotion_analyzer.detect_emotion(text)
    sentiment_data = emotion_analyzer.analyze_sentiment(text)
    
    # Extract key topics using TF-IDF
    topics = text_processor.extract_key_topics(text, n_topics=3)
    
    result = {
        'sentiment': sentiment_data['score'] if sentiment_data['label'] == 'POSITIVE' else -sentiment_data['score'],
        'emotion': emotion_data['primary_emotion']['label'],
        'severity': max([e['score'] for e in emotion_data['all_emotions']]),
        'topics': topics,
        'raw_emotions': emotion_data['all_emotions'],
        'context': {
            'embedding': text_processor.encode_text(text).tolist()
        }
    }
    
    # Cache result
    cache.set(cache_key, json.dumps(result), timeout=3600)
    return result


def predict_mindstate(diary_text: str, recent_activities: List[Dict]) -> Dict:
    """Predict mind state from diary text and activities"""
    predictor = get_mindstate_predictor()
    return predictor.predict_mind_state(diary_text, recent_activities)

def find_similar_entries(query_text: str, entry_embeddings: List[Dict]) -> List[Dict]:
    """Find diary entries similar to query text"""
    text_processor = get_text_processor()
    query_embedding = text_processor.encode_text(query_text)
    
    similarities = []
    for entry in entry_embeddings:
        similarity = text_processor.get_text_similarity(
            query_text, 
            entry.get('text', '')
        )
        similarities.append({
            'entry_id': entry['id'],
            'similarity': similarity
        })
    
    # Sort by similarity
    return sorted(similarities, key=lambda x: x['similarity'], reverse=True)

def transcribe_audio(s3_key: str) -> str:
    """Transcribe audio using speech recognition"""
    # This would use a proper speech recognition model in production
    # For now return a placeholder
    return "(Transcribed text would appear here)"



from django.core.cache import cache

def cache_user_diary_embedding(user, entry_id, embedding):
    """
    Store diary embeddings per user for AI chat memory.
    Structure:
    cache["user_diary_embeddings:{user_id}"] = [
        {"entry_id": id, "embedding": embedding, "text": text}, ...
    ]
    """
    cache_key = f"user_diary_embeddings:{user.id}"
    user_entries = cache.get(cache_key, [])
    user_entries.append({"entry_id": entry_id, "embedding": embedding})
    # Keep last N entries (e.g., 100)
    user_entries = user_entries[-100:]
    cache.set(cache_key, user_entries, timeout=24*3600)  # cache 1 day
