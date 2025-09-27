# app: syllabus/views.py
from rest_framework import viewsets, permissions
from .models import Exam, Subject, Topic, Subtopic, Concept
from .serializers import ExamSerializer, SubjectSerializer, TopicSerializer, SubtopicSerializer, ConceptSerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.prefetch_related('subjects__topics__subtopics__concepts')
    serializer_class = ExamSerializer
    # permission_classes = [permissions.IsAuthenticated]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.prefetch_related('topics__subtopics__concepts')
    serializer_class = SubjectSerializer
    # permission_classes = [permissions.IsAuthenticated]

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.prefetch_related('subtopics__concepts')
    serializer_class = TopicSerializer
    # permission_classes = [permissions.IsAuthenticated]

class SubtopicViewSet(viewsets.ModelViewSet):
    queryset = Subtopic.objects.prefetch_related('concepts')
    serializer_class = SubtopicSerializer
    # permission_classes = [permissions.IsAuthenticated]

class ConceptViewSet(viewsets.ModelViewSet):
    queryset = Concept.objects.all()
    serializer_class = ConceptSerializer
    # permission_classes = [permissions.IsAuthenticated]
