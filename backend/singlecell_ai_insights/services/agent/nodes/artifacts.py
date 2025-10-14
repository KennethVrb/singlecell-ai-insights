"""Artifact generation nodes (tables and plots)."""

from ..tools import find_and_generate_plot_url, find_and_generate_table_url


def make_table(state):
    """Find and link to existing MultiQC table for the metric."""
    metric_key = state.get('metric_key')
    question = state.get('question')

    if not metric_key:
        # No specific metric, link to general stats table
        table_url = find_and_generate_table_url(
            state['run_id'], None, question
        )
    else:
        # Find table for specific metric
        table_url = find_and_generate_table_url(
            state['run_id'], metric_key, question
        )

    state['table_url'] = table_url
    return state


def plot_metric(state):
    """Find and link to existing MultiQC plot for the metric."""
    # Only find plot if we have an explicit metric_key
    # (from lookup_metric node), not for general questions
    metric_key = state.get('metric_key')
    question = state.get('question')

    if not metric_key:
        state['plot_url'] = None
        return state

    # Find and generate presigned URL for MultiQC plot
    plot_url = find_and_generate_plot_url(
        state['run_id'], metric_key, question
    )

    state['plot_url'] = plot_url
    state['metric_key'] = metric_key
    return state
