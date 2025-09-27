# import datetime
# from django.utils.timezone import now
# from .models import UserProgress, DailyTarget
# from syllabus.models import Concept

# def build_daily_targets(user, study_date, daily_budget_minutes=180):
#     # Clear old targets for this date
#     DailyTarget.objects.filter(user=user, study_date=study_date).delete()

#     today = study_date
#     progresses = UserProgress.objects.filter(user=user).select_related("concept")

#     scored_concepts = []
#     for p in progresses:
#         c = p.concept
#         days_since = (
#             (today - p.last_studied.date()).days if p.last_studied else 999
#         )
#         r = 1 + days_since / 7.0
#         base = c.weightage * (1 - p.mastery) * c.difficulty * r
#         carryover_bonus = 5.0 if p.carryover_flag else 0.0
#         decay_bonus = 0.01 * days_since
#         priority = base + carryover_bonus + decay_bonus
#         efficiency = priority / (c.estimated_time or 1)

#         scored_concepts.append(
#             dict(progress=p, concept=c, priority=priority, efficiency=efficiency)
#         )

#     # Force carryovers first
#     carryovers = [x for x in scored_concepts if x["progress"].carryover_flag]
#     carryovers.sort(key=lambda x: -x["priority"])

#     remaining_budget = daily_budget_minutes
#     selected = []

#     for item in carryovers:
#         if remaining_budget <= 0:
#             break
#         t = min(item["concept"].estimated_time, remaining_budget)
#         selected.append((item["concept"], t))
#         remaining_budget -= t

#     # Then pick by efficiency
#     non_carryovers = [x for x in scored_concepts if not x["progress"].carryover_flag]
#     non_carryovers.sort(key=lambda x: -x["efficiency"])

#     for item in non_carryovers:
#         if remaining_budget <= 0:
#             break
#         est = item["concept"].estimated_time
#         if est <= remaining_budget:
#             selected.append((item["concept"], est))
#             remaining_budget -= est

#     # Save into DB
#     for concept, allocated_time in selected:
#         DailyTarget.objects.create(
#             user=user,
#             study_date=study_date,
#             concept=concept,
#             allocated_time=allocated_time,
#         )

#     return selected






# def update_progress(user, concept, score: float = None, understood: str = None):
#     """
#     Update mastery using hybrid approach:
#     - Quiz score (objective)
#     - Self-assessment understood (subjective)
#     """

#     progress, _ = UserProgress.objects.get_or_create(user=user, concept=concept)

#     today = now().date()
#     progress.last_studied = now()
#     if score is not None:
#         progress.last_score = score

#     # --- Hybrid decision ---
#     mastery_boost = 0.0
#     ease_boost = 0.0

#     # 🎯 Objective: quiz score
#     if score is not None:
#         if score >= 0.85:  # strong performance
#             mastery_boost += 0.12
#             ease_boost += 0.08
#         elif 0.6 <= score < 0.85:  # moderate performance
#             mastery_boost += 0.05
#             ease_boost += 0.02
#         else:  # weak performance
#             mastery_boost -= 0.03
#             ease_boost -= 0.05

#     # 🧠 Subjective: user confidence
#     if understood == "yes":
#         mastery_boost += 0.06
#         ease_boost += 0.05
#     elif understood == "partial":
#         mastery_boost += 0.02
#     elif understood == "no":
#         mastery_boost -= 0.02

#     # --- Apply boosts ---
#     progress.mastery = min(1.0, max(0.0, progress.mastery + mastery_boost))
#     progress.ease_factor = max(1.2, progress.ease_factor + ease_boost)

#     # Interval scheduling (like SM-2 algorithm style)
#     if progress.mastery > 0.8:
#         progress.interval_days = max(1, round(progress.interval_days * progress.ease_factor))
#     elif 0.5 <= progress.mastery <= 0.8:
#         progress.interval_days = 1
#     else:
#         progress.interval_days = 0

#     progress.next_review = today + datetime.timedelta(days=progress.interval_days)
#     progress.carryover_flag = progress.mastery < 0.5

#     progress.revision_count += 1
#     progress.save()
#     return progress




# from datetime import timedelta
# from django.utils.timezone import now
# from .models import Concept, DailyTarget, UserConceptProgress, WeakArea, ManualFocus

# # -----------------------------
# # Helpers
# # -----------------------------
# def pick_concepts(concepts, available_minutes):
#     selected, used_time = [], 0
#     for c in concepts:
#         if used_time + c.estimated_time <= available_minutes:
#             selected.append(c)
#             used_time += c.estimated_time
#         else:
#             break
#     return selected


# def get_carryover(user):
#     return UserConceptProgress.objects.filter(user=user, carryover_flag=True).order_by('mastery')


# def get_weak(user):
#     weak_ids = WeakArea.objects.filter(user=user, active=True).values_list("concept_id", flat=True)
#     return Concept.objects.filter(id__in=weak_ids).order_by('weightage')


# def get_new(user):
#     studied_ids = UserConceptProgress.objects.filter(user=user).values_list("concept_id", flat=True)
#     return Concept.objects.exclude(id__in=studied_ids).order_by('weightage')


# def get_revision(user):
#     return UserConceptProgress.objects.filter(user=user, mastery__lt=1.0).order_by('next_review')


# def get_forced_subtopic(user, available_minutes):
#     focus = ManualFocus.objects.filter(user=user, active=True).first()
#     if not focus:
#         return []
#     concepts = Concept.objects.filter(subtopic=focus.subtopic).order_by('id')
#     return pick_concepts(concepts, available_minutes)


# # -----------------------------
# # Dynamic Weights
# # -----------------------------
# def compute_dynamic_weights(user, exam_date, total_days=180):
#     today = now().date()
#     days_left = max(1, (exam_date - today).days)
#     T = min(1.0, days_left / total_days)
#     total_concepts = Concept.objects.count()
#     studied_concepts = UserConceptProgress.objects.filter(user=user).count()
#     S = studied_concepts / total_concepts if total_concepts else 0
#     weak_count = WeakArea.objects.filter(user=user).count()
#     W = weak_count / studied_concepts if studied_concepts else 0

#     new_w = (1 - S) * 0.5 + T * 0.2
#     weak_w = 0.2 + (W * 0.5)
#     carry_w = 0.2
#     rev_w = S * 0.3 + (1 - T) * 0.3
#     total = new_w + weak_w + carry_w + rev_w

#     return {
#         "new": new_w / total,
#         "weak": weak_w / total,
#         "carry": carry_w / total,
#         "rev": rev_w / total
#     }


# def allocate_time(total_minutes, weights):
#     total_weight = sum(weights.values())
#     return {k: int(total_minutes * (v / total_weight)) for k, v in weights.items()}


# # -----------------------------
# # Main Builder
# # -----------------------------
# def build_daily_targets(user, study_date, daily_budget_minutes=180, exam_date=None):
#     DailyTarget.objects.filter(user=user, study_date=study_date).delete()

#     # Forced subtopic first
#     forced = get_forced_subtopic(user, daily_budget_minutes)
#     used_time = sum(c.estimated_time for c in forced)
#     remaining = daily_budget_minutes - used_time

#     # Dynamic weights
#     weights = compute_dynamic_weights(user, exam_date) if exam_date else {"new":0.4,"weak":0.3,"carry":0.2,"rev":0.1}
#     time_alloc = allocate_time(remaining, weights)

#     # Pick concepts
#     new_c = pick_concepts(get_new(user), time_alloc["new"])
#     weak_c = pick_concepts(get_weak(user), time_alloc["weak"])
#     carry_c = pick_concepts(get_carryover(user), time_alloc["carry"])
#     rev_c = pick_concepts([ucp.concept for ucp in get_revision(user)], time_alloc["rev"])

#     all_targets = forced + new_c + weak_c + carry_c + rev_c

#     # Fail-safe: at least 1 new concept/day
#     if not new_c and get_new(user).exists():
#         all_targets.append(get_new(user).first())

#     # Save to DB
#     for concept in all_targets:
#         DailyTarget.objects.create(
#             user=user,
#             concept=concept,
#             study_date=study_date,
#             allocated_time=concept.estimated_time,
#             status="pending"
#         )

#     return all_targets





from datetime import timedelta
from django.utils.timezone import now
from .models import Concept, DailyTarget, ManualFocus
from progress.models import UserConceptProgress
# -----------------------------
# Helpers
# -----------------------------
def pick_concepts(concepts, available_minutes):
    """Pick concepts until the available time is exhausted."""
    selected, used_time = [], 0
    for c in concepts:
        if used_time + c.estimated_time <= available_minutes:
            selected.append(c)
            used_time += c.estimated_time
        else:
            break
    return selected


def get_carryover(user):
    """Return concepts that need carryover (mastery < 0.5)."""
    return [ucp.concept for ucp in UserConceptProgress.objects.filter(user=user, carryover_flag=True).order_by('mastery')]


def get_weak(user):
    """Return weak concepts dynamically (mastery < 0.5)."""
    return Concept.objects.filter(
        id__in=UserConceptProgress.objects.filter(user=user, mastery__lt=0.5).values_list('concept_id', flat=True)
    ).order_by('weightage')


def get_new(user):
    """Return concepts not yet studied by the user."""
    studied_ids = UserConceptProgress.objects.filter(user=user).values_list("concept_id", flat=True)
    return Concept.objects.exclude(id__in=studied_ids).order_by('weightage')


def get_revision(user):
    """Return concepts needing revision (mastery < 1.0)."""
    return [ucp.concept for ucp in UserConceptProgress.objects.filter(user=user, mastery__lt=1.0).order_by('next_review')]


def get_forced_subtopic(user, available_minutes):
    """Return concepts from the user-selected forced subtopic."""
    focus = ManualFocus.objects.filter(user=user, active=True).first()
    if not focus:
        return []
    concepts = Concept.objects.filter(subtopic=focus.subtopic).order_by('id')
    return pick_concepts(concepts, available_minutes)


# -----------------------------
# Dynamic Weights
# -----------------------------
def compute_dynamic_weights(user, exam_date=None, total_days=180):
    """Compute dynamic weights for new, weak, carryover, and revision concepts."""
    today = now().date()
    days_left = max(1, (exam_date - today).days) if exam_date else total_days
    T = min(1.0, days_left / total_days)

    total_concepts = Concept.objects.count()
    studied_concepts = UserConceptProgress.objects.filter(user=user).count()
    S = studied_concepts / total_concepts if total_concepts else 0

    weak_count = UserConceptProgress.objects.filter(user=user, mastery__lt=0.5).count()
    W = weak_count / studied_concepts if studied_concepts else 0

    # Base weights
    new_w = (1 - S) * 0.5 + T * 0.2
    weak_w = 0.2 + (W * 0.5)
    carry_w = 0.2
    rev_w = S * 0.3 + (1 - T) * 0.3

    total = new_w + weak_w + carry_w + rev_w
    return {
        "new": new_w / total,
        "weak": weak_w / total,
        "carry": carry_w / total,
        "rev": rev_w / total
    }


def allocate_time(total_minutes, weights):
    """Allocate minutes proportionally based on weights."""
    total_weight = sum(weights.values())
    return {k: int(total_minutes * (v / total_weight)) for k, v in weights.items()}


# -----------------------------
# Main Builder
# -----------------------------
def build_daily_targets(user, study_date, daily_budget_minutes=180, exam_date=None):
    """Generate and save daily targets for a user."""
    DailyTarget.objects.filter(user=user, study_date=study_date).delete()

    # 1️⃣ Forced subtopic first
    forced = get_forced_subtopic(user, daily_budget_minutes)
    used_time = sum(c.estimated_time for c in forced)
    remaining = max(daily_budget_minutes - used_time, 0)

    # 2️⃣ Compute dynamic weights
    weights = compute_dynamic_weights(user, exam_date) if exam_date else {"new":0.4,"weak":0.3,"carry":0.2,"rev":0.1}
    time_alloc = allocate_time(remaining, weights)

    # 3️⃣ Pick concepts for each category
    new_c = pick_concepts(get_new(user), time_alloc["new"])
    weak_c = pick_concepts(get_weak(user), time_alloc["weak"])
    carry_c = pick_concepts(get_carryover(user), time_alloc["carry"])
    rev_c = pick_concepts(get_revision(user), time_alloc["rev"])

    all_targets = forced + new_c + weak_c + carry_c + rev_c

    # 4️⃣ Fail-safe: ensure at least 1 new concept/day
    if not new_c and get_new(user).exists():
        all_targets.append(get_new(user).first())

    # 5️⃣ Save to DB
    for concept in all_targets:
        DailyTarget.objects.create(
            user=user,
            concept=concept,
            study_date=study_date,
            allocated_time=concept.estimated_time,
            status="pending"
        )

    return all_targets
