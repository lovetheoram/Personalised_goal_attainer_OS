from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import UserConceptProgress
from .serializers import UserProgressSerializer, UpdateProgressSerializer
from .services import update_progress, update_progress_bulk, get_user_progress, get_weak_concepts
from syllabus.models import Concept, Subject

class UserProgressViewSet(viewsets.ModelViewSet):
    """
    Handles user progress on concepts.
    Includes full listing, mastery updates, analytics, and tree structure.
    """
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        user = self.request.user
        return UserConceptProgress.objects.filter(user=user)\
            .select_related('concept__subtopic__topic__subject')\
            .order_by(
                'concept__subtopic__topic__subject',
                'concept__subtopic__topic',
                'concept__subtopic',
                'concept'
            )

    # ---------------------------
    # 1️⃣ Full progress
    # ---------------------------
    @action(detail=False, methods=["get"])
    def full_progress(self, request):
        qs = get_user_progress(request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # ---------------------------
    # 2️⃣ Update single mastery
    # ---------------------------
    @action(detail=False, methods=["post"])
    def update_mastery(self, request):
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        concept_id = serializer.validated_data["concept_id"]
        score = serializer.validated_data.get("score")
        understood = serializer.validated_data.get("understood")
        concept = Concept.objects.get(id=concept_id)

        ucp = update_progress(request.user, concept, score, understood)
        return Response(self.get_serializer(ucp).data, status=status.HTTP_200_OK)

    # ---------------------------
    # 3️⃣ Bulk update mastery
    # ---------------------------
    @action(detail=False, methods=["post"])
    def update_mastery_bulk(self, request):
        results = request.data.get("results", [])
        if not results:
            return Response({"error": "No results provided"}, status=status.HTTP_400_BAD_REQUEST)

        updated = update_progress_bulk(request.user, results)
        serializer = self.get_serializer(updated, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ---------------------------
    # 4️⃣ Weak concepts
    # ---------------------------
    @action(detail=False, methods=["get"])
    def weak_concepts(self, request):
        qs = get_weak_concepts(request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    # ---------------------------
    # 5️⃣ Tree structure
    # ---------------------------
    @action(detail=False, methods=["get"])
    def tree(self, request):
        progresses = self.get_queryset()
        progress_map = {p.concept_id: p for p in progresses}

        tree_data = []
        subjects = Subject.objects.prefetch_related('topics__subtopics__concepts').all()

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
                            "status": getattr(progress, "status", "learning")
                        })
                    sub_data["concepts"].sort(key=lambda x: x["mastery"], reverse=True)
                    topic_data["subtopics"].append(sub_data)
                subj_data["topics"].append(topic_data)
            tree_data.append(subj_data)

        return Response(tree_data, status=status.HTTP_200_OK)

    # ---------------------------
    # 6️⃣ Concept detail
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
