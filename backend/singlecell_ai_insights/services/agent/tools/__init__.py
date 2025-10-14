"""Agent tools package."""

from .comparative_analysis import (
    calculate_sample_statistics,
    compare_samples,
    generate_comparative_summary,
    identify_outliers,
)
from .multiqc_parser import (
    collect_general_stats_meta,
    extract_fastqc_module_statuses,
    extract_general_stats_samples,
    infer_metric_key_from_question,
)
from .multiqc_plots import (
    find_and_generate_plot_url,
    find_and_generate_table_url,
    find_plot_for_metric,
)
from .s3_utils import (
    generate_presigned_url,
    load_json_from_s3,
    put_s3_bytes_and_presign,
)
from .vector_store import (
    build_fastqc_status_panels,
    build_general_stats_panels,
)

__all__ = [
    'build_fastqc_status_panels',
    'build_general_stats_panels',
    'calculate_sample_statistics',
    'collect_general_stats_meta',
    'compare_samples',
    'extract_fastqc_module_statuses',
    'extract_general_stats_samples',
    'find_and_generate_plot_url',
    'find_and_generate_table_url',
    'find_plot_for_metric',
    'generate_comparative_summary',
    'generate_presigned_url',
    'identify_outliers',
    'infer_metric_key_from_question',
    'load_json_from_s3',
    'put_s3_bytes_and_presign',
]
