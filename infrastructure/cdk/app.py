#!/usr/bin/env python3
import os

import aws_cdk as cdk
from cdk.budget_stack import BudgetStack
from cdk.main_stack import MainStack

app = cdk.App()

# Get account and region from environment variables or AWS CLI defaults
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION')

# If not provided, CDK will use current AWS environment
if account and region:
    env = cdk.Environment(account=account, region=region)
else:
    # Use current AWS environment
    env = None

# Get stack name prefix from environment or use default
stack_prefix = os.getenv('CDK_STACK_PREFIX', 'ScAI')

# Single parent stack containing all infrastructure
MainStack(
    app,
    f'{stack_prefix}Stack',
    env=env,
    description='SingleCell AI Insights infrastructure',
)

# Optional: Budget alerts (set BUDGET_EMAIL env var to enable)
budget_email = os.getenv('BUDGET_EMAIL')
if budget_email:
    BudgetStack(
        app,
        f'{stack_prefix}BudgetStack',
        email=budget_email,
        env=env,
        description='Cost monitoring and budget alerts',
    )

app.synth()
