"""LLM synthesis node."""

from ..config import llm


def calculate_confidence(state):
    """Calculate confidence score for the answer."""
    confidence = 0
    reasons = []

    # Factor 1: Number of retrieved documents (max 35 points)
    num_docs = len(state.get('retrieved', []))
    if num_docs >= 3:
        confidence += 35
        reasons.append(f'Found {num_docs} relevant documents')
    elif num_docs >= 1:
        confidence += 20
        reasons.append(f'Found {num_docs} document(s)')
    else:
        confidence += 5
        reasons.append('No specific documents retrieved')

    # Factor 2: Data availability (max 30 points)
    if state.get('tabular') and len(state.get('tabular', [])) > 0:
        confidence += 30
        reasons.append('Tabular data available')
    elif state.get('samples'):
        confidence += 15
        reasons.append('Sample data available')

    # Factor 3: Metric specificity (max 20 points)
    if state.get('metric_key'):
        confidence += 20
        reasons.append('Specific metric requested')
    elif state.get('retrieved'):
        confidence += 15
        reasons.append('General context available')

    # Factor 4: Question clarity (max 15 points)
    question_length = len(state.get('question', '').split())
    if 3 <= question_length <= 40:
        confidence += 15
        reasons.append('Clear question')
    else:
        confidence += 8

    return min(confidence, 100), ' • '.join(reasons)


def synthesize(state):
    """Synthesize final answer using LLM with context."""
    # Build compact context
    context_blocks = []

    # Table preview
    if state.get('tabular'):
        rows = state['tabular'][:10]
        if rows:
            # Collect all unique keys across all rows
            all_keys = set()
            for r in rows:
                all_keys.update(r.keys())
            header = sorted(all_keys)

            lines = [','.join(header)]
            for r in rows:
                lines.append(','.join(str(r.get(h, '')) for h in header))
            context_blocks.append('TABLE_PREVIEW\n' + '\n'.join(lines))

    # Retrieved panels
    if state.get('retrieved'):
        for d in state['retrieved'][:4]:
            mod = d.metadata.get('module')
            snippet = d.page_content[:800]
            context_blocks.append(f'[{mod}] {snippet}')

    # Format conversation history
    history_text = ''
    history = state.get('conversation_history', [])
    if history:
        history_lines = []
        for msg in history[-6:]:  # Last 6 messages (3 exchanges)
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]  # Truncate long messages
            history_lines.append(f'{role.upper()}: {content}')
        history_text = '\n'.join(history_lines)

    # Build artifact instructions (without actual URLs to avoid truncation)
    artifact_instructions = []
    if state.get('table_urls'):
        num_tables = len(state.get('table_urls', []))
        artifact_instructions.append(
            f'- Mention that {num_tables} data table(s) are available '
            'for download '
            '(do not include the actual links, '
            'they will be added automatically)'
        )
    if state.get('plot_urls'):
        num_plots = len(state.get('plot_urls', []))
        artifact_instructions.append(
            f'- Mention that {num_plots} plot visualization(s) '
            'are available '
            '(do not include any image markdown, it will be added '
            'automatically)'
        )

    prompt = f"""
    You are a genomics QC assistant for MultiQC (nf-core/scrnaseq).
    
    Conversation History:
    {history_text if history_text else 'None'}
    
    Current Question: {state['question']}

    Context (table preview and module snippets):
    {chr(10).join(context_blocks) if context_blocks else 'None'}

    Instructions:
    - Answer concisely and directly using markdown formatting.
    - Focus on explaining the data and providing actionable insights.
    - DO NOT include any image tags, plot links, or download links - these 
      are automatically added in separate sections after your answer.
    - If the question is unrelated to QC metrics, answer normally based on 
      your general knowledge.
    - Don't mention "context", "retrieved documents", or system internals - 
      users only care about the answer.
    - When relevant, cite specific modules inline (e.g., fastqc, umi_tools).
    - Provide specific, actionable recommendations when appropriate 
      (e.g., "trim adapters", "increase sequencing depth").
    - Use conversation history to provide contextual, coherent answers.
    {chr(10).join(artifact_instructions) if artifact_instructions else ''}
    """

    msg = llm.invoke(prompt)

    # Build clean, structured response
    answer_parts = []

    # 1. Main explanation first
    answer_parts.append(msg.content)

    # 2. Visualizations section (if any)
    if state.get('plot_urls'):
        plot_urls = state.get('plot_urls', [])
        if plot_urls:
            answer_parts.append('\n\n---\n')
            answer_parts.append('\n## 📊 Visualizations\n')
            for plot_data in plot_urls:
                label = plot_data.get('label', 'Plot')
                url = plot_data.get('url')
                answer_parts.append(f'\n### {label}\n')
                answer_parts.append(f'![{label}]({url})\n')

    # 3. Data downloads section (if any)
    if state.get('table_urls'):
        table_urls = state.get('table_urls', [])
        if table_urls:
            answer_parts.append('\n\n---\n')
            answer_parts.append('\n## 📥 Download Data\n\n')
            for table_data in table_urls:
                label = table_data.get('label', 'Data')
                url = table_data.get('url')
                answer_parts.append(f'- [{label}]({url})\n')

    state['answer'] = ''.join(answer_parts)
    # naive citations list from retrieved modules
    state['citations'] = sorted(
        list(
            {
                d.metadata.get('module')
                for d in state.get('retrieved', [])
                if d.metadata.get('module')
            }
        )
    )

    # Calculate confidence score
    confidence, explanation = calculate_confidence(state)
    state['confidence'] = confidence
    state['confidence_explanation'] = explanation

    # Add warning note for low confidence
    if confidence < 30:
        state['notes'] = [
            *state.get('notes', []),
            '⚠️ Low confidence - answer may be incomplete or uncertain',
        ]

    return state
