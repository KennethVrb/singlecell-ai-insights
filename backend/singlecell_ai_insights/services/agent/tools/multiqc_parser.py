"""MultiQC data parsing utilities."""


def collect_general_stats_meta(data):
    """Extract metadata for general stats metrics."""
    meta = {}
    sections = data.get('report_general_stats_headers') or []
    for section in sections:
        if not isinstance(section, dict):
            continue
        for metric_name, config in section.items():
            if isinstance(config, dict):
                meta[metric_name] = config
    return meta


def extract_general_stats_samples(data):
    """Extract sample metrics from general stats."""
    meta_lookup = collect_general_stats_meta(data)
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


def extract_fastqc_module_statuses(data):
    """Extract FastQC module pass/warn/fail statuses."""
    module_statuses = {}
    raw_data = data.get('report_saved_raw_data', {})
    fastqc_data = raw_data.get('multiqc_fastqc', {})

    for sample, modules in fastqc_data.items():
        if not isinstance(modules, dict):
            continue
        if sample.lower() == 'multiqc':
            continue

        sample_statuses = {}
        for module_name, status in modules.items():
            if isinstance(status, str) and status in ('pass', 'warn', 'fail'):
                sample_statuses[module_name] = status

        if sample_statuses:
            module_statuses[sample] = sample_statuses

    return module_statuses


def infer_metric_key_from_question(q, samples):
    """Infer which metric key the question is asking about."""
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
