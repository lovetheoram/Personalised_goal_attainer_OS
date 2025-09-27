from django.db import models
from django.conf import settings
from syllabus.models import Concept,Subtopic




class DailyTarget(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    study_date = models.DateField()
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    allocated_time = models.IntegerField()
    status = models.CharField(max_length=20, default="pending")  # pending/completed


class WeakArea(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class ManualFocus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
