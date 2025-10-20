"""
MultiQC artifacts (plots and tables) URL generation from LLM-selected indices.
"""

from ..config import REPORTS_BUCKET
from .s3_utils import generate_presigned_url

# All available MultiQC plots with labels
ALL_PLOTS = [
    (
        'mqc_fastqc_sequence_duplication_levels_plot_1.png',
        'Sequence Duplication Levels',
    ),
    (
        'mqc_fastqc_per_base_sequence_quality_plot_1.png',
        'Per Base Sequence Quality',
    ),
    (
        'mqc_fastqc_per_sequence_quality_scores_plot_1.png',
        'Per Sequence Quality Scores',
    ),
    (
        'mqc_fastqc_per_sequence_gc_content_plot_Percentages.png',
        'Per Sequence GC Content',
    ),
    ('mqc_fastqc_per_base_n_content_plot_1.png', 'Per Base N Content'),
    ('mqc_fastqc_sequence_counts_plot_1.png', 'Sequence Counts'),
    ('mqc_fastqc_adapter_content_plot_1.png', 'Adapter Content'),
    (
        'mqc_fastqc_per_base_sequence_content_plot_1.png',
        'Per Base Sequence Content',
    ),
    (
        'mqc_fastqc_sequence_length_distribution_plot_1.png',
        'Sequence Length Distribution',
    ),
]


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


def generate_plot_urls_from_indices(run_id, indices):
    """
    Generate presigned URLs for plots by indices.

    Args:
        run_id: The run ID
        indices: List of plot indices (0-8)

    Returns:
        list: List of dicts with 'url' and 'label' keys
    """
    if not indices:
        return []

    valid_indices = [i for i in indices if 0 <= i < len(ALL_PLOTS)]
    return [
        {
            'url': generate_plot_url(run_id, ALL_PLOTS[i][0]),
            'label': ALL_PLOTS[i][1],
        }
        for i in valid_indices
    ]


# All available MultiQC data tables with labels
ALL_TABLES = [
    (
        'mqc_fastqc_sequence_duplication_levels_plot_1.txt',
        'Sequence Duplication Levels Data',
    ),
    (
        'mqc_fastqc_per_base_sequence_quality_plot_1.txt',
        'Per Base Sequence Quality Data',
    ),
    (
        'mqc_fastqc_per_sequence_quality_scores_plot_1.txt',
        'Per Sequence Quality Scores Data',
    ),
    (
        'mqc_fastqc_per_sequence_gc_content_plot_Percentages.txt',
        'Per Sequence GC Content Data (Percentages)',
    ),
    (
        'mqc_fastqc_per_sequence_gc_content_plot_Counts.txt',
        'Per Sequence GC Content Data (Counts)',
    ),
    (
        'mqc_fastqc_per_base_n_content_plot_1.txt',
        'Per Base N Content Data',
    ),
    (
        'mqc_fastqc_sequence_counts_plot_1.txt',
        'Sequence Counts Data',
    ),
]


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


def generate_table_urls_from_indices(run_id, indices):
    """
    Generate presigned URLs for tables by indices.

    Args:
        run_id: The run ID
        indices: List of table indices (0-6)

    Returns:
        list: List of dicts with 'url' and 'label' keys
    """
    if not indices:
        return []

    valid_indices = [i for i in indices if 0 <= i < len(ALL_TABLES)]
    return [
        {
            'url': generate_table_url(run_id, ALL_TABLES[i][0]),
            'label': ALL_TABLES[i][1],
        }
        for i in valid_indices
    ]
