# target/serializers.py
from rest_framework import serializers
from .models import TargetPlan, PlanTask
from planner.serializers import GoalSerializer, MindStateSerializer
from syllabus.serializers import ConceptSerializer  # you should have a serializer for Concept

class PlanTaskSerializer(serializers.ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = PlanTask
        fields = ['id', 'concept', 'allocated_minutes', 'scheduled_start', 'scheduled_end', 'progress_snapshot', 'decision_log']

class TargetPlanSerializer(serializers.ModelSerializer):
    tasks = PlanTaskSerializer(many=True, read_only=True)
    mindstate = MindStateSerializer(read_only=True)
    goal = GoalSerializer(read_only=True)

    class Meta:
        model = TargetPlan
        fields = ['id', 'plan_date', 'plan_type', 'budget_minutes', 'weights', 'tasks', 'mindstate', 'goal']
