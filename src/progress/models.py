from django.db import models
from django.conf import settings
from syllabus.models import Concept,Subtopic

# -----------------------------
# User Tracking Models
# -----------------------------
class UserConceptProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    mastery = models.FloatField(default=0.0)      # 0-1
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    next_review = models.DateField(null=True, blank=True)
    last_score = models.FloatField(null=True, blank=True)
    last_studied = models.DateTimeField(null=True, blank=True)
    revision_count = models.IntegerField(default=0)
    carryover_flag = models.BooleanField(default=False)