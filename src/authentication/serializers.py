from rest_framework import serializers
from .models import User, Profile
from achievement.models import UserAchievement


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["dob", "bio", "avatar"]


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source="achievement.name", read_only=True)

    class Meta:
        model = UserAchievement
        fields = ["id", "achievement_name", "earned_at"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    achievements = UserAchievementSerializer(many=True, source="userachievement_set", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "exam_year", "profile", "achievements"]
