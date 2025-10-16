from django.conf import settings
from django.db import models


class Conversation(models.Model):
    run = models.ForeignKey(
        'Run', on_delete=models.CASCADE, related_name='conversations'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = [['run', 'user']]

    def __str__(self):
        return (
            f'Conversation for {self.run.name} by {self.user.username} '
            f'(updated {self.updated_at})'
        )


class Message(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    citations = models.JSONField(default=list, blank=True)
    notes = models.JSONField(default=list, blank=True)
    metric_key = models.CharField(max_length=255, null=True, blank=True)
    confidence = models.IntegerField(null=True, blank=True)
    confidence_explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.content[:50]
        return f'{self.role}: {preview}...'
