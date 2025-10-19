# SingleCell AI Insights

**Tagline:** AI agent that analyzes genomic QC reports through natural language conversation

## Inspiration

I'm a tech lead at a bioinformatics company. Our scientists spend hours manually analyzing MultiQC quality control reports—hundreds of metrics across dozens of samples. Questions like "Which samples failed?" or "Why is this duplication rate high?" require deep expertise and tedious manual inspection.

The key realization: MultiQC outputs are highly structured and consistent across workflows. Every report has the same JSON format, same metric names, same documentation structure. This makes them perfect for AI assistance—the agent doesn't need to understand arbitrary data formats, it can learn the MultiQC schema once and apply it everywhere.

I wanted to learn about agentic AI workflows, and this hackathon was the perfect opportunity to build something practical: an AI agent that lets researchers ask questions about their data in plain English.

## What it does

You ask questions about your genomic quality control data in natural language. The agent:

1. **Loads** MultiQC reports from AWS HealthOmics workflows
2. **Analyzes** using LangGraph workflow:
   - Routes questions to specialized nodes (sample lookup, metric comparison, or RAG)
   - Calculates statistics and detects outliers
   - Retrieves relevant documentation via FAISS vector search
3. **Links** to existing MultiQC artifacts (tables, plots) with presigned S3 URLs
4. **Interprets** results and suggests next steps for scientists
5. **Responds** with natural language answers using Claude Sonnet 4

**Example questions:**

- "Which samples have quality issues?"
- "Show me duplication rates across all samples"
- "Why does sample X have low mapping rates?"

The agent streams progress in real-time, maintains conversation history, and provides downloadable artifacts.

## How I built it

**Stack:** React 19 + TypeScript (frontend), Django + LangGraph (backend), AWS CDK (infrastructure)

### **Agent Workflow (LangGraph)**

I built an 8-node directed graph:

1. **load_multiqc** - Downloads MultiQC JSON from S3
2. **ensure_index** - Builds FAISS vector index from documentation panels
3. **route_intent** - Routes to one of three analysis strategies (keyword-based):
   - **lookup_samples** - Identifies samples with quality issues
   - **lookup_metric** - Extracts specific metrics with outlier detection
   - **rag** - Semantic search over MultiQC documentation
4. **make_table** - Finds relevant table in MultiQC report, generates presigned S3 URL
5. **plot_metric** - Finds relevant plot in MultiQC report, generates presigned S3 URL
6. **synthesize** - Uses Claude Sonnet 4 to generate natural language answer

All nodes flow through the same path (make_table → plot_metric → synthesize), but the analysis node determines what data gets passed forward. The agent links to existing MultiQC artifacts rather than generating new ones.

Why LangGraph? Traditional RAG is stateless. Quality analysis needs multi-step reasoning with state accumulation across nodes.

### **Frontend**

React with streaming responses (Server-Sent Events). Users see progress as the agent works through each node. JWT auth with httpOnly cookies, React Query for caching.

### **Infrastructure**

AWS CDK deploys:

- CloudFront (routes `/` to S3, `/api/*` to ALB)
- ECS Fargate (Django backend, auto-scales 1-4 tasks)
- RDS PostgreSQL (conversation history)
- VPC with 3-tier subnets (public/private/isolated)

One-command deployment: `./stack_upgrade.py --infrastructure --backend --frontend`

## Challenges I ran into

**LangGraph state management:** Took me a while to understand how state flows between nodes. Early nodes would add data, but later nodes couldn't access it. Fixed by using explicit state updates instead of relying on automatic merging.

**Selecting relevant artifacts:** MultiQC reports contain a number of tables and plots. The agent needs to pick the right ones based on the question. Built logic to match metric keys from the question to artifact filenames and metadata, with fallbacks to general stats when no specific match is found.

**Learning AWS CDK:** I've set up AWS infrastructure before using CloudFormation templates, but this was my first time using CDK. The Python-based approach is more flexible, but came with a learning curve—reading docs to understand this IaC language.

**MultiQC data variability:** Different workflows produce different structures. Built a normalization layer to handle missing keys and flatten nested metrics.

## Accomplishments that I'm proud of

**Built my first agentic AI system:** The LangGraph workflow works end-to-end. It performs multi-step reasoning, autonomous decision-making, and tool integration.

**Deployed on real AWS infrastructure:** Not just a local prototype. Zero-downtime deployments, auto-scaling, proper security (isolated subnets, Secrets Manager). One-command deployment automation.

**Streaming UX:** Users see progress as the agent works ("Loading data..." → "Building index..." → "Analyzing..."). Makes the AI feel less like a black box.

**Solves a real problem:** Bioinformatics teams spend hours on manual QC analysis. This agent interprets metrics, detects outliers, and explains issues in natural language.

## What I learned

**Agentic AI is different:** It's not about chaining prompts. It's about orchestrating specialized functions that collaborate. LangGraph's graph-based approach with conditional edges was key.

**Infrastructure first:** Writing CDK stacks upfront felt like overhead, but I destroyed/recreated infrastructure 20+ times during development. Having solid infrastructure let me iterate on the agent without deployment headaches.

**Streaming UX matters:** The agent takes 10-15 seconds to respond, but users don't complain because they see progress. Transparency > speed.

**AWS Bedrock works well:** No API key management (IAM roles), low latency (~2-3s), regional deployment. For AWS-native apps, it's simpler than external APIs.

## What's next for SingleCell AI Insights

I'm planning to demo this MVP within my company to collect feedback and figure out next steps. We have an existing pipeline platform where the AI agent can get built into and scaled.

**Better agent capabilities:**

- Persistent vector store (Pinecone/Weaviate) instead of in-memory FAISS
- LLM-based intent classification instead of keyword matching
- Expanded knowledge base (nf-core docs, best practices, troubleshooting)
- Support for more output types (VCF files, alignment stats, variant calling)
- Guardrails and output validation

**Enterprise features:**

- Custom quality thresholds per workflow type
- Batch analysis across multiple runs
- LIMS integration for sample metadata
- PDF export for compliance

**Advanced AI:**

- Automated troubleshooting (suggest parameter adjustments)
- Cross-study analysis (patterns across hundreds of runs)
- Multi-pipeline support (rnaseq, atacseq, chipseq, sarek)

---

## Tech Stack

**Frontend:** React 19, TypeScript, Vite, TailwindCSS, shadcn/ui  
**Backend:** Django 4.2, LangGraph, AWS Bedrock (Claude Sonnet 4 + Titan Embeddings)  
**Infrastructure:** AWS CDK, ECS Fargate, RDS PostgreSQL, CloudFront, S3  
**Deployment:** One-command: `./stack_upgrade.py --infrastructure --backend --frontend`
