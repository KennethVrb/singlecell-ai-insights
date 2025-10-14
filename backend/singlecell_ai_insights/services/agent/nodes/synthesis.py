"""LLM synthesis node."""

from ..config import llm


def synthesize(state):
    """Synthesize final answer using LLM with context."""
    # Build compact context
    context_blocks = []

    # Table preview
    if state.get('tabular'):
        rows = state['tabular'][:10]
        if rows:
            header = list(rows[0].keys())
            lines = [','.join(header)]
            for r in rows:
                lines.append(','.join(str(r[h]) for h in header))
            context_blocks.append('TABLE_PREVIEW\n' + '\n'.join(lines))

    # Retrieved panels
    if state.get('retrieved'):
        for d in state['retrieved'][:4]:
            mod = d.metadata.get('module')
            snippet = d.page_content[:800]
            context_blocks.append(f'[{mod}] {snippet}')

    # Artifact links
    links = []
    if state.get('table_url'):
        links.append(f'CSV: {state["table_url"]}')
    if state.get('plot_url'):
        links.append(f'Plot: {state["plot_url"]}')

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

    prompt = f"""
    You are a genomics QC assistant for MultiQC (nf-core/scrnaseq).
    
    Conversation History:
    {history_text if history_text else 'None'}
    
    Current Question: {state['question']}

    Artifacts (presigned):
    {chr(10).join(links) if links else 'None'}

    Context (table preview and module snippets):
    {chr(10).join(context_blocks) if context_blocks else 'None'}

    Instructions:
    - Answer concisely and concretely.
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
    """

    msg = llm.invoke(prompt)
    state['answer'] = msg.content
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
    return state
