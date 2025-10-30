from django.db import models
from django.conf import settings
import uuid
from planner.models import Goal, MindState
from syllabus.models import Concept
# ------------------------
# TargetPlan: daily/weekly plan for user
# ------------------------
class TargetPlan(models.Model):
    PLAN_TYPES = [('daily','Daily'),('weekly','Weekly'),('restart','Restart'),('challenge','Challenge')]
    STATUS_CHOICES = [('active','Active'),('executing','Executing'),('completed','Completed'),('cancelled','Cancelled')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.ForeignKey(Goal, null=True, blank=True, on_delete=models.SET_NULL)
    plan_date = models.DateField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='daily')
    budget_minutes = models.IntegerField(default=180)
    source = models.CharField(max_length=30, default='auto')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    weights = models.JSONField(null=True, blank=True)  # adaptive weights for task allocation
    mindstate = models.ForeignKey(MindState, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('user','plan_date','plan_type'),)
        ordering = ['plan_date']

# ------------------------
# PlanTask: atomic task in a plan
# ------------------------
class PlanTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(TargetPlan, on_delete=models.CASCADE, related_name='tasks')
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='plan_tasks')
    allocated_minutes = models.IntegerField()
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    progress_snapshot = models.JSONField(null=True, blank=True)  # optional
    decision_log = models.ForeignKey('planner.DecisionLog', null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

