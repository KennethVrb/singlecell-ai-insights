"""Analysis nodes for sample lookup, metric lookup, and RAG."""

from ..config import DUP_THRESH, MAPPED_MIN
from ..tools import (
    generate_comparative_summary,
    infer_metric_key_from_question,
)


def lookup_samples(state):
    """Identify flagged samples based on heuristics and FastQC failures."""
    q = state['question'].lower()
    rows = []
    module_statuses = state.get('module_statuses', {})

    # simple heuristics; adjust to your lab norms
    for s, m in state['samples'].items():
        dup_vals = [
            v
            for k, v in m.items()
            if isinstance(v, (int, float)) and 'dup' in k.lower()
        ]
        mapped_tokens = [
            'mapped',
            'align',
            'total_sequences',
            'read_count',
            'unique_reads',
        ]
        mapped_vals = [
            v
            for k, v in m.items()
            if isinstance(v, (int, float))
            and any(token in k.lower() for token in mapped_tokens)
        ]
        dup = max(dup_vals) if dup_vals else 0.0
        mapped = max(mapped_vals) if mapped_vals else 0.0

        # Check FastQC module failures
        sample_modules = module_statuses.get(s, {})
        failed_modules = [k for k, v in sample_modules.items() if v == 'fail']
        warned_modules = [k for k, v in sample_modules.items() if v == 'warn']

        flag = (
            (dup > DUP_THRESH)
            or (mapped < MAPPED_MIN)
            or len(failed_modules) > 0
        )

        if 'failed' in q or 'flag' in q or 'which sample' in q:
            if flag:
                row = {
                    'sample': s,
                    'duplication': round(float(dup), 3),
                    'mapped': int(mapped),
                }
                if failed_modules:
                    row['failed_modules'] = ', '.join(failed_modules)
                if warned_modules:
                    row['warned_modules'] = ', '.join(warned_modules)
                row['flag'] = True
                rows.append(row)

    state['tabular'] = rows or None
    notes = [f'Heuristics: dup>{DUP_THRESH} OR mapped<{int(MAPPED_MIN)}']
    if any(module_statuses.values()):
        notes.append('Also flagging samples with FastQC module failures')
    state['notes'].append(' | '.join(notes))
    return state


def lookup_metric(state):
    """Extract metric values with comparative analysis."""
    q = state['question'].lower()
    chosen = infer_metric_key_from_question(q, state['samples'])
    hits = []
    if chosen:
        for s, m in state['samples'].items():
            if chosen in m and isinstance(m[chosen], (int, float)):
                hits.append(
                    {'sample': s, 'metric': chosen, 'value': m[chosen]}
                )

        # Add comparative analysis
        comparative = generate_comparative_summary(state['samples'], chosen)
        if comparative:
            # Add outlier flags to table
            outlier_samples = {
                o['sample'] for o in comparative['stats']['outliers']
            }
            for hit in hits:
                if hit['sample'] in outlier_samples:
                    hit['outlier'] = True

            # Add insights to notes
            if comparative['insights']:
                state['notes'].extend(comparative['insights'])

    state['metric_key'] = chosen
    state['tabular'] = hits or None
    return state


def rag(state):
    """Retrieve relevant documents from vector store."""
    vs = state.get('vs')
    if vs:
        retr = vs.as_retriever(search_kwargs={'k': 4})
        state['retrieved'] = retr.get_relevant_documents(state['question'])
    else:
        state['retrieved'] = []
    return state
