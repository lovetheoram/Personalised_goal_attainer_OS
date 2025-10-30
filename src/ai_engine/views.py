from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import (
    infer_text, analyze_goal, predict_mindstate,
    find_similar_entries
)
from diary.models import DiaryEntry
from planner.models import Goal

@api_view(['GET'])
def health(request):
    return Response({
        'status': 'ok',
        'ml': 'active',
        'models': [
            'emotion_analyzer',
            'text_processor',
            'goal_analyzer',
            'mindstate_predictor'
        ]
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_text(request):
    """Analyze text using NLP models"""
    text = request.data.get('text')
    if not text:
        return Response(
            {'error': 'Text is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    analysis = infer_text(text)
    return Response(analysis)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_goal_text(request):
    """Analyze goal text and provide suggestions"""
    text = request.data.get('text')
    if not text:
        return Response(
            {'error': 'Goal text is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    analysis = analyze_goal(text)
    return Response(analysis)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_user_mindstate(request):
    """Predict user's mind state from diary and activities"""
    diary_text = request.data.get('diary_text')
    if not diary_text:
        return Response(
            {'error': 'Diary text is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get recent activities
    recent_activities = []
    
    # Get recent goals
    goals = Goal.objects.filter(
        user=request.user,
        status__in=['active', 'completed']
    ).order_by('-updated_at')[:5]
    for goal in goals:
        recent_activities.append({
            'type': 'goal',
            'completed': goal.status == 'completed',
            'timestamp': goal.updated_at
        })
    
    # Get recent diary entries
    entries = DiaryEntry.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    for entry in entries:
        recent_activities.append({
            'type': 'diary',
            'completed': True,
            'timestamp': entry.created_at
        })
    
    prediction = predict_mindstate(diary_text, recent_activities)
    return Response(prediction)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_similar_diary_entries(request):
    """Find diary entries similar to query text"""
    query = request.data.get('query')
    if not query:
        return Response(
            {'error': 'Query text is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user's diary entries
    entries = DiaryEntry.objects.filter(user=request.user).order_by('-created_at')
    entry_data = []
    
    for entry in entries:
        text = entry.transcript or entry.raw_text or ''
        if text:
            entry_data.append({
                'id': str(entry.id),
                'text': text,
                'created_at': entry.created_at
            })
    
    similar_entries = find_similar_entries(query, entry_data)
    return Response(similar_entries)
