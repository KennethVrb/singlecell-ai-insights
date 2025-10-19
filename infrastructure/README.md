# Infrastructure Deployment

## Prerequisites

- AWS CLI configured (`aws configure`)
- Python environment with dependencies: `pip install -r requirements.txt`

## Setup (One-time)

Push Python base image to your ECR:

```bash
# Login to ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

# Pull and push Python base image
docker pull python:3.12-bookworm
docker tag python:3.12-bookworm <account>.dkr.ecr.<region>.amazonaws.com/python:3.12-bookworm
docker push <account>.dkr.ecr.<region>.amazonaws.com/python:3.12-bookworm
```

## Deploy

```bash
# Deploy CDK infrastructure
./stack_upgrade.py --infrastructure

# Build and push backend Docker image
./stack_upgrade.py --backend

# Deploy everything
./stack_upgrade.py --infrastructure --backend
```

## What It Does

- `--infrastructure`: Deploys S3, ECR, and CodeBuild via CDK
- `--backend`: Creates source zip, uploads to S3, triggers CodeBuild to build Docker image
