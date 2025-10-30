from django.db.models import Avg, Count
from django.utils import timezone
from .models import UserDailyStats, UserTrend
from planner.models import MindState, Goal
from diary.models import DiaryEntry
from target.models import TargetPlan

def update_daily_stats(user, date=None):
    """
    Update or create daily statistics for a user.
    """
    if date is None:
        date = timezone.now().date()
        
    # Get mind state data
    mindstates = MindState.objects.filter(user=user, date=date)
    mind_metrics = mindstates.aggregate(
        avg_focus=Avg('focus'),
        avg_energy=Avg('energy'),
        avg_motivation=Avg('motivation')
    )
    
    # Count emotion occurrences for the day
    emotions = mindstates.values('emotion').annotate(count=Count('emotion')).order_by('-count')
    dominant_emotion = emotions[0]['emotion'] if emotions else None
    
    # Goal metrics
    active_goals = Goal.objects.filter(user=user, status='active').count()
    completed_goals = Goal.objects.filter(
        user=user, 
        status='completed', 
        updated_at__date=date
    ).count()
    
    # Diary metrics
    diary_entries = DiaryEntry.objects.filter(
        user=user,
        created_at__date=date
    ).count()
    
    # Get average sentiment if available in processed data
    diary_sentiments = DiaryEntry.objects.filter(
        user=user,
        created_at__date=date,
        processed__has_key='sentiment'
    ).values_list('processed__sentiment', flat=True)
    sentiment_score = sum(diary_sentiments) / len(diary_sentiments) if diary_sentiments else None
    
    # Task completion
    tasks_completed = TargetPlan.objects.filter(
        user=user,
        study_date=date,
        status='completed'
    ).count()
    
    # Update stats
    stats, _ = UserDailyStats.objects.update_or_create(
        user=user,
        date=date,
        defaults={
            'avg_focus': mind_metrics['avg_focus'] or 0.0,
            'avg_energy': mind_metrics['avg_energy'] or 0.0,
            'avg_motivation': mind_metrics['avg_motivation'] or 0.0,
            'dominant_emotion': dominant_emotion,
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'diary_entries': diary_entries,
            'sentiment_score': sentiment_score,
            'tasks_completed': tasks_completed,
        }
    )
    return stats

def analyze_trends(user, days=30):
    """
    Analyze user trends over the specified period.
    """
    end_date = timezone.now().date()
    start_date = end_date - timezone.timedelta(days=days)
    
    # Get daily stats for the period
    daily_stats = UserDailyStats.objects.filter(
        user=user,
        date__range=(start_date, end_date)
    ).order_by('date')
    
    if not daily_stats:
        return []
    
    trends = []
    
    # Analyze focus trend
    focus_values = [stat.avg_focus for stat in daily_stats]
    focus_trend = calculate_trend(focus_values)
    trends.append(UserTrend(
        user=user,
        trend_type='focus',
        start_date=start_date,
        end_date=end_date,
        trend_value=focus_trend['slope'],
        confidence=focus_trend['confidence'],
        insights={
            'peak_days': focus_trend['peak_days'],
            'pattern': focus_trend['pattern']
        }
    ))
    
    # Analyze motivation trend
    motivation_values = [stat.avg_motivation for stat in daily_stats]
    motivation_trend = calculate_trend(motivation_values)
    trends.append(UserTrend(
        user=user,
        trend_type='motivation',
        start_date=start_date,
        end_date=end_date,
        trend_value=motivation_trend['slope'],
        confidence=motivation_trend['confidence'],
        insights={
            'peak_days': motivation_trend['peak_days'],
            'pattern': motivation_trend['pattern']
        }
    ))
    
    # Save all trends
    UserTrend.objects.bulk_create(trends)
    return trends

def calculate_trend(values):
    """
    Calculate trend metrics for a series of values.
    Returns slope, confidence, and pattern insights.
    """
    if not values:
        return {
            'slope': 0,
            'confidence': 0,
            'peak_days': [],
            'pattern': 'insufficient_data'
        }
    
    # Simple linear regression for slope
    n = len(values)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    slope = numerator / denominator if denominator != 0 else 0
    
    # Find peak days (local maxima)
    peak_days = [
        i for i in range(1, n-1)
        if values[i] > values[i-1] and values[i] > values[i+1]
    ]
    
    # Determine pattern
    if abs(slope) < 0.1:
        pattern = 'stable'
    elif slope > 0:
        pattern = 'improving'
    else:
        pattern = 'declining'
    
    # Calculate confidence based on variance
    variance = sum((v - y_mean) ** 2 for v in values) / n
    confidence = 1 / (1 + variance)  # normalize to 0-1
    
    return {
        'slope': slope,
        'confidence': confidence,
        'peak_days': peak_days,
        'pattern': pattern
    }