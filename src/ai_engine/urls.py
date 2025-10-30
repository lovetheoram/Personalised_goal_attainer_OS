from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health, name='ai-health'),
    path('analyze/text/', views.analyze_text, name='analyze-text'),
    path('analyze/goal/', views.analyze_goal_text, name='analyze-goal'),
    path('predict/mindstate/', views.predict_user_mindstate, name='predict-mindstate'),
    path('find/similar-entries/', views.find_similar_diary_entries, name='find-similar-entries'),
]
