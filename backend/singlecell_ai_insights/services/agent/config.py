"""Configuration and AWS clients for agent service."""

import os

import boto3
from langchain_aws import BedrockEmbeddings, ChatBedrock

# Use non-interactive backend for matplotlib
os.environ.setdefault('MPLBACKEND', 'Agg')

# Environment variables
BEDROCK_MODEL_ID = os.environ['BEDROCK_MODEL_ID']
BEDROCK_EMBED_MODEL_ID = os.environ['BEDROCK_EMBED_MODEL_ID']
AWS_REGION = os.environ['AWS_REGION']

REPORTS_BUCKET = os.environ['REPORTS_BUCKET']
ARTIFACT_BUCKET = os.environ['ARTIFACT_BUCKET']
PRESIGN_TTL = '3600'

# Quality thresholds
DUP_THRESH = 0.7
MAPPED_MIN = 1e6

# AWS Clients
session = boto3.Session(region_name=AWS_REGION)
s3 = session.client('s3')

# LangChain/LangGraph
llm = ChatBedrock(model_id=BEDROCK_MODEL_ID, region_name=AWS_REGION)
emb = BedrockEmbeddings(
    model_id=BEDROCK_EMBED_MODEL_ID, region_name=AWS_REGION
)
