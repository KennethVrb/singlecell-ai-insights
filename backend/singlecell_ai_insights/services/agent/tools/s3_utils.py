"""S3 utilities for agent service."""

import json

from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings

from ..exceptions import AgentServiceError


def load_json_from_s3(bucket, key):
    """Load and parse JSON from S3."""
    try:
        obj = settings.AWS_S3_CLIENT.get_object(Bucket=bucket, Key=key)
    except (BotoCoreError, ClientError) as exc:
        raise AgentServiceError(
            f'Unable to load {key} from bucket {bucket}'
        ) from exc
    return json.loads(obj['Body'].read())


def put_s3_bytes_and_presign(bucket, key, body, content_type):
    """Upload bytes to S3 and return presigned URL."""
    try:
        settings.AWS_S3_CLIENT.put_object(
            Bucket=bucket, Key=key, Body=body, ContentType=content_type
        )
    except (BotoCoreError, ClientError) as exc:
        raise AgentServiceError(
            f'Unable to upload artifact {key} to bucket {bucket}'
        ) from exc
    url = settings.AWS_S3_CLIENT.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=settings.AWS_S3_PRESIGN_TTL,
    )
    return url


def generate_presigned_url(bucket, key):
    """Generate presigned URL for an existing S3 object."""
    url = settings.AWS_S3_CLIENT.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=settings.AWS_S3_PRESIGN_TTL,
    )
    return url
