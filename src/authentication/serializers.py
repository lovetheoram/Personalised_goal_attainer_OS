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
    profile = ProfileSerializer()
    achievements = UserAchievementSerializer(many=True, source="userachievement_set", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "exam_year", "profile", "achievements"]

    def update(self,instance,validated_data):
        profile_data=validated_data.pop("profile",None)
        instance=super().update(instance,validated_data)

        if profile_data is not None:
            profile=getattr(instance,"profile",None)
            for attr,value in profile_data.items():
                setattr(profile,attr,value)
            profile.save()
        return instance