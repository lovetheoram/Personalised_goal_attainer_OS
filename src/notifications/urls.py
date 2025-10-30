from django.urls import path
from .views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationPreferenceView
)

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notification-preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
]
