from django.db import models
from django.conf import settings

# -----------------------------
# Core Models
# -----------------------------
class Exam(models.Model):
    name = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    name = models.TextField()
    weightage = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.TextField()
    weightage = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.TextField()
    weightage = models.FloatField(default=1.0)

    def __str__(self):
        return self.name


class Concept(models.Model):
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(blank=True)
    estimated_time = models.IntegerField(default=30)  # minutes
    weightage = models.FloatField(default=1.0)
    resources = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name
