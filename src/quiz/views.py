from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import date
from django.utils.dateparse import parse_date
from .services import generate_ai_quiz, submit_quiz_results

class QuizViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def start(self, request):
        user = request.user
        study_date = request.query_params.get("date")
        study_date = parse_date(study_date) if study_date else date.today()
        questions = generate_ai_quiz(user, study_date)
        return Response(questions, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def submit(self, request):
        user = request.user
        study_date = request.data.get("study_date")
        study_date = parse_date(study_date) if study_date else date.today()

        results = request.data.get("results", [])
        understood = request.data.get("understood")

        if not results:
            return Response({"error": "No results provided"}, status=status.HTTP_400_BAD_REQUEST)

        resp = submit_quiz_results(user, study_date, results, understood)
        return Response(resp, status=status.HTTP_200_OK)
