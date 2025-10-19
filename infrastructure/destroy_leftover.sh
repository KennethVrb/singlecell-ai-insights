#!/bin/bash

# S3 buckets to delete
BUCKETS=(
  "sc-ai-insights-source"
)

# ECR repositories to delete
ECR_REPOS=(
  "sc-ai-insights-backend"
)

echo "Deleting S3 buckets..."
for BUCKET in "${BUCKETS[@]}"; do
  echo "  - $BUCKET"
  aws s3api delete-objects --bucket "$BUCKET" \
    --delete "$(aws s3api list-object-versions --bucket "$BUCKET" \
    --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null || true
  
  aws s3api delete-objects --bucket "$BUCKET" \
    --delete "$(aws s3api list-object-versions --bucket "$BUCKET" \
    --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json)" 2>/dev/null || true
  
  aws s3 rb "s3://$BUCKET" 2>/dev/null || true
done
echo "✓ S3 buckets deleted"

echo "Deleting ECR repositories..."
for REPO in "${ECR_REPOS[@]}"; do
  echo "  - $REPO"
  aws ecr delete-repository --repository-name "$REPO" --force 2>/dev/null || true
done
echo "✓ ECR repositories deleted"
