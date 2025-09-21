"""Application configuration for the scrna-ai-insights Django app."""
from __future__ import annotations

from django.apps import AppConfig


class ScrnaAiInsightsConfig(AppConfig):
    """Configuration object for the scrna-ai-insights application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "scrna_ai_insights"
    verbose_name = "scrna-ai-insights"
