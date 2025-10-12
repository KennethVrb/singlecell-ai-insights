import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from singlecell_ai_insights.models.run import Run
from singlecell_ai_insights.services import agent

from .serializers import AgentChatRequestSerializer

logger = logging.getLogger(__name__)


class RunAgentChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        run = get_object_or_404(Run, pk=pk)
        serializer = AgentChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data['question']
        metric_key = serializer.validated_data.get('metric_key')
        if metric_key == '':
            metric_key = None

        try:
            result = agent.chat(run.run_id, question, metric_key=metric_key)
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

        return Response(result, status=status.HTTP_200_OK)
