from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('achievement', 'Achievement'),
        ('goal_reminder', 'Goal Reminder'),
        ('goal_milestone', 'Goal Milestone'),
        ('mindstate_alert', 'Mind State Alert'),
        ('streak_alert', 'Streak Alert'),
        ('diary_reminder', 'Diary Reminder'),
        ('motivation_boost', 'Motivation Boost'),
        ('progress_update', 'Progress Update'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    sent = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    send_at = models.DateTimeField(null=True, blank=True)
    context_data = models.JSONField(null=True, blank=True)  # Store related IDs or metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'sent', 'send_at']),
            models.Index(fields=['user', 'notification_type']),
        ]

class NotificationPreference(models.Model):
    """
    Stores user preferences for different notification types
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=Notification.NOTIFICATION_TYPES)
    enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'notification_type')
