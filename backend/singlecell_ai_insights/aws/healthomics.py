from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional

from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class HealthOmicsClientError(RuntimeError):
    """Wrap boto3 errors so views can distinguish client failures."""


def _coerce_datetime(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        if timezone.is_naive(value):
            return timezone.make_aware(value)
        return value
    raw = str(value)
    if raw.endswith('Z'):
        raw = raw.replace('Z', '+00:00')
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        logger.debug('Unable to parse datetime value: %s', value)
        return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


def _sanitize_metadata(value):
    if isinstance(value, dict):
        return {key: _sanitize_metadata(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_sanitize_metadata(item) for item in value]
    if isinstance(value, datetime):
        return (
            _coerce_datetime(value).isoformat()
            if _coerce_datetime(value)
            else None
        )
    return value


def _extract_pipeline_name(
    item: Dict[str, object], cache: Dict[str, str]
) -> str:
    workflow_id = item.get('workflowId')
    if workflow_id:
        workflow_id_str = str(workflow_id)
        if workflow_id_str in cache:
            return cache[workflow_id_str]

        workflow = settings.AWS_HEALTHOMICS_CLIENT.get_workflow(
            id=workflow_id_str, type='READY2RUN'
        )

        if isinstance(workflow, dict):
            for key in ('name', 'displayName', 'workflowName'):
                name = workflow.get(key)
                if name:
                    cache[workflow_id_str] = str(name)
                    return cache[workflow_id_str]

    fallback = (
        item.get('workflowId')
        or item.get('workflowArn')
        or item.get('pipeline')
        or ''
    )
    return str(fallback)


def list_runs() -> List[Dict[str, object]]:
    """Return normalized run metadata from AWS HealthOmics."""

    paginator = settings.AWS_HEALTHOMICS_CLIENT.get_paginator('list_runs')

    runs: List[Dict[str, object]] = []
    workflow_name_cache: Dict[str, str] = {}
    try:
        for page in paginator.paginate():
            page_items = page.get('items') or page.get('runs') or []
            for item in page_items:
                runs.append(
                    {
                        'run_id': item.get('id') or item.get('runId'),
                        'name': item.get('name', ''),
                        'status': item.get('status', ''),
                        'pipeline': _extract_pipeline_name(
                            item, workflow_name_cache
                        ),
                        'created_at': _coerce_datetime(
                            item.get('creationTime') or item.get('createdTime')
                        ),
                        'started_at': _coerce_datetime(
                            item.get('startTime') or item.get('startTime')
                        ),
                        'completed_at': _coerce_datetime(
                            item.get('stopTime') or item.get('stopTime')
                        ),
                        's3_report_key': item.get('output')
                        or item.get('outputUri')
                        or '',
                        'metadata': _sanitize_metadata(item),
                    }
                )
    except (BotoCoreError, ClientError) as exc:
        raise HealthOmicsClientError(
            'Unable to list HealthOmics runs'
        ) from exc

    return [run for run in runs if run['run_id']]
