# SingleCell AI Insights

An intelligent assistant for analyzing AWS HealthOmics single-cell RNA sequencing pipeline outputs using agentic AI workflows powered by AWS Bedrock and LangGraph.

## Overview

SingleCell AI Insights transforms complex MultiQC quality control reports into actionable insights through natural language conversations. Ask questions in plain English and get intelligent answers backed by data analysis, visualizations, and recommendations.

**Key Features:**
- 🤖 **Agentic AI Workflow** - LangGraph orchestrates multi-step reasoning with Claude Sonnet 4
- 💬 **Natural Language Interface** - Ask questions about your sequencing data in plain English
- 📊 **Intelligent Analysis** - Automatic outlier detection, statistical analysis, and data interpretation
- 🔍 **RAG-Powered Search** - FAISS vector store for semantic search across MultiQC documentation
- 📈 **Smart Artifact Selection** - AI intelligently selects relevant plots and tables from MultiQC reports
- ☁️ **Production-Ready AWS Infrastructure** - ECS Fargate, RDS, CloudFront, auto-scaling

## Architecture

- **Frontend**: React 19 + TypeScript, Vite, TailwindCSS, shadcn/ui
- **Backend**: Django 4.2 + DRF, LangGraph agentic workflows
- **AI**: AWS Bedrock (Claude Sonnet 4 + Titan Embeddings)
- **Infrastructure**: AWS ECS Fargate, RDS PostgreSQL, CloudFront CDN, S3
- **Deployment**: One-command CDK deployment with zero-downtime updates

See [ARCHITECTURE.md](ARCHITECTURE.md) and [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) for detailed diagrams.

## Quick Start

### For Judges/Evaluators

See [JUDGE_GUIDE.md](JUDGE_GUIDE.md) for a complete walkthrough of features and evaluation criteria.

### Local Development

#### Prerequisites
- Python 3.12+
- Node.js 18+ and pnpm
- AWS credentials with HealthOmics and Bedrock permissions

#### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r dev-requirements.txt  # Optional: for linting/formatting
   ```

3. Configure environment:
   ```bash
   cp backend/.env-example backend/.env
   # Edit backend/.env with your AWS credentials and settings
   ```

4. Run migrations:
   ```bash
   cd backend
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   pnpm install
   ```

2. Configure environment:
   ```bash
   cp .env-example .env
   # Edit .env to point to your backend (default: http://localhost:8000/api)
   ```

3. Start the development server:
   ```bash
   pnpm dev
   ```

The frontend will be available at `http://localhost:5173`.

### AWS Deployment

See [infrastructure/README.md](infrastructure/README.md) for complete deployment instructions.

**Quick deploy:**
```bash
cd infrastructure
export BUDGET_EMAIL=your-email@example.com

# Initial deployment
./stack_upgrade.py --infrastructure --backend --frontend

# Get CloudFront domain from outputs
aws cloudformation describe-stacks --stack-name MainStack \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomain'].OutputValue" --output text

# Re-deploy with CloudFront domain
./stack_upgrade.py --infrastructure --param CloudFrontDomain=<your-domain>.cloudfront.net
./stack_upgrade.py --backend
```

## Project Structure

```
singlecell-ai-insights/
├── backend/                    # Django backend
│   ├── singlecell_ai_insights/
│   │   ├── api/               # REST API endpoints
│   │   ├── aws/               # AWS service integrations
│   │   ├── models/            # Database models
│   │   ├── services/          # LangGraph agent workflows
│   │   └── tests/             # Test suite
│   ├── requirements.txt
│   └── manage.py
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/               # API client
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── providers/         # Context providers
│   └── package.json
├── infrastructure/             # AWS CDK infrastructure
│   ├── cdk/                   # CDK stacks
│   └── stack_upgrade.py       # Deployment script
└── pipeline_output_example/    # Sample MultiQC data
```

## Testing

**Backend:**
```bash
cd backend
pytest
# or
python manage.py test
```

**Frontend:**
```bash
cd frontend
pnpm test
```

## Key Technologies

- **LangGraph** - Agentic workflow orchestration with directed graphs
- **AWS Bedrock** - Claude Sonnet 4 for chat, Titan for embeddings
- **FAISS** - Vector similarity search for RAG
- **Django REST Framework** - API backend with JWT authentication
- **React Query** - Server state management and caching
- **Server-Sent Events** - Real-time streaming responses

## Documentation

- [JUDGE_GUIDE.md](JUDGE_GUIDE.md) - Evaluation guide for hackathon judges
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) - Mermaid diagrams
- [infrastructure/README.md](infrastructure/README.md) - Deployment guide
- [HACKATHON_SUBMISSION.md](HACKATHON_SUBMISSION.md) - Hackathon submission details

## License

MIT
