from django.db import models
from django.conf import settings

class Achievement(models.Model):
    """
    Defines an achievement/badge type.
    """
    CRITERIA_CHOICES = [
        ("streak", "Streak"),
        ("mastery", "Mastery"),
        ("daily_target", "Daily Target Completion"),
        ("weak_area", "Weak Area Improvement"),
        ("points", "Points"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=255, null=True, blank=True)  # URL/path to badge icon
    criteria_type = models.CharField(max_length=50, choices=CRITERIA_CHOICES)
    criteria_value = models.IntegerField()  # e.g., days for streak, % for mastery, points, etc.

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """
    Tracks which user has earned which achievements.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")
