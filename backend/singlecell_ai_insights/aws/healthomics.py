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


def _extract_output_location(item):
    uri = item.get('runOutputUri')
    if not uri:
        return '', ''

    value = str(uri)

    if value.startswith('s3://'):
        full_path = value.split('s3://')[1]
        bucket, key = full_path.split('/', 1)
        return bucket, f'{key.strip("/")}/'

    return '', value


def _normalize_run(item, workflow_name_cache, fallback=None):
    combined = {}
    if isinstance(fallback, dict):
        combined.update(fallback)
    if isinstance(item, dict):
        combined.update(item)

    bucket, key = _extract_output_location(combined)

    run_id = combined.get('id') or combined.get('runId')
    name = combined.get('name') or ''
    status = combined.get('status') or ''

    normalized = {
        'run_id': run_id,
        'name': str(name),
        'status': str(status),
        'pipeline': _extract_pipeline_name(combined, workflow_name_cache),
        'created_at': _coerce_datetime(
            combined.get('creationTime') or combined.get('createdTime')
        ),
        'started_at': _coerce_datetime(
            combined.get('startTime') or combined.get('startedTime')
        ),
        'completed_at': _coerce_datetime(
            combined.get('stopTime') or combined.get('completedTime')
        ),
        'output_dir_bucket': bucket,
        'output_dir_key': key or str(combined.get('outputUri') or ''),
        'metadata': _sanitize_metadata(combined),
    }

    return normalized


def list_runs() -> List[Dict[str, object]]:
    """Return normalized run metadata from AWS HealthOmics."""

    paginator = settings.AWS_HEALTHOMICS_CLIENT.get_paginator('list_runs')

    collected = {}
    workflow_name_cache: Dict[str, str] = {}
    try:
        for page in paginator.paginate():
            page_items = page.get('items') or page.get('runs') or []
            for item in page_items:
                run_id = item.get('id') or item.get('runId')
                if not run_id:
                    continue
                collected[str(run_id)] = item
    except (BotoCoreError, ClientError) as exc:
        raise HealthOmicsClientError(
            'Unable to list HealthOmics runs'
        ) from exc

    runs: List[Dict[str, object]] = []

    for run_id, base_item in collected.items():
        detailed = None
        try:
            detailed_response = settings.AWS_HEALTHOMICS_CLIENT.get_run(
                id=run_id
            )
            if (
                isinstance(detailed_response, dict)
                and 'run' in detailed_response
            ):
                detailed = detailed_response.get('run')
            else:
                detailed = detailed_response
        except (BotoCoreError, ClientError) as exc:
            logger.warning(
                'Unable to fetch run details for %s: %s', run_id, exc
            )
            detailed = base_item

        normalized = _normalize_run(
            detailed, workflow_name_cache, fallback=base_item
        )
        if normalized.get('run_id'):
            runs.append(normalized)

    return runs
