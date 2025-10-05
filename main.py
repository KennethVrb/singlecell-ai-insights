#!/usr/bin/env python3
"""CLI entrypoint for normalizing MultiQC data or chatting with Claude."""

import argparse
import sys
from pathlib import Path

from src.chat import ClaudeBedrockChat
from src.tools.normalizer import normalize


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            'Normalize MultiQC results or chat with Claude on Bedrock.'
        ),
    )
    subparsers = parser.add_subparsers(dest='command')

    normalize_parser = subparsers.add_parser(
        'normalize',
        help='Normalize MultiQC data from a directory.',
    )
    normalize_parser.add_argument(
        'input_dir',
        help='Directory containing multiqc_data.json.',
    )
    normalize_parser.add_argument(
        '--json-output',
        help='Path to write normalized JSON output. Defaults to stdout only.',
    )
    normalize_parser.add_argument(
        '--text-output',
        help='Path to write human-readable summary text.',
    )

    chat_parser = subparsers.add_parser(
        'chat',
        help='Start or resume a chat with Claude about normalized results.',
    )
    chat_parser.add_argument(
        '--payload',
        default='normalized.json',
        help='Path to normalized JSON payload (default: normalized.json).',
    )
    chat_parser.add_argument(
        '--system-prompt',
        help='Override the default system prompt.',
    )
    chat_parser.add_argument(
        '--ask',
        help='Send a single question to Claude before interactive mode.',
    )
    chat_parser.add_argument(
        '--once',
        action='store_true',
        help='Send only the question from --ask and exit.',
    )
    chat_parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Disable interactive prompt after initial question.',
    )
    chat_parser.add_argument(
        '--model-id',
        help='Override the Bedrock model identifier.',
    )
    chat_parser.add_argument(
        '--max-tokens',
        type=int,
        help='Maximum tokens for Claude responses.',
    )
    chat_parser.add_argument(
        '--temperature',
        type=float,
        help='Sampling temperature.',
    )
    chat_parser.add_argument(
        '--top-p',
        type=float,
        help='Nucleus sampling probability mass.',
    )
    chat_parser.add_argument(
        '--top-k',
        type=int,
        help='Top-k sampling threshold.',
    )

    return parser.parse_args(argv)


def run_normalize(args):
    input_dir = Path(args.input_dir)
    json_output = args.json_output
    text_output = args.text_output

    normalize(input_dir, json_output, text_output)


def build_chat(args):
    options = {}
    if args.model_id:
        options['model_id'] = args.model_id
    if args.max_tokens is not None:
        options['max_tokens'] = args.max_tokens
    if args.temperature is not None:
        options['temperature'] = args.temperature
    if args.top_p is not None:
        options['top_p'] = args.top_p
    if args.top_k is not None:
        options['top_k'] = args.top_k

    chat = ClaudeBedrockChat(**options)

    payload_path = Path(args.payload)
    if payload_path.exists():
        chat.load_context_from_file(
            payload_path,
            system_prompt=args.system_prompt,
        )
    else:
        chat.set_context(system_prompt=args.system_prompt)
    return chat


def run_chat(args):
    chat = build_chat(args)

    if args.ask:
        reply = chat.ask(args.ask)
        print('Claude:', reply)
        if args.once:
            return
    if args.no_interactive:
        return

    print('Starting interactive chat. Press Enter on an empty line to exit.')
    while True:
        try:
            message = input('You: ').strip()
        except EOFError:
            print('')
            break
        except KeyboardInterrupt:
            print('')
            break
        if not message:
            break
        reply = chat.ask(message)
        print('Claude:', reply)


def main(argv=None):
    args = parse_args(argv)
    if args.command == 'normalize':
        run_normalize(args)
    elif args.command == 'chat':
        run_chat(args)
    else:
        message = 'Specify a command. Use --help for more information.'
        print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
