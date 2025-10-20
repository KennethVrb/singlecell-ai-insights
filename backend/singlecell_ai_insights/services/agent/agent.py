"""Main agent interface."""

import logging

from botocore.exceptions import BotoCoreError, ClientError

from .exceptions import AgentServiceError
from .graph import APP_GRAPH, build_streaming_graph

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


def chat_stream(run_id, question, conversation_history=None, metric_key=None):
    """
    Stream agent chat responses with progress updates.

    Args:
        run_id: The run ID to analyze
        question: User's question
        conversation_history: Optional list of previous messages
        metric_key: Optional metric key to focus on

    Yields:
        dict: Progress updates and final result

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

        # Build streaming graph that yields progress
        streaming_graph = build_streaming_graph()

        # Stream through each node execution
        for event in streaming_graph.stream(state):
            # event is a dict with node name as key
            node_name = next(iter(event.keys()))
            node_state = event[node_name]

            # Emit progress based on node
            if node_name == 'load_multiqc':
                yield {
                    'type': 'status',
                    'step': 'load',
                    'message': 'Loading MultiQC data from S3...',
                }
            elif node_name == 'ensure_index':
                yield {
                    'type': 'status',
                    'step': 'index',
                    'message': 'Building vector index for semantic search...',
                }
            elif node_name in ['lookup_samples', 'lookup_metric', 'rag']:
                yield {
                    'type': 'status',
                    'step': 'analyze',
                    'message': 'Analyzing question and retrieving context...',
                }
            elif node_name == 'make_table':
                yield {
                    'type': 'status',
                    'step': 'table',
                    'message': 'Selecting relevant data tables...',
                }
            elif node_name == 'plot_metric':
                yield {
                    'type': 'status',
                    'step': 'plot',
                    'message': 'Selecting relevant visualizations...',
                }
            elif node_name == 'synthesize':
                yield {
                    'type': 'status',
                    'step': 'synthesize',
                    'message': 'Generating answer...',
                }

        # Get final result
        final_state = node_state

        # Yield final answer
        yield {
            'type': 'answer',
            'content': {
                'answer': final_state.get('answer', ''),
                'citations': final_state.get('citations', []),
                'metric_key': final_state.get('metric_key'),
                'notes': final_state.get('notes', []),
            },
        }

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
