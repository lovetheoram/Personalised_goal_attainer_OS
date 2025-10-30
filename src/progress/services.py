import datetime
from django.utils.timezone import now
from django.db.models import Avg, Sum,Count
from syllabus.models import Concept
from .models import UserConceptProgress, UserProgressHistory
from achievement.services import check_achievements
from leaderboard.services import update_leaderboard


def update_progress(user, concept, score: float = None, understood: str = None):
    progress, _ = UserConceptProgress.objects.get_or_create(user=user, concept=concept)
    today = now().date()

    progress.last_studied = now()
    if score is not None:
        progress.last_score = score

    # --- Adaptive logic ---
    mastery_boost = 0.0
    ease_boost = 0.0

    if score is not None:
        if score >= 0.85:
            mastery_boost += 0.12
            ease_boost += 0.08
        elif 0.6 <= score < 0.85:
            mastery_boost += 0.05
            ease_boost += 0.02
        else:
            mastery_boost -= 0.03
            ease_boost -= 0.05

    if understood == "yes":
        mastery_boost += 0.06
        ease_boost += 0.05
    elif understood == "partial":
        mastery_boost += 0.02
    elif understood == "no":
        mastery_boost -= 0.02

    # Apply updates
    progress.mastery = min(1.0, max(0.0, progress.mastery + mastery_boost))
    progress.ease_factor = max(1.2, progress.ease_factor + ease_boost)

    # Interval scheduling
    if progress.mastery > 0.8:
        progress.interval_days = max(1, round(progress.interval_days * progress.ease_factor))
    elif 0.5 <= progress.mastery <= 0.8:
        progress.interval_days = 1
    else:
        progress.interval_days = 0

    progress.next_review = today + datetime.timedelta(days=progress.interval_days)
    progress.carryover_flag = progress.mastery < 0.5
    progress.revision_count += 1

    # ✅ Points
    points_earned = int(mastery_boost * 100 + (score or 0) * 50)
    progress.points += points_earned

    # ✅ Status
    if progress.mastery >= 0.9:
        progress.status = 'mastered'
    elif progress.mastery >= 0.5:
        progress.status = 'review'
    else:
        progress.status = 'learning'

    # ✅ Streak tracking
    if progress.last_studied and (today - progress.last_studied.date()).days == 1:
        progress.streak += 1
    elif not progress.last_studied or (today - progress.last_studied.date()).days > 1:
        progress.streak = 1

    progress.save()

    # Record history
    UserProgressHistory.objects.create(
        progress=progress,
        mastery=progress.mastery,
        ease_factor=progress.ease_factor,
        points=progress.points
    )

    # Triggers
    check_achievements(user)
    update_leaderboard(user)

    return progress


def update_progress_bulk(user, results):
    updated = []
    for r in results:
        try:
            concept = Concept.objects.get(id=r['concept_id'])
        except Concept.DoesNotExist:
            continue
        score = r.get('score')
        understood = r.get('understood')
        ucp = update_progress(user, concept, score, understood)
        updated.append(ucp)
    return updated


def get_user_progress(user):
    return UserConceptProgress.objects.filter(user=user).order_by('subject_name', 'topic_name')


def get_weak_concepts(user):
    return UserConceptProgress.objects.filter(user=user, mastery__lt=0.5)


def get_due_reviews(user):
    today = now().date()
    return UserConceptProgress.objects.filter(user=user, next_review__lte=today)


def get_user_analytics(user):
    stats = UserConceptProgress.objects.filter(user=user).aggregate(
        total_points=Sum('points'),
        avg_mastery=Avg('mastery'),
        total_concepts=Count('id'),
    )
    return stats
