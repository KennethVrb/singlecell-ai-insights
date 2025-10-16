"""LangGraph workflow definition."""

from langgraph.graph import END, START, StateGraph

from .nodes import (
    ensure_index,
    load_multiqc,
    lookup_metric,
    lookup_samples,
    make_table,
    plot_metric,
    rag,
    route_intent,
    synthesize,
)


def build_graph():
    """Build and compile the agent workflow graph."""
    graph = StateGraph(dict)
    graph.add_node('load_multiqc', load_multiqc)
    graph.add_node('ensure_index', ensure_index)
    graph.add_node('lookup_samples', lookup_samples)
    graph.add_node('lookup_metric', lookup_metric)
    graph.add_node('rag', rag)
    graph.add_node('make_table', make_table)
    graph.add_node('plot_metric', plot_metric)
    graph.add_node('synthesize', synthesize)

    graph.add_edge(START, 'load_multiqc')
    graph.add_edge('load_multiqc', 'ensure_index')
    graph.add_conditional_edges(
        'ensure_index',
        route_intent,
        {
            'lookup_samples': 'lookup_samples',
            'lookup_metric': 'lookup_metric',
            'rag': 'rag',
        },
    )
    graph.add_edge('lookup_samples', 'make_table')
    graph.add_edge('lookup_metric', 'make_table')
    graph.add_edge('rag', 'make_table')
    graph.add_edge('make_table', 'plot_metric')
    graph.add_edge('plot_metric', 'synthesize')
    graph.add_edge('synthesize', END)

    return graph.compile()


def build_streaming_graph():
    """Build and compile the agent workflow graph with streaming enabled."""
    return build_graph()


APP_GRAPH = build_graph()
