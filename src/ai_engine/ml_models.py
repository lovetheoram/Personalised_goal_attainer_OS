# from transformers import pipeline
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.ensemble import RandomForestClassifier
# from sentence_transformers import SentenceTransformer

# class EmotionAnalyzer:
#     """
#     Handles emotion detection and sentiment analysis in text
#     """
#     def __init__(self):
#         self.sentiment_analyzer = pipeline("sentiment-analysis")
#         self.emotion_classifier = pipeline("text-classification", 
#                                         model="j-hartmann/emotion-english-distilroberta-base", 
#                                         return_all_scores=True)
        
#     def analyze_sentiment(self, text: str) -> dict:
#         """Analyze sentiment of text"""
#         result = self.sentiment_analyzer(text)[0]
#         return {
#             'label': result['label'],
#             'score': result['score']
#         }
    
#     def detect_emotion(self, text: str) -> dict:
#         """Detect emotions in text"""
#         emotions = self.emotion_classifier(text)[0]
#         return {
#             'primary_emotion': max(emotions, key=lambda x: x['score']),
#             'all_emotions': emotions
#         }

# class TextProcessor:
#     """
#     Handles text preprocessing and feature extraction
#     """
#     def __init__(self):
#         self.vectorizer = TfidfVectorizer(
#             max_features=5000,
#             stop_words='english',
#             ngram_range=(1, 2)
#         )
#         self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
#     def extract_features(self, texts: list[str]) -> np.ndarray:
#         """Extract TF-IDF features from texts"""
#         return self.vectorizer.fit_transform(texts)
    
#     def encode_text(self, text: str) -> np.ndarray:
#         """Get semantic embedding for text"""
#         return self.encoder.encode(text)
    
#     def get_text_similarity(self, text1: str, text2: str) -> float:
#         """Calculate semantic similarity between two texts"""
#         emb1 = self.encode_text(text1)
#         emb2 = self.encode_text(text2)
#         return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))


# class MindStatePredictor:
#     """
#     Predicts mind state metrics from diary entries and behavior
#     """
#     def __init__(self):
#         self.text_processor = TextProcessor()
#         self.emotion_analyzer = EmotionAnalyzer()
        
#     def predict_mind_state(self, diary_text: str, recent_activities: list[dict]) -> dict:
#         """
#         Predict mind state metrics from diary text and recent activities
#         """
#         # Analyze emotions in diary
#         emotion_data = self.emotion_analyzer.detect_emotion(diary_text)
#         sentiment_data = self.emotion_analyzer.analyze_sentiment(diary_text)
        
#         # Calculate base metrics
#         focus_base = 0.5
#         energy_base = 0.5
#         motivation_base = 0.5
        
#         # Adjust based on emotion
#         emotion_adjustments = {
#             'joy': {'focus': 0.1, 'energy': 0.2, 'motivation': 0.2},
#             'sadness': {'focus': -0.1, 'energy': -0.2, 'motivation': -0.1},
#             'anger': {'focus': -0.2, 'energy': 0.1, 'motivation': -0.1},
#             'fear': {'focus': -0.1, 'energy': 0.1, 'motivation': -0.2},
#             'surprise': {'focus': -0.1, 'energy': 0.1, 'motivation': 0.0},
#         }
        
#         primary_emotion = emotion_data['primary_emotion']['label']
#         if primary_emotion in emotion_adjustments:
#             adj = emotion_adjustments[primary_emotion]
#             focus_base += adj['focus']
#             energy_base += adj['energy']
#             motivation_base += adj['motivation']
        
#         # Adjust based on sentiment
#         sentiment_score = sentiment_data['score']
#         if sentiment_data['label'] == 'POSITIVE':
#             motivation_base += 0.1 * sentiment_score
#         else:
#             motivation_base -= 0.1 * sentiment_score
        
#         # Adjust based on recent activities
#         # if recent_activities:
#         #     completion_rate = sum(1 for a in recent_activities if a.get('completed')) / len(recent_activities)
#         #     motivation_base += 0.1 * completion_rate
#         #     focus_base += 0.05 * completion_rate
        
#         # Ensure values are in [0,1] range
#         return {
#             'focus': max(0, min(1, focus_base)),
#             'energy': max(0, min(1, energy_base)),
#             'motivation': max(0, min(1, motivation_base)),
#             # context
#             # 'primary_emotion': primary_emotion,
#             'emotion_scores': emotion_data['all_emotions'],
#             'context': sentiment_data
#         }



import random
import numpy as np

class EmotionAnalyzer:
    """
    Dummy version of emotion + sentiment analyzer.
    Returns mock outputs for testing.
    """
    def __init__(self):
        pass

    def analyze_sentiment(self, text: str) -> dict:
        """Return random positive/negative sentiment"""
        label = random.choice(["POSITIVE", "NEGATIVE"])
        score = round(random.uniform(0.5, 0.99), 2)
        return {"label": label, "score": score}

    def detect_emotion(self, text: str) -> dict:
        """Return random emotion distribution"""
        emotions = ["joy", "sadness", "anger", "fear", "surprise"]
        scores = np.random.dirichlet(np.ones(len(emotions)), size=1)[0]  # random normalized probs
        emotion_scores = {e: round(float(s), 3) for e, s in zip(emotions, scores)}
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        return {
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores
        }


class TextProcessor:
    """
    Dummy text processing & feature extraction.
    Returns fake embeddings and similarity scores.
    """
    def __init__(self):
        pass

    def extract_features(self, texts: list[str]) -> np.ndarray:
        """Return random feature matrix"""
        return np.random.rand(len(texts), 10)

    def encode_text(self, text: str) -> np.ndarray:
        """Return fake embedding"""
        np.random.seed(len(text))
        return np.random.rand(10)

    def get_text_similarity(self, text1: str, text2: str) -> float:
        """Return random similarity score"""
        return round(random.uniform(0.2, 0.95), 3)


class MindStatePredictor:
    """
    Dummy mind state predictor for fast local testing.
    """
    def __init__(self):
        self.text_processor = TextProcessor()
        self.emotion_analyzer = EmotionAnalyzer()

        self.emotion_adjustments = {
            "joy": {"focus": 0.1, "energy": 0.2, "motivation": 0.2},
            "sadness": {"focus": -0.1, "energy": -0.2, "motivation": -0.1},
            "anger": {"focus": -0.2, "energy": 0.1, "motivation": -0.1},
            "fear": {"focus": -0.1, "energy": 0.1, "motivation": -0.2},
            "surprise": {"focus": -0.1, "energy": 0.1, "motivation": 0.0},
        }

    def predict_mind_state(self, diary_text: str, recent_activities: list[dict] | None = None) -> dict:
        """
        Return mock mind state predictions.
        """
        emotion_data = self.emotion_analyzer.detect_emotion(diary_text)
        sentiment_data = self.emotion_analyzer.analyze_sentiment(diary_text)

        focus, energy, motivation = 0.5, 0.5, 0.5

        primary_emotion = emotion_data["primary_emotion"]
        if primary_emotion in self.emotion_adjustments:
            adj = self.emotion_adjustments[primary_emotion]
            focus += adj["focus"]
            energy += adj["energy"]
            motivation += adj["motivation"]

        sentiment_score = sentiment_data["score"]
        if sentiment_data["label"] == "POSITIVE":
            motivation += 0.1 * sentiment_score
        else:
            motivation -= 0.1 * sentiment_score

        if recent_activities:
            completion_rate = sum(a.get("completed", False) for a in recent_activities) / len(recent_activities)
            focus += 0.05 * completion_rate
            motivation += 0.1 * completion_rate

        def clip(x): return max(0, min(1, round(x, 3)))

        return {
            "focus": clip(focus),
            "energy": clip(energy),
            "motivation": clip(motivation),
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_data["emotion_scores"],
            "sentiment": sentiment_data
        }


# Example test
if __name__ == "__main__":
    predictor = MindStatePredictor()
    sample_text = "I felt productive today but a bit anxious about tomorrow."
    result = predictor.predict_mind_state(sample_text, [{"completed": True}, {"completed": False}])
    print(result)
