# SingleCell AI Insights - AWS Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              INTERNET / USERS                                │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTPS
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS CloudFront (CDN)                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Single Distribution (*.cloudfront.net)                              │  │
│  │  • Default: S3 Origin (Frontend)                                     │  │
│  │  • /api/*: ALB Origin (Backend API)                                  │  │
│  │  • /admin/*: ALB Origin (Django Admin)                               │  │
│  │  • /static/*: ALB Origin (Django Static Files)                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└───────────────────┬──────────────────────────────┬──────────────────────────┘
                    │                              │
        ┌───────────▼────────────┐    ┌───────────▼────────────┐
        │   S3: Frontend Bucket  │    │  Application Load      │
        │   (React SPA)          │    │  Balancer (ALB)        │
        │   • index.html         │    │  • HTTP → HTTPS        │
        │   • assets/            │    │  • Health checks       │
        └────────────────────────┘    └───────────┬────────────┘
                                                   │ HTTP :8000
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VPC (10.0.0.0/16)                               │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        PUBLIC SUBNETS (2 AZs)                          │ │
│  │  ┌──────────────────┐              ┌──────────────────┐               │ │
│  │  │  NAT Gateway 1   │              │  NAT Gateway 2   │               │ │
│  │  │  (Elastic IP)    │              │  (Elastic IP)    │               │ │
│  │  └──────────────────┘              └──────────────────┘               │ │
│  │           │                                  │                          │ │
│  └───────────┼──────────────────────────────────┼──────────────────────────┘ │
│              │                                  │                            │
│  ┌───────────▼──────────────────────────────────▼──────────────────────────┐ │
│  │                      PRIVATE SUBNETS (2 AZs)                            │ │
│  │  ┌────────────────────────────────────────────────────────────────┐    │ │
│  │  │               ECS Fargate Cluster                              │    │ │
│  │  │  ┌──────────────────────────────────────────────────────────┐ │    │ │
│  │  │  │  ECS Service: sc-ai-insights-service                     │ │    │ │
│  │  │  │  ┌────────────────────────────────────────────────────┐  │ │    │ │
│  │  │  │  │  Task: Django Backend                              │  │ │    │ │
│  │  │  │  │  • Container: DjangoContainer (1 vCPU, 2GB RAM)    │  │ │    │ │
│  │  │  │  │  • Image: ECR (sc-ai-insights-backend:latest)      │  │ │    │ │
│  │  │  │  │  • Port: 8000 (Gunicorn)                           │  │ │    │ │
│  │  │  │  │  • Auto-scaling: 1-4 tasks                         │  │ │    │ │
│  │  │  │  │  • Health checks: /api/health/                     │  │ │    │ │
│  │  │  │  └────────────────────────────────────────────────────┘  │ │    │ │
│  │  │  └──────────────────────────────────────────────────────────┘ │    │ │
│  │  └────────────────────────────────────────────────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│              │                                  │                            │
│  ┌───────────▼──────────────────────────────────▼──────────────────────────┐ │
│  │                     ISOLATED SUBNETS (2 AZs)                            │ │
│  │  ┌────────────────────────────────────────────────────────────────┐    │ │
│  │  │  RDS PostgreSQL (db.t4g.small)                                 │    │ │
│  │  │  • Database: singlecell_ai                                     │    │ │
│  │  │  • Multi-AZ: No (cost optimization)                            │    │ │
│  │  │  • Backup: 7 days retention                                    │    │ │
│  │  │  • Encryption: At rest                                         │    │ │
│  │  │  • Credentials: Secrets Manager                                │    │ │
│  │  └────────────────────────────────────────────────────────────────┘    │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXTERNAL AWS SERVICES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │  S3 Buckets        │  │  ECR Repository    │  │  CodeBuild         │    │
│  │  • Reports         │  │  • Backend images  │  │  • Build project   │    │
│  │  • Source (zip)    │  │  • Python base     │  │  • Dockerfile      │    │
│  │  • Artifacts (CSV) │  └────────────────────┘  └────────────────────┘    │
│  └────────────────────┘                                                      │
│                                                                               │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐    │
│  │  Secrets Manager   │  │  CloudWatch Logs   │  │  AWS Budgets       │    │
│  │  • DB credentials  │  │  • ECS logs        │  │  • Cost alerts     │    │
│  │  • Django secret   │  │  • 1 week retention│  │  • Email notify    │    │
│  └────────────────────┘  └────────────────────┘  └────────────────────┘    │
│                                                                               │
│  ┌────────────────────┐  ┌────────────────────┐                             │
│  │  AWS Bedrock       │  │  AWS HealthOmics   │                             │
│  │  • Claude Sonnet 4 │  │  • Workflow runs   │                             │
│  │  • Titan Embed v2  │  │  • Run metadata    │                             │
│  └────────────────────┘  └────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details for draw.io

### 1. **User Layer** (Top)
- Icon: User/Browser icon
- Label: "Users / Judges"
- Connection: HTTPS arrow down to CloudFront

### 2. **CloudFront Distribution** (Edge Layer)
- Icon: AWS CloudFront icon
- Label: "CloudFront Distribution"
- Sub-components:
  - Box: "Path Routing"
    - `/` → S3 (Frontend)
    - `/api/*` → ALB (Backend)
    - `/admin/*` → ALB (Django Admin)
    - `/static/*` → ALB (Static Files)
- Features: SSL/TLS, DDoS Protection, Caching

### 3. **Frontend (S3)**
- Icon: AWS S3 bucket icon
- Label: "Frontend Bucket"
- Contents: React SPA, index.html, assets/
- Connection: CloudFront → S3 (default behavior)

### 4. **Application Load Balancer**
- Icon: AWS ELB icon
- Label: "Application Load Balancer"
- Features: Health checks, Target groups
- Connection: CloudFront → ALB (path-based routing)

### 5. **VPC** (Large container)
- Icon: AWS VPC icon
- Label: "VPC (10.0.0.0/16)"
- Contains 3 subnet tiers:

#### **Public Subnets** (Top tier in VPC)
- Icon: Public subnet icon
- 2 boxes (AZ-a, AZ-b)
- Contains: NAT Gateways with Elastic IPs
- Connection: Internet Gateway

#### **Private Subnets** (Middle tier in VPC)
- Icon: Private subnet icon
- 2 boxes (AZ-a, AZ-b)
- Contains: ECS Fargate tasks
- Connection: NAT Gateway → Internet

#### **Isolated Subnets** (Bottom tier in VPC)
- Icon: Isolated subnet icon
- 2 boxes (AZ-a, AZ-b)
- Contains: RDS database
- No internet access

### 6. **ECS Cluster** (Inside Private Subnets)
- Icon: AWS ECS icon
- Label: "ECS Fargate Cluster"
- Components:
  - Service: "sc-ai-insights-service"
  - Task Definition: Django container
  - Auto-scaling: 1-4 tasks
  - Container: 1 vCPU, 2GB RAM
  - Port: 8000

### 7. **RDS Database** (Inside Isolated Subnets)
- Icon: AWS RDS icon
- Label: "PostgreSQL (db.t4g.small)"
- Features: Encrypted, Automated backups
- Connection: ECS → RDS (port 5432)

### 8. **External Services** (Right side or bottom)

#### **Storage & Build**
- S3 Buckets (3 icons):
  - Reports bucket
  - Source bucket
  - Frontend bucket
- ECR Repository
- CodeBuild project

#### **Security & Monitoring**
- Secrets Manager (2 secrets)
- CloudWatch Logs
- AWS Budgets

#### **AI & Data**
- AWS Bedrock (Claude + Embeddings)
- AWS HealthOmics (Workflow data)

## Data Flow Diagram

```
┌─────────┐
│  User   │
└────┬────┘
     │ 1. HTTPS Request
     ▼
┌─────────────────┐
│   CloudFront    │
└────┬────────────┘
     │ 2. Route based on path
     │
     ├─────────────────────┐
     │                     │
     ▼                     ▼
┌─────────┐          ┌─────────┐
│   S3    │          │   ALB   │
│Frontend │          └────┬────┘
└─────────┘               │ 3. Forward to ECS
                          ▼
                     ┌─────────────┐
                     │ ECS Fargate │
                     │   Django    │
                     └─────┬───────┘
                           │ 4. Query data
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   ┌─────────┐       ┌─────────┐       ┌──────────┐
   │   RDS   │       │ Bedrock │       │HealthOmics│
   │Database │       │   AI    │       │   API    │
   └─────────┘       └─────────┘       └──────────┘
```

## Security Architecture

```
┌────────────────────────────────────────────────┐
│           Security Layers                      │
├────────────────────────────────────────────────┤
│                                                │
│  1. CloudFront                                 │
│     • AWS Shield Standard (DDoS)               │
│     • SSL/TLS termination                      │
│     • HTTPS redirect                           │
│                                                │
│  2. Application Load Balancer                  │
│     • Security groups (port 80 only)           │
│     • Health checks                            │
│                                                │
│  3. ECS Tasks                                  │
│     • Private subnets (no public IP)           │
│     • IAM task roles (least privilege)         │
│     • Security groups (ALB → 8000 only)        │
│                                                │
│  4. RDS Database                               │
│     • Isolated subnets (no internet)           │
│     • Security groups (ECS → 5432 only)        │
│     • Encryption at rest                       │
│     • Secrets Manager for credentials          │
│                                                │
│  5. Authentication                             │
│     • JWT tokens (httpOnly cookies)            │
│     • Django authentication                    │
│     • No public registration                   │
│                                                │
└────────────────────────────────────────────────┘
```

## Cost Optimization Features

```
┌────────────────────────────────────────────────┐
│         Cost-Optimized Components              │
├────────────────────────────────────────────────┤
│                                                │
│  • RDS: db.t4g.small (~$24/mo)                 │
│    - ARM-based Graviton2                       │
│    - 20% cheaper than t3                       │
│                                                │
│  • ECS: Single task, auto-scale to 4           │
│    - Only pay for what you use                 │
│                                                │
│  • CloudFront: First 1TB free                  │
│    - Caching reduces origin requests           │
│                                                │
│  • S3: Lifecycle policies                      │
│    - Intelligent tiering available             │
│                                                │
│  • CloudWatch: 1 week log retention            │
│    - Minimal storage costs                     │
│                                                │
│  • NAT Gateway: Single AZ (can add 2nd)        │
│    - ~$32/mo vs $64/mo for HA                  │
│                                                │
│  Total: ~$160-210/month                        │
│                                                │
└────────────────────────────────────────────────┘
```

## draw.io Tips

### Color Coding
- **Public/Internet**: Light blue (#E3F2FD)
- **CloudFront/CDN**: Orange (#FFE0B2)
- **VPC**: Light gray (#F5F5F5)
- **Public Subnets**: Green (#E8F5E9)
- **Private Subnets**: Yellow (#FFF9C4)
- **Isolated Subnets**: Red (#FFEBEE)
- **External Services**: Purple (#F3E5F5)

### Icons to Use
- AWS official icon set (available in draw.io)
- Use grouped containers for VPC, subnets
- Arrows with labels for data flow
- Dashed lines for optional/conditional flows

### Layout Suggestions
1. **Top-down flow**: User → CloudFront → ALB/S3 → ECS → RDS
2. **Left-to-right**: External services on the right
3. **Grouped boxes**: VPC contains all subnets
4. **Clear labels**: Service names, ports, protocols
