#!/usr/bin/env python3
import os

import aws_cdk as cdk
from cdk.codebuild_stack import CodeBuildStack

app = cdk.App()

# Get account and region from environment variables or AWS CLI defaults
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION')

# If not provided, CDK will use current AWS CLI credentials
if account and region:
    env = cdk.Environment(account=account, region=region)
else:
    # Use current AWS environment
    env = None

CodeBuildStack(
    app,
    'ScAICodeBuildStack',
    env=env,
    description='CodeBuild infrastructure for SingleCell AI Insights backend',
)

app.synth()
