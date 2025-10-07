from datetime import datetime
from datetime import timezone as dt_timezone
from unittest.mock import MagicMock

from botocore.exceptions import BotoCoreError
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from singlecell_ai_insights.models import Run

MOCK_HEALTHOMICS_CLIENT = MagicMock(name='MockHealthOmicsClient')


@override_settings(AWS_HEALTHOMICS_CLIENT=MOCK_HEALTHOMICS_CLIENT)
class RunEndpointTests(APITestCase):
    def setUp(self):
        super().setUp()
        MOCK_HEALTHOMICS_CLIENT.reset_mock()
        MOCK_HEALTHOMICS_CLIENT.get_paginator.side_effect = None
        MOCK_HEALTHOMICS_CLIENT.get_paginator.return_value = MagicMock()
        MOCK_HEALTHOMICS_CLIENT.get_workflow.reset_mock()
        MOCK_HEALTHOMICS_CLIENT.get_workflow.side_effect = None
        MOCK_HEALTHOMICS_CLIENT.get_workflow.return_value = {
            'name': 'Mock Workflow'
        }
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

        response = self.client.get('/api/runs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        MOCK_HEALTHOMICS_CLIENT.get_paginator.assert_called_once_with(
            'list_runs'
        )
        MOCK_HEALTHOMICS_CLIENT.get_workflow.assert_called_once_with(
            id='2174942',
            type='READY2RUN',
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['run_id'], 'run-123')
        self.assertEqual(response.data[0]['pipeline'], 'Example Workflow')
        self.assertTrue(
            Run.objects.filter(run_id='run-123', name='Example Run').exists()
        )
        self.assertEqual(
            Run.objects.get(run_id='run-123').pipeline, 'Example Workflow'
        )

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
        self.assertTrue(
            Run.objects.filter(
                run_id=run.run_id, name='Cached Run', status='COMPLETED'
            ).exists()
        )

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
