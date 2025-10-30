from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from analytics.services import update_daily_stats, analyze_trends
from analytics.models import UserDailyStats, UserTrend
from analytics.serializers import UserDailyStatsSerializer, UserTrendSerializer


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def update_daily_stats(self, request):
        """
        Trigger calculation of daily stats for today or a specific date.
        """
        user = request.user
        date_str = request.data.get("date")
        date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None
        
        stats = update_daily_stats(user, date)
        serializer = UserDailyStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def daily_stats(self, request):
        """
        Fetch daily stats for a specific date or today.
        """
        user = request.user
        date_str = request.query_params.get("date")
        date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.now().date()
        
        stats = UserDailyStats.objects.filter(user=user, date=date).first()
        if not stats:
            return Response({"error": "No stats found for this date"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserDailyStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def analyze_trends(self, request):
        """
        Trigger trend analysis for a user over a period of days (default 30).
        """
        user = request.user
        days = int(request.data.get("days", 30))
        
        trends = analyze_trends(user, days=days)
        serializer = UserTrendSerializer(trends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """
        Fetch all trend records for a user, optionally filtered by type.
        """
        user = request.user
        trend_type = request.query_params.get("trend_type")
        
        trends = UserTrend.objects.filter(user=user)
        if trend_type:
            trends = trends.filter(trend_type=trend_type)
        
        serializer = UserTrendSerializer(trends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
