from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from singlecell_ai_insights.models import Run
from singlecell_ai_insights.services.agent import AgentServiceError


class RunAgentChatTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username='chat-user',
            password='strong-pass',
        )

    def authenticate(self):
        self.client.force_authenticate(self.user)

    def create_run(self):
        return Run.objects.create(
            run_id='run-123',
            name='Example Run',
        )

    def test_requires_authentication(self):
        run = self.create_run()

        response = self.client.post(
            f'/api/runs/{run.pk}/chat/',
            {'question': 'How is the run doing?'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_chat_returns_payload(self):
        run = self.create_run()
        self.authenticate()
        payload = {
            'answer': 'Example answer',
            'citations': ['module'],
            'table_url': 'https://example.com/table.csv',
            'plot_url': 'https://example.com/plot.png',
            'metric_key': 'duplication',
            'notes': ['note'],
        }

        with patch(
            'singlecell_ai_insights.services.agent.chat', return_value=payload
        ) as mock_chat:
            response = self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Show me details'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), payload)
        mock_chat.assert_called_once_with(
            run.run_id, 'Show me details', metric_key=None
        )

    def test_agent_error_returns_bad_gateway(self):
        run = self.create_run()
        self.authenticate()

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            side_effect=AgentServiceError('boom'),
        ):
            response = self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Cause failure'},
                format='json',
            )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(
            response.json(),
            {'detail': 'Unable to complete agent request.'},
        )

    def test_validation_error_missing_question(self):
        run = self.create_run()
        self.authenticate()

        response = self.client.post(
            f'/api/runs/{run.pk}/chat/',
            {},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('question', response.json())
