from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserConceptProgress
from .serializers import UserProgressSerializer, UpdateProgressSerializer
from .services import update_progress, update_progress_bulk, get_user_progress, get_weak_concepts
from syllabus.models import Concept
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import UserConceptProgress
from syllabus.models import Subject, Topic, Subtopic, Concept
from .serializers import UserProgressSerializer

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



# purnima22121
    @action(detail=False, methods=["get"])
    def tree(self, request):
        user = request.user
        progresses = self.get_queryset()
        progress_map = {p.concept_id: p for p in progresses}

        tree_data = []
        subjects = Subject.objects.prefetch_related(
            'topics__subtopics__concepts'
        ).all()

        for subj in subjects:
            subj_data = {"subject_name": subj.name, "topics": []}
            for topic in subj.topics.all():
                topic_data = {"topic_name": topic.name, "subtopics": []}
                for subtopic in topic.subtopics.all():
                    sub_data = {"subtopic_name": subtopic.name, "concepts": []}
                    for concept in subtopic.concepts.all():
                        progress = progress_map.get(concept.id)
                        sub_data["concepts"].append({
                            "concept_id": concept.id,
                            "concept_name": concept.name,
                            "mastery": getattr(progress, "mastery", 0.0),
                            "points": getattr(progress, "points", 0),
                            "ease_factor": getattr(progress, "ease_factor", 2.5),
                        })
                    # sort concepts by mastery descending
                    sub_data["concepts"].sort(key=lambda x: x["mastery"], reverse=True)
                    topic_data["subtopics"].append(sub_data)
                subj_data["topics"].append(topic_data)
            tree_data.append(subj_data)

        return Response(tree_data, status=status.HTTP_200_OK)

    # ---------------------------
    # 2️⃣ Concept detail endpoint
    # ---------------------------
    @action(detail=False, methods=["get"])
    def concept_detail(self, request):
        concept_id = request.query_params.get("concept_id")
        if not concept_id:
            return Response({"error": "concept_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            progress = self.get_queryset().get(concept_id=concept_id)
        except UserConceptProgress.DoesNotExist:
            return Response({"error": "Progress not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
