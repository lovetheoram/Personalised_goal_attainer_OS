from django.db.models import Prefetch
from syllabus.models import Subject, Topic, Subtopic, Concept

# -----------------------------
# Subjects
# -----------------------------
def fetch_subjects():
    return list(Subject.objects.all().values("id", "name", "weightage"))

# -----------------------------
# Topics
# -----------------------------
def fetch_topics(subject_name: str):
    try:
        subject = Subject.objects.prefetch_related(
            Prefetch("topics", queryset=Topic.objects.all())
        ).get(name__iexact=subject_name)
        return list(subject.topics.all().values("id", "name", "weightage"))
    except Subject.DoesNotExist:
        return {"error": "Subject not found"}

# -----------------------------
# Subtopics
# -----------------------------
def fetch_subtopics(topic_name: str):
    try:
        topic = Topic.objects.prefetch_related(
            Prefetch("subtopics", queryset=Subtopic.objects.all())
        ).get(name__iexact=topic_name)
        return list(topic.subtopics.all().values("id", "name", "weightage"))
    except Topic.DoesNotExist:
        return {"error": "Topic not found"}

# -----------------------------
# Concepts
# -----------------------------
def fetch_concepts(subtopic_name: str):
    try:
        subtopic = Subtopic.objects.prefetch_related(
            Prefetch("concepts", queryset=Concept.objects.all())
        ).get(name__iexact=subtopic_name)
        return list(subtopic.concepts.all().values(
            "id", "name", "description", "weightage", "difficulty"
        ))
    except Subtopic.DoesNotExist:
        return {"error": "Subtopic not found"}

# -----------------------------
# Concept Detail
# -----------------------------
def fetch_concept_detail(concept_name: str):
    try:
        concept = Concept.objects.get(name__iexact=concept_name)
        return {
            "name": concept.name,
            "description": concept.description,
            "estimated_time": concept.estimated_time,
            "weightage": concept.weightage,
            "resources": concept.resources
        }
    except Concept.DoesNotExist:
        return {"error": "Concept not found"}
