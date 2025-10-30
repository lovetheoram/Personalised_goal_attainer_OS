from rest_framework.routers import DefaultRouter
from .views import UserProgressViewSet

router = DefaultRouter()
router.register(r'progress', UserProgressViewSet, basename='progress')

urlpatterns = router.urls
