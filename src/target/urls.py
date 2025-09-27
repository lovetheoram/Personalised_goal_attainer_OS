# progress/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DailyTargetViewSet

router = DefaultRouter()
router.register(r'daily_targets', DailyTargetViewSet, basename='daily-target')


urlpatterns =router.urls
