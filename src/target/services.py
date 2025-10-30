from datetime import date, timedelta
from django.db import transaction
from .models import TargetPlan, PlanTask, Goal
from progress.models import UserConceptProgress
from syllabus.models import Concept
from planner.services import log_decision  # import from planner
from planner.models import MindState

# ------------------------
# Helper: pick concepts fitting in available minutes
# ------------------------
def pick_concepts(concepts_qs, available_minutes):
    selected = []
    used = 0
    for c in concepts_qs:
        est = getattr(c, 'estimated_time', 20) or 20
        if used + est <= available_minutes:
            selected.append(c)
            used += est
        else:
            break
    return selected

# ------------------------
# Concept selectors
# ------------------------
def get_carryover(user):
    return [ucp.concept for ucp in UserConceptProgress.objects.filter(user=user, carryover_flag=True).order_by('mastery')]

def get_weak(user):
    return Concept.objects.filter(
        id__in=UserConceptProgress.objects.filter(user=user, mastery__lt=0.5).values_list('concept_id', flat=True)
    ).order_by('weightage')

def get_new(user):
    studied_ids = UserConceptProgress.objects.filter(user=user).values_list('concept_id', flat=True)
    return Concept.objects.exclude(id__in=studied_ids).order_by('weightage')

def get_revision(user):
    return [ucp.concept for ucp in UserConceptProgress.objects.filter(user=user, mastery__lt=1.0).order_by('next_review')]

# ------------------------
# Adaptive weighting
# ------------------------
def compute_dynamic_weights(user, exam_date=None, total_days=180):
    today = date.today()
    days_left = max(1, (date.fromisoformat(exam_date) - today).days) if exam_date else total_days

    total_concepts = Concept.objects.count()
    studied_concepts = UserConceptProgress.objects.filter(user=user).count()
    S = studied_concepts / total_concepts if total_concepts else 0

    weak_count = UserConceptProgress.objects.filter(user=user, mastery__lt=0.5).count()
    W = weak_count / studied_concepts if studied_concepts else 0

    new_w = (1 - S) * 0.5 + days_left/total_days * 0.2
    weak_w = 0.2 + (W * 0.5)
    carry_w = 0.2
    rev_w = S * 0.3 + (1 - days_left/total_days) * 0.3

    total = new_w + weak_w + carry_w + rev_w
    return {'new': new_w / total, 'weak': weak_w / total, 'carry': carry_w / total, 'rev': rev_w / total}

def adaptive_weights(base_weights, mindstate: MindState):
    w = base_weights.copy()
    for k in ['new','weak','carry','rev']:
        w[k] = max(0.05, w.get(k,0.0))

    if mindstate:
        if mindstate.focus < 0.45:
            w['new'] *= 0.6
            w['rev'] *= 1.4
        if mindstate.energy < 0.4:
            w['weak'] *= 0.6
            w['carry'] *= 1.2
        if mindstate.motivation > 0.7:
            w['new'] *= 1.2
            w['weak'] *= 0.9

    s = sum(w.values())
    return {k:(v/s) for k,v in w.items()}

# ------------------------
# Core: daily plan builder
# ------------------------
@transaction.atomic
def build_daily_plan(user, study_date, budget_minutes=180, exam_date=None, plan_type='daily', goal: Goal = None, mindstate: MindState = None):
    """Generate a daily/weekly plan for user, decoupled from planner services."""
    if isinstance(study_date, str):
        study_date = date.fromisoformat(study_date)

    # remove previous auto plans
    TargetPlan.objects.filter(user=user, plan_date=study_date, source='auto').delete()

    # fetch mindstate if not provided
    if mindstate is None:
        mindstate = MindState.objects.filter(user=user, date=study_date).last()

    base = compute_dynamic_weights(user, exam_date)
    weights = adaptive_weights(base, mindstate)

    # select concepts for today
    new_c = pick_concepts(get_new(user), int(budget_minutes * weights['new']))
    weak_c = pick_concepts(get_weak(user), int(budget_minutes * weights['weak']))
    carry_c = pick_concepts(get_carryover(user), int(budget_minutes * weights['carry']))
    rev_c = pick_concepts(get_revision(user), int(budget_minutes * weights['rev']))
    all_concepts = new_c + weak_c + carry_c + rev_c

    plan = TargetPlan.objects.create(
        user=user,
        goal=goal,
        plan_date=study_date,
        plan_type=plan_type,
        budget_minutes=budget_minutes,
        source='auto',
        weights=weights,
        mindstate=mindstate
    )

    # create PlanTasks
    for concept in all_concepts:
        est = getattr(concept,'estimated_time',20) or 20
        snapshot = {}
        ucp = UserConceptProgress.objects.filter(user=user, concept=concept).first()
        if ucp:
            snapshot = {
                'mastery': ucp.mastery,
                'ease_factor': ucp.ease_factor,
                'interval_days': ucp.interval_days
            }
        PlanTask.objects.create(
            plan=plan,
            concept=concept,
            allocated_minutes=est,
            progress_snapshot=snapshot
        )

    # log decision via planner service
    log_decision(
        user=user,
        plan_id=plan.id,
        action={'type':'plan_generated','source':'auto'},
        rationale=f"Adaptive plan generated with weights={weights}"
    )

    return plan

# ------------------------
# Carryover reassignment
# ------------------------
def reassign_carryovers():
    tasks = PlanTask.objects.filter(status='carryover')
    for t in tasks:
        user = t.plan.user
        next_date = t.plan.plan_date + timedelta(days=1)
        plan = TargetPlan.objects.filter(user=user, plan_date=next_date, source='auto').first()
        if not plan:
            plan = build_daily_plan(user, next_date, budget_minutes=t.plan.budget_minutes)
        t.plan = plan
        t.status = 'pending'
        t.save()


def get_latest_plan_tasks(user, study_date=None):
    study_date = study_date or date.today()

    # Get the most recent plan created today (if multiple)
    latest_plan = (
        TargetPlan.objects
        .filter(user=user, plan_date=study_date)
        .order_by('-created_at')
        .first()
    )

    if not latest_plan:
        return None, []

    # Get all tasks belonging to this plan
    tasks = PlanTask.objects.filter(plan=latest_plan)
    return tasks