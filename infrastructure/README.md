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

### First-Time Deployment

**Important**: The first deployment requires two passes because the CloudFront hostname is only available after infrastructure creation, and Django needs it for CSRF/CORS configuration.

```bash
# Optional: Set budget email for cost alerts
export BUDGET_EMAIL=your-email@example.com

# Step 1: Initial infrastructure deployment (creates CloudFront distribution)
./stack_upgrade.py --infrastructure --backend --frontend

# Step 2: Get the CloudFront domain from CloudFormation outputs
# Look for "CloudFrontDomain" in the AWS Console -> CloudFormation -> MainStack -> Outputs
# Or run: aws cloudformation describe-stacks --stack-name MainStack --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDomain'].OutputValue" --output text

# Step 3: Re-deploy infrastructure with CloudFront domain parameter
./stack_upgrade.py --infrastructure --param CloudFrontDomain=<your-cloudfront-domain>.cloudfront.net

# Example:
# ./stack_upgrade.py --infrastructure --param CloudFrontDomain=dc0blpquzem84.cloudfront.net

# Step 4: Re-deploy backend to pick up the CloudFront hostname
./stack_upgrade.py --backend
```

### Subsequent Deployments

After the initial setup, you can deploy components individually or all at once:

```bash
# Deploy everything
./stack_upgrade.py --infrastructure --backend --frontend

# Or deploy individual components
./stack_upgrade.py --backend
./stack_upgrade.py --frontend
```

## What It Does

- `--infrastructure`: Deploys VPC, RDS, S3, ECR, ECS, ALB, CloudFront via CDK
- `--backend`: Creates source zip, uploads to S3, triggers CodeBuild to build Docker image, forces ECS deployment
- `--frontend`: Builds React app with Vite, uploads to S3 frontend bucket
