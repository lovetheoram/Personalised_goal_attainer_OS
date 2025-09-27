# app: syllabus/serializers.py
from rest_framework import serializers
from .models import Exam, Subject, Topic, Subtopic, Concept

# ------------------------
# Concept Serializer
# ------------------------
class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concept
        fields = ('id', 'subtopic', 'name',  'description', 'estimated_time', 'weightage',  'resources', 'created_at', 'updated_at')

# ------------------------
# Subtopic Serializer
# ------------------------
class SubtopicSerializer(serializers.ModelSerializer):
    concepts = ConceptSerializer(many=True, read_only=True)

    class Meta:
        model = Subtopic
        fields = ('id', 'topic', 'name', 'weightage', 'concepts', 'created_at', 'updated_at')

# ------------------------
# Topic Serializer
# ------------------------
class TopicSerializer(serializers.ModelSerializer):
    subtopics = SubtopicSerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ('id', 'subject', 'name', 'weightage', 'subtopics', 'created_at', 'updated_at')

# ------------------------
# Subject Serializer
# ------------------------
class SubjectSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Subject
        fields = ('id', 'exam', 'name', 'weightage', 'topics', 'created_at', 'updated_at')

# ------------------------
# Exam Serializer
# ------------------------
class ExamSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ('id', 'name',  'start_date', 'end_date', 'subjects', 'created_at', 'updated_at')
