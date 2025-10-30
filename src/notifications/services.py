from django.utils import timezone
from django.db.models import Q
from .models import Notification, NotificationPreference
from planner.models import MindState, Goal
from diary.models import DiaryEntry
from datetime import timedelta

def create_notification(user, title, message, notification_type, context_data=None, 
                       priority='medium', send_at=None):
    """
    Create a new notification with user preferences check
    """
    # Check if user wants this type of notification
    pref = NotificationPreference.objects.get_or_create(
        user=user,
        notification_type=notification_type,
        defaults={'enabled': True}
    )[0]
    
    if not pref.enabled:
        return None
        
    # Check quiet hours
    current_time = timezone.localtime().time()
    if (pref.quiet_hours_start and pref.quiet_hours_end and 
        current_time >= pref.quiet_hours_start and 
        current_time <= pref.quiet_hours_end):
        # If in quiet hours, schedule for end of quiet hours
        send_at = timezone.now().replace(
            hour=pref.quiet_hours_end.hour,
            minute=pref.quiet_hours_end.minute
        )
    
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        context_data=context_data,
        send_at=send_at
    )

def check_mindstate_notifications(user):
    """
    Check if any mindstate-related notifications should be created
    """
    today = timezone.now().date()
    recent_states = MindState.objects.filter(
        user=user,
        date__gte=today - timedelta(days=3)
    ).order_by('-date')
    
    if not recent_states:
        return
    
    latest = recent_states.first()
    
    # Alert for low motivation
    if latest.motivation < 0.3:
        create_notification(
            user=user,
            title="Motivation Check-In",
            message="We noticed your motivation is a bit low. Would you like some tips to boost it?",
            notification_type='mindstate_alert',
            priority='high',
            context_data={'mindstate_id': str(latest.id)}
        )
    
    # Alert for high stress (based on emotion)
    if latest.emotion in ['stressed', 'overwhelmed', 'anxious']:
        create_notification(
            user=user,
            title="Stress Management",
            message="Taking a short break might help reduce stress. Want to try a quick meditation?",
            notification_type='mindstate_alert',
            priority='high'
        )

def check_goal_notifications(user):
    """
    Create notifications for goals
    """
    today = timezone.now().date()
    
    # Check approaching deadlines
    upcoming_goals = Goal.objects.filter(
        user=user,
        status='active',
        target_date__isnull=False,
        target_date__gt=today,
        target_date__lte=today + timedelta(days=7)
    )
    
    for goal in upcoming_goals:
        days_left = (goal.target_date - today).days
        create_notification(
            user=user,
            title=f"Goal Deadline Approaching: {goal.title}",
            message=f"You have {days_left} days left to achieve this goal. Need help planning?",
            notification_type='goal_reminder',
            priority='medium',
            context_data={'goal_id': str(goal.id)}
        )
    
    # Check completed goals
    just_completed = Goal.objects.filter(
        user=user,
        status='completed',
        updated_at__date=today
    )
    
    for goal in just_completed:
        create_notification(
            user=user,
            title=f"Goal Achieved: {goal.title}",
            message="Congratulations! Would you like to set a new goal?",
            notification_type='goal_milestone',
            priority='medium',
            context_data={'goal_id': str(goal.id)}
        )

def check_diary_streak(user):
    """
    Check diary writing streak and send notifications
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Check if wrote diary yesterday
    wrote_yesterday = DiaryEntry.objects.filter(
        user=user,
        created_at__date=yesterday
    ).exists()
    
    if not wrote_yesterday:
        # Get current streak
        streak_days = 0
        check_date = yesterday - timedelta(days=1)
        
        while DiaryEntry.objects.filter(user=user, created_at__date=check_date).exists():
            streak_days += 1
            check_date -= timedelta(days=1)
        
        if streak_days > 0:
            create_notification(
                user=user,
                title="Don't Break Your Diary Streak!",
                message=f"You had a {streak_days}-day diary streak going. Write today to keep it alive!",
                notification_type='diary_reminder',
                priority='high'
            )
    
    # If haven't written today, remind in the evening
    wrote_today = DiaryEntry.objects.filter(
        user=user,
        created_at__date=today
    ).exists()
    
    if not wrote_today:
        evening_reminder = timezone.now().replace(hour=20, minute=0)
        if timezone.now().time() < evening_reminder.time():
            create_notification(
                user=user,
                title="Daily Diary Reminder",
                message="Don't forget to write in your diary today!",
                notification_type='diary_reminder',
                priority='medium',
                send_at=evening_reminder
            )