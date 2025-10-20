"""LLM-based artifact (plots and tables) selection."""

import logging
import time

from ..config import llm

logger = logging.getLogger(__name__)


def select_artifacts_with_llm(question, metric_key=None):
    """
    Use LLM to intelligently select relevant plots and tables.

    Args:
        question: User's question
        metric_key: Optional metric key for context

    Returns:
        dict with 'plot_indices' and 'table_indices' lists
    """
    available_plots = [
        '0: Sequence Duplication Levels',
        '1: Per Base Sequence Quality',
        '2: Per Sequence Quality Scores',
        '3: Per Sequence GC Content',
        '4: Per Base N Content',
        '5: Sequence Counts',
        '6: Adapter Content',
        '7: Per Base Sequence Content (heatmap)',
        '8: Sequence Length Distribution',
    ]

    available_tables = [
        '0: Sequence Duplication Levels Data',
        '1: Per Base Sequence Quality Data',
        '2: Per Sequence Quality Scores Data',
        '3: Per Sequence GC Content Data (Percentages)',
        '4: Per Sequence GC Content Data (Counts)',
        '5: Per Base N Content Data',
        '6: Sequence Counts Data',
    ]

    context = f'Metric: {metric_key}' if metric_key else 'No specific metric'

    prompt = f"""You are selecting relevant MultiQC visualizations and data 
        tables for a user question.

        User Question: "{question}"
        Context: {context}

        Available Plots:
        {chr(10).join(available_plots)}

        Available Data Tables:
        {chr(10).join(available_tables)}

        Task: Select the most relevant plots and tables to help answer 
        this question.

        Rules:
        - If the question is general or asks for "overview"/"summary"/"all", 
        select multiple items
        - If the question is specific (e.g., "duplication rates"), 
        select only relevant items
        - If the question asks for data/tables/csv, prioritize tables
        - If the question asks for plots/charts/visualizations, prioritize 
          plots
        - If unsure, select 2-4 most relevant items
        - Return empty lists if the question is not about QC metrics

        Respond in this exact format:
        PLOTS: [comma-separated indices, e.g., 0,1,2]
        TABLES: [comma-separated indices, e.g., 0,1]
        REASONING: [brief explanation]

        Example responses:
        PLOTS: 0,1,2
        TABLES: 0,1
        REASONING: Question asks about quality and duplication, showing 
        relevant plots and data tables.

        PLOTS: 3
        TABLES: 3,4
        REASONING: Question specifically about GC content, showing GC plot and 
        both data tables.

        PLOTS:
        TABLES:
        REASONING: Question is not about QC metrics, no artifacts needed.
        """

    try:
        # Add small delay to avoid rapid-fire requests
        time.sleep(0.5)

        response = llm.invoke(prompt)
        content = response.content.strip()

        logger.info(f'LLM artifact selection for question: {question[:50]}...')
        logger.debug(f'LLM response: {content}')

        plot_indices = []
        table_indices = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('PLOTS:'):
                indices_str = line.replace('PLOTS:', '').strip()
                if indices_str:
                    try:
                        plot_indices = [
                            int(i.strip())
                            for i in indices_str.split(',')
                            if i.strip()
                        ]
                    except ValueError:
                        logger.warning(
                            f'Failed to parse plot indices: {indices_str}'
                        )
            elif line.startswith('TABLES:'):
                indices_str = line.replace('TABLES:', '').strip()
                if indices_str:
                    try:
                        table_indices = [
                            int(i.strip())
                            for i in indices_str.split(',')
                            if i.strip()
                        ]
                    except ValueError:
                        logger.warning(
                            f'Failed to parse table indices: {indices_str}'
                        )

        logger.info(
            f'Selected {len(plot_indices)} plots, {len(table_indices)} tables'
        )

        return {
            'plot_indices': plot_indices,
            'table_indices': table_indices,
        }

    except Exception as e:
        logger.error(f'Error in LLM artifact selection: {e}')
        return {'plot_indices': [0, 1, 2], 'table_indices': [0, 1]}
