from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserConceptProgress
from .serializers import UserProgressSerializer, UpdateProgressSerializer
from .services import update_progress, update_progress_bulk, get_user_progress, get_weak_concepts
from syllabus.models import Concept

User = get_user_model()


class UserProgressViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet to handle user progress on concepts.
    Supports listing, retrieving, and custom actions for mastery updates.
    """
    queryset = UserConceptProgress.objects.all()
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        # Replace with request.user in production
        # user = User.objects.get(id=1)
        user=self.request.user
        return UserConceptProgress.objects.filter(user=user)\
            .select_related('concept__subtopic__topic__subject')\
            .order_by(
                'concept__subtopic__topic__subject',
                'concept__subtopic__topic',
                'concept__subtopic',
                'concept'
            )

    @action(detail=False, methods=["get"])
    def full_progress(self, request):
        """Fetch all user progress"""
        # user = User.objects.get(id=1)
        user=request.user
        qs = get_user_progress(user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def update_mastery(self, request):
        """Update mastery for a single concept"""
        # user = User.objects.get(id=1)
        user=request.user
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        concept_id = serializer.validated_data["concept_id"]
        score = serializer.validated_data.get("score")
        understood = serializer.validated_data.get("understood")
        concept = Concept.objects.get(id=concept_id)

        ucp = update_progress(user, concept, score, understood)
        return Response(self.get_serializer(ucp).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def update_mastery_bulk(self, request):
        """Update mastery for multiple concepts"""
        # user = User.objects.get(id=1)
        user=request.user

        results = request.data.get("results", [])
        if not results:
            return Response({"error": "No results provided"}, status=status.HTTP_400_BAD_REQUEST)

        updated = update_progress_bulk(user, results)
        serializer = self.get_serializer(updated, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def weak_concepts(self, request):
        """Fetch concepts with mastery < 0.5"""
        # user = User.objects.get(id=1)
        user=request.user
        
        qs = get_weak_concepts(user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
