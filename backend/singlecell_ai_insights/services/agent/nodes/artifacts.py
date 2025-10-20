"""Artifact generation nodes (tables and plots)."""

from ..tools import (
    generate_plot_urls_from_indices,
    generate_table_urls_from_indices,
    select_artifacts_with_llm,
)


def make_table(state):
    """Find and link to existing MultiQC tables using LLM selection."""
    metric_key = state.get('metric_key')
    question = state.get('question')

    # Use LLM to intelligently select relevant tables
    selection = select_artifacts_with_llm(question, metric_key)
    table_indices = selection.get('table_indices', [])

    # Generate URLs for selected tables
    table_urls = generate_table_urls_from_indices(
        state['run_id'], table_indices
    )

    state['table_urls'] = table_urls
    return state


def plot_metric(state):
    """Find and link to existing MultiQC plots using LLM selection."""
    metric_key = state.get('metric_key')
    question = state.get('question', '')

    # Use LLM to intelligently select relevant plots
    selection = select_artifacts_with_llm(question, metric_key)
    plot_indices = selection.get('plot_indices', [])

    # Generate URLs for selected plots
    plot_urls = generate_plot_urls_from_indices(state['run_id'], plot_indices)

    state['plot_urls'] = plot_urls
    if metric_key:
        state['metric_key'] = metric_key

    return state
