**[Screen: Application homepage]**

"Hi, I'm Kenneth, and I built SingleCell AI Insights for the AWS Hackathon. in my company our scientists spend hours manually analyzing outputs from bioinformatics pipelines while these reports have a reproducable format making it a prime candidate for AI analysis. This also made it a perfect as a subject for this hackathon.
"I mainly built this MVP to validate my idea: can AI assist with this analysis?

**[Screen: Runs list page]**

"Here's the platform. I've manually executed three single-cell RNA-seq pipelines on AWS Healthomics as thats not part of this MVP — two successful, and one failed—to demonstrate both scenarios."

**[Click on a successful run]**

"Each run shows metadata, status, and normalized quality metrics. But the real power is the AI agent."

**[Click on download MultiQC report]**
"But first, let me show you how a report looks like."

"As you can see, the report contains statistics, visualizations and tables. The data might change but the format is always the same. So we can use AI to analyze this data and provide insights to the scientists."

**[Highlight the chat panel]**

"This chat interface lets scientists ask questions about their data in plain English—turning 30+ minutes of manual inspection into a 30-second conversation."

"let's ask: 'Show me duplication rates across all samples'"

"Under the hood, this is powered by LangGraph which orchestrates the analysis workflow."
it has nodes that handle different tasks:

- Build vector index
- Route questions based on intent
- Analyze samples or metrics
- Use AI to intelligently select relevant charts and tables from MultiQC reports
- Generate presigned S3 URLs for selected artifacts
- Synthesize answers with Claude Sonnet 4"

**[Show streaming progress]**

"The agent routes this to the metric lookup node, calculates statistics, detects outliers..."

"...and provides links to the original MultiQC table and visualization. These are presigned S3 URLs to the actual artifacts."

## Infrastructure

"The entire stack is deployed on AWS:

- React static files on S3
- Django backend (with agent) running on ECS Fargate
- Cloudfront distribution exposing both frontend and api
- RDS PostgreSQL as database
- Secrets Manager for security
- Django has access to both HealthOmics and Bedrock
- CDK for infrastructure as code"

## MVP Scope & Future (2:30 - 2:50)

**[Screen: Back to application or slides]**

"For this hackathon MVP, I made deliberate trade-offs:

- Agent embedded in Django, not a separate microservice
- In-memory Similarity Search instead of persistent vector database
- Keyword-based routing for question types (though artifact selection uses LLM intelligence)
- Single pipeline type only"

"But I built it with production readiness in mind to showcase AWS capabilities.
The architecture uses production-grade services:

- ECS Fargate with auto-scaling
- RDS PostgreSQL for persistence
- CloudFront with proper routing
- Secrets Manager for security
- CDK for infrastructure as code
- One command deployment & stack upgrade

"To further improve the MVP to make it production ready, you'd add:

- Persistent vector store
- Domain specific knowledge bases
- Separate agent service
- LLM-based routing
- Multi-pipeline support
- Pipeline triggering capabilities"

---

## Closing (2:50 - 3:00)

**[Screen: Application homepage or final slide]**

"This is my first agentic AI system—an MVP proof-of-concept built with production-grade AWS services to demonstrate what's possible. The platform showcases real AWS capabilities and is live to explore."

**[Show URL and credentials on screen]**

"Thanks for watching! Check out the repository for architecture diagrams, deployment guides, and full documentation."
I have also sent the credentials needed to access the platform as part of the hackaton submision form called JUDGE_CREDENTIALS.txt
