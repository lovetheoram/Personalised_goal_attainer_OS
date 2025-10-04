from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Achievement, UserAchievement
from .serializers import AchievementSerializer, UserAchievementSerializer
from .services import check_achievements

class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    def get_queryset(self):
        # Optionally filter by user for unlocked
        return Achievement.objects.all()

    @action(detail=False, methods=['get'])
    def unlocked(self, request):
        user_achievements = UserAchievement.objects.filter(user=request.user)
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def check(self, request):
        check_achievements(request.user)
        return Response({"status": "Achievements updated"})
