
from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('chatbot/',include('chatbot.urls')),
    path('syllabus/',include('syllabus.urls')),
    path('target/',include('target.urls')),
    path('quiz/',include('quiz.urls')),
    path('progress/',include('progress.urls')),
    path('leaderboard/',include('leaderboard.urls')),
    path('achievements/',include('achievement.urls')),
    path('auth/',include('authentication.urls')),
    path('planner/',include('planner.urls')),
    path('diary/',include('diary.urls')),
    path('notifications/',include('notifications.urls')),
    path('api_gateway/',include('api_gateway.urls')),
    path('analytics/',include('analytics.urls')),
    path('ai_engine/',include('ai_engine.urls')),
    
]
