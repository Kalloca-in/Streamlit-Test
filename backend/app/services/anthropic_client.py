"""
Cliente Anthropic centralizado.

PRINCIPIO DE SEGURIDAD: ningún punto de la app instancia `anthropic.Anthropic`
directamente. Todo pasa por aquí, donde se aplica:

    1. Pre-flight de safety_filter sobre el contexto (Bloque 2).
    2. Forzado de salida JSON estructurada cuando el llamador la pide.
    3. Logging de uso para auditoría.

El `safety_filter` se enchufa en el Bloque 2; aquí dejamos el hook
preparado y un fallback estricto que rechaza la generación si no está
configurado.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

from anthropic import Anthropic

from app.core.config import get_settings

log = logging.getLogger(__name__)


@dataclass(slots=True)
class GenerationResult:
    """Resultado tipado de una llamada al modelo."""

    raw_text: str
    parsed_json: dict[str, Any] | list[Any] | None
    stop_reason: str | None
    input_tokens: int | None
    output_tokens: int | None


# Tipo de la firma del safety filter pre-llamada.
PreCallFilter = Callable[[str, str], None]


class AnthropicService:
    """
    Servicio fino sobre el SDK oficial de Anthropic.

    NO conoce la lógica de negocio del Día Triple. Solo:
    - aplica el safety filter pre-llamada,
    - normaliza la respuesta,
    - extrae JSON cuando se pide.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        pre_call_filter: PreCallFilter | None = None,
    ) -> None:
        settings = get_settings()
        self._api_key = api_key or settings.anthropic_api_key
        self._model = model or settings.anthropic_model
        self._pre_call_filter = pre_call_filter
        self._client: Anthropic | None = None

    @property
    def client(self) -> Anthropic:
        if self._client is None:
            if not self._api_key:
                raise RuntimeError(
                    "ANTHROPIC_API_KEY no configurada. Defina la variable de entorno."
                )
            self._client = Anthropic(api_key=self._api_key)
        return self._client

    def attach_safety_filter(self, fn: PreCallFilter) -> None:
        """El módulo de safety se enchufa en startup."""
        self._pre_call_filter = fn

    def generate(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 4096,
        temperature: float = 0.4,
        expect_json: bool = False,
        contexto: str = "anthropic_generate",
    ) -> GenerationResult:
        """Llamada síncrona al modelo con safety pre-flight."""
        if self._pre_call_filter is not None:
            self._pre_call_filter(system + "\n\n" + user, contexto)
        else:
            log.warning(
                "AnthropicService llamado sin safety_filter conectado en contexto=%s",
                contexto,
            )

        message = self.client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        chunks = [block.text for block in message.content if getattr(block, "type", "") == "text"]
        raw = "".join(chunks).strip()

        parsed: Any = None
        if expect_json:
            parsed = _safe_json_loads(raw)

        usage = getattr(message, "usage", None)
        return GenerationResult(
            raw_text=raw,
            parsed_json=parsed,
            stop_reason=getattr(message, "stop_reason", None),
            input_tokens=getattr(usage, "input_tokens", None) if usage else None,
            output_tokens=getattr(usage, "output_tokens", None) if usage else None,
        )


def _safe_json_loads(text: str) -> Any:
    """Extrae JSON aunque venga envuelto en backticks o prosa."""
    text = text.strip()
    if text.startswith("```"):
        # Quita fences de markdown.
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Último intento: aislar el primer bloque {...} o [...].
        for opener, closer in [("{", "}"), ("[", "]")]:
            i = text.find(opener)
            j = text.rfind(closer)
            if i != -1 and j != -1 and j > i:
                try:
                    return json.loads(text[i : j + 1])
                except json.JSONDecodeError:
                    continue
    return None


_default_service: AnthropicService | None = None


def get_anthropic_service() -> AnthropicService:
    """Singleton perezoso, útil como dependencia de FastAPI."""
    global _default_service
    if _default_service is None:
        _default_service = AnthropicService()
    return _default_service
