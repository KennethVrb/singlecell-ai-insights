import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from singlecell_ai_insights.models import Conversation, Message
from singlecell_ai_insights.models.run import Run
from singlecell_ai_insights.services import agent

from .serializers import AgentChatRequestSerializer, MessageSerializer

logger = logging.getLogger(__name__)


class RunAgentChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Retrieve conversation history for a run."""
        run = get_object_or_404(Run, pk=pk)
        conversation = (
            Conversation.objects.filter(run=run, user=request.user)
            .prefetch_related('messages')
            .first()
        )

        if not conversation:
            return Response({'messages': []}, status=status.HTTP_200_OK)

        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(
            {'messages': serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request, pk):
        run = get_object_or_404(Run, pk=pk)
        serializer = AgentChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']
        metric_key = serializer.validated_data.get('metric_key')
        if metric_key == '':
            metric_key = None

        # Get or create conversation
        conversation, _ = Conversation.objects.get_or_create(
            run=run, user=request.user
        )

        # Save user message
        Message.objects.create(
            conversation=conversation, role=Message.ROLE_USER, content=question
        )

        # Get conversation history (last 10 messages for context)
        messages_qs = conversation.messages.values('role', 'content').order_by(
            '-created_at'
        )[:10]
        history = list(reversed(list(messages_qs)))

        try:
            result = agent.chat(
                run.run_id,
                question,
                conversation_history=history,
                metric_key=metric_key,
            )
        except agent.AgentServiceError as exc:
            logger.warning(
                'Agent chat failed for run %s: %s',
                run.pk or run.run_id,
                exc,
            )
            return Response(
                {'detail': 'Unable to complete agent request.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save assistant message
        assistant_message = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=result.get('answer', ''),
            citations=result.get('citations', []),
            notes=result.get('notes', []),
            metric_key=result.get('metric_key'),
        )

        # Return the saved message instead of raw result
        serializer = MessageSerializer(assistant_message)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete conversation history for a run."""
        run = get_object_or_404(Run, pk=pk)
        deleted_count, _ = Conversation.objects.filter(
            run=run, user=request.user
        ).delete()

        logger.info(
            'Deleted %d conversation(s) for run %s by user %s',
            deleted_count,
            run.pk or run.run_id,
            request.user.username,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
