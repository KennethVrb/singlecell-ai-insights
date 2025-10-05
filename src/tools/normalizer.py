import json

FASTQC_STATUS_KEYS = [
    'basic_statistics',
    'per_base_sequence_quality',
    'per_tile_sequence_quality',
    'per_sequence_quality_scores',
    'per_base_sequence_content',
    'per_sequence_gc_content',
    'per_base_n_content',
    'sequence_length_distribution',
    'sequence_duplication_levels',
    'overrepresented_sequences',
    'adapter_content',
]


def detect_modules(d):
    mods = set()
    # Reported data sources
    for k in d.get('report_data_sources', {}).keys():
        mods.add(k)
    # Infer from saved raw data
    for k in d.get('report_saved_raw_data', {}).keys():
        # entries look like "multiqc_fastqc", "multiqc_snippy"
        mods.add(k.replace('multiqc_', '').capitalize())
    return sorted(mods)


def extract_variant_summary(d):
    # Prefer saved raw data (Snippy), fallback to general stats block
    # if present
    snippy = (
        d.get('report_saved_raw_data', {})
        .get('multiqc_snippy', {})
        .get('multiqc', {})
    )
    if snippy:
        return {'total_variants': int(snippy.get('VariantTotal', 0))}
    # Fallback
    gs = d.get('report_general_stats_data', [])
    if gs and isinstance(gs[0], dict):
        v = gs[0].get('multiqc', {})
        return {'total_variants': int(v.get('VariantTotal', 0))}
    return {'total_variants': 0}


def coerce_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def build_fastqc_summary(sample_data):
    """
    Return dict with pass/warn/fail arrays based on standard
    FastQC sections.
    """
    result = {'pass': [], 'warn': [], 'fail': []}
    for key in FASTQC_STATUS_KEYS:
        status = sample_data.get(key)
        # status values are "pass" | "warn" | "fail"
        if status in result:
            result[status].append(
                key.replace('per_base_sequence_quality', 'per_base_quality')
                .replace('per_tile_sequence_quality', 'per_tile_quality')
                .replace(
                    'per_sequence_quality_scores',
                    'per_sequence_quality_scores',
                )
                .replace(
                    'per_base_sequence_content', 'per_base_sequence_content'
                )
                .replace('per_sequence_gc_content', 'gc_content')
                .replace('per_base_n_content', 'n_content')
                .replace('sequence_length_distribution', 'length_distribution')
                .replace(
                    'sequence_duplication_levels',
                    'sequence_duplication_levels',
                )
                .replace(
                    'overrepresented_sequences', 'overrepresented_sequences'
                )
                .replace('adapter_content', 'adapter_content')
                .replace('basic_statistics', 'basic_statistics')
            )
    return result


def extract_samples_fastqc(d):
    """Pull per-sample metrics from multiqc_fastqc block."""
    out = {}
    fastqc = d.get('report_saved_raw_data', {}).get('multiqc_fastqc', {})
    # Also try general stats for derived values like percent_fails if provided
    percent_fails_map = {}
    percent_dups_map = {}
    percent_gc_map = {}
    avg_len_map = {}
    total_reads_map = {}

    for block in d.get('report_general_stats_data', []):
        # blocks can be per-tool dicts or per-sample dict
        if not isinstance(block, dict):
            continue
        for sample, vals in block.items():
            if not isinstance(vals, dict):
                continue
            if 'percent_fails' in vals:
                percent_fails_map[sample] = coerce_float(vals['percent_fails'])
            if 'percent_duplicates' in vals:
                percent_dups_map[sample] = coerce_float(
                    vals['percent_duplicates']
                )
            if 'percent_gc' in vals:
                percent_gc_map[sample] = coerce_float(vals['percent_gc'])
            if 'avg_sequence_length' in vals:
                avg_len_map[sample] = coerce_float(vals['avg_sequence_length'])
            if 'total_sequences' in vals:
                total_reads_map[sample] = int(
                    coerce_float(vals['total_sequences'])
                )

    for sample, sdata in fastqc.items():
        # Metrics
        gc = percent_gc_map.get(sample, coerce_float(sdata.get('%GC')))
        avg_len = avg_len_map.get(
            sample,
            coerce_float(
                sdata.get('avg_sequence_length')
                or sdata.get('Sequence length')
            ),
        )
        total_reads = total_reads_map.get(
            sample, int(coerce_float(sdata.get('Total Sequences')))
        )
        # Duplicate %: prefer general-stats "percent_duplicates";
        # else 100 - deduplicated%
        dup_pct = percent_dups_map.get(sample)
        if dup_pct is None:
            dedup = coerce_float(
                sdata.get('total_deduplicated_percentage'), None
            )
            if dedup is not None:
                dup_pct = max(0.0, 100.0 - dedup)
        if dup_pct is None:
            dup_pct = 0.0

        # % of modules failed: prefer general-stats; else compute
        # from status keys
        fails_pct = percent_fails_map.get(sample)
        if fails_pct is None:
            statuses = [sdata.get(k) for k in FASTQC_STATUS_KEYS if k in sdata]
            total = len(statuses) or 1
            fails = sum(1 for s in statuses if s == 'fail')
            fails_pct = (fails / total) * 100.0

        out[sample] = {
            'gc_content_percent': round(gc, 1) if gc is not None else None,
            'avg_read_length_bp': round(avg_len, 1)
            if avg_len is not None
            else None,
            'total_reads': total_reads,
            'duplicate_reads_percent': round(dup_pct, 1),
            'failed_modules_percent': round(fails_pct, 1),
            'fastqc_summary': build_fastqc_summary(sdata),
        }
    return out


def normalize_multiqc(inp_path, out_path):
    with open(inp_path, 'r') as f:
        d = json.load(f)

    samples = extract_samples_fastqc(d)
    modules = detect_modules(d)
    variant_summary = extract_variant_summary(d)

    # High-level quality note (very short, LLM-friendly)
    # Example heuristic: flag if any sample dup% > 40 or any fail present
    issues = []
    for s, md in samples.items():
        if md['duplicate_reads_percent'] >= 40:
            issues.append(
                f'{s} high duplicates ({md["duplicate_reads_percent"]}%)'
            )
        if md['fastqc_summary']['fail']:
            issues.append(
                f'{s} failed {", ".join(md["fastqc_summary"]["fail"])}'
            )
    quality_summary = (
        'Overall high sequencing quality.'
        if not issues
        else ' ; '.join(issues)
    )

    out = {
        'summary': {
            'samples_analyzed': len(samples),
            'modules': modules,
            'variant_summary': variant_summary,
        },
        'samples': samples,
        'quality_summary': quality_summary,
    }

    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, sort_keys=False)
