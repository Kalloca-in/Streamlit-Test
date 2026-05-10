"""Ephemeral session store backed by Redis.

Every write goes through this class. Every write sets the TTL. There is no
public API on this class that allows persistence beyond the TTL. There is no
"export" method. There is no "share" method. The only way data leaves Redis
is via the live WebSocket of the active session and via the debrief returned
to that same client.

Key layout:
- session:{sid}            -> SessionState JSON
- session:{sid}:defense    -> DefenseModel JSON
- session:{sid}:lock       -> reentrancy guard for the WebSocket handler
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.config import get_settings
from app.models.defense import DefenseModel
from app.models.session import SessionState

if TYPE_CHECKING:
    from redis.asyncio import Redis


_SESSION_KEY = "session:{sid}"
_DEFENSE_KEY = "session:{sid}:defense"


class SessionStore:
    def __init__(self, redis: "Redis", ttl_seconds: int | None = None) -> None:
        self._r = redis
        self._ttl = ttl_seconds or get_settings().session_ttl_seconds

    @property
    def ttl_seconds(self) -> int:
        return self._ttl

    # -- session state ------------------------------------------------------

    async def save_session(self, state: SessionState) -> None:
        await self._r.set(
            _SESSION_KEY.format(sid=state.session_id),
            state.model_dump_json(),
            ex=self._ttl,
        )

    async def load_session(self, sid: str) -> SessionState | None:
        raw = await self._r.get(_SESSION_KEY.format(sid=sid))
        if raw is None:
            return None
        return SessionState.model_validate_json(raw)

    # -- defense model ------------------------------------------------------

    async def save_defense(self, defense: DefenseModel) -> None:
        await self._r.set(
            _DEFENSE_KEY.format(sid=defense.session_id),
            defense.model_dump_json(),
            ex=self._ttl,
        )

    async def load_defense(self, sid: str) -> DefenseModel | None:
        raw = await self._r.get(_DEFENSE_KEY.format(sid=sid))
        if raw is None:
            return None
        return DefenseModel.model_validate_json(raw)

    # -- destruction --------------------------------------------------------

    async def destroy(self, sid: str) -> list[str]:
        """Wipe everything tied to a session id. Returns the keys that were
        present (used by the "Verify deletion" UI in the debrief)."""
        keys = [
            _SESSION_KEY.format(sid=sid),
            _DEFENSE_KEY.format(sid=sid),
        ]
        existed: list[str] = []
        for k in keys:
            if await self._r.exists(k):
                existed.append(k)
        if existed:
            await self._r.delete(*existed)
        return existed

    async def remaining_ttl(self, sid: str) -> int:
        """Seconds until the session expires. -2 if no key, -1 if no TTL set."""
        return await self._r.ttl(_SESSION_KEY.format(sid=sid))
