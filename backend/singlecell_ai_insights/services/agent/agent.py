"""Main agent interface."""

import logging

from botocore.exceptions import BotoCoreError, ClientError

from .exceptions import AgentServiceError
from .graph import APP_GRAPH

logger = logging.getLogger(__name__)


def chat(run_id, question, conversation_history=None, metric_key=None):
    """
    Chat with the agent about a MultiQC run.

    Args:
        run_id: The run ID to analyze
        question: User's question
        conversation_history: Optional list of previous messages
        metric_key: Optional metric key to focus on

    Returns:
        dict with answer, citations, metric_key, notes

    Raises:
        AgentServiceError: If any error occurs during processing
    """
    try:
        state = {
            'run_id': run_id,
            'question': question,
            'conversation_history': conversation_history or [],
        }
        if metric_key:
            state['metric_key'] = metric_key

        result = APP_GRAPH.invoke(state)
    except AgentServiceError:
        raise
    except (BotoCoreError, ClientError) as exc:
        logger.exception('AWS error while running MultiQC chat')
        raise AgentServiceError(
            'AWS request failed during MultiQC chat'
        ) from exc
    except Exception as exc:
        logger.exception('Unexpected error during MultiQC chat')
        raise AgentServiceError(
            'Unexpected error during MultiQC chat'
        ) from exc

    return {
        'answer': result.get('answer', ''),
        'citations': result.get('citations', []),
        'metric_key': result.get('metric_key'),
        'notes': result.get('notes', []),
    }
