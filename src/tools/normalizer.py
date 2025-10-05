import json
from pathlib import Path


def load_payload(input_dir):
    json_path = input_dir / 'multiqc_data.json'
    if not json_path.exists():
        raise FileNotFoundError(
            'missing multiqc_data.json in {}'.format(str(input_dir))
        )
    with json_path.open('r', encoding='utf-8') as handle:
        return json.load(handle)


def collect_headers(payload):
    headers = {}
    order = []
    for block in payload.get('report_general_stats_headers', []):
        for key, meta in block.items():
            headers[key] = meta
            order.append(key)
    return headers, order


def collect_samples(payload):
    samples = {}
    for block in payload.get('report_general_stats_data', []):
        for sample, metrics in block.items():
            sample_metrics = samples.setdefault(sample, {})
            for key, value in metrics.items():
                sample_metrics[key] = value
    return samples


def numeric_values(samples):
    values = {}
    for metrics in samples.values():
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                bucket = values.setdefault(key, [])
                bucket.append(float(value))
    return values


def metric_ranges(values):
    ranges = {}
    for key, bucket in values.items():
        minimum = min(bucket)
        maximum = max(bucket)
        ranges[key] = {
            'min': minimum,
            'max': maximum,
            'range': maximum - minimum,
        }
    return ranges


def normalize_samples(samples, ranges):
    normalized = {}
    for sample, metrics in samples.items():
        sample_payload = {}
        for key, value in metrics.items():
            if not isinstance(value, (int, float)):
                continue
            info = ranges.get(key)
            if not info:
                continue
            denominator = info['range']
            if denominator:
                norm = (float(value) - info['min']) / denominator
            else:
                norm = 0.0
            sample_payload[key] = {
                'raw': float(value),
                'normalized': round(norm, 6),
            }
        if sample_payload:
            normalized[sample] = sample_payload
    return normalized


def build_context(samples, headers, order):
    lines = []
    for sample in sorted(samples):
        lines.append('Sample {}'.format(sample))
        for key in order:
            stats = samples[sample].get(key)
            if not stats:
                continue
            meta = headers.get(key, {})
            title = meta.get('title', key)
            description = meta.get('description')
            raw_value = stats['raw']
            normalized_value = stats['normalized']
            raw_display = '{:.4g}'.format(raw_value)
            normalized_display = '{:.4f}'.format(normalized_value)
            if description:
                line = (
                    f'  - {title} ({key}): raw {raw_display} normalized '
                    f'{normalized_display} | {description}'
                )
            else:
                line = (
                    f'  - {title} ({key}): raw {raw_display} '
                    f'normalized {normalized_display}'
                )
            lines.append(line)
        lines.append('')
    return '\n'.join(lines).strip()


def build_metrics_metadata(ranges, headers):
    metadata = {}
    for key, info in ranges.items():
        meta = headers.get(key, {})
        metadata[key] = {
            'title': meta.get('title', key),
            'description': meta.get('description'),
            'min': info['min'],
            'max': info['max'],
        }
    return metadata


def normalize(input_dir, json_output, text_output):
    payload = load_payload(input_dir)
    headers, order = collect_headers(payload)
    samples = collect_samples(payload)
    values = numeric_values(samples)
    ranges = metric_ranges(values)
    normalized = normalize_samples(samples, ranges)
    context_text = build_context(normalized, headers, order)
    metrics_metadata = build_metrics_metadata(ranges, headers)
    output_payload = {
        'metrics': metrics_metadata,
        'samples': normalized,
        'context_text': context_text,
    }
    if json_output:
        json_path = Path(json_output)
        with json_path.open('w', encoding='utf-8') as handle:
            json.dump(output_payload, handle, indent=2)
    if text_output:
        text_path = Path(text_output)
        with text_path.open('w', encoding='utf-8') as handle:
            handle.write(context_text)
    if not text_output:
        print(context_text)
