#!/bin/bash

# S3 buckets to delete
BUCKETS=(
  "sc-ai-insights-source"
  "sc-ai-insights-reports"
  "sc-ai-insights-frontend"
)

# ECR repositories to delete
ECR_REPOS=(
  "sc-ai-insights-backend"
)

# Secrets Manager secrets to delete
SECRETS=(
  "sc-ai-insights-db-credentials"
  "sc-ai-insights-db-connection"
  "sc-ai-insights-django-secret"
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
  aws ecr delete-repository --repository-name "$REPO" --force > /dev/null || true
done
echo "✓ ECR repositories deleted"

echo "Deleting Secrets Manager secrets..."
for SECRET in "${SECRETS[@]}"; do
  echo "  - $SECRET"
  aws secretsmanager delete-secret --secret-id "$SECRET" --force-delete-without-recovery > /dev/null 2>&1 || true
done
echo "✓ Secrets deleted"
