"""Intent routing logic."""


def route_intent(state):
    """Route to appropriate analysis node based on question intent."""
    q = state['question'].lower()
    if any(
        w in q
        for w in [
            'which sample',
            'failed',
            'flag',
            'low quality',
            'bad',
            'outlier',
        ]
    ):
        return 'lookup_samples'
    if any(
        w in q
        for w in [
            'duplication',
            'duplicate',
            'umi',
            'complexity',
            'gc',
            'mapped',
            'align',
            'counts',
            'depth',
        ]
    ):
        return 'lookup_metric'
    if any(w in q for w in ['why', 'explain', 'root cause', 'recommend']):
        return 'rag'
    return 'rag'
