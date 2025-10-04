from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import LeaderboardEntry
from .serializers import LeaderboardSerializer

User = get_user_model()

class LeaderboardViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for tracking user points, streaks, and rank
    """
    queryset = LeaderboardEntry.objects.all()
    serializer_class = LeaderboardSerializer

    def get_queryset(self):
        """
        Override to filter queryset if needed.
        """
        return LeaderboardEntry.objects.all()

    @action(detail=False, methods=["get"])
    def top(self, request):
        """Get top 10 users globally"""
        top_users = LeaderboardEntry.objects.order_by('-points', '-streak')[:10]
        serializer = self.get_serializer(top_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user's leaderboard entry"""
        user = request.user  # Use the authenticated user
        entry = LeaderboardEntry.objects.filter(user=user).first()
        if not entry:
            return Response({"error": "No leaderboard entry found for the user"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(entry)
        return Response(serializer.data)  # Add this missing return statement