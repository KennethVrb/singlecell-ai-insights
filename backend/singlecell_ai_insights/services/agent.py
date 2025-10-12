"""Django service utilities for chatting about MultiQC outputs."""

import csv
import io
import json
import logging
import os
import uuid

os.environ.setdefault('MPLBACKEND', 'Agg')

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from langchain.docstore.document import Document

# In-memory vector store for PoC - to be replaced with OpenSearch later
from langchain.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings, ChatBedrock

# LangChain/LangGraph
from langgraph.graph import END, START, StateGraph

# Use non-interactive backend for matplotlib
from matplotlib import pyplot as plt

# ------------ Config ------------
logger = logging.getLogger(__name__)


BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']
BEDROCK_EMBED_MODEL_ID = os.environ['BEDROCK_EMBED_MODEL_ID']
AWS_REGION = os.environ['AWS_REGION']

REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
ARTIFACT_BUCKET = os.environ['ARTIFACT_BUCKET']
PRESIGN_TTL = '3600'

DUP_THRESH = 0.7
MAPPED_MIN = 1e6

# --- AWS Clients ---
session = boto3.Session(region_name=AWS_REGION)
s3 = session.client('s3')

# --- LangChain/LangGraph ---
llm = ChatBedrock(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION)
emb = BedrockEmbeddings(
    model_id=BEDROCK_EMBED_MODEL_ID, region_name=AWS_REGION
)


class AgentServiceError(RuntimeError):
    """Domain error raised for agent-related failures."""


# --- Helpers ---
def _load_json_from_s3(bucket, key):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
    except (BotoCoreError, ClientError) as exc:
        raise AgentServiceError(
            'Unable to load %s from bucket %s' % (key, bucket)
        ) from exc
    return json.loads(obj['Body'].read())


def _put_s3_bytes_and_presign(bucket, key, body, content_type):
    try:
        s3.put_object(
            Bucket=bucket, Key=key, Body=body, ContentType=content_type
        )
    except (BotoCoreError, ClientError) as exc:
        raise AgentServiceError(
            'Unable to upload artifact %s to bucket %s' % (key, bucket)
        ) from exc
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=PRESIGN_TTL,
    )
    return url


def _infer_metric_key_from_question(q, samples):
    q = q.lower()
    tokens = ['dup', 'umi', 'gc', 'mapped', 'counts', 'n_content', 'align']
    hint = next((t for t in tokens if t in q), None)
    if not samples:
        return None
    # Pick first matching metric across samples; fallback to any numeric metric
    for s, m in samples.items():
        for k in m.keys():
            if hint and hint in k.lower():
                return k
    for s, m in samples.items():
        for k, v in m.items():
            if isinstance(v, (int, float)):
                return k
    return None


def _collect_general_stats_meta(data):
    meta = {}
    sections = data.get('report_general_stats_headers') or []
    for section in sections:
        if not isinstance(section, dict):
            continue
        for metric_name, config in section.items():
            if isinstance(config, dict):
                meta[metric_name] = config
    return meta


def _extract_general_stats_samples(data):
    meta_lookup = _collect_general_stats_meta(data)
    samples = {}
    key_meta = {}
    entries = data.get('report_general_stats_data') or []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for sample, metrics in entry.items():
            if not isinstance(metrics, dict):
                continue
            if sample.lower() == 'multiqc':
                continue
            sample_metrics = samples.setdefault(sample, {})
            for metric_name, value in metrics.items():
                if not isinstance(value, (int, float)):
                    continue
                meta = meta_lookup.get(metric_name, {})
                namespace = meta.get('namespace')
                key_parts = []
                if namespace:
                    key_parts.append(str(namespace).lower())
                key_parts.append(metric_name)
                metric_key = '.'.join(key_parts)
                sample_metrics[metric_key] = value
                if meta:
                    key_meta[metric_key] = meta
    return samples, key_meta


def _build_general_stats_panels(samples, key_meta):
    panels = []
    for sample, metrics in samples.items():
        if not metrics:
            continue
        lines = []
        for metric_key in sorted(metrics.keys()):
            value = metrics[metric_key]
            meta = key_meta.get(metric_key, {})
            title = meta.get('title') or metric_key
            namespace = meta.get('namespace')
            label = title
            if namespace:
                label = f'[{namespace}] {title or metric_key}'
            lines.append(f'{label}: {value}')
        content = 'Sample: %s\n%s' % (sample, '\n'.join(lines))
        panels.append(
            Document(
                page_content=content,
                metadata={'module': 'general_stats', 'sample': sample},
            )
        )
    return panels


# --- Nodes ---
def load_multiqc(state):
    key = f'{state["run_id"]}/pubdir/multiqc/multiqc_data/multiqc_data.json'
    try:
        data = _load_json_from_s3(REPORTS_BUCKET, key)
    except AgentServiceError as exc:
        raise AgentServiceError(
            'multiqc_data.json not found at s3://%s/%s' % (REPORTS_BUCKET, key)
        ) from exc

    samples, metric_meta = _extract_general_stats_samples(data)
    panels = _build_general_stats_panels(samples, metric_meta)
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
    state['notes'] = []
    return state


def ensure_index(state):
    # In-memory FAISS for PoC; swap with OpenSearch later
    docs = state.get('panels', [])
    if docs:
        state['vs'] = FAISS.from_documents(docs, emb)
    else:
        state['vs'] = None
    return state


def route_intent(state):
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


def lookup_samples(state):
    q = state['question'].lower()
    rows = []

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
        flag = (dup > DUP_THRESH) or (mapped < MAPPED_MIN)

        if 'failed' in q or 'flag' in q or 'which sample' in q:
            if flag:
                rows.append(
                    {
                        'sample': s,
                        'duplication': round(float(dup), 3),
                        'mapped': int(mapped),
                        'flag': True,
                    }
                )

    state['tabular'] = rows or None
    state['notes'].append(
        f'Heuristics: dup>{DUP_THRESH} OR mapped<{int(MAPPED_MIN)}.'
    )
    return state


def lookup_metric(state):
    q = state['question'].lower()
    chosen = _infer_metric_key_from_question(q, state['samples'])
    hits = []
    if chosen:
        for s, m in state['samples'].items():
            if chosen in m and isinstance(m[chosen], (int, float)):
                hits.append(
                    {'sample': s, 'metric': chosen, 'value': m[chosen]}
                )
    state['metric_key'] = chosen
    state['tabular'] = hits or None
    return state


def rag(state):
    vs = state.get('vs')
    if vs:
        retr = vs.as_retriever(search_kwargs={'k': 4})
        state['retrieved'] = retr.get_relevant_documents(state['question'])
    else:
        state['retrieved'] = []
    return state


def make_table(state):
    rows = state.get('tabular')
    if not rows:
        # fallback: try to assemble a simple sample/metric table for
        # chosen metric
        metric_key = state.get(
            'metric_key'
        ) or _infer_metric_key_from_question(
            state['question'], state['samples']
        )
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
    url = _put_s3_bytes_and_presign(
        ARTIFACT_BUCKET, key, csv_bytes, 'text/csv'
    )
    state['table_url'] = url
    return state


def plot_metric(state):
    metric_key = state.get('metric_key') or _infer_metric_key_from_question(
        state['question'], state['samples']
    )
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
    url = _put_s3_bytes_and_presign(
        ARTIFACT_BUCKET, key, png_bytes, 'image/png'
    )
    state['plot_url'] = url
    state['metric_key'] = metric_key
    return state


def synthesize(state):
    # Build compact context
    context_blocks = []

    # Table preview
    if state.get('tabular'):
        rows = state['tabular'][:10]
        if rows:
            header = list(rows[0].keys())
            lines = [','.join(header)]
            for r in rows:
                lines.append(','.join(str(r[h]) for h in header))
            context_blocks.append('TABLE_PREVIEW\n' + '\n'.join(lines))

    # Retrieved panels
    if state.get('retrieved'):
        for d in state['retrieved'][:4]:
            mod = d.metadata.get('module')
            snippet = d.page_content[:800]
            context_blocks.append(f'[{mod}] {snippet}')

    # Artifact links
    links = []
    if state.get('table_url'):
        links.append(f'CSV: {state["table_url"]}')
    if state.get('plot_url'):
        links.append(f'Plot: {state["plot_url"]}')

    prompt = f"""
    You are a genomics QC assistant for MultiQC (nf-core/scrnaseq).
    Question: {state['question']}

    Artifacts (presigned):
    {chr(10).join(links) if links else 'None'}

    Context (table preview and module snippets):
    {chr(10).join(context_blocks) if context_blocks else 'None'}

    Instructions:
    - Answer concisely and concretely.
    - When referencing modules, cite inline like 
        [fastqc], [umi_tools], [picard] if relevant.
    - If recommending actions, be specific
        (e.g., "trim adapters", "increase sequencing depth", 
        "adjust UMI dedup settings").
    """

    msg = llm.invoke(prompt)
    state['answer'] = msg.content
    # naive citations list from retrieved modules
    state['citations'] = sorted(
        list(
            {
                d.metadata.get('module')
                for d in state.get('retrieved', [])
                if d.metadata.get('module')
            }
        )
    )
    return state


# --- Build Graph ---
def _build_graph():
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


APP_GRAPH = _build_graph()


# --- Interface ---
def chat(run_id, question, metric_key=None):
    try:
        state = {
            'run_id': run_id,
            'question': question,
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
        'table_url': result.get('table_url'),
        'plot_url': result.get('plot_url'),
        'metric_key': result.get('metric_key'),
        'notes': result.get('notes', []),
    }
