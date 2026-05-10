"""Cliente Anthropic centralizado.

Todo paso por aquí para uniformar:
- modelo y parámetros por defecto
- caching de prompts del sistema (system prompts grandes y estables)
- structured outputs vía output_config.format
- manejo tipado de errores en español
- logging metadata-only en logs/generations.jsonl (nunca contenido)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
GENERATIONS_LOG = LOGS_DIR / "generations.jsonl"


@dataclass
class LLMResponse:
    text: str
    parsed: Any | None
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_creation_tokens: int
    model: str
    stop_reason: str


class LLMError(Exception):
    """Error visible al operador con mensaje en español."""


_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError(
                "Falta ANTHROPIC_API_KEY en el entorno. Copia .env.example a .env y configura la clave."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def model_name() -> str:
    return os.environ.get("MODEL_NAME", "claude-opus-4-7")


def call(
    *,
    system: str,
    user_message: str,
    max_tokens: int = 4000,
    cache_system: bool = True,
    output_schema: dict[str, Any] | None = None,
) -> LLMResponse:
    """Llamada estándar al modelo.

    El system prompt se cachea cuando supera ~1024 tokens (umbral de Opus).
    Si se pasa output_schema, se usa structured outputs y .parsed contiene
    el JSON ya validado.
    """
    client = get_client()
    model = model_name()

    system_blocks: list[dict[str, Any]] = [{"type": "text", "text": system}]
    if cache_system:
        system_blocks[0]["cache_control"] = {"type": "ephemeral"}

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_blocks,
        "messages": [{"role": "user", "content": user_message}],
    }
    if output_schema is not None:
        kwargs["output_config"] = {
            "format": {"type": "json_schema", "schema": output_schema}
        }

    try:
        response = client.messages.create(**kwargs)
    except anthropic.RateLimitError as e:
        raise LLMError(
            "El servicio está saturado (rate limit). Esperá unos segundos y reintentá."
        ) from e
    except anthropic.APIStatusError as e:
        if e.status_code >= 500:
            raise LLMError(
                f"El servicio devolvió un error temporal ({e.status_code}). Reintentá."
            ) from e
        raise LLMError(f"Error de API ({e.status_code}): {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise LLMError("Sin conexión al servicio. Verificá tu red.") from e

    text = "".join(b.text for b in response.content if b.type == "text")

    parsed: Any | None = None
    if output_schema is not None and text.strip():
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as e:
            raise LLMError(
                "El modelo devolvió JSON inválido pese al esquema estructurado. Reintentá."
            ) from e

    return LLMResponse(
        text=text,
        parsed=parsed,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        cache_read_tokens=response.usage.cache_read_input_tokens or 0,
        cache_creation_tokens=response.usage.cache_creation_input_tokens or 0,
        model=response.model,
        stop_reason=response.stop_reason or "",
    )


def log_generation(
    *,
    operator_hash: str,
    section: str,
    config: dict[str, Any],
    usage: LLMResponse | None,
) -> None:
    """Registra metadata de una generación. NUNCA registra contenido."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "operator_hash": operator_hash,
        "section": section,
        "config": config,
        "model": usage.model if usage else None,
        "input_tokens": usage.input_tokens if usage else None,
        "output_tokens": usage.output_tokens if usage else None,
        "cache_read_tokens": usage.cache_read_tokens if usage else None,
    }
    with GENERATIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
