# target/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from .models import TargetPlan, PlanTask
from .serializers import TargetPlanSerializer, PlanTaskSerializer
from .services import build_daily_plan, reassign_carryovers
from planner.models import Goal, MindState

class TargetPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TargetPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TargetPlan.objects.filter(user=self.request.user).select_related('goal','mindstate').prefetch_related('tasks')

    @action(detail=False, methods=['post'])
    def generate_daily_plan(self, request):
        study_date = request.data.get('study_date')
        budget_minutes = request.data.get('budget_minutes', 180)
        goal_id = request.data.get('goal_id')
        plan_type = request.data.get('plan_type', 'daily')

        if not study_date:
            return Response({"error":"study_date is required"}, status=status.HTTP_400_BAD_REQUEST)
        study_date = parse_date(study_date)
        goal = Goal.objects.filter(id=goal_id).first() if goal_id else None
        mindstate = MindState.objects.filter(user=request.user, date=study_date).last()

        plan = build_daily_plan(request.user, study_date, budget_minutes, plan_type=plan_type, goal=goal, mindstate=mindstate)
        serializer = self.get_serializer(plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def reassign_carryover_tasks(self, request):
        reassign_carryovers()
        return Response({"status":"carryover tasks reassigned"}, status=status.HTTP_200_OK)


class PlanTaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlanTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        study_date = self.request.query_params.get('study_date')
        qs = PlanTask.objects.filter(plan__user=self.request.user).select_related('concept','plan')
        if study_date:
            qs = qs.filter(plan__plan_date=study_date)
        return qs.order_by('plan__plan_date')
