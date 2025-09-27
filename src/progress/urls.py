# progress/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProgressViewSet

router = DefaultRouter()
router.register(r'user_progress', UserProgressViewSet, basename='user-progress')


urlpatterns =router.urls
