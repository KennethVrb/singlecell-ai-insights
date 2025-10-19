"""Configuration and AWS clients for agent service."""

import os

from langchain_aws import BedrockEmbeddings, ChatBedrock

# Use non-interactive backend for matplotlib
os.environ.setdefault('MPLBACKEND', 'Agg')

# Environment variables
BEDROCK_MODEL_ID = 'eu.anthropic.claude-sonnet-4-20250514-v1:0'
BEDROCK_EMBED_MODEL_ID = 'amazon.titan-embed-text-v2:0'
AWS_REGION = os.environ['AWS_REGION']

REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
ARTIFACT_BUCKET = os.environ['ARTIFACT_BUCKET']


# Quality thresholds
DUP_THRESH = 0.7
MAPPED_MIN = 1e6


# LangChain/LangGraph
llm = ChatBedrock(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION)
emb = BedrockEmbeddings(
    model_id=BEDROCK_EMBED_MODEL_ID, region_name=AWS_REGION
)
