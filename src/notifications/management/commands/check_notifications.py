from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from notifications.services import (
    check_mindstate_notifications,
    check_goal_notifications,
    check_diary_streak,
)
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = "Check and create notifications for all users"

    def handle(self, *args, **kwargs):
        now = timezone.localtime()
        print(f"🔄 Running notification check at {now.strftime('%Y-%m-%d %H:%M:%S')}")

        for user in User.objects.all():
            check_mindstate_notifications(user)
            check_goal_notifications(user)
            check_diary_streak(user)

        self.stdout.write(self.style.SUCCESS("✅ Notifications updated for all users"))
