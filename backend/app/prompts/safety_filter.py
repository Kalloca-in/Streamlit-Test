"""Reference / contract module for the safety_filter pipeline.

The active enforcement lives in `app.services.safety_filter`. This module
documents *what* is being enforced and exposes a small constant surface for
tests and observability.
"""

from __future__ import annotations

PROMPT_VERSION = "safety_filter.v1"


SAFETY_CONTRACT = """
The attacker MUST NOT:

1. Use real brand, bank, institution, or person names. Detected via:
   - Curated blocklist (REAL_BRAND_BLOCKLIST in services/safety_filter.py)
   - Real-domain pattern check (anything not under .example/.test/.invalid/.localhost)

2. Approach red-line topics:
   - Death of the user's specific real family members
   - Sexual content
   - Partisan political content
   - Explicit physical threats
   - Terminal illness of children

3. Request real personal data of the user:
   - Real ID numbers, real addresses, real personal passwords, real
     payment credentials. (The user's CHARACTER may have plausible
     fictional data; the player themselves never gives real data.)

When triggered, the message is rewritten or replaced by a neutral
in-character cover line. The interception is logged ONLY by category, never
by content.
"""

INTERCEPTION_CATEGORIES = (
    "real_brand",
    "real_domain",
    "red_line_topic",
    "real_user_pii_request",
)
