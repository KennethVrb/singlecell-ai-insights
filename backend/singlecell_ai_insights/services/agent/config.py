"""Configuration and AWS clients for agent service."""

import os

import boto3
from botocore.config import Config
from langchain_aws import BedrockEmbeddings, ChatBedrock

# Use non-interactive backend for matplotlib
os.environ.setdefault('MPLBACKEND', 'Agg')

# Environment variables
BEDROCK_MODEL_ID = 'eu.anthropic.claude-sonnet-4-20250514-v1:0'
BEDROCK_EMBED_MODEL_ID = 'amazon.titan-embed-text-v2:0'
AWS_REGION = os.environ['AWS_REGION']

REPORTS_BUCKET = os.environ['REPORTS_BUCKET']


# Quality thresholds
DUP_THRESH = 0.7
MAPPED_MIN = 1e6


# Configure boto3 client with retry settings
bedrock_config = Config(
    retries={'max_attempts': 10, 'mode': 'adaptive'},
    read_timeout=300,
)

bedrock_client = boto3.client(
    'bedrock-runtime', region_name=AWS_REGION, config=bedrock_config
)

# LangChain/LangGraph with custom client
llm = ChatBedrock(
    model_id=BEDROCK_MODEL_ID,
    client=bedrock_client,
    model_kwargs={
        'max_tokens': 4096,
        'temperature': 0.7,
    },
)
emb = BedrockEmbeddings(
    model_id=BEDROCK_EMBED_MODEL_ID, region_name=AWS_REGION
)
