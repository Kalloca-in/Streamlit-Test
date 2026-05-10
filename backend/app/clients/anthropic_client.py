"""Anthropic client wrapper.

Single async client reused per process. The wrapper exposes only the surface
the rest of the app needs (`messages.create`-like calls), so we can swap or
mock it cleanly in tests.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from anthropic import AsyncAnthropic

from app.config import get_settings


@lru_cache
def get_anthropic() -> AsyncAnthropic:
    settings = get_settings()
    if not settings.anthropic_api_key and settings.env == "prod":
        raise RuntimeError("ANTHROPIC_API_KEY is required in prod.")
    return AsyncAnthropic(api_key=settings.anthropic_api_key or "test-key")


async def complete(
    *,
    system: str,
    messages: list[dict[str, Any]],
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.8,
) -> str:
    """Single-shot completion. Returns the concatenated text of the response."""
    client = get_anthropic()
    settings = get_settings()
    response = await client.messages.create(
        model=model or settings.model,
        system=system,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    parts: list[str] = []
    for block in response.content:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)
