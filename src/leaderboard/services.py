from .models import LeaderboardEntry
from progress.models import UserConceptProgress
from django.db import models
from django.utils import timezone  # Import timezone

def update_leaderboard(user):
    total_points = UserConceptProgress.objects.filter(user=user).aggregate(
        total=models.Sum('points')
    )['total'] or 0

    streak = UserConceptProgress.objects.filter(
        user=user, last_studied__date=timezone.now().date()  # Fixed date comparison
    ).count()  # can enhance for consecutive days

    entry, _ = LeaderboardEntry.objects.get_or_create(user=user)
    entry.points = total_points
    entry.streak = streak
    entry.save()

    # Update global rank
    all_entries = LeaderboardEntry.objects.all().order_by('-points')
    for i, e in enumerate(all_entries, start=1):
        e.rank = i
        e.save()
