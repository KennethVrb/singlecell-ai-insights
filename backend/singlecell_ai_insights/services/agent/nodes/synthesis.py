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
    if state.get('table_url'):
        artifact_instructions.append(
            '- Mention that a CSV download is available '
            'at the end of your response'
        )
    if state.get('plot_url'):
        artifact_instructions.append(
            '- Mention that a plot visualization is available'
        )

    prompt = f"""
    You are a genomics QC assistant for MultiQC (nf-core/scrnaseq).
    
    Conversation History:
    {history_text if history_text else 'None'}
    
    Current Question: {state['question']}

    Context (table preview and module snippets):
    {chr(10).join(context_blocks) if context_blocks else 'None'}

    Instructions:
    - Answer concisely and concretely using markdown formatting.
    - If the user question has nothing to with the run, 
      act like any normal assistant. Just answer based on your knowledge.
    - Dont mention anything about system given context. 
      The users dont care what context your were given.
    - When referencing modules, cite inline like 
        fastqc, umi_tools, picard if relevant.
    - If recommending actions, be specific
        (e.g., "trim adapters", "increase sequencing depth", 
        "adjust UMI dedup settings").
    - Use conversation history to provide contextual answers.
    {chr(10).join(artifact_instructions) if artifact_instructions else ''}
    """

    msg = llm.invoke(prompt)
    answer = msg.content

    # Append artifact links after LLM response to avoid truncation
    if state.get('table_url'):
        answer += '\n\n---\n\n**📊 Download Full Data**\n\n'
        answer += f'[Download MultiQC Data (CSV)]({state["table_url"]})'
    if state.get('plot_url'):
        answer += '\n\n---\n\n**📈 Visualization**\n\n'
        answer += f'![Quality Metrics Plot]({state["plot_url"]})'

    state['answer'] = answer
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
