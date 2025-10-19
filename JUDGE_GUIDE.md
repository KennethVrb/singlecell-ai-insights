# SingleCell AI Insights - Judge Guide

## Quick Start

**Application URL**: [PROVIDED AS PART OF SUBMISSION]
**Login Credentials**: [PROVIDED AS PART OF SUBMISSION]

1. Visit the application URL
2. Log in with provided credentials
3. You'll land on the **Runs Dashboard**

## What This Platform Does

SingleCell AI Insights lets you ask natural language questions about genomic quality control data from AWS HealthOmics workflows. Instead of manually inspecting MultiQC reports, you can have a conversation with an AI agent that understands the data.

## Platform Walkthrough

### 1. Runs Dashboard

When you first log in, you'll see a list of AWS HealthOmics workflow runs:

- **Run ID**: Unique identifier for each workflow
- **Status**: COMPLETED, RUNNING, FAILED, etc.
- **Workflow**: Type of pipeline (currently only scRNAseq with STARsolo)
- **Created**: When the workflow was started
- **Actions**: Click any row to view details

**Try this**: Click on any COMPLETED run to explore it.

### 2. Run Detail Page

Each run has:

- **Metadata**: Run ID, status, workflow type, creation time
- **Normalized Context**: Structured workflow parameters and settings
- **MultiQC Report**: Download button for the full quality control report
- **AI Chat Panel**: Ask questions about this run's data

### 3. AI Agent Chat

This is where the magic happens. The chat panel lets you ask questions in plain English.

**Quick start:** When you first open the chat, you'll see **suggested questions** you can click to get started:

- 📊 "Which samples have high duplication rates?"
- 🔍 "Are there any outliers in this run?"
- 📈 "What's the average GC content?"
- 📉 "Show me quality score distribution"
- ⚠️ "Which samples failed QC tests?"

**How it works:**

1. Click a suggested question or type your own in the chat input
2. The agent streams progress in real-time:
   - "Loading MultiQC data from S3..."
   - "Building vector index for semantic search..."
   - "Analyzing question..."
   - "Synthesizing final answer..."
3. You get a natural language answer with:
   - Explanation of what the data shows
   - Links to relevant tables/plots from MultiQC
   - Interpretation and next steps
   - Conversation history is maintained

## More Example Questions to Try

### Basic Quality Checks

- "Which samples have quality issues?"
- "Are there any samples that failed QC?"
- "What's the overall quality of this run?"

### Specific Metrics

- "Show me duplication rates across all samples"
- "What are the mapping rates for each sample?"
- "Display GC content distribution"

### Comparative Analysis

- "Which sample has the highest read count?"
- "Are there any outliers in the data?"
- "Compare quality metrics across samples"

### Root Cause Analysis

- "Why does sample X have low mapping rates?"
- "What could cause high duplication in sample Y?"
- "Explain the quality issues in this run"

### Follow-up Questions

The agent maintains conversation history, so you can ask follow-ups:

- "What about sample Z?" (after asking about sample Y)
- "Show me a plot of that" (after getting a table)
- "What should I do about this?" (after identifying an issue)

## Troubleshooting

**Can't log in?**

- Check credentials are correct
- Ensure cookies are enabled in your browser

**Chat not responding?**

- Check that the run status is COMPLETED
- Refresh the page and try again
- Check browser console for errors

**Artifacts not loading?**

- Presigned URLs expire after 1 hour
- Refresh the chat to get new URLs

**Questions not working well?**

- Try rephrasing the question
- Be specific about which metric or sample
- Check that the MultiQC report exists for this run

## Feedback Welcome

This is an MVP built during the hackathon. The goal is to demonstrate the potential of AI-assisted bioinformatics analysis. Feedback on:

- Agent accuracy and helpfulness
- UX and streaming experience
- Feature gaps or bugs
- Ideas for improvement
