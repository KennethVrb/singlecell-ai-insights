import logging

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from singlecell_ai_insights.aws import healthomics
from singlecell_ai_insights.models.run import Run
from singlecell_ai_insights.services.agent.config import REPORTS_BUCKET
from singlecell_ai_insights.services.agent.tools import load_json_from_s3

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

    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get summary metrics for a run (cached in DB)."""
        run = self.get_object()

        # Return cached metrics if available
        if run.metrics:
            return Response(run.metrics)

        # Check if run has MultiQC data
        if not run.output_dir_bucket or not run.output_dir_key:
            return Response(
                {'detail': 'MultiQC data not available for this run.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Fetch and parse MultiQC data
        try:
            key = f'{run.run_id}/pubdir/multiqc/multiqc_data/multiqc_data.json'
            data = load_json_from_s3(REPORTS_BUCKET, key)

            # Extract key metrics
            general_stats = data.get('report_general_stats_data', [])
            if not general_stats:
                return Response(
                    {'detail': 'No metrics found in MultiQC data.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Merge all dictionaries and filter out 'multiqc' entries
            samples = {}
            for stats_dict in general_stats:
                for sample_name, sample_data in stats_dict.items():
                    if sample_name.lower() != 'multiqc':
                        samples[sample_name] = sample_data

            if not samples:
                return Response(
                    {'detail': 'No sample metrics found in MultiQC data.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Extract common metrics (adjust based on your MultiQC data)
            metrics_summary = {
                'total_samples': len(samples),
                'samples': [],
            }

            # Add per-sample metrics
            for sample_name, sample_data in samples.items():
                metrics_summary['samples'].append(
                    {
                        'name': sample_name,
                        'duplication_rate': sample_data.get(
                            'percent_duplicates'
                        ),
                        'gc_content': sample_data.get('percent_gc'),
                        'total_sequences': sample_data.get('total_sequences'),
                    }
                )

            # Cache in database
            run.metrics = metrics_summary
            run.save(update_fields=['metrics'])

            return Response(metrics_summary)

        except Exception:
            logger.exception('Failed to load metrics for run %s', run.run_id)
            return Response(
                {'detail': 'Unable to load metrics from MultiQC data.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
