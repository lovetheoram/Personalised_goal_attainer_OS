from django.db import models
from django.conf import settings
from syllabus.models import Concept

class UserConceptProgress(models.Model):
    STATUS_CHOICES = [
        ('learning', 'Learning'),
        ('review', 'Review'),
        ('mastered', 'Mastered')
    ]
    
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
    points = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='learning')

    class Meta:
        unique_together = (('user', 'concept'),)


class UserProgressHistory(models.Model):
    progress = models.ForeignKey(UserConceptProgress, on_delete=models.CASCADE, related_name='history')
    mastery = models.FloatField()
    ease_factor = models.FloatField()
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
