import datetime
from django.utils.timezone import now
from .models import UserConceptProgress, Concept

def update_progress(user, concept, score: float = None, understood: str = None):
    """
    Update mastery using hybrid approach:
    - Objective: quiz score
    - Subjective: user self-assessment
    """
    progress, _ = UserConceptProgress.objects.get_or_create(user=user, concept=concept)
    today = now().date()
    progress.last_studied = now()

    if score is not None:
        progress.last_score = score

    # --- Hybrid calculation ---
    mastery_boost = 0.0
    ease_boost = 0.0

    # Objective (quiz score)
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

    # Subjective (user confidence)
    if understood == "yes":
        mastery_boost += 0.06
        ease_boost += 0.05
    elif understood == "partial":
        mastery_boost += 0.02
    elif understood == "no":
        mastery_boost -= 0.02

    # Apply boosts
    progress.mastery = min(1.0, max(0.0, progress.mastery + mastery_boost))
    progress.ease_factor = max(1.2, progress.ease_factor + ease_boost)

    # Interval scheduling (SM-2 style)
    if progress.mastery > 0.8:
        progress.interval_days = max(1, round(progress.interval_days * progress.ease_factor))
    elif 0.5 <= progress.mastery <= 0.8:
        progress.interval_days = 1
    else:
        progress.interval_days = 0

    progress.next_review = today + datetime.timedelta(days=progress.interval_days)
    progress.carryover_flag = progress.mastery < 0.5
    progress.revision_count += 1

    progress.save()
    return progress


# -----------------------------
# Bulk update using hybrid logic
# -----------------------------
def update_progress_bulk(user, results):
    """
    results = [
        {"concept_id": 1, "score": 0.8, "understood": "yes"},
        ...
    ]
    """
    updated = []
    for r in results:
        concept = Concept.objects.get(id=r['concept_id'])
        score = r.get('score')
        understood = r.get('understood')
        ucp = update_progress(user, concept, score, understood)
        updated.append(ucp)
    return updated


# -----------------------------
# Fetch all progress for a user
# -----------------------------
def get_user_progress(user):
    return UserConceptProgress.objects.filter(user=user)\
        .select_related('concept__subtopic__topic__subject')\
        .order_by(
            'concept__subtopic__topic__subject',
            'concept__subtopic__topic',
            'concept__subtopic',
            'concept'
        )


# -----------------------------
# Weak concepts dynamically (mastery < 0.5)
# -----------------------------
def get_weak_concepts(user):
    return UserConceptProgress.objects.filter(user=user, mastery__lt=0.5)
