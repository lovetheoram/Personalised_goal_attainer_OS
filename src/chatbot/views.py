from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from .services import detect_intent, handle_intent

class ChatViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def send(self, request):
        user = request.user
        message = request.data.get("message", "").strip()
        session_id = request.data.get("session_id")

        if not message:
            return Response({"error": "Message cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=user)
        else:
            session = ChatSession.objects.create(user=user)

        # Save user message
        ChatMessage.objects.create(session=session, role='user', text=message)

        # Detect intent and handle
        intent = detect_intent(message)
        bot_response = handle_intent(user, intent, message)

        # Save bot message
        ChatMessage.objects.create(session=session, role='bot', text=str(bot_response))

        # Include session_id in response for tracking
        bot_response['session_id'] = session.id
        return Response(bot_response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def history(self, request):
        user = request.user
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response({"error": "session_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        session = get_object_or_404(ChatSession, id=session_id, user=user)
        messages = ChatMessage.objects.filter(session=session).order_by("created_at")
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
