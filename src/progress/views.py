from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth import get_user_model
from .models import UserConceptProgress
from .serializers import UserProgressSerializer, UpdateProgressSerializer
from .services import update_progress, update_progress_bulk, get_user_progress
from syllabus.models import Concept
User = get_user_model()

class UserProgressViewSet(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        user = User.objects.get(id=1)
        return UserConceptProgress.objects.filter(user=user)

    @action(detail=False, methods=["post"])
    def update_mastery(self, request):
        user = User.objects.get(id=1)
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        concept_id = serializer.validated_data["concept_id"]
        score = serializer.validated_data.get("score")
        understood = serializer.validated_data.get("understood")
        concept = Concept.objects.get(id=concept_id)
        ucp = update_progress(user, concept, score, understood)

        return Response(UserProgressSerializer(ucp).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def update_mastery_bulk(self, request):
        user = User.objects.get(id=1)
        results = request.data.get("results", [])
        if not results:
            return Response({"error": "No results provided"}, status=status.HTTP_400_BAD_REQUEST)

        updated = update_progress_bulk(user, results)
        serializer = UserProgressSerializer(updated, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def full_progress(self, request):
        user = User.objects.get(id=1)
        qs = get_user_progress(user)
        serializer = UserProgressSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
