#!/bin/bash
set -e

# Default stack prefix
STACK_PREFIX="${1:-ScAI}"

echo "🔍 Fetching infrastructure details..."

# Get stack outputs
STACK_NAME="${STACK_PREFIX}Stack"
CLUSTER_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='EcsClusterName'].OutputValue" \
    --output text)

SERVICE_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='EcsServiceName'].OutputValue" \
    --output text)

if [ -z "$CLUSTER_NAME" ] || [ -z "$SERVICE_NAME" ]; then
    echo "❌ Could not find ECS cluster/service in stack outputs"
    exit 1
fi

echo "   Cluster: $CLUSTER_NAME"
echo "   Service: $SERVICE_NAME"
echo ""

# Find running task
echo "🔍 Finding running ECS task..."
TASK_ARN=$(aws ecs list-tasks \
    --cluster "$CLUSTER_NAME" \
    --service-name "$SERVICE_NAME" \
    --desired-status RUNNING \
    --query 'taskArns[0]' \
    --output text)

if [ -z "$TASK_ARN" ] || [ "$TASK_ARN" = "None" ]; then
    echo "❌ No running tasks found. Is the service running?"
    exit 1
fi

TASK_ID=$(echo "$TASK_ARN" | awk -F'/' '{print $NF}')
echo "   Task: $TASK_ID"
echo ""

# Connect interactively
echo "🚀 Connecting to ECS container..."
echo ""
echo "💡 Once connected, you can create a user with:"
echo "   python manage.py shell -c \\"
echo "     from django.contrib.auth import get_user_model; \\"
echo "     User = get_user_model(); \\"
echo "     user, created = User.objects.get_or_create(username='admin', email='admin@example.com'); \\"
echo "     user.set_password('your-password'); \\"
echo "     user.is_staff = True; \\"
echo "     user.save(); \\"
echo "     print('User created!' if created else 'User updated!')\\"
echo ""
echo "   Or use: python manage.py createsuperuser"
echo ""

aws ecs execute-command \
    --cluster "$CLUSTER_NAME" \
    --task "$TASK_ID" \
    --container DjangoContainer \
    --interactive \
    --command "/bin/bash"
