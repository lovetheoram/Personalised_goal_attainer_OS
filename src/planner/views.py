from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import MindState, Goal, DecisionLog
from .serializers import MindStateSerializer, GoalSerializer, DecisionLogSerializer

class MindStateViewSet(viewsets.ModelViewSet):
    queryset = MindState.objects.all()
    serializer_class = MindStateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

class DecisionLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DecisionLog.objects.all()
    serializer_class = DecisionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
