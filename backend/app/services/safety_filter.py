"""Safety filter applied before every attacker message reaches the user.

Two layers:

1. Hard blocklist: real banks, real institutions, real people, real domains.
   The list is intentionally incomplete — defense in depth, not defense in
   one. The semantic check below catches the long tail.
2. Red-line topics: explicit content the attacker may never approach
   regardless of how the conversation got there.

When triggered, the filter returns a `FilterResult` with the rewritten text
and an interception category. Logs record only the category, never the
content.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

from app.data_catalogs import fictitious_brands

# ---------------------------------------------------------------------------
# Real-world entity blocklist.
#
# Curated, lowercase, word-boundary matched. Not exhaustive by design.
# ---------------------------------------------------------------------------

REAL_BRAND_BLOCKLIST: set[str] = {
    # Banks (international)
    "santander", "bbva", "citibank", "hsbc", "scotiabank", "jpmorgan",
    "wells fargo", "bank of america", "goldman sachs", "deutsche bank",
    # Banks (LATAM real)
    "banco pichincha", "produbanco", "banco bolivariano", "banco guayaquil",
    "banco del pacífico", "banco del pacifico", "banco internacional",
    "banco de chile", "bancolombia", "davivienda", "banamex",
    "banco azteca", "banco galicia", "banco macro",
    # Big tech
    "google", "microsoft", "apple", "amazon", "meta", "facebook",
    "instagram", "whatsapp", "tiktok", "twitter", "linkedin", "github",
    "openai", "anthropic", "netflix", "spotify",
    # Payment / fintech real
    "paypal", "stripe", "mercadopago", "mercado pago", "nequi", "yape",
    "binance", "coinbase", "kraken",
    # Telco real
    "claro", "movistar", "tigo", "telefónica", "telefonica", "vodafone", "att",
    # Delivery / streaming real
    "uber", "rappi", "didi", "pedidosya", "doordash", "deliveroo",
    "disney plus", "disney+", "hbo", "hbo max", "amazon prime",
    # Government / regulators (sample)
    "sri", "irs", "afip", "dian", "sat", "policía nacional", "policia nacional",
    "fbi", "interpol", "cia",
    # Universities (sample real)
    "harvard", "mit", "stanford", "uba", "unam",
}

# Domains that obviously map to real services
REAL_DOMAIN_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b\w+\.(com|net|org|io|gov|edu|co|gob|gob\.\w+)\b", re.IGNORECASE),
]

ALLOWED_DOMAIN_SUFFIXES = (".example", ".test", ".invalid", ".localhost")


class InterceptionCategory(StrEnum):
    REAL_BRAND = "real_brand"
    REAL_DOMAIN = "real_domain"
    RED_LINE_TOPIC = "red_line_topic"
    REAL_USER_PII_REQUEST = "real_user_pii_request"
    NONE = "none"


@dataclass(frozen=True)
class FilterResult:
    safe_text: str
    category: InterceptionCategory
    intercepted: bool


# Red-line categories: cheap keyword check + a curated phrase list.
# Semantic check happens upstream via the evaluator / model output guards.
_RED_LINE_PATTERNS: dict[InterceptionCategory, list[re.Pattern[str]]] = {
    InterceptionCategory.RED_LINE_TOPIC: [
        re.compile(r"\b(murió|muerte|fallec\w+) (tu|su) (madre|padre|hijo|hija)\b", re.I),
        re.compile(r"\b(cáncer|cancer|leucemia) (terminal|de tu hij\w+|de su hij\w+)\b", re.I),
        re.compile(r"\b(amenaz\w*|matar(te|los?|la)?|hacer(te)? daño)\b", re.I),
        re.compile(r"\b(sex\w+|porno\w*|desnud\w*)\b", re.I),
        re.compile(r"\b(votar por|partido (político|politico)|campaña electoral)\b", re.I),
    ],
    InterceptionCategory.REAL_USER_PII_REQUEST: [
        re.compile(
            r"\b(d[áa]me|env[íi]ame|comp[áa]rteme) "
            r"(tu|su) (cédula real|cedula real|dni real|cuenta bancaria real|"
            r"contraseña personal real|tarj\w+ de cr[ée]dito real|"
            r"direcci[óo]n de tu casa real)\b",
            re.I,
        ),
    ],
}


def _build_brand_pattern(blocklist: set[str]) -> re.Pattern[str]:
    sorted_terms = sorted(blocklist, key=len, reverse=True)
    escaped = [re.escape(t) for t in sorted_terms]
    return re.compile(r"(?<!\w)(" + "|".join(escaped) + r")(?!\w)", re.IGNORECASE)


_BRAND_PATTERN = _build_brand_pattern(REAL_BRAND_BLOCKLIST)


def _strip_real_domains(text: str) -> tuple[str, bool]:
    """Remove anything that looks like a real domain (anything not in
    .example/.test/.invalid/.localhost). Returns (cleaned, hit)."""
    hit = False

    def replace(match: re.Match[str]) -> str:
        nonlocal hit
        token = match.group(0)
        lower = token.lower()
        if lower.endswith(ALLOWED_DOMAIN_SUFFIXES):
            return token
        hit = True
        return "[dominio-no-permitido.example]"

    cleaned = REAL_DOMAIN_PATTERNS[0].sub(replace, text)
    return cleaned, hit


def _replace_real_brands(text: str) -> tuple[str, bool]:
    """Replace any blocklisted brand with a fictitious analog from the catalog."""
    catalog = fictitious_brands()
    fallback = catalog[0]["display_name"] if catalog else "Marca Ficticia"
    hit = False

    def pick_replacement(_: re.Match[str]) -> str:
        nonlocal hit
        hit = True
        return fallback

    cleaned = _BRAND_PATTERN.sub(pick_replacement, text)
    return cleaned, hit


def _check_red_lines(text: str) -> InterceptionCategory:
    for category, patterns in _RED_LINE_PATTERNS.items():
        for p in patterns:
            if p.search(text):
                return category
    return InterceptionCategory.NONE


def _neutralize_red_line(text: str, category: InterceptionCategory) -> str:
    """Replace the entire turn with a neutral, in-character cover line.

    Rationale: trying to surgically excise red-line content risks leaving
    enough context that the user can reconstruct it. Better to drop the turn.
    """
    return (
        "Mira, mejor cambiemos de tema. ¿Podemos seguir con lo que te "
        "comentaba antes?"
    )


def filter_attacker_message(text: str) -> FilterResult:
    """Apply the full filter pipeline to a candidate attacker message."""
    if not text or not text.strip():
        return FilterResult(safe_text=text, category=InterceptionCategory.NONE, intercepted=False)

    red_line = _check_red_lines(text)
    if red_line != InterceptionCategory.NONE:
        return FilterResult(
            safe_text=_neutralize_red_line(text, red_line),
            category=red_line,
            intercepted=True,
        )

    cleaned, brand_hit = _replace_real_brands(text)
    cleaned, domain_hit = _strip_real_domains(cleaned)

    if brand_hit:
        return FilterResult(safe_text=cleaned, category=InterceptionCategory.REAL_BRAND, intercepted=True)
    if domain_hit:
        return FilterResult(safe_text=cleaned, category=InterceptionCategory.REAL_DOMAIN, intercepted=True)

    return FilterResult(safe_text=cleaned, category=InterceptionCategory.NONE, intercepted=False)
