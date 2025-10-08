import logging

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from singlecell_ai_insights.aws import healthomics
from singlecell_ai_insights.models.run import Run

from .serializers import RunSerializer

logger = logging.getLogger(__name__)


class RunListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
                            's3_report_key': run.get('s3_report_key') or '',
                            'metadata': run.get('metadata') or {},
                        },
                    )
            except healthomics.HealthOmicsClientError as exc:
                logger.warning('HealthOmics runs refresh failed: %s', exc)
                return Response(
                    {'detail': 'Unable to retrieve runs from HealthOmics.'},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        queryset = Run.objects.all()

        data = RunSerializer(queryset, many=True).data
        return Response(data)
