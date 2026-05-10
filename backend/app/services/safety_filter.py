"""
Safety filter — defensa estructural de los principios no negociables.

Se invoca:

1. PRE-GENERACIÓN (`safety_pre_call_filter`): se conecta como hook al
   `AnthropicService` y bloquea cualquier prompt que contenga marca
   real, OSINT del usuario, dificultad > 3 o tema de línea roja.

2. POST-GENERACIÓN (`validate_dia_triple_safe`): valida un DiaTripleCreate
   ya estructurado. Última barrera antes de persistir en la base.

Ambos caminos derivan del mismo motor (`SafetyFilter.scan`) para que la
verdad sea una sola.

PRINCIPIO: el filtro falla CERRADO. Si hay duda, levanta excepción y
loguea. Mejor un Día Triple no generado que uno con marca real.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.data.blocklist_marcas_reales import (
    OSINT_REAL_USER_PATTERNS,
    RED_LINE_TOPICS,
    REAL_BRAND_BLOCKLIST,
)
from app.models.safety_log import SafetyLog
from app.schemas.dia_triple import DiaTripleCreate
from app.services.marcas_catalog import nombres_validos_lower, slugs_validos

log = logging.getLogger(__name__)


# --- Motivos canónicos del bloqueo ---
MOTIVO_MARCA_REAL = "marca_real_detectada"
MOTIVO_RED_LINE = "tema_linea_roja"
MOTIVO_OSINT_USUARIO = "osint_usuario_real"
MOTIVO_DIFICULTAD_EXCEDIDA = "dificultad_excedida"
MOTIVO_MARCA_NO_CATALOGADA = "marca_ficticia_no_catalogada"
MOTIVO_CATALOGO_VACIO = "catalogo_marcas_vacio"


class SafetyViolation(Exception):
    """Violación detectada por el filtro. Bloquea la operación."""

    def __init__(self, motivo: str, detalles: dict, contexto: str, payload_extracto: str = "") -> None:
        super().__init__(f"[{motivo}] {detalles}")
        self.motivo = motivo
        self.detalles = detalles
        self.contexto = contexto
        self.payload_extracto = payload_extracto[:1000]


# --- Normalización ---
_PUNCT_TO_SPACE = re.compile(r"[^\w\s]+", re.UNICODE)


def _normalize(text: str) -> str:
    """Minúsculas + sin tildes + puntuación a espacios + colapso de espacios."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = _PUNCT_TO_SPACE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass(frozen=True)
class _CompiledRule:
    motivo: str
    pattern: re.Pattern[str]
    label: str  # qué fue lo que matcheó (para detalles)


def _compile_rules() -> list[_CompiledRule]:
    rules: list[_CompiledRule] = []

    for term in REAL_BRAND_BLOCKLIST:
        # Normaliza el término antes de compilar para consistencia con _normalize.
        norm = _normalize(term)
        if not norm:
            continue
        # \b en bordes y \s+ entre palabras para tolerar espacios variables.
        body = r"\s+".join(re.escape(w) for w in norm.split())
        rules.append(
            _CompiledRule(
                motivo=MOTIVO_MARCA_REAL,
                pattern=re.compile(rf"(?<!\w){body}(?!\w)"),
                label=term,
            )
        )

    for topic, frases in RED_LINE_TOPICS:
        for frase in frases:
            norm = _normalize(frase)
            body = r"\s+".join(re.escape(w) for w in norm.split())
            rules.append(
                _CompiledRule(
                    motivo=MOTIVO_RED_LINE,
                    pattern=re.compile(rf"(?<!\w){body}(?!\w)"),
                    label=f"{topic}:{frase}",
                )
            )

    for patt in OSINT_REAL_USER_PATTERNS:
        norm = _normalize(patt)
        body = r"\s+".join(re.escape(w) for w in norm.split())
        rules.append(
            _CompiledRule(
                motivo=MOTIVO_OSINT_USUARIO,
                pattern=re.compile(rf"(?<!\w){body}(?!\w)"),
                label=patt,
            )
        )

    return rules


_RULES_CACHE: list[_CompiledRule] | None = None


def _rules() -> list[_CompiledRule]:
    global _RULES_CACHE
    if _RULES_CACHE is None:
        _RULES_CACHE = _compile_rules()
    return _RULES_CACHE


# --- API pública ---


class SafetyFilter:
    """Motor de chequeo. Stateless excepto por las reglas compiladas."""

    @staticmethod
    def scan_text(text: str, contexto: str) -> None:
        """
        Escanea texto libre. Si encuentra una violación, levanta SafetyViolation.
        El catálogo de marcas ficticias NO se valida aquí (no hay forma robusta
        de exigir que aparezca alguna). Eso se hace post-generación con
        validate_dia_triple_safe.
        """
        if not text:
            return
        normalized = _normalize(text)
        for rule in _rules():
            m = rule.pattern.search(normalized)
            if m:
                detalles = {"label": rule.label, "match": m.group(0)}
                _persistir_log(
                    motivo=rule.motivo,
                    contexto=contexto,
                    payload_extracto=text[:1000],
                    detalles=detalles,
                )
                raise SafetyViolation(
                    motivo=rule.motivo,
                    detalles=detalles,
                    contexto=contexto,
                    payload_extracto=text,
                )

    @staticmethod
    def assert_difficulty(nivel: int, contexto: str) -> None:
        max_d = get_settings().max_difficulty
        if nivel > max_d:
            detalles = {"nivel_solicitado": nivel, "max_permitido": max_d}
            _persistir_log(
                motivo=MOTIVO_DIFICULTAD_EXCEDIDA,
                contexto=contexto,
                payload_extracto=str(detalles),
                detalles=detalles,
            )
            raise SafetyViolation(
                motivo=MOTIVO_DIFICULTAD_EXCEDIDA,
                detalles=detalles,
                contexto=contexto,
            )


def safety_pre_call_filter(text: str, contexto: str) -> None:
    """Hook que el AnthropicService invoca antes de cada llamada."""
    SafetyFilter.scan_text(text, contexto=contexto)


def validate_dia_triple_safe(dt: DiaTripleCreate, contexto: str = "validate_dia_triple") -> None:
    """
    Validación post-generación de un DiaTripleCreate completo.

    Aplica:
    1. Techo de dificultad (redundante con CHECK constraint, defensa en profundidad).
    2. Cada marca_ficticia_slug existe en el catálogo cerrado.
    3. Texto narrativo (cuerpo, asunto, remitente_aparente, nota_revelacion)
       no contiene marcas reales ni temas de línea roja.
    """
    SafetyFilter.assert_difficulty(int(dt.nivel_dificultad), contexto)

    catalogo = slugs_validos()
    if not catalogo:
        # Fail-closed: sin catálogo cargado, no se aprueba nada.
        _persistir_log(
            motivo=MOTIVO_CATALOGO_VACIO,
            contexto=contexto,
            payload_extracto=dt.titulo,
            detalles={},
        )
        raise SafetyViolation(
            motivo=MOTIVO_CATALOGO_VACIO,
            detalles={},
            contexto=contexto,
        )

    for acto in dt.actos:
        slug = acto.marca_ficticia_slug
        if slug is not None and slug not in catalogo:
            detalles = {"slug": slug, "rol": acto.rol.value}
            _persistir_log(
                motivo=MOTIVO_MARCA_NO_CATALOGADA,
                contexto=contexto,
                payload_extracto=acto.cuerpo[:300],
                detalles=detalles,
            )
            raise SafetyViolation(
                motivo=MOTIVO_MARCA_NO_CATALOGADA,
                detalles=detalles,
                contexto=contexto,
            )

    # Escaneo de texto narrativo concatenado.
    blob_partes = [dt.titulo, dt.nota_revelacion]
    for acto in dt.actos:
        blob_partes.extend([acto.remitente_aparente, acto.asunto or "", acto.cuerpo])
        for ind in acto.indicadores:
            blob_partes.extend([ind.fragmento, ind.explicacion])

    blob = "\n".join(blob_partes)
    SafetyFilter.scan_text(blob, contexto=contexto)


def catalogo_es_seguro_contra_blocklist() -> tuple[bool, list[str]]:
    """
    Self-check del catálogo de marcas ficticias contra la blocklist.

    Devuelve (ok, colisiones). Útil como test y como gate de CI.
    """
    colisiones: list[str] = []
    for nombre in nombres_validos_lower():
        normalized = _normalize(nombre)
        for rule in _rules():
            if rule.motivo != MOTIVO_MARCA_REAL:
                continue
            if rule.pattern.search(normalized):
                colisiones.append(f"{nombre} ⟶ matched {rule.label}")
    return (len(colisiones) == 0, colisiones)


# --- Persistencia del log ---


def _persistir_log(
    *, motivo: str, contexto: str, payload_extracto: str, detalles: dict
) -> None:
    """
    Persiste en safety_logs si la DB está disponible. Si no (entorno de test
    sin DB real), loguea a stderr. NUNCA bloquea la decisión por error de log.
    """
    try:
        db = SessionLocal()
        try:
            db.add(
                SafetyLog(
                    motivo=motivo,
                    contexto=contexto,
                    payload_extracto=payload_extracto,
                    detalles=detalles,
                )
            )
            db.commit()
        finally:
            db.close()
    except Exception as e:  # noqa: BLE001
        log.warning(
            "No se pudo persistir SafetyLog (motivo=%s, contexto=%s): %s",
            motivo,
            contexto,
            e,
        )
