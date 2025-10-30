from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MindStateViewSet, GoalViewSet, DecisionLogViewSet

router = DefaultRouter()
router.register(r'mindstates', MindStateViewSet, basename='mindstate')
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'decisions', DecisionLogViewSet, basename='decisionlog')

urlpatterns = [
    path('', include(router.urls)),
]
