"""MultiQC plot and table discovery and URL generation."""

from ..config import REPORTS_BUCKET
from .s3_utils import generate_presigned_url

# Mapping of metric keywords to MultiQC plot filenames
METRIC_TO_PLOT_MAP = {
    'duplication': 'mqc_fastqc_sequence_duplication_levels_plot_1.png',
    'duplicate': 'mqc_fastqc_sequence_duplication_levels_plot_1.png',
    'dup': 'mqc_fastqc_sequence_duplication_levels_plot_1.png',
    'quality': 'mqc_fastqc_per_base_sequence_quality_plot_1.png',
    'base_quality': 'mqc_fastqc_per_base_sequence_quality_plot_1.png',
    'sequence_quality': 'mqc_fastqc_per_sequence_quality_scores_plot_1.png',
    'gc': 'mqc_fastqc_per_sequence_gc_content_plot_Percentages.png',
    'gc_content': 'mqc_fastqc_per_sequence_gc_content_plot_Percentages.png',
    'n_content': 'mqc_fastqc_per_base_n_content_plot_1.png',
    'counts': 'mqc_fastqc_sequence_counts_plot_1.png',
    'read_count': 'mqc_fastqc_sequence_counts_plot_1.png',
    'reads': 'mqc_fastqc_sequence_counts_plot_1.png',
}


def find_plot_for_metric(metric_key, question=None):
    """
    Find the appropriate MultiQC plot for a given metric.

    Args:
        metric_key: The metric key being analyzed
        question: Optional user question for additional context

    Returns:
        str: Plot filename or None if no match found
    """
    if not metric_key:
        return None

    # Check direct metric key match
    metric_lower = metric_key.lower()
    for keyword, plot_file in METRIC_TO_PLOT_MAP.items():
        if keyword in metric_lower:
            return plot_file

    # Check question for additional context
    if question:
        question_lower = question.lower()
        for keyword, plot_file in METRIC_TO_PLOT_MAP.items():
            if keyword in question_lower:
                return plot_file

    return None


def generate_plot_url(run_id, plot_filename):
    """
    Generate presigned URL for a MultiQC plot.

    Args:
        run_id: The run ID
        plot_filename: Name of plot file (e.g., 'mqc_fastqc_..._plot_1.png')

    Returns:
        str: Presigned S3 URL
    """
    key = f'{run_id}/pubdir/multiqc/multiqc_plots/png/{plot_filename}'
    return generate_presigned_url(REPORTS_BUCKET, key)


def find_and_generate_plot_url(run_id, metric_key, question=None):
    """
    Find appropriate plot and generate presigned URL.

    Args:
        run_id: The run ID
        metric_key: The metric being analyzed
        question: Optional user question

    Returns:
        str: Presigned URL or None if no plot found
    """
    plot_file = find_plot_for_metric(metric_key, question)
    if not plot_file:
        return None

    return generate_plot_url(run_id, plot_file)


def generate_table_url(run_id, table_filename):
    """
    Generate presigned URL for a MultiQC data table.

    Args:
        run_id: The run ID
        table_filename: Name of table file (e.g., 'multiqc_general_stats.txt')

    Returns:
        str: Presigned S3 URL
    """
    key = f'{run_id}/pubdir/multiqc/multiqc_data/{table_filename}'
    return generate_presigned_url(REPORTS_BUCKET, key)


def find_and_generate_table_url(run_id, metric_key, question=None):
    """
    Find appropriate table and generate presigned URL.

    Args:
        run_id: The run ID
        metric_key: The metric being analyzed
        question: Optional user question

    Returns:
        str: Presigned URL or None if no table found
    """
    # For most metrics, use the corresponding plot data table
    plot_file = find_plot_for_metric(metric_key, question)
    if plot_file:
        # Convert plot filename to data table filename
        # e.g., mqc_fastqc_..._plot_1.png -> mqc_fastqc_..._plot_1.txt
        table_file = plot_file.replace('.png', '.txt')
        return generate_table_url(run_id, table_file)

    # Fallback to general stats table
    return generate_table_url(run_id, 'multiqc_general_stats.txt')
