# SingleCell AI Insights - Architecture Diagrams (Mermaid)

## Complete Architecture Diagram

```mermaid
architecture-beta
    group internet(cloud)[Internet]
    group cdn(cloud)[CloudFront CDN]
    group vpc(cloud)[VPC 10.0.0.0/16]
    group public(cloud)[Public Subnets] in vpc
    group private(cloud)[Private Subnets] in vpc
    group isolated(cloud)[Isolated Subnets] in vpc
    group ecs_cluster(server)[ECS Fargate Cluster] in private
    group aws_services(cloud)[AWS Services]
    
    service users(internet)[Users/Judges] in internet
    service cloudfront(cloud)[CloudFront Distribution] in cdn
    service s3_frontend(disk)[S3 Frontend Bucket] in cdn
    service alb(server)[Application Load Balancer]
    
    service nat1(server)[NAT Gateway 1] in public
    service nat2(server)[NAT Gateway 2] in public
    
    service ecs_service(server)[ECS Service] in ecs_cluster
    service django_task(server)[Django Backend Task] in ecs_cluster
    
    service rds(database)[RDS PostgreSQL] in isolated
    
    service s3_reports(disk)[S3 Reports Bucket] in aws_services
    service s3_source(disk)[S3 Source Bucket] in aws_services
    service ecr(disk)[ECR Repository] in aws_services
    service codebuild(server)[CodeBuild] in aws_services
    service secrets(disk)[Secrets Manager] in aws_services
    service cloudwatch(disk)[CloudWatch Logs] in aws_services
    service bedrock(server)[AWS Bedrock] in aws_services
    service healthomics(server)[AWS HealthOmics] in aws_services
    
    users:R --> L:cloudfront
    cloudfront:B --> T:s3_frontend
    cloudfront:R --> L:alb
    alb:R --> L:ecs_service{group}
    ecs_service:B --> T:django_task
    django_task:R --> L:rds{group}
    
    nat1:B --> T:django_task
    nat2:B --> T:django_task
    
    django_task:R --> L:s3_reports
    django_task:R --> L:secrets
    django_task:R --> L:cloudwatch
    django_task:R --> L:bedrock
    django_task:R --> L:healthomics
    
    codebuild:T --> B:ecr
    codebuild:L --> R:s3_source
    ecr:L --> R:django_task
```

## Simplified Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as 👥 User
    participant CF as ☁️ CloudFront
    participant ALB as ⚖️ ALB
    participant ECS as 🐳 Django (ECS)
    participant RDS as 🗄️ PostgreSQL
    participant Bedrock as 🤖 Bedrock AI
    participant HealthOmics as 🧬 HealthOmics
    
    User->>CF: HTTPS Request
    CF->>CF: Route based on path
    
    alt Frontend Request (/)
        CF->>User: Serve React SPA from S3
    else API Request (/api/*)
        CF->>ALB: Forward to backend
        ALB->>ECS: HTTP :8000
        ECS->>RDS: Query database
        RDS-->>ECS: Return data
        ECS->>HealthOmics: Fetch workflow runs
        HealthOmics-->>ECS: Run metadata
        ECS-->>ALB: JSON response
        ALB-->>CF: Response
        CF-->>User: JSON data
    else Chat Request (/api/runs/*/chat/)
        CF->>ALB: Forward to backend
        ALB->>ECS: HTTP :8000
        ECS->>RDS: Get run data
        ECS->>Bedrock: AI inference
        Bedrock-->>ECS: AI response
        ECS->>RDS: Save conversation
        ECS-->>ALB: JSON response
        ALB-->>CF: Response
        CF-->>User: Chat message
    end
```

## Security Architecture

```mermaid
graph LR
    subgraph Internet["🌐 Internet"]
        Attacker[⚠️ Potential Threats]
    end
    
    subgraph Layer1["Layer 1: Edge Protection"]
        Shield[🛡️ AWS Shield Standard<br/>DDoS Protection]
        CFSec[🔒 CloudFront<br/>SSL/TLS<br/>HTTPS Only]
    end
    
    subgraph Layer2["Layer 2: Load Balancer"]
        ALBSG[🔐 ALB Security Group<br/>Port 80 from CF only]
        HealthCheck[✅ Health Checks]
    end
    
    subgraph Layer3["Layer 3: Application"]
        ECSSG[🔐 ECS Security Group<br/>Port 8000 from ALB only]
        IAM[👤 IAM Task Role<br/>Least Privilege]
        JWT[🎫 JWT Authentication<br/>httpOnly Cookies]
    end
    
    subgraph Layer4["Layer 4: Data"]
        RDSSG[🔐 RDS Security Group<br/>Port 5432 from ECS only]
        Encryption[🔐 Encryption at Rest]
        SecretsM[🔑 Secrets Manager<br/>Credential Rotation]
    end
    
    subgraph Layer5["Layer 5: Network"]
        PrivateSubnet[🔒 Private Subnets<br/>No Public IPs]
        IsolatedSubnet[🔐 Isolated Subnets<br/>No Internet Access]
    end
    
    Attacker -->|Blocked| Shield
    Shield --> CFSec
    CFSec --> ALBSG
    ALBSG --> HealthCheck
    HealthCheck --> ECSSG
    ECSSG --> IAM
    IAM --> JWT
    JWT --> RDSSG
    RDSSG --> Encryption
    Encryption --> SecretsM
    ECSSG -.-> PrivateSubnet
    RDSSG -.-> IsolatedSubnet
    
    classDef threatStyle fill:#FFCDD2,stroke:#C62828,stroke-width:2px
    classDef protectionStyle fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    
    class Attacker threatStyle
    class Shield,CFSec,ALBSG,ECSSG,RDSSG,Encryption,SecretsM,JWT,IAM protectionStyle
```

## Deployment Pipeline

```mermaid
graph LR
    subgraph Developer["👨‍💻 Developer"]
        Code[📝 Code Changes<br/>Backend/Frontend]
    end
    
    subgraph BuildPipeline["🔨 Build Pipeline"]
        Zip[📦 Create Source Zip]
        S3Upload[☁️ Upload to S3]
        CBTrigger[▶️ Trigger CodeBuild]
        DockerBuild[🐳 Build Docker Image]
        ECRPush[📤 Push to ECR]
    end
    
    subgraph Deployment["🚀 Deployment"]
        ECSUpdate[🔄 Update ECS Service]
        HealthCheck[✅ Health Checks]
        TaskSwap[🔀 Blue/Green Deploy<br/>min: 100%, max: 200%]
        OldTaskDrain[⏳ Drain Old Tasks]
        Complete[✅ Deployment Complete]
    end
    
    subgraph Monitoring["📊 Monitoring"]
        Logs[📋 CloudWatch Logs]
        Metrics[📈 ECS Metrics]
        BudgetAlert[💰 Budget Alerts]
    end
    
    Code --> Zip
    Zip --> S3Upload
    S3Upload --> CBTrigger
    CBTrigger --> DockerBuild
    DockerBuild --> ECRPush
    ECRPush --> ECSUpdate
    ECSUpdate --> HealthCheck
    HealthCheck --> TaskSwap
    TaskSwap --> OldTaskDrain
    OldTaskDrain --> Complete
    
    Complete --> Logs
    Complete --> Metrics
    Complete --> BudgetAlert
    
    classDef devStyle fill:#E1F5FE,stroke:#0277BD,stroke-width:2px
    classDef buildStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    classDef deployStyle fill:#C8E6C9,stroke:#388E3C,stroke-width:2px
    classDef monitorStyle fill:#F3E5F5,stroke:#7B1FA2,stroke-width:2px
    
    class Developer devStyle
    class BuildPipeline buildStyle
    class Deployment deployStyle
    class Monitoring monitorStyle
```

## Cost Breakdown

```mermaid
pie title Monthly Cost Distribution (~$200/month)
    "RDS db.t4g.small" : 24
    "ECS Fargate (1 task)" : 30
    "NAT Gateway" : 32
    "ALB" : 16
    "CloudFront & Data Transfer" : 30
    "Bedrock API (moderate use)" : 40
    "CloudWatch & Other" : 28
```

## Network Flow

```mermaid
graph TB
    subgraph Internet["🌐 Internet"]
        IGW[Internet Gateway]
    end
    
    subgraph PublicSubnets["Public Subnets"]
        NAT[NAT Gateway<br/>Elastic IP]
    end
    
    subgraph PrivateSubnets["Private Subnets"]
        ECS[ECS Tasks<br/>No Public IP]
    end
    
    subgraph IsolatedSubnets["Isolated Subnets"]
        RDS[RDS Database<br/>No Internet]
    end
    
    IGW -->|Inbound| NAT
    NAT -->|Outbound Only| ECS
    ECS -->|Internal| RDS
    ECS -.->|No Direct Access| IGW
    RDS -.->|No Access| NAT
    
    classDef publicStyle fill:#E8F5E9,stroke:#388E3C,stroke-width:2px
    classDef privateStyle fill:#FFF9C4,stroke:#F57F17,stroke-width:2px
    classDef isolatedStyle fill:#FFEBEE,stroke:#C62828,stroke-width:2px
    
    class PublicSubnets publicStyle
    class PrivateSubnets privateStyle
    class IsolatedSubnets isolatedStyle
```

## How to Use These Diagrams

### In GitHub README
Just paste the mermaid code blocks - GitHub will render them automatically!

### Export as Images
1. Use [Mermaid Live Editor](https://mermaid.live/)
2. Paste the code
3. Export as PNG/SVG

### In Documentation
- GitHub/GitLab: Native support
- Notion: Use mermaid blocks
- Confluence: Use mermaid macro
- VS Code: Install Mermaid extension

### For Presentations
1. Export from Mermaid Live Editor
2. Import PNG/SVG into PowerPoint/Keynote
3. Or use reveal.js with mermaid plugin
