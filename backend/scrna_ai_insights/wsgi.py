"""WSGI config for the SingleCell AI Insights project."""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scrna_ai_insights.settings")

application = get_wsgi_application()
