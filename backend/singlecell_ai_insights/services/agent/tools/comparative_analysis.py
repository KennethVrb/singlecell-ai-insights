"""Comparative analysis utilities for sample comparisons."""

import statistics


def calculate_sample_statistics(samples, metric_key):
    """
    Calculate statistics for a metric across samples.

    Returns:
        dict with mean, stdev, min, max, outliers
    """
    values = []
    sample_values = {}

    for sample, metrics in samples.items():
        value = metrics.get(metric_key)
        if isinstance(value, (int, float)):
            values.append(float(value))
            sample_values[sample] = float(value)

    if len(values) < 2:
        return None

    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0
    min_val = min(values)
    max_val = max(values)

    # Identify outliers (>2 standard deviations from mean)
    outliers = []
    if stdev > 0:
        for sample, value in sample_values.items():
            z_score = abs(value - mean) / stdev
            if z_score > 2:
                outliers.append(
                    {
                        'sample': sample,
                        'value': value,
                        'z_score': round(z_score, 2),
                        'deviation': 'high' if value > mean else 'low',
                    }
                )

    return {
        'metric_key': metric_key,
        'mean': round(mean, 3),
        'stdev': round(stdev, 3),
        'min': round(min_val, 3),
        'max': round(max_val, 3),
        'count': len(values),
        'outliers': outliers,
        'sample_values': sample_values,
    }


def compare_samples(samples, metric_key):
    """
    Generate pairwise comparisons between samples for a metric.

    Returns:
        list of comparison dicts with sample pairs and ratios
    """
    sample_values = {}
    for sample, metrics in samples.items():
        value = metrics.get(metric_key)
        if isinstance(value, (int, float)) and value > 0:
            sample_values[sample] = float(value)

    if len(sample_values) < 2:
        return []

    comparisons = []
    sample_list = sorted(
        sample_values.items(), key=lambda x: x[1], reverse=True
    )

    # Compare highest vs lowest
    if len(sample_list) >= 2:
        highest = sample_list[0]
        lowest = sample_list[-1]
        ratio = highest[1] / lowest[1] if lowest[1] > 0 else float('inf')

        comparisons.append(
            {
                'higher_sample': highest[0],
                'higher_value': round(highest[1], 3),
                'lower_sample': lowest[0],
                'lower_value': round(lowest[1], 3),
                'ratio': round(ratio, 2),
                'difference': round(highest[1] - lowest[1], 3),
            }
        )

    return comparisons


def identify_outliers(samples, metric_key, threshold=2.0):
    """
    Identify outlier samples for a specific metric.

    Args:
        samples: Sample metrics dict
        metric_key: Metric to analyze
        threshold: Z-score threshold (default 2.0)

    Returns:
        list of outlier samples with details
    """
    stats = calculate_sample_statistics(samples, metric_key)
    if not stats or stats['stdev'] == 0:
        return []

    return stats['outliers']


def generate_comparative_summary(samples, metric_key):
    """
    Generate a human-readable comparative summary.

    Returns:
        dict with summary text and key insights
    """
    stats = calculate_sample_statistics(samples, metric_key)
    if not stats:
        return None

    comparisons = compare_samples(samples, metric_key)

    insights = []

    # Outlier insights
    if stats['outliers']:
        for outlier in stats['outliers']:
            direction = 'higher' if outlier['deviation'] == 'high' else 'lower'
            insights.append(
                f'{outlier["sample"]} is {outlier["z_score"]}SD {direction} '
                'than average'
            )

    # Comparison insights
    if comparisons:
        comp = comparisons[0]
        if comp['ratio'] > 2:
            insights.append(
                f'{comp["higher_sample"]} has {comp["ratio"]}x higher '
                f'{metric_key} than {comp["lower_sample"]}'
            )

    summary_text = (
        f'Metric: {metric_key}\n'
        f'Mean: {stats["mean"]} (±{stats["stdev"]})\n'
        f'Range: {stats["min"]} - {stats["max"]}\n'
        f'Outliers: {len(stats["outliers"])} of {stats["count"]} samples'
    )

    return {
        'summary': summary_text,
        'insights': insights,
        'stats': stats,
        'comparisons': comparisons,
    }
