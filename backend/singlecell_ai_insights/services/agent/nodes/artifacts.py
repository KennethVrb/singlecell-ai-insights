"""Artifact generation nodes (tables and plots)."""

import csv
import io
import uuid

from matplotlib import pyplot as plt

from ..config import ARTIFACT_BUCKET
from ..tools import put_s3_bytes_and_presign


def make_table(state):
    """Generate CSV table from tabular data."""
    rows = state.get('tabular')
    if not rows:
        # Only create fallback table if we explicitly have a metric_key
        # (from lookup_metric node), not for general RAG questions
        metric_key = state.get('metric_key')
        if metric_key:
            tmp = []
            for s, m in state['samples'].items():
                if metric_key in m and isinstance(m[metric_key], (int, float)):
                    tmp.append({'sample': s, metric_key: m[metric_key]})
            rows = tmp or None

    if not rows:
        state['table_url'] = None
        return state

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = buf.getvalue().encode('utf-8')

    key = f'{state["run_id"]}/artifacts/{uuid.uuid4().hex}.csv'
    url = put_s3_bytes_and_presign(ARTIFACT_BUCKET, key, csv_bytes, 'text/csv')
    state['table_url'] = url
    return state


def plot_metric(state):
    """Generate bar plot for a specific metric."""
    # Only create plot if we have an explicit metric_key
    # (from lookup_metric node), not for general questions
    metric_key = state.get('metric_key')
    if not metric_key:
        state['plot_url'] = None
        return state

    xs, ys = [], []
    for s, m in state['samples'].items():
        v = m.get(metric_key)
        if isinstance(v, (int, float)):
            xs.append(s)
            ys.append(float(v))

    if not xs:
        state['plot_url'] = None
        return state

    fig = plt.figure(figsize=(10, 4))
    plt.bar(range(len(xs)), ys)
    plt.xticks(range(len(xs)), xs, rotation=45, ha='right')
    plt.title(metric_key)
    plt.ylabel('value')
    plt.tight_layout()

    png_buf = io.BytesIO()
    fig.savefig(png_buf, format='png', dpi=160)
    plt.close(fig)
    png_bytes = png_buf.getvalue()

    key = f'{state["run_id"]}/artifacts/{uuid.uuid4().hex}.png'
    url = put_s3_bytes_and_presign(
        ARTIFACT_BUCKET, key, png_bytes, 'image/png'
    )
    state['plot_url'] = url
    state['metric_key'] = metric_key
    return state
