from rest_framework import serializers
from .models import MindState, Goal, DecisionLog

class MindStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MindState
        fields = '__all__'

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = '__all__'

class DecisionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionLog
        fields = '__all__'
