# SingleCell AI Insights - Demo Video Script (3 minutes)

## Opening (0:00 - 0:20)

**[Screen: Application homepage]**

"Hi, I'm Kenneth, and I built SingleCell AI Insights for the AWS Hackathon. in my company our scientists spend hours manually analyzing MultiQC quality control reports—hundreds of metrics across dozens of samples. Questions like 'Which samples failed?' or 'Why is this duplication rate high?' require deep expertise and tedious manual inspection."

"I built this MVP to validate my idea: can AI assist with this analysis? The platform connects to AWS HealthOmics to fetch workflow runs. I've manually executed three single-cell RNA-seq pipelines—two successful, one failed—to demonstrate both scenarios."

**[Show tagline on screen]**

"Instead of spending 30+ minutes manually inspecting MultiQC reports, scientists can now ask questions in plain English and get answers in 30 seconds."

---

## Problem & Solution (0:20 - 0:45)

**[Screen: Runs list page]**

"Here's the platform. It connects to AWS HealthOmics to fetch workflow runs. I've manually executed three single-cell RNA-seq pipelines—two successful, one failed—to demonstrate both scenarios."

**[Click on a successful run]**

"Each run shows metadata, status, and normalized quality metrics. But the real power is the AI agent."

**[Highlight the chat panel]**

"This chat interface lets scientists ask questions about their data in plain English—turning 30+ minutes of manual inspection into a 30-second conversation."

---

## Demo: AI Agent in Action (0:45 - 2:00)

**[Screen: Run detail page with chat]**

### Question 1: Sample Quality (0:45 - 1:05)

**[Type: "Which samples have quality issues?"]**

"Let me ask: 'Which samples have quality issues?'"

**[Show streaming progress indicators]**

"Watch the progress indicators—you can see the agent working through each step:"

- Loading MultiQC data from S3
- Building the vector index
- Analyzing samples
- Generating the answer

**[Show the response with sample names and metrics]**

"The agent identifies problematic samples, explains why they're flagged, and provides specific metrics."

---

### Question 2: Metric Analysis (1:05 - 1:25)

**[Type: "Show me duplication rates across all samples"]**

"Now let's ask: 'Show me duplication rates across all samples'"

**[Show streaming progress]**

"The agent routes this to the metric lookup node, calculates statistics, detects outliers..."

**[Show response with table link and plot link]**

"...and provides links to the original MultiQC table and visualization. These are presigned S3 URLs to the actual artifacts."

**[Click one of the links to show it opens]**

---

### Question 3: Interpretation (1:25 - 1:45)

**[Type: "Why does sample X have low mapping rates?"]**

"Finally: 'Why does sample X have low mapping rates?'"

**[Show streaming progress]**

"This question triggers the RAG node—it searches the MultiQC documentation using FAISS vector similarity..."

**[Show response with explanation and recommendations]**

"...and provides an interpretation with potential causes and recommended next steps."

---

## Technical Architecture (1:45 - 2:30)

**[Screen: Architecture diagram or code editor showing key files]**

"Under the hood, this is powered by LangGraph which orchestrates the analysis workflow."

**[Show graph structure briefly]**

"Each node has a specific job:

- Load data from S3
- Build FAISS vector index
- Route questions based on intent
- Analyze samples or metrics
- Find relevant artifacts
- Synthesize answers with Claude Sonnet 4"

**[Screen: Infrastructure overview]**

"The entire stack is deployed on AWS:

- React 19 frontend with real-time streaming
- Django backend with embedded agent service
- ECS Fargate for auto-scaling
- RDS for conversation history
- CloudFront for global distribution"

**[Show terminal with deployment command]**

"One command deploys everything: infrastructure, backend, and frontend."

---

## MVP Scope & Future (2:30 - 2:50)

**[Screen: Back to application or slides]**

"For this hackathon MVP, I made deliberate trade-offs:

- Agent embedded in Django, not a separate microservice
- In-memory FAISS, not a persistent vector database
- Keyword-based routing, not LLM-based intent classification
- Single pipeline type only"

"But I built it with production readiness in mind to showcase AWS capabilities. The architecture uses production-grade services:

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

**[Fade out]**

---

## Tips for Recording

1. **Keep it moving** - Don't wait for full responses, show snippets and move on
2. **Use cursor highlights** - Circle or highlight important UI elements
3. **Pre-type questions** - Have them ready to paste to save time
4. **Show real responses** - Don't fake it, but pick the best examples
5. **Practice timing** - Rehearse to hit exactly 3 minutes
6. **Use transitions** - Smooth cuts between sections

## Screen Recording Setup

- **Resolution:** 1920x1080 (Full HD)
- **Frame rate:** 30fps minimum
- **Audio:** Clear microphone, no background noise
- **Browser:** Chrome/Firefox with clean profile (no extensions visible)
- **Zoom level:** 100% or 110% for readability
- **Cursor:** Make it larger/highlighted if possible

## Pre-Recording Checklist

- [ ] Clear browser cache and cookies
- [ ] Login with judge credentials
- [ ] Have all questions pre-written in a text file
- [ ] Close unnecessary browser tabs
- [ ] Disable notifications
- [ ] Test microphone levels
- [ ] Have architecture diagrams ready
- [ ] Practice run-through at least twice
