from rest_framework import serializers
from .models import DailyTarget

class DailyTargetSerializer(serializers.ModelSerializer):
    concept_name = serializers.CharField(source="concept.name", read_only=True)
    topic_name = serializers.CharField(source="concept.topic.name", read_only=True)

    class Meta:
        model = DailyTarget
        fields = ["id", "study_date", "concept", "concept_name", "topic_name", "allocated_time"]




