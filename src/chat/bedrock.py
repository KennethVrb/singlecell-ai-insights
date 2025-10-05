import json
from pathlib import Path

import boto3

DEFAULT_BEDROCK_REGION = 'eu-west-1'
DEFAULT_MODEL_ID = 'eu.anthropic.claude-3-haiku-20240307-v1:0'
ANTHROPIC_VERSION = 'bedrock-2023-05-31'
DEFAULT_SYSTEM_PROMPT = (
    'You are an expert computational biologist helping interpret MultiQC '
    'reports. Explain sequencing quality metrics in plain language and '
    'recommend concrete follow-up actions when possible. Give concise, '
    'direct answers.'
)


def load_normalized_payload(path):
    """Load normalized MultiQC results from a JSON file.

    Args:
        path: File path pointing to a JSON document produced by
            `src.tools.normalizer.normalize`.

    Returns:
        Dictionary containing the normalized payload.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the payload cannot be parsed as JSON.
    """
    json_path = Path(path)
    if not json_path.exists():
        raise FileNotFoundError('missing normalized payload: {}'.format(path))
    with json_path.open('r', encoding='utf-8') as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise ValueError(
                'invalid JSON payload in {}'.format(path)
            ) from exc
    return data


class ClaudeBedrockChat:
    """Maintain a conversation with Claude about MultiQC results."""

    def __init__(
        self,
        client=None,
        model_id=None,
        region=None,
        max_tokens=2048,
        temperature=0.2,
        top_p=None,
        top_k=None,
        system_prompt=None,
        context_text=None,
    ):
        if region is None:
            region = DEFAULT_BEDROCK_REGION
        if client is None:
            client = boto3.client('bedrock-runtime', region_name=region)
        if model_id is None:
            model_id = DEFAULT_MODEL_ID
        if system_prompt is None:
            system_prompt = DEFAULT_SYSTEM_PROMPT

        self.client = client
        self.model_id = model_id
        self.region = region
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.base_system_prompt = system_prompt
        self.system_prompt = system_prompt
        self.context_text = None
        self.messages = [
            {
                'role': 'system',
                'content': [
                    {
                        'type': 'text',
                        'text': system_prompt,
                    }
                ],
            }
        ]

        if context_text:
            self.set_context(context_text=context_text)

    def reset_conversation(self):
        """Clear the stored messages for a fresh interaction."""
        self.messages = []

    def set_context(
        self,
        context_text=None,
        normalized_payload=None,
        system_prompt=None,
    ):
        """Attach MultiQC context to the conversation.

        Args:
            context_text: Formatted summary of MultiQC metrics.
            normalized_payload: Parsed normalized payload; the
                `context_text` key will be used if present.
            system_prompt: Optional override for the system prompt.
        """
        if context_text is None and normalized_payload:
            context_text = normalized_payload.get('context_text')
        if system_prompt is None:
            system_prompt = self.base_system_prompt

        prompt_lines = [system_prompt.strip()]
        if context_text:
            prompt_lines.append(
                'MultiQC normalized summary:\n{}'.format(context_text.strip())
            )
        self.system_prompt = '\n\n'.join(prompt_lines).strip()
        self.context_text = context_text
        self.reset_conversation()

    def _build_messages(self, message):
        compiled = list(self.messages)
        compiled.append(
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': message,
                    }
                ],
            }
        )
        return compiled

    def _invoke(self, message, max_tokens=None, temperature=None):
        payload = {
            'anthropic_version': ANTHROPIC_VERSION,
            'max_tokens': max_tokens or self.max_tokens,
            'temperature': temperature
            if temperature is not None
            else self.temperature,
            'messages': self._build_messages(message),
        }
        if self.system_prompt:
            payload['system'] = self.system_prompt
        if self.top_p is not None:
            payload['top_p'] = self.top_p
        if self.top_k is not None:
            payload['top_k'] = self.top_k

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(payload),
        )
        body = response['body'].read()
        data = json.loads(body)
        text_parts = []
        for block in data.get('content', []):
            if block.get('type') == 'text':
                text_parts.append(block.get('text', ''))
        return ''.join(text_parts).strip()

    def ask(self, message, max_tokens=None, temperature=None):
        """Send a user message and return Claude's reply."""
        reply = self._invoke(
            message, max_tokens=max_tokens, temperature=temperature
        )
        self.messages.append(
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': message,
                    }
                ],
            }
        )
        self.messages.append(
            {
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': reply,
                    }
                ],
            }
        )
        return reply

    def history(self):
        """Return the conversation history accumulated so far."""
        return list(self.messages)

    def load_context_from_file(self, path, system_prompt=None):
        """Load normalized results from disk and refresh the context."""
        payload = load_normalized_payload(path)
        self.set_context(
            context_text=payload.get('context_text'),
            normalized_payload=payload,
            system_prompt=system_prompt,
        )
        return payload
