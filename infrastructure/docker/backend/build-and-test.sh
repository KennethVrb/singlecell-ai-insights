#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔨 Building Django Docker image...${NC}"

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$PROJECT_ROOT"

# Build the image
docker build \
    -f infrastructure/docker/backend/Dockerfile \
    -t singlecell-ai-insights-backend:latest \
    .

echo -e "${GREEN}✅ Build complete!${NC}"

# Test the image
echo -e "${YELLOW}🧪 Testing image...${NC}"

# Check if image exists
if docker image inspect singlecell-ai-insights-backend:latest > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Image exists${NC}"
else
    echo -e "${RED}❌ Image not found${NC}"
    exit 1
fi

# Check image size
IMAGE_SIZE=$(docker image inspect singlecell-ai-insights-backend:latest --format='{{.Size}}' | awk '{print $1/1024/1024}')
echo -e "${GREEN}📦 Image size: ${IMAGE_SIZE} MB${NC}"

# Optional: Run container for quick test
read -p "Do you want to run a test container? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🚀 Starting test container...${NC}"
    echo -e "${YELLOW}Note: This will fail without proper environment variables${NC}"
    
    docker run --rm \
        -p 8000:8000 \
        -e DJANGO_SECRET_KEY=test-secret-key \
        -e DJANGO_DEBUG=True \
        -e AWS_REGION=eu-west-1 \
        -e AWS_S3_PRESIGN_TTL=3600 \
        -e REPORTS_BUCKET=test-reports \
        singlecell-ai-insights-backend:latest
fi

echo -e "${GREEN}✅ All done!${NC}"
