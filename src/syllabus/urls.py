# app: syllabus/urls.py
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, SubjectViewSet, TopicViewSet, SubtopicViewSet, ConceptViewSet

router = DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'subtopics', SubtopicViewSet)
router.register(r'concepts', ConceptViewSet)

urlpatterns = router.urls
