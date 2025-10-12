from django.db import models
from django.utils import timezone


class Run(models.Model):
    run_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=64, blank=True)
    pipeline = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    output_dir_bucket = models.CharField(max_length=255, blank=True)
    output_dir_key = models.CharField(max_length=512, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    normalized_context = models.JSONField(null=True, blank=True)
    indexed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name or self.run_id
