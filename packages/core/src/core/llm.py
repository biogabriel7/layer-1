"""Shared OpenRouter helpers used by the extractor and both judges.

Consolidates client bootstrap (dotenv + env check + base URL), the JSON
chat-completions call shape, and the markdown-fence stripping that some
OpenRouter responses wrap JSON in.
"""

import json
import os
import sys
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def make_client() -> OpenAI:
    """Build an OpenRouter-backed OpenAI client from OPENROUTER_API_KEY."""
    load_dotenv(".env.local")
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return OpenAI(base_url=_OPENROUTER_BASE_URL, api_key=api_key)


def call_json(
    client: OpenAI,
    system_prompt: str,
    user_msg: str,
    *,
    model: str,
) -> dict[str, Any]:
    """Issue a JSON chat-completion and return the parsed object.

    The anthropic-cache transform is opt-in per model: OpenRouter passes it
    through only to Anthropic backends; other providers ignore or reject it.
    """
    extra_body: dict[str, Any] = {}
    if model.startswith("anthropic/"):
        extra_body["transforms"] = ["anthropic-cache"]

    response = client.chat.completions.create(
        model=model,
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ],
        extra_body=extra_body,
    )
    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("LLM returned empty content")
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    parsed: dict[str, Any] = json.loads(text)
    return parsed
