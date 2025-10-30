from rest_framework.routers import DefaultRouter
from .views import DiaryEntryViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'entries', DiaryEntryViewSet, basename='diaryentry')

urlpatterns = [
    path('', include(router.urls)),
]
