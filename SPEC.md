# SingleCell AI Insights – POC Specification

## 1. Overview
SingleCell AI Insights is a proof-of-concept platform that lets researchers interact with single-cell transcriptomics outputs (produced by the nf-core/singlecell pipeline) using a conversational AI assistant. Instead of navigating the HTML report, CSV exports, and PNG plots manually, users choose from a small library of preloaded reports and ask questions in natural language to obtain insights.

The POC validates feasibility across:
- **Multimodal data understanding** (HTML, CSV, PNG summaries)
- **Retrieval-augmented conversation** over existing reports
- **Serverless-friendly architecture** that can later scale to many users and datasets

## 2. Goals
- Demonstrate an end-to-end flow from report selection to AI-assisted Q&A.
- Showcase how AWS Bedrock-hosted models (accessed via LangChain) can answer domain-specific questions.
- Provide a React web interface with intuitive report browsing and chat UX.
- Implement a Django + Django Ninja backend that exposes APIs, performs retrieval/augmentation, and orchestrates AWS services.
- Stand up a production-like vector store tier to support semantic retrieval across curated reports.
- Deploy core services on AWS serverless primitives to illustrate scalability.

## 3. Non-Goals
- Generating or running the nf-core/singlecell pipeline itself.
- Processing arbitrary user-uploaded reports.
- Production-grade security, monitoring, or cost optimization.
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
                         Retrieval Layer (LangChain + Vector Store)
                                    ↓
         Vector Store (OpenSearch Serverless / pgvector) + Report Artifacts in S3 + Metadata (DynamoDB)
                                    ↓
                            AWS Bedrock (LLM endpoint)
```

### Frontend (React)
- Single-page application that lists available reports and launches the chat interface.
- State management (e.g., Redux Toolkit or React Query) to cache report metadata and conversation history.
- UI components:
  - Report selector
  - Chat window with conversational history
  - Context panel showing linked CSV tables or plots upon demand
- Authentication stub or simple access token (POC-level security).

### Backend (Django + Django Ninja)
- Exposed via AWS API Gateway → Lambda using ASGI adapter (e.g., Mangum).
- API endpoints:
  1. `GET /reports`: list curated POC reports (metadata, sample IDs, etc.).
  2. `POST /chat/query`: accepts `{report_id, user_query, conversation_context}` and returns AI response.
  3. `GET /reports/{id}/artifacts`: returns signed URLs for HTML/CSV/PNG assets (optional for UI preview).
- Business logic:
  - Retrieve report metadata from DynamoDB or static JSON.
  - Use LangChain to construct a retrieval-augmented prompt (HTML parsed to text, CSV -> summary embeddings).
  - Persist and query embeddings in the vector store to ground model responses in the selected report.
  - Invoke AWS Bedrock LLM, passing prompt and attachments as needed.
  - Post-process AI answer, include references or chart links where possible.

### Data & Storage
- **S3 Buckets:** store curated HTML reports, CSV exports, PNG plots.
- **DynamoDB (or static config):** metadata about each report (sample name, pipeline version, artifact paths).
- **Vector Store:** a managed service such as AWS OpenSearch Serverless or a serverless Postgres+pgvector instance that persists embeddings for parsed report sections and enables semantic retrieval during every chat interaction.

### AI & Retrieval
- Use LangChain to orchestrate:
  - Loading report artifacts.
  - Splitting HTML/text into chunks.
  - Converting CSV key metrics into text summaries.
  - Storing/retrieving embeddings in the dedicated vector store.
  - Constructing prompts with context snippets.
- Primary model: AWS Bedrock-hosted LLM (Claude, Titan, etc.).
- Guardrails: prompt templates that emphasize factual accuracy and referencing provided context.
- Vector store lifecycle: initial ingestion job generates embeddings for each artifact and writes them to the managed vector service; each chat query performs similarity search before invoking the model.

### Serverless Deployment
- **Backend:** packaged as a Lambda function using container image or zipped dependencies.
- **API Gateway:** handles HTTPS routing and simple auth (API keys or Cognito for future).
- **Static Frontend Hosting:** React app deployed to S3 + CloudFront.
- **Vector Store Deployment:** managed service provisioned via IaC (e.g., OpenSearch Serverless collection or Aurora Serverless with pgvector extension) seeded with embeddings during deployment.
- **Infrastructure as Code:** optional CDK or Terraform scripts for reproducibility (lightweight for POC).

## 6. POC Scope & Assumptions
- Limited to 2–3 curated nf-core/singlecell reports stored in S3.
- Manual preprocessing allowed (e.g., generating embeddings offline).
- Vector store provisioned and populated as part of the POC deployment to ensure semantic search is always available.
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
| Limited context window | Large HTML/CSV content may exceed model limits | Chunking strategy, pre-summarization via LangChain |
| Latency | Serverless cold starts and LLM latency | Provisioned concurrency for critical Lambdas, caching embeddings |
| Data parsing complexity | HTML reports may need custom parsing | Use BeautifulSoup or nf-core structured outputs; preprocess offline |

## 10. Future Enhancements
- User-uploaded report ingestion with automated parsing/embedding.
- Multi-report comparisons and cross-sample analytics.
- Advanced visualization integration (interactive plots).
- Robust authentication/authorization (Cognito, IAM).
- Cost monitoring and usage analytics dashboards.
