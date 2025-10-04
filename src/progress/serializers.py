from rest_framework import serializers
from .models import UserConceptProgress

class UserProgressSerializer(serializers.ModelSerializer):
    concept_name = serializers.CharField(source='concept.name', read_only=True)
    subtopic_name = serializers.CharField(source='concept.subtopic.name', read_only=True)
    topic_name = serializers.CharField(source='concept.subtopic.topic.name', read_only=True)
    subject_name = serializers.CharField(source='concept.subtopic.topic.subject.name', read_only=True)

    class Meta:
        model = UserConceptProgress
        fields = [
            'id', 'concept', 'concept_name',
            'subtopic_name', 'topic_name', 'subject_name',
            'mastery', 'ease_factor', 'interval_days', 'next_review',
            'last_score', 'last_studied', 'revision_count', 'carryover_flag','points','streak'
        ]

class UpdateProgressSerializer(serializers.Serializer):
    concept_id = serializers.IntegerField()
    score = serializers.FloatField(min_value=0.0, max_value=1.0, required=False)
    understood = serializers.ChoiceField(choices=["yes", "partial", "no"], required=False)
