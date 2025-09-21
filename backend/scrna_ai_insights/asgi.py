"""ASGI config for the SingleCell AI Insights project."""
from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scrna_ai_insights.settings")

application = get_asgi_application()
