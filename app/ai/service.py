# app/ai/service.py
from __future__ import annotations
import os
from openai import OpenAI

_client: OpenAI | None = None

def get_client() -> OpenAI:
    """
    OpenAI v1 клиентин бир жолу түзүп, кайра-кайра колдонот.
    ПРОКСИ ЖОК! base_url да бербейбиз (Azure колдонбосок).
    """
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing")
        _client = OpenAI(api_key=api_key)
    return _client

def ask(text: str, model: str | None = None) -> str:
    """
    Responses API менен жөнөкөй тексттик жооп кайтарат.
    """
    client = get_client()
    model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.responses.create(model=model, input=text)
    return getattr(resp, "output_text", "").strip()
