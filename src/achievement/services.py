from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum
from .models import Achievement, UserAchievement
from progress.models import UserConceptProgress
from target.models import DailyTarget

def check_achievements(user):
    """
    Check all achievements for the user and award new ones.
    Returns a list of newly unlocked achievement names.
    """
    today = now().date()
    achievements = Achievement.objects.all()
    user_progress = UserConceptProgress.objects.filter(user=user)
    today_targets = DailyTarget.objects.filter(user=user, study_date=today)

    unlocked = []

    for ach in achievements:
        # Skip already unlocked achievements
        if UserAchievement.objects.filter(user=user, achievement=ach).exists():
            continue

        earned = False

        # 🎯 Streak logic
        if ach.criteria_type == "streak":
            days_required = ach.criteria_value
            streak_count = 0
            for i in range(days_required):
                day = today - timedelta(days=i)
                if user_progress.filter(last_studied__date=day).exists():
                    streak_count += 1
                else:
                    break  # streak broken
            if streak_count >= days_required:
                earned = True

        # 📈 Mastery logic
        elif ach.criteria_type == "mastery":
            threshold = ach.criteria_value / 100.0
            if user_progress.filter(mastery__gte=threshold).exists():
                earned = True

        # ✅ Daily Target Completion
        elif ach.criteria_type == "daily_target":
            if today_targets.exists() and all(t.status == "completed" for t in today_targets):
                earned = True

        # 💪 Weak Area Improvement
        elif ach.criteria_type == "weak_area":
            weak_improved_count = user_progress.filter(
                mastery__gte=0.5, revision_count__gte=ach.criteria_value
            ).count()
            if weak_improved_count >= 1:
                earned = True

        # ⭐ Points milestone
        elif ach.criteria_type == "points":
            total_points = user_progress.aggregate(total=Sum("points"))["total"] or 0
            if total_points >= ach.criteria_value:
                earned = True

        # Save achievement if unlocked
        if earned:
            ua, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=ach,
                defaults={"earned_at": now()},
            )
            if created:
                unlocked.append(ach.name)

    return unlocked
