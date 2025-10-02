# SingleCell AI Insights – POC Specification

## 1. Overview
SingleCell AI Insights is a proof-of-concept platform that lets researchers interact with single-cell transcriptomics outputs (produced by the nf-core/singlecell pipeline) using a conversational AI assistant. Instead of navigating the HTML report, CSV exports, and PNG plots manually, users choose from a small library of preloaded reports and ask questions in natural language to obtain insights.

The POC validates feasibility across:
- **Retrieval-augmented conversation** over existing reports
- **Serverless-friendly architecture** that can later scale to many users and datasets

## 2. Goals
- Demonstrate an end-to-end flow from report selection to AI-assisted Q&A.
- Showcase how AWS Bedrock-hosted models can answer domain-specific questions using normalized HTML context.
- Provide a React web interface with intuitive report browsing and chat UX.
- Implement a Django + Django Ninja backend that exposes APIs, pulls normalized report context, and orchestrates AWS Bedrock calls.
- Normalize curated HTML reports via a lightweight Lambda job so they can be supplied as grounded context to the model.
- Deploy core services on AWS serverless primitives to illustrate scalability.

## 3. Non-Goals
- Generating or running the nf-core/singlecell pipeline itself.
- Processing arbitrary user-uploaded reports.
{{ ... }}
- Automated interpretation of every possible output artifact; scope is limited to the curated reports used in the POC.

## 4. Personas & Use Cases
### Personas
- **Bioinformatician/Scientist:** wants quick interpretations of differential expression or QC stats without digging into the full report.
- **Lab Manager:** needs high-level summaries across selected experiments.

### Key Use Cases
1. **Select report & ask general questions:** e.g., “Which clusters show the highest mitochondrial gene expression?”
2. **Dive into QC metrics:** “What is the percentage of cells filtered out?”
3. **Compare sample conditions:** “Summarize differences between treatment and control in this report.”
4. **Understand plots:** “Describe what the UMAP plot indicates for the top clusters.”
## 5. System Architecture

### High-Level Diagram (conceptual)
```
React Frontend → API Gateway → Django + Django Ninja (running on AWS Lambda)
                                   ↓
                 Normalized HTML Context in S3 (produced by Lambda ingestion)
                                   ↓
                           AWS Bedrock (LLM endpoint)
```

### Frontend (React)
- Single-page application that lists available reports and launches the chat interface.
- State management (e.g., Redux Toolkit or React Query) to cache report metadata and conversation history.
{{ ... }}
  2. `POST /chat/query`: accepts `{report_id, user_query, conversation_context}` and returns AI response.
- Business Logic:
  - Retrieve report metadata from DynamoDB or static JSON.
  - Fetch normalized HTML text (preprocessed via Lambda) for the selected report.
  - Construct a grounded prompt by combining the user question with relevant HTML sections.
  - Invoke AWS Bedrock LLM directly and return the generated answer with contextual hints.

### Data & Storage
- **S3 Buckets:** store curated HTML reports, normalized HTML text outputs, and optional CSV/PNG artifacts.
- **DynamoDB (or static config):** metadata about each report (sample name, pipeline version, normalized text location).
### AI & Retrieval
- Lambda-based ingestion:
  - Load HTML reports from S3 and strip navigation/boilerplate to produce clean text sections.
  - Optionally summarize key CSV metrics and append to the normalized text.
  - Write normalized outputs back to S3 with metadata describing section titles and offsets.
- Chat flow:
  - Backend retrieves the normalized text for the selected report, selects relevant sections, and crafts a prompt.
  - Primary model: AWS Bedrock-hosted LLM (Claude, Titan, etc.) invoked with the grounded prompt.
- Guardrails: prompt templates that emphasize factual accuracy, section citations, and user-friendly follow-ups.

### Serverless Deployment
- **Backend:** packaged as a Lambda function using container image or zipped dependencies.
- **API Gateway:** handles HTTPS routing and simple auth (API keys or Cognito for future).
- **Static Frontend Hosting:** React app deployed to S3 + CloudFront.
{{ ... }}

## 6. POC Scope & Assumptions
- Limited to 2–3 curated nf-core/singlecell reports stored in S3.
- Manual preprocessing allowed (e.g., running the HTML normalization Lambda on demand).
- Normalized HTML text is generated ahead of queries; no dedicated vector store is required for the MVP.
- Minimal auth: static API key or user selection screen; production SSO deferred.
- Observability limited to CloudWatch logs.
- Chat history stored client-side for session duration; no persistent conversation DB required.

## 7. API Contract (Draft)

### `GET /reports`
**Response:**
```json
[
  {
    "id": "report-001",
    "title": "Patient A – Baseline",
    "description": "nf-core/singlecell run 2024-01-15",
    "availableArtifacts": ["html", "csv_summary", "umap_png"]
  }
]
```

### `POST /chat/query`
**Request:**
```json
{
  "report_id": "report-001",
  "user_query": "Which clusters show high mitochondrial gene content?",
  "conversation_context": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```
**Response:**
```json
{
  "answer": "Clusters 3 and 5 show elevated mitochondrial content...",
  "citations": [
    {"type": "csv", "label": "qc_metrics.csv", "url": "https://..."}
  ],
  "follow_up_questions": [
    "Would you like a summary of the filtering thresholds?"
  ]
}
```

## 8. Security & Compliance (POC-level)
- Restrict access via API key or allowlist.
- Ensure reports contain no PHI for the demo.
- Encrypt S3 buckets at rest, enforce HTTPS in transit.
- Log Bedrock calls for auditing.

## 9. Risks & Mitigations
| Risk | Description | Mitigation |
|------|-------------|------------|
| Model hallucinations | LLM may invent results not present in reports | Strict prompt templates, provide citations, consider retrieval confidence scores |
| Limited context window | Large HTML content may exceed model limits | Chunking strategy during normalization, tailored prompt budgets |
| Latency | Serverless cold starts and LLM latency | Provisioned concurrency for critical Lambdas, caching embeddings |
| Data parsing complexity | HTML reports may need custom parsing | Use BeautifulSoup or nf-core structured outputs; preprocess offline |

## 10. Future Enhancements
- User-uploaded report ingestion with automated parsing/embedding.
- Multi-report comparisons and cross-sample analytics.
- Advanced visualization integration (interactive plots).
- Robust authentication/authorization (Cognito, IAM).
- Cost monitoring and usage analytics dashboards.
