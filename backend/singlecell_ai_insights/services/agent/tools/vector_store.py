"""Vector store document builders."""

from langchain.docstore.document import Document


def build_general_stats_panels(samples, key_meta):
    """Build vector store documents from general stats."""
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
        content = f'Sample: {sample}\n' + '\n'.join(lines)
        panels.append(
            Document(
                page_content=content,
                metadata={'module': 'general_stats', 'sample': sample},
            )
        )
    return panels


def build_fastqc_status_panels(module_statuses):
    """Build vector store documents from FastQC module statuses."""
    panels = []
    for sample, statuses in module_statuses.items():
        if not statuses:
            continue

        lines = []
        failed = []
        warned = []
        passed = []

        for module_name, status in sorted(statuses.items()):
            readable_name = module_name.replace('_', ' ').title()
            lines.append(f'{readable_name}: {status}')

            if status == 'fail':
                failed.append(readable_name)
            elif status == 'warn':
                warned.append(readable_name)
            elif status == 'pass':
                passed.append(readable_name)

        summary_parts = []
        if failed:
            summary_parts.append(f'FAILED modules: {", ".join(failed)}')
        if warned:
            summary_parts.append(f'WARNING modules: {", ".join(warned)}')

        summary = (
            ' | '.join(summary_parts)
            if summary_parts
            else 'All modules passed'
        )
        content = (
            f'Sample: {sample}\n'
            f'FastQC Status Summary: {summary}\n\n'
            f'Module Details:\n' + '\n'.join(lines)
        )

        panels.append(
            Document(
                page_content=content,
                metadata={
                    'module': 'fastqc_status',
                    'sample': sample,
                    'failed_count': len(failed),
                    'warned_count': len(warned),
                },
            )
        )

    return panels
