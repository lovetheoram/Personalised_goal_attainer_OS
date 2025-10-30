from django.db import models
from django.conf import settings

class UserDailyStats(models.Model):
    """
    Aggregates daily user statistics for analytics.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    
    # Mind state metrics
    avg_focus = models.FloatField(default=0.0)
    avg_energy = models.FloatField(default=0.0)
    avg_motivation = models.FloatField(default=0.0)
    dominant_emotion = models.CharField(max_length=50, null=True, blank=True)
    
    # Goal metrics
    active_goals = models.IntegerField(default=0)
    completed_goals = models.IntegerField(default=0)
    
    # Diary metrics
    diary_entries = models.IntegerField(default=0)
    sentiment_score = models.FloatField(null=True, blank=True)
    
    # Progress metrics
    points_earned = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

class UserTrend(models.Model):
    """
    Tracks long-term trends and patterns.
    """
    TREND_TYPES = [
        ('focus', 'Focus'),
        ('motivation', 'Motivation'),
        ('productivity', 'Productivity'),
        ('mood', 'Mood'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trend_type = models.CharField(max_length=20, choices=TREND_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    trend_value = models.FloatField()  # normalized -1 to 1
    confidence = models.FloatField()   # 0 to 1
    insights = models.JSONField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'trend_type', 'start_date']),
        ]
