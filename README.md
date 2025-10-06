# Single-cell AI Insights

Utilities for normalizing MultiQC reports and discussing sequencing quality with Claude via Amazon Bedrock.

> **New:** see [`docs/poc_solution.md`](docs/poc_solution.md) for a proposed React + Django proof-of-concept that surfaces
> HealthOmics runs, exposes MultiQC metrics from S3, and embeds the Claude chatbot in a web UI.

## Installation

```bash
pip install -r requirements.txt
```

Ensure AWS credentials are configured with access to Bedrock.

## Usage

### Normalize MultiQC Results

```bash
python main.py normalize /path/to/multiqc/output --json-output normalized.json
```

This command reads `multiqc_data.json`, computes normalized metrics, and writes structured output alongside a human-readable summary.

### Chat with Claude

```bash
python main.py chat --payload normalized.json --ask "Which samples look concerning?"
```

The chat command loads the normalized payload and opens an interactive conversation with Claude. Use `--system-prompt`, `--model-id`, and sampling arguments to customize responses. Provide `--once` to skip interactive mode.

## Project Structure

- `src/tools/normalize.py` contains utilities for parsing MultiQC data and building summaries.
- `src/chat/bedrock.py` implements `ClaudeBedrockChat` for communicating with Claude.
- `docs/claude_chat.md` offers additional configuration notes for the chat layer.
- `docs/poc_solution.md` outlines the end-to-end web proof-of-concept architecture.

## Requirements

- Python 3.9+
- AWS account with Bedrock access
- `boto3`
