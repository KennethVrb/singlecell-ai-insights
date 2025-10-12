from datetime import datetime
from datetime import timezone as dt_timezone
from unittest.mock import MagicMock

from botocore.exceptions import BotoCoreError
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from singlecell_ai_insights.models import Run


class MockHealthOmicsClient:
    def __init__(self):
        self.reset()

    def reset(self):
        self.paginator = MagicMock()
        self.paginator.paginate = MagicMock(return_value=[])

        self.get_paginator = MagicMock(return_value=self.paginator)
        self.get_paginator.side_effect = None

        self.get_workflow = MagicMock(return_value={'name': 'Mock Workflow'})
        self.get_workflow.side_effect = None

        self.get_run = MagicMock(return_value={'run': {}})
        self.get_run.side_effect = None


MOCK_HEALTHOMICS_CLIENT = MockHealthOmicsClient()


class MockS3Client:
    def __init__(self):
        self.generate_presigned_url = MagicMock(
            return_value='https://example.com/presigned'
        )


@override_settings(
    AWS_HEALTHOMICS_CLIENT=MOCK_HEALTHOMICS_CLIENT,
    AWS_S3_CLIENT=MockS3Client(),
)
class RunEndpointTests(APITestCase):
    def setUp(self):
        super().setUp()
        settings.AWS_S3_CLIENT.generate_presigned_url.reset_mock()
        MOCK_HEALTHOMICS_CLIENT.reset()
        self.mock_paginator = MOCK_HEALTHOMICS_CLIENT.paginator

        self.user = get_user_model().objects.create_user(
            username='tester', password='strong-pass'
        )

    def authenticate(self):
        self.client.force_authenticate(self.user)

    def test_requires_authentication(self):
        response = self.client.get('/api/runs/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_initial_request_fetches_from_healthomics(self):
        self.authenticate()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [
            {
                'items': [
                    {
                        'id': 'run-123',
                        'name': 'Example Run',
                        'status': 'COMPLETED',
                        'workflowId': '2174942',
                        'creationTime': datetime(
                            2024, 1, 1, tzinfo=dt_timezone.utc
                        ),
                        'completionTime': datetime(
                            2024, 1, 2, tzinfo=dt_timezone.utc
                        ),
                        'output': 's3://bucket/report.zip',
                        'sample': 'A',
                    }
                ]
            }
        ]
        MOCK_HEALTHOMICS_CLIENT.get_paginator.return_value = mock_paginator
        MOCK_HEALTHOMICS_CLIENT.get_workflow.return_value = {
            'name': 'Example Workflow'
        }
        MOCK_HEALTHOMICS_CLIENT.get_run.return_value = {
            'run': {
                'id': 'run-123',
                'runOutputUri': 's3://bucket/run-123/',
                'status': 'COMPLETED',
            }
        }

        response = self.client.get('/api/runs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MOCK_HEALTHOMICS_CLIENT.get_paginator.assert_called_once_with(
            'list_runs'
        )
        MOCK_HEALTHOMICS_CLIENT.get_workflow.assert_called_once_with(
            id='2174942',
            type='READY2RUN',
        )
        MOCK_HEALTHOMICS_CLIENT.get_run.assert_called_once_with(id='run-123')
        self.assertEqual(len(response.data), 1)
        created_run = Run.objects.get(run_id='run-123')
        self.assertEqual(response.data[0]['pk'], created_run.pk)
        self.assertEqual(response.data[0]['pipeline'], 'Example Workflow')
        self.assertEqual(created_run.pipeline, 'Example Workflow')
        self.assertEqual(created_run.output_dir_bucket, 'bucket')
        self.assertEqual(created_run.output_dir_key, 'run-123/')
        self.assertEqual(response.data[0]['output_dir_bucket'], 'bucket')
        self.assertEqual(response.data[0]['output_dir_key'], 'run-123/')

    def test_refresh_parameter_forces_update(self):
        self.authenticate()
        Run.objects.create(
            run_id='run-old',
            name='Old Run',
            status='PENDING',
            pipeline='wf-old',
            created_at=timezone.now(),
        )
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{'items': []}]
        MOCK_HEALTHOMICS_CLIENT.get_paginator.return_value = mock_paginator

        response = self.client.get('/api/runs/?refresh=true')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MOCK_HEALTHOMICS_CLIENT.get_paginator.assert_called_once_with(
            'list_runs'
        )

    def test_refresh_failure_returns_error_even_with_cache(self):
        self.authenticate()
        run = Run.objects.create(
            run_id='run-cached',
            name='Cached Run',
            status='COMPLETED',
            pipeline='wf',
            created_at=timezone.now(),
        )
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = BotoCoreError(
            error_message='boom'
        )
        MOCK_HEALTHOMICS_CLIENT.get_paginator.return_value = mock_paginator

        response = self.client.get('/api/runs/?refresh=true')

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.data['detail'],
            'Unable to retrieve runs from HealthOmics.',
        )
        self.assertTrue(Run.objects.filter(pk=run.pk).exists())

    def test_returns_error_when_refresh_fails_without_cache(self):
        self.authenticate()
        mock_paginator = MagicMock()
        mock_paginator.paginate.side_effect = BotoCoreError(
            error_message='boom'
        )
        MOCK_HEALTHOMICS_CLIENT.get_paginator.return_value = mock_paginator

        response = self.client.get('/api/runs/?refresh=true')

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.data['detail'],
            'Unable to retrieve runs from HealthOmics.',
        )

    def test_run_detail_view(self):
        self.authenticate()
        run = Run.objects.create(
            run_id='run-123',
            name='Example Run',
            status='COMPLETED',
            pipeline='wf',
            created_at=timezone.now(),
            output_dir_bucket='bucket',
            output_dir_key='run-123/',
        )

        response = self.client.get(f'/api/runs/{run.pk}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['run_id'], run.run_id)
        self.assertEqual(response.data['name'], run.name)
        self.assertEqual(response.data['status'], run.status)
        self.assertEqual(response.data['pipeline'], run.pipeline)
        self.assertEqual(
            response.data['output_dir_key'],
            run.output_dir_key,
        )
        self.assertEqual(response.data['metadata'], run.metadata)

    def test_run_multiqc_report_view(self):
        self.authenticate()
        run = Run.objects.create(
            run_id='run-123',
            name='Example Run',
            status='COMPLETED',
            pipeline='wf',
            created_at=timezone.now(),
            output_dir_bucket='bucket',
            output_dir_key='run-123/',
        )

        response = self.client.get(f'/api/runs/{run.pk}/multiqc-report/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['multiqc_report_url'],
            'https://example.com/presigned',
        )
        settings.AWS_S3_CLIENT.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': 'bucket',
                'Key': 'run-123/pubdir/multiqc/multiqc_report.html',
            },
            ExpiresIn=int(settings.AWS_S3_PRESIGN_TTL),
        )

    def test_run_multiqc_report_view_not_available(self):
        self.authenticate()
        run = Run.objects.create(
            run_id='run-404',
            name='Example Run',
            status='COMPLETED',
            pipeline='wf',
            created_at=timezone.now(),
            output_dir_bucket='',
            output_dir_key='',
        )

        response = self.client.get(f'/api/runs/{run.pk}/multiqc-report/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['detail'], 'MultiQC report not available.'
        )
