import uuid
from django.db import models
from django.conf import settings

# ------------------------
# MindState: captures user emotion/focus/energy/motivation
# ------------------------
class MindState(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    focus = models.FloatField(default=0.5)
    energy = models.FloatField(default=0.5)
    motivation = models.FloatField(default=0.5)
    emotion = models.CharField(max_length=50, default='neutral')
    context = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user','date'),)
        ordering = ['-date']

# ------------------------
# Goal: long-term objective
# ------------------------
class Goal(models.Model):
    GOAL_TYPES = [('exam','Exam'), ('project','Project'), ('habit','Habit')]
    STATUS_CHOICES = [('active','Active'), ('completed','Completed'), ('on_hold','On Hold'), ('cancelled','Cancelled')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=GOAL_TYPES, default='habit')
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# ------------------------
# DecisionLog: tracks why plan/task was created/changed
# ------------------------
class DecisionLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    diary_entry_id = models.UUIDField(null=True, blank=True)
    plan_id = models.UUIDField(null=True, blank=True)  # can link to TargetPlan in target_generation
    mind_state = models.JSONField(null=True, blank=True)
    action = models.JSONField()  # e.g., {'type':'plan_generated','source':'clarity'}
    rationale = models.TextField(null=True, blank=True)
    model_version = models.CharField(max_length=50, default='clarity-rule-v0')
    created_at = models.DateTimeField(auto_now_add=True)
