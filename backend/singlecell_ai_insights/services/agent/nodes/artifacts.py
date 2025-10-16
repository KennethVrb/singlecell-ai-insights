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
    metric_key = state.get('metric_key')
    question = state.get('question', '')

    # Try to find plot even without explicit metric_key
    # by checking the question for plot keywords
    plot_url = find_and_generate_plot_url(
        state['run_id'], metric_key, question
    )

    state['plot_url'] = plot_url
    if metric_key:
        state['metric_key'] = metric_key

    return state
