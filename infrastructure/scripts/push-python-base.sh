#!/bin/bash
set -e

# Colors
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🐍 Pushing Python base image to ECR...${NC}"

# Get ECR repository URI from CDK stack
cd "$(dirname "$0")/../cdk"
PYTHON_BASE_REPO=$(aws cloudformation describe-stacks \
    --stack-name ScAICodeBuildStack \
    --query 'Stacks[0].Outputs[?OutputKey==`PythonBaseRepositoryUri`].OutputValue' \
    --output text)

if [ -z "$PYTHON_BASE_REPO" ]; then
    echo "❌ Could not find PythonBaseRepositoryUri in stack outputs"
    echo "   Make sure the CDK stack is deployed"
    exit 1
fi

echo -e "${GREEN}   Repository: ${PYTHON_BASE_REPO}${NC}"

# Get AWS region
AWS_REGION=$(aws configure get region || echo "eu-west-1")
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)

echo -e "${YELLOW}📥 Pulling python:3.12-bookworm from Docker Hub...${NC}"
docker pull python:3.12-bookworm

echo -e "${YELLOW}🏷️  Tagging image...${NC}"
docker tag python:3.12-bookworm ${PYTHON_BASE_REPO}:3.12-bookworm
docker tag python:3.12-bookworm ${PYTHON_BASE_REPO}:latest

echo -e "${YELLOW}🔐 Logging in to ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com

echo -e "${YELLOW}📤 Pushing to ECR...${NC}"
docker push ${PYTHON_BASE_REPO}:3.12-bookworm
docker push ${PYTHON_BASE_REPO}:latest

echo -e "${GREEN}✅ Python base image pushed successfully!${NC}"
echo -e "${GREEN}   Image: ${PYTHON_BASE_REPO}:3.12-bookworm${NC}"
