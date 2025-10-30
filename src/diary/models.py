import uuid
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class DiaryEntry(TimeStampedModel):
    INPUT_TYPES = [('text','text'),('voice','voice'),('quick_tap','quick_tap')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diary_entries')
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES)
    raw_text = models.TextField(null=True, blank=True)
    audio_s3_key = models.TextField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    processed = models.JSONField(null=True, blank=True)
    privacy_flags = models.JSONField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=['user','created_at'])]

    def __str__(self):
        return f'DiaryEntry {self.id} by {self.user}'
