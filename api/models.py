from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Pipeline(models.Model):
    STATUS_CHOICES = [
        ("CREATED", "Created"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CREATED")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status


# -------------------------------------------------------
#  PIPELINE STEP (individual building blocks)
# -------------------------------------------------------
class PipelineStep(models.Model):
    STEP_TYPES = [
        ("SCRAPE", "Scrape Website"),
        ("SUMMARIZE", "Summarize Text"),
        ("TRANSLATE", "Translate Text"),
        ("NOTIFY", "Send Notification"),
        ("CUSTOM", "Custom Python Step"),
    ]

    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="steps")
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    order = models.IntegerField()
    input_data = models.JSONField(default=dict)
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.step_type}"
