import logging

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from singlecell_ai_insights.aws import healthomics
from singlecell_ai_insights.models.run import Run

from .serializers import RunSerializer, RunSummarySerializer

logger = logging.getLogger(__name__)


class RunViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Run.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RunSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return RunSummarySerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        should_refresh = (
            request.query_params.get('refresh', '').lower() in {'1', 'true'}
            or not Run.objects.exists()
        )

        if should_refresh:
            try:
                for run in healthomics.list_runs():
                    Run.objects.update_or_create(
                        run_id=run['run_id'],
                        defaults={
                            'name': run.get('name') or '',
                            'status': run.get('status') or '',
                            'pipeline': run.get('pipeline') or '',
                            'created_at': run.get('created_at')
                            or timezone.now(),
                            'started_at': run.get('started_at'),
                            'completed_at': run.get('completed_at'),
                            'output_dir_bucket': (
                                run.get('output_dir_bucket') or ''
                            ),
                            'output_dir_key': run.get('output_dir_key') or '',
                        },
                    )
            except healthomics.HealthOmicsClientError as exc:
                logger.warning('HealthOmics runs refresh failed: %s', exc)
                return Response(
                    {'detail': 'Unable to retrieve runs from HealthOmics.'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='multiqc-report')
    def multiqc_report(self, request, pk=None):
        run = self.get_object()
        url = run.get_multiqc_report_url()
        if not url:
            return Response(
                {'detail': 'MultiQC report not available.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({'multiqc_report_url': url})
