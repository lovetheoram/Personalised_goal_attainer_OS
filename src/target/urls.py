# target/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TargetPlanViewSet, PlanTaskViewSet

router = DefaultRouter()
router.register(r'plans', TargetPlanViewSet, basename='targetplan')
router.register(r'tasks', PlanTaskViewSet, basename='plantask')

urlpatterns = [
    path('', include(router.urls)),
]
