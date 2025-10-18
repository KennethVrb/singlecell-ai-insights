#!/usr/bin/env python3
import os
from pathlib import Path

import aws_cdk as cdk
from cdk.codebuild_stack import CodeBuildStack
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print(
        '⚠️  Warning: .env file not found. Copy .env-example to '
        '.env and configure.'
    )
    print(f'   Expected location: {env_path}')

app = cdk.App()

# Validate required environment variables
required_vars = ['CDK_DEFAULT_ACCOUNT', 'CDK_DEFAULT_REGION']
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise ValueError(
        f'Missing required environment variables: {", ".join(missing_vars)}\n'
        f'Please create a .env file based on .env-example'
    )

env = cdk.Environment(
    account=os.getenv('CDK_DEFAULT_ACCOUNT'),
    region=os.getenv('CDK_DEFAULT_REGION'),
)

CodeBuildStack(
    app,
    'ScAICodeBuildStack',
    env=env,
    description='CodeBuild infrastructure for SingleCell AI Insights backend',
)

app.synth()
