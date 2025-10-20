"""Agent tools package."""

from .artifact_selector import select_artifacts_with_llm
from .comparative_analysis import (
    calculate_sample_statistics,
    compare_samples,
    generate_comparative_summary,
    identify_outliers,
)
from .multiqc_artifacts import (
    generate_plot_urls_from_indices,
    generate_table_urls_from_indices,
)
from .multiqc_parser import (
    collect_general_stats_meta,
    extract_fastqc_module_statuses,
    extract_general_stats_samples,
    infer_metric_key_from_question,
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
    'generate_comparative_summary',
    'generate_plot_urls_from_indices',
    'generate_presigned_url',
    'generate_table_urls_from_indices',
    'identify_outliers',
    'infer_metric_key_from_question',
    'load_json_from_s3',
    'put_s3_bytes_and_presign',
    'select_artifacts_with_llm',
]
