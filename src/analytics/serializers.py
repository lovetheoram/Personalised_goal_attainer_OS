# analytics/serializers.py
from rest_framework import serializers
from .models import UserDailyStats, UserTrend


class UserDailyStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDailyStats
        fields = [
            'user',
            'date',
            'avg_focus',
            'avg_energy',
            'avg_motivation',
            'dominant_emotion',
            'active_goals',
            'completed_goals',
            'diary_entries',
            'sentiment_score',
            'points_earned',
            'tasks_completed',
        ]
        read_only_fields = fields  # All fields are computed, read-only


class UserTrendSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTrend
        fields = [
            'user',
            'trend_type',
            'start_date',
            'end_date',
            'trend_value',
            'confidence',
            'insights',
        ]
        read_only_fields = fields  # Computed analytics, read-only
