import logging

from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


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

    def get_multiqc_report_s3_key(self):
        if not self.output_dir_key:
            return None
        base = self.output_dir_key.strip('/')
        if not base:
            return None
        return f'{base}/pubdir/multiqc/multiqc_report.html'

    def get_multiqc_report_url(self):
        if not self.output_dir_bucket:
            return None
        report_key = self.get_multiqc_report_s3_key()
        if not report_key:
            return None

        try:
            return settings.AWS_S3_CLIENT.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.output_dir_bucket,
                    'Key': report_key,
                },
                ExpiresIn=int(settings.AWS_S3_PRESIGN_TTL),
            )
        except (BotoCoreError, ClientError) as exc:
            logger.warning(
                'Unable to presign MultiQC report for run %s: %s',
                self.pk or self.run_id,
                exc,
            )
            return None
