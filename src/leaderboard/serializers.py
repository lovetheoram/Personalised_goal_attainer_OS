from rest_framework import serializers
from .models import LeaderboardEntry

class LeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderboardEntry
        fields = ["user", "points", "streak", "rank"]  # Fixed typo in 'rank'
