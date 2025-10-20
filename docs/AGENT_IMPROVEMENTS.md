# Agent Service Improvement Roadmap

This document outlines potential improvements and enhancements for the SingleCell AI Insights agent service.

## Recent Changes (Completed)

### Architecture Refactoring ✅
- **Modularized agent service** into separate packages:
  - `nodes/` - Graph workflow nodes (analysis, artifacts, synthesis)
  - `tools/` - Reusable utilities (parsers, comparisons, vector store)
  - `config.py` - Centralized configuration
  - `exceptions.py` - Custom error handling
  - `graph.py` - LangGraph workflow definition

### MultiQC Integration ✅
- **Replaced custom artifact generation** with MultiQC outputs:
  - Tables: Link to existing MultiQC TSV files instead of generating CSVs
  - Plots: Link to existing MultiQC PNG files instead of matplotlib generation
  - Benefits: Better quality, more plot types, less code, consistent with MultiQC
- **Smart table selection**:
  - General stats table for summary metrics (duplication, GC, counts)
  - Module-specific tables for detailed analysis (FastQC, Snippy)
- **Plot mapping**: Keyword-based mapping to MultiQC plot files

### Comparative Analysis ✅
- **Outlier detection**: Identify samples that deviate from the mean
- **Sample comparisons**: Statistical analysis between samples
- **Summary generation**: LLM-powered comparative insights

### Frontend Improvements ✅
- **Inline artifact rendering**: Tables and plots embedded in markdown responses
- **Download buttons**: Styled download links for MultiQC data
- **Responsive tables**: Horizontal scroll, proper sizing, TSV parsing
- **Image constraints**: Max height/width to prevent overflow

---

## Proposed Improvements

### 1. Enhanced Natural Language Understanding

**Current State:**
- Basic keyword matching for intent detection
- Simple metric key inference from question text
- Limited support for complex queries

**Improvements:**
- [ ] **Better intent classification**
  - Use LLM to classify intent (comparison, outlier detection, general QC, etc.)
  - Support multi-intent queries ("Show me duplication AND quality")
  - Handle negations ("samples WITHOUT high duplication")

- [ ] **Advanced query parsing**
  - Extract multiple metrics from single question
  - Support aggregations: "What's the average GC content?"
  - Handle conditional queries: "Which samples have >30% duplication AND <40% GC?"
  - Support ranking: "Top 3 samples by quality score"

- [ ] **Entity extraction**
  - Identify specific sample names in questions
  - Extract numeric thresholds ("samples with >50% duplication")
  - Recognize module names (FastQC, Snippy, etc.)

**Implementation:**
```python
# Add to nodes/analysis.py
def classify_intent(state):
    """Use LLM to classify user intent and extract entities."""
    prompt = f"""
    Classify the user's intent and extract key entities.
    
    Question: {state['question']}
    
    Return JSON:
    {{
      "intent": "comparison|outlier|general_qc|specific_metric",
      "metrics": ["list", "of", "metrics"],
      "samples": ["specific", "samples"],
      "thresholds": {{"metric": value}},
      "aggregation": "avg|max|min|count|null"
    }}
    """
    # Parse LLM response and update state
```

---

### 2. Quality Thresholds & Automated Alerts

**Current State:**
- No automatic quality flagging
- Users must interpret metrics manually

**Improvements:**
- [ ] **Configurable thresholds**
  - Define quality thresholds per metric (e.g., duplication >30% = warning)
  - Support different thresholds for different experiment types
  - Allow user customization via UI or config file

- [ ] **Automatic flagging**
  - Scan all samples on load and flag issues
  - Prioritize critical vs warning issues
  - Generate summary of all QC issues

- [ ] **Actionable recommendations**
  - Suggest specific fixes based on failures
  - Link to relevant documentation
  - Provide example commands/parameters

**Implementation:**
```python
# Add to tools/quality_thresholds.py
THRESHOLDS = {
    'duplication': {'warning': 30, 'critical': 50},
    'gc_content': {'min': 35, 'max': 65},
    'failed_tests': {'warning': 1, 'critical': 3},
}

def check_quality_thresholds(samples, thresholds=THRESHOLDS):
    """Flag samples that exceed quality thresholds."""
    issues = []
    for sample, metrics in samples.items():
        for metric, value in metrics.items():
            if metric in thresholds:
                # Check thresholds and generate issues
                pass
    return issues

# Add to nodes/analysis.py
def flag_quality_issues(state):
    """Automatically flag quality issues in samples."""
    issues = check_quality_thresholds(state['samples'])
    state['quality_issues'] = issues
    return state
```

---

### 3. Multi-Run Comparisons

**Current State:**
- Analysis limited to single run
- No cross-run comparisons

**Improvements:**
- [ ] **Cross-run analysis**
  - Compare metrics across multiple runs
  - Identify trends over time
  - Detect batch effects

- [ ] **Run grouping**
  - Group runs by experiment, date, or custom tags
  - Aggregate statistics across groups
  - Compare groups (e.g., before/after protocol change)

- [ ] **Differential analysis**
  - Identify metrics that differ significantly between runs
  - Visualize trends across runs
  - Generate comparative reports

**Implementation:**
```python
# Add to api/runs/views.py
class RunComparisonView(APIView):
    """Compare metrics across multiple runs."""
    def post(self, request):
        run_ids = request.data.get('run_ids', [])
        metric = request.data.get('metric')
        # Fetch and compare runs
        return Response(comparison_data)

# Add to services/agent/tools/multi_run.py
def compare_runs(run_ids, metric_key):
    """Compare a specific metric across multiple runs."""
    # Load MultiQC data for each run
    # Aggregate and compare
    pass
```

---

### 4. Citation & Source Tracking

**Current State:**
- Basic module-level citations
- No link back to specific data sources

**Improvements:**
- [ ] **Detailed citations**
  - Link to specific MultiQC sections/plots
  - Show which samples contributed to answer
  - Cite specific data points used

- [ ] **Interactive citations**
  - Click citation to view source data
  - Highlight relevant sections in MultiQC report
  - Show data provenance chain

- [ ] **Export citations**
  - Generate bibliography for reports
  - Include data DOIs when available
  - Format citations in standard styles

**Implementation:**
```python
# Enhance nodes/synthesis.py
def generate_detailed_citations(state):
    """Generate detailed citations with source links."""
    citations = []
    for doc in state.get('retrieved', []):
        citation = {
            'module': doc.metadata.get('module'),
            'section': doc.metadata.get('section'),
            'samples': doc.metadata.get('samples', []),
            'url': f"#multiqc_{doc.metadata.get('module')}"
        }
        citations.append(citation)
    return citations
```

---

### 5. Follow-up Question Suggestions

**Current State:**
- No guidance for next steps
- Users must think of follow-up questions

**Improvements:**
- [ ] **Context-aware suggestions**
  - Suggest related questions based on current answer
  - Adapt suggestions to detected issues
  - Prioritize most relevant follow-ups

- [ ] **Progressive disclosure**
  - Start with high-level overview
  - Suggest drilling down into specifics
  - Guide users through QC workflow

- [ ] **Smart prompts**
  - "Would you like to see quality scores?"
  - "Should I compare these samples?"
  - "Want to identify outliers?"

**Implementation:**
```python
# Add to nodes/synthesis.py
def suggest_followups(state):
    """Generate contextual follow-up question suggestions."""
    suggestions = []
    
    # If showing duplication, suggest quality
    if 'duplication' in state.get('metric_key', ''):
        suggestions.append("Show me per-base quality scores")
    
    # If outliers detected, suggest comparison
    if state.get('outliers'):
        suggestions.append("Compare outlier samples to the rest")
    
    # If failures detected, suggest investigation
    if any('FAILED' in str(s) for s in state.get('samples', {}).values()):
        suggestions.append("Which tests failed and why?")
    
    state['suggestions'] = suggestions[:3]  # Limit to 3
    return state
```

---

### 6. Export & Report Generation

**Current State:**
- No export functionality beyond individual downloads
- No report generation

**Improvements:**
- [ ] **PDF/HTML reports**
  - Generate comprehensive QC reports
  - Include key metrics, plots, and recommendations
  - Customizable templates

- [ ] **Data export**
  - Export filtered/analyzed data in various formats
  - Include metadata and analysis parameters
  - Support batch export for multiple runs

- [ ] **Shareable summaries**
  - Generate shareable links to analysis results
  - Create presentation-ready slides
  - Export to common formats (Word, PowerPoint, etc.)

**Implementation:**
```python
# Add to api/runs/views.py
class RunReportView(APIView):
    """Generate comprehensive QC report."""
    def post(self, request, pk):
        run = get_object_or_404(Run, pk=pk)
        format = request.data.get('format', 'pdf')  # pdf, html, docx
        
        # Generate report using template
        report = generate_report(run, format)
        
        return FileResponse(report, filename=f'run_{pk}_report.{format}')
```

---

### 7. Conversation Memory & Context

**Current State:**
- Basic conversation history in state
- Limited context awareness

**Improvements:**
- [ ] **Persistent conversation memory**
  - Remember user preferences across sessions
  - Track frequently asked questions
  - Learn from user feedback

- [ ] **Context-aware responses**
  - Reference previous questions/answers
  - Maintain analysis context across questions
  - Support "show me more" style follow-ups

- [ ] **Session management**
  - Save/load analysis sessions
  - Share sessions with team members
  - Export conversation history

**Implementation:**
```python
# Enhance models/run.py
class ConversationSession(models.Model):
    """Persistent conversation sessions."""
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    """Individual messages in a session."""
    session = models.ForeignKey(ConversationSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

### 8. Advanced Visualizations

**Current State:**
- Links to static MultiQC plots
- No interactive visualizations

**Improvements:**
- [ ] **Interactive plots**
  - Generate Plotly/D3.js interactive charts
  - Support zoom, pan, hover tooltips
  - Allow filtering/highlighting samples

- [ ] **Custom visualizations**
  - Create visualizations not in MultiQC
  - Support custom plot types (scatter, heatmap, etc.)
  - Generate comparison plots across runs

- [ ] **Plot customization**
  - Allow users to customize colors, labels
  - Support different plot styles
  - Export plots in various formats

**Implementation:**
```python
# Add to tools/plotting.py
def generate_interactive_plot(data, plot_type='scatter'):
    """Generate interactive Plotly visualization."""
    import plotly.graph_objects as go
    
    if plot_type == 'scatter':
        fig = go.Figure(data=go.Scatter(
            x=data['x'],
            y=data['y'],
            mode='markers',
            text=data['labels']
        ))
    
    # Convert to JSON for frontend
    return fig.to_json()
```

---

### 9. Performance Optimization

**Current State:**
- Loads full MultiQC data on every request
- No caching of expensive operations

**Improvements:**
- [ ] **Caching strategy**
  - Cache parsed MultiQC data
  - Cache vector store indices
  - Cache LLM responses for common questions

- [ ] **Lazy loading**
  - Load only required data sections
  - Stream large responses
  - Paginate results

- [ ] **Background processing**
  - Pre-process MultiQC data on run completion
  - Build indices asynchronously
  - Queue expensive operations

**Implementation:**
```python
# Add to services/agent/config.py
from django.core.cache import cache

def get_cached_multiqc_data(run_id):
    """Get MultiQC data with caching."""
    cache_key = f'multiqc_data_{run_id}'
    data = cache.get(cache_key)
    
    if data is None:
        data = load_json_from_s3(REPORTS_BUCKET, f'{run_id}/pubdir/multiqc/multiqc_data/multiqc_data.json')
        cache.set(cache_key, data, timeout=3600)  # 1 hour
    
    return data
```

---

### 10. User Feedback & Learning

**Current State:**
- No feedback mechanism
- No learning from user interactions

**Improvements:**
- [ ] **Feedback collection**
  - Thumbs up/down on responses
  - Report incorrect/unhelpful answers
  - Suggest improvements

- [ ] **Learning from feedback**
  - Track which responses are helpful
  - Identify common failure patterns
  - Improve prompts based on feedback

- [ ] **A/B testing**
  - Test different prompt strategies
  - Compare LLM models
  - Optimize for user satisfaction

**Implementation:**
```python
# Add to api/runs/views.py
class MessageFeedbackView(APIView):
    """Collect feedback on agent responses."""
    def post(self, request, message_id):
        feedback = request.data.get('feedback')  # 'helpful', 'not_helpful'
        comment = request.data.get('comment', '')
        
        # Store feedback
        MessageFeedback.objects.create(
            message_id=message_id,
            feedback=feedback,
            comment=comment,
            user=request.user
        )
        
        return Response({'status': 'success'})
```

---

## Priority Recommendations

Based on impact and effort, here's a suggested implementation order:

### High Priority (High Impact, Moderate Effort)
1. **Quality Thresholds & Alerts** - Immediate value for users
2. **Enhanced NLU** - Significantly improves user experience
3. **Follow-up Suggestions** - Guides users through workflow

### Medium Priority (High Impact, High Effort)
4. **Multi-Run Comparisons** - Valuable for longitudinal studies
5. **Export & Reports** - Essential for sharing results
6. **Performance Optimization** - Improves scalability

### Lower Priority (Nice to Have)
7. **Advanced Visualizations** - Enhances but not critical
8. **Citation Improvements** - Useful for research contexts
9. **User Feedback System** - Long-term improvement
10. **Conversation Memory** - Quality of life enhancement

---

## Technical Considerations

### LLM Costs
- Monitor token usage for expensive operations
- Consider caching common responses
- Use smaller models for classification tasks
- Implement rate limiting for production

### Scalability
- Design for multiple concurrent users
- Consider async processing for slow operations
- Implement proper database indexing
- Use CDN for static assets (plots, reports)

### Testing
- Add unit tests for new tools/nodes
- Integration tests for graph workflows
- End-to-end tests for critical paths
- Load testing for performance validation

### Documentation
- Document all new features
- Provide examples for complex queries
- Create user guides for advanced features
- Maintain API documentation

---

## Contributing

When implementing improvements:

1. **Follow existing patterns** - Maintain consistency with current architecture
2. **Keep it modular** - New features should be self-contained
3. **Test thoroughly** - Add tests for new functionality
4. **Document changes** - Update relevant documentation
5. **Consider backwards compatibility** - Don't break existing features

---

## Notes

- This roadmap is a living document and should be updated as priorities change
- User feedback should drive prioritization
- Consider technical debt when planning new features
- Balance new features with maintenance and bug fixes
