"""Data loading and indexing nodes."""

import json

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from ..config import REPORTS_BUCKET, emb
from ..exceptions import AgentServiceError
from ..tools import (
    build_fastqc_status_panels,
    build_general_stats_panels,
    extract_fastqc_module_statuses,
    extract_general_stats_samples,
    load_json_from_s3,
)


def load_multiqc(state):
    """Load MultiQC data from S3 and extract samples/metrics."""
    key = f'{state["run_id"]}/pubdir/multiqc/multiqc_data/multiqc_data.json'
    try:
        data = load_json_from_s3(REPORTS_BUCKET, key)
    except AgentServiceError as exc:
        raise AgentServiceError(
            f'multiqc_data.json not found at s3://{REPORTS_BUCKET}/{key}'
        ) from exc

    samples, metric_meta = extract_general_stats_samples(data)
    module_statuses = extract_fastqc_module_statuses(data)

    panels = build_general_stats_panels(samples, metric_meta)
    panels.extend(build_fastqc_status_panels(module_statuses))

    if not panels and isinstance(data, dict):
        # Fallback to a generic document for debugging
        panels.append(
            Document(
                page_content=json.dumps(data)[:10000],
                metadata={'module': 'multiqc_raw'},
            )
        )

    state['samples'] = samples
    state['panels'] = panels
    state['metric_meta'] = metric_meta
    state['module_statuses'] = module_statuses
    state['notes'] = []
    return state


def ensure_index(state):
    """Build in-memory FAISS vector store from panels."""
    docs = state.get('panels', [])
    if docs:
        state['vs'] = FAISS.from_documents(docs, emb)
    else:
        state['vs'] = None
    return state
