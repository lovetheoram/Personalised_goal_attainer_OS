from django.urls import path
from .views import index, health

urlpatterns = [
    path('', index, name='api-index'),
    path('health/', health, name='api-health'),
]
