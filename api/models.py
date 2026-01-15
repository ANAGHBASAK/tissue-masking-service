"""
Optional models for tracking jobs and storing reference profiles.
"""
from django.db import models
import uuid


class TissueMaskingJob(models.Model):
    """Track processing jobs (optional)"""
    job_id = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metrics = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.job_id} - {self.status}"


class ReferenceStainProfile(models.Model):
    """Store reference stain profiles for normalization"""
    stain_type = models.CharField(
        max_length=50,
        choices=[
            ('HE', 'H&E'),
            ('IHC', 'IHC'),
            ('PAP', 'PAP'),
        ]
    )
    profile_data = models.JSONField()  # Reference distribution stats
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.stain_type} Profile - {self.created_at}"
