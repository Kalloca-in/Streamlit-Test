"""Heuristics for detecting end-of-session conditions.

Three classes of detection:

1. Capture: the user just produced content matching the attacker's objective.
   For now we use cheap pattern checks (credentials, OTPs, etc.) — good
   enough to catch obvious wins. A future refinement would call an LLM
   classifier.

2. Victory: the user explicitly shut the attacker down legitimately. Cheap
   keyword check on user text + attacker decided to retire (signaled by
   the attacker output containing a retreat marker).

3. Time-out: handled by the WebSocket loop using `state.elapsed_seconds`.
"""

from __future__ import annotations

import re

from app.models.attacker import AttackerObjective

_CREDENTIAL_PATTERNS = [
    re.compile(r"\b\d{4,8}\b"),  # OTP-shaped
    re.compile(r"contraseña\s*[:=]\s*\S+", re.I),
    re.compile(r"clave\s*[:=]\s*\S+", re.I),
    re.compile(r"password\s*[:=]\s*\S+", re.I),
    re.compile(r"\botp\b\s*[:=]\s*\S+", re.I),
    re.compile(r"código\s+(?:de\s+)?(?:verificación|seguridad|otp|sms)\s*[:=]?\s*\d{3,8}", re.I),
]

_CLICK_PATTERNS = [
    re.compile(r"\b(ya\s+entré|hice\s+clic|abrí\s+el\s+enlace|cliqu[eé])\b", re.I),
]

_INDUCED_ACTION_PATTERNS = [
    re.compile(r"\b(transferí|envié|aprobé|autoricé|cambi[eé]\s+la\s+contraseña)\b", re.I),
]

_VICTORY_PATTERNS = [
    re.compile(r"\b(no\s+voy\s+a\s+colaborar|esto\s+es\s+un\s+intento|reportar(é|e)|"
                r"voy\s+a\s+verificar\s+por\s+otro\s+canal|consult[áa]r[éa]\s+con|"
                r"no\s+puedo\s+confirmar\s+esto|no\s+te\s+conozco)\b", re.I),
]


def detect_capture(user_text: str, objective: AttackerObjective) -> bool:
    if objective == AttackerObjective.EXTRACT_CREDENTIAL:
        return any(p.search(user_text) for p in _CREDENTIAL_PATTERNS)
    if objective == AttackerObjective.INDUCE_CLICK:
        return any(p.search(user_text) for p in _CLICK_PATTERNS)
    if objective == AttackerObjective.INDUCE_ACTION:
        return any(p.search(user_text) for p in _INDUCED_ACTION_PATTERNS)
    if objective == AttackerObjective.EXTRACT_SENSITIVE_DATA:
        # Heuristic: user replied with a >50-char chunk of structured-looking data.
        return bool(re.search(r"[A-Z0-9_-]{8,}", user_text)) and len(user_text) > 60
    return False


def detect_victory(user_text: str) -> bool:
    return any(p.search(user_text) for p in _VICTORY_PATTERNS)
