from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from datetime import date

from .models import DailyTarget
from .serializers import DailyTargetSerializer
from .services import build_daily_targets
from django.contrib.auth import get_user_model
from syllabus.models import Concept

User = get_user_model()


# -----------------------------
# DailyTarget ViewSet
# -----------------------------
class DailyTargetViewSet(viewsets.ModelViewSet):
    serializer_class = DailyTargetSerializer

    def get_queryset(self):
        user = User.objects.get(id=1)
        return DailyTarget.objects.filter(user=user)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        user = User.objects.get(id=1)
        study_date = request.data.get("study_date", str(date.today()))
        budget = int(request.data.get("budget", 180))
        exam_date = request.data.get("exam_date", None)

        # Use final engine logic
        if exam_date:
            exam_date = date.fromisoformat(exam_date)
        build_daily_targets(user, date.fromisoformat(study_date), daily_budget_minutes=budget, exam_date=exam_date)

        qs = DailyTarget.objects.filter(user=user, study_date=study_date)
        return Response(DailyTargetSerializer(qs, many=True).data, status=status.HTTP_201_CREATED)
