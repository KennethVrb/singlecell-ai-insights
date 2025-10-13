from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from singlecell_ai_insights.models import Conversation, Message, Run
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
        data = response.json()
        self.assertEqual(data['content'], 'Example answer')
        self.assertEqual(data['role'], Message.ROLE_ASSISTANT)
        self.assertEqual(data['citations'], ['module'])
        self.assertEqual(data['table_url'], 'https://example.com/table.csv')
        self.assertEqual(data['plot_url'], 'https://example.com/plot.png')
        self.assertEqual(data['metric_key'], 'duplication')

        mock_chat.assert_called_once_with(
            run.run_id,
            'Show me details',
            conversation_history=[
                {'role': 'user', 'content': 'Show me details'}
            ],
            metric_key=None,
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


class ConversationHistoryTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username='history-user',
            password='strong-pass',
        )
        self.client.force_authenticate(self.user)

    def create_run(self):
        return Run.objects.create(
            run_id='run-456',
            name='History Test Run',
        )

    def test_get_empty_conversation_returns_empty_messages(self):
        run = self.create_run()

        response = self.client.get(f'/api/runs/{run.pk}/chat/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'messages': []})

    def test_get_conversation_returns_all_messages(self):
        run = self.create_run()
        conversation = Conversation.objects.create(run=run)

        msg1 = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content='First question',
        )
        msg2 = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content='First answer',
            citations=['module1'],
        )
        msg3 = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content='Second question',
        )

        response = self.client.get(f'/api/runs/{run.pk}/chat/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['messages']), 3)
        self.assertEqual(data['messages'][0]['id'], msg1.id)
        self.assertEqual(data['messages'][0]['role'], Message.ROLE_USER)
        self.assertEqual(data['messages'][0]['content'], 'First question')
        self.assertEqual(data['messages'][1]['id'], msg2.id)
        self.assertEqual(data['messages'][1]['role'], Message.ROLE_ASSISTANT)
        self.assertEqual(data['messages'][1]['content'], 'First answer')
        self.assertEqual(data['messages'][1]['citations'], ['module1'])
        self.assertEqual(data['messages'][2]['id'], msg3.id)

    def test_post_creates_user_message(self):
        run = self.create_run()

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ):
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Test question'},
                format='json',
            )

        conversation = Conversation.objects.get(run=run)
        user_messages = conversation.messages.filter(role=Message.ROLE_USER)
        self.assertEqual(user_messages.count(), 1)
        self.assertEqual(user_messages.first().content, 'Test question')

    def test_post_creates_assistant_message(self):
        run = self.create_run()

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Agent response',
                'citations': ['fastqc', 'picard'],
                'table_url': 'https://example.com/table.csv',
                'plot_url': 'https://example.com/plot.png',
                'metric_key': 'duplication',
                'notes': ['Note 1'],
            },
        ):
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Test question'},
                format='json',
            )

        conversation = Conversation.objects.get(run=run)
        assistant_messages = conversation.messages.filter(
            role=Message.ROLE_ASSISTANT
        )
        self.assertEqual(assistant_messages.count(), 1)

        msg = assistant_messages.first()
        self.assertEqual(msg.content, 'Agent response')
        self.assertEqual(msg.citations, ['fastqc', 'picard'])
        self.assertEqual(msg.table_url, 'https://example.com/table.csv')
        self.assertEqual(msg.plot_url, 'https://example.com/plot.png')
        self.assertEqual(msg.metric_key, 'duplication')
        self.assertEqual(msg.notes, ['Note 1'])

    def test_post_passes_conversation_history_to_agent(self):
        run = self.create_run()
        conversation = Conversation.objects.create(run=run)

        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_USER,
            content='Previous question',
        )
        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content='Previous answer',
        )

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'New response',
                'citations': [],
                'notes': [],
            },
        ) as mock_chat:
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'New question'},
                format='json',
            )

        mock_chat.assert_called_once()
        call_kwargs = mock_chat.call_args[1]
        history = call_kwargs['conversation_history']

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['role'], Message.ROLE_USER)
        self.assertEqual(history[0]['content'], 'Previous question')
        self.assertEqual(history[1]['role'], Message.ROLE_ASSISTANT)
        self.assertEqual(history[1]['content'], 'Previous answer')

    def test_post_limits_conversation_history_to_last_10_messages(self):
        run = self.create_run()
        conversation = Conversation.objects.create(run=run)

        for i in range(12):
            Message.objects.create(
                conversation=conversation,
                role=Message.ROLE_USER,
                content=f'Question {i}',
            )
            Message.objects.create(
                conversation=conversation,
                role=Message.ROLE_ASSISTANT,
                content=f'Answer {i}',
            )

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ) as mock_chat:
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Latest question'},
                format='json',
            )

        call_kwargs = mock_chat.call_args[1]
        history = call_kwargs['conversation_history']

        self.assertEqual(len(history), 10)
        self.assertEqual(history[0]['content'], 'Answer 7')
        self.assertEqual(history[-1]['content'], 'Latest question')

    def test_post_creates_conversation_if_not_exists(self):
        run = self.create_run()
        self.assertEqual(Conversation.objects.filter(run=run).count(), 0)

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ):
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'First question'},
                format='json',
            )

        self.assertEqual(Conversation.objects.filter(run=run).count(), 1)

    def test_post_reuses_existing_conversation(self):
        run = self.create_run()
        conversation = Conversation.objects.create(run=run)

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ):
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Question'},
                format='json',
            )

        self.assertEqual(Conversation.objects.filter(run=run).count(), 1)
        self.assertEqual(Conversation.objects.get(run=run).id, conversation.id)

    def test_post_with_metric_key_passes_to_agent(self):
        run = self.create_run()

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ) as mock_chat:
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Question', 'metric_key': 'fastqc.percent_gc'},
                format='json',
            )

        call_kwargs = mock_chat.call_args[1]
        self.assertEqual(call_kwargs['metric_key'], 'fastqc.percent_gc')

    def test_post_with_empty_metric_key_converts_to_none(self):
        run = self.create_run()

        with patch(
            'singlecell_ai_insights.services.agent.chat',
            return_value={
                'answer': 'Response',
                'citations': [],
                'notes': [],
            },
        ) as mock_chat:
            self.client.post(
                f'/api/runs/{run.pk}/chat/',
                {'question': 'Question', 'metric_key': ''},
                format='json',
            )

        call_kwargs = mock_chat.call_args[1]
        self.assertEqual(call_kwargs['metric_key'], None)

    def test_get_requires_authentication(self):
        run = self.create_run()
        self.client.force_authenticate(None)

        response = self.client.get(f'/api/runs/{run.pk}/chat/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
