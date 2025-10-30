from progress.models import UserConceptProgress


def get_user_progress(user) -> list[dict]:
    """Return all concepts with user's progress details."""
    progress_qs = UserConceptProgress.objects.filter(user=user).select_related('concept')
    return [
        {
            "concept_id": p.concept.id,
            "concept_name": p.concept.name,
            "mastery": p.mastery,
            "last_studied": p.last_studied,
            "last_score": p.last_score,
        }
        for p in progress_qs
    ]
