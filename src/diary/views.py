from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from diary.services import create_diary_entry
from chatbot.models import ChatSession, ChatMessage
from chatbot.services.intents import detect_intent
from chatbot.services.handler import handle_intent
from ai_engine.services import transcribe_audio
from django.utils import timezone
from datetime import datetime, time


class DiaryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_time_based_session(self, user):
        """Get or create a session based on time of day"""
        now = datetime.now().time()
        today = timezone.now().date()

        if time(6, 0) <= now < time(10, 0):
            label = "Morning"
        elif time(10, 0) <= now < time(14, 0):
            label = "Afternoon"
        elif time(14, 0) <= now < time(18, 0):
            label = "Evening"
        elif time(18, 0) <= now < time(22, 0):
            label = "Late Evening"
        elif time(22, 0) <= now or now < time(2, 0):
            label = "Midnight"
        else:
            label = "Pre-Morning"

        session, _ = ChatSession.objects.get_or_create(
            user=user,
            session_name=f"{today} - {label}"
        )
        return session

    @action(detail=False, methods=['post'])
    def create_entry(self, request):
        user = request.user
        input_type = request.data.get("input_type", "text")
        raw_text = request.data.get("raw_text", "").strip()
        audio_s3_key = request.data.get("audio_s3_key")

        if not raw_text and not audio_s3_key:
            return Response({"error": "No input provided"}, status=status.HTTP_400_BAD_REQUEST)

        # --- Step 1: Transcribe if voice ---
        if input_type == "voice" and audio_s3_key:
            raw_text = transcribe_audio(audio_s3_key)

        # --- Step 2: Detect intent ---
        intent = detect_intent(raw_text or "")

        # --- Step 3: Get session ---
        session = self.get_time_based_session(user)

        # --- Step 4: Save user message ---
        ChatMessage.objects.create(session=session, role="user", text=raw_text or "[voice input]")

        # --- Step 5: Decide if diary + AI processing needed ---
        reflective_intents = ["chat", "diary_reflection", "start_diary", "improve_mindstate"]
        diary_entry_id = None

        if intent in reflective_intents:
            diary_entry = create_diary_entry(
                user=user,
                input_type=input_type,
                raw_text=raw_text,
                audio_s3_key=audio_s3_key,
            )
            diary_entry_id = diary_entry.id

        # --- Step 6: Handle intent & generate bot reply ---
        bot_reply = handle_intent(user, intent, raw_text or "")

        # --- Step 7: Save bot message (optional) ---
        if intent in reflective_intents:
            ChatMessage.objects.create(session=session, role="bot", text=str(bot_reply))

        # --- Step 8: Return response ---
        return Response({
            "reply": bot_reply,
            "diary_entry_id": diary_entry_id,
            "session_id": session.id,
            "intent": intent
        }, status=status.HTTP_200_OK)
