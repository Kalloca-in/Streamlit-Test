"""FastAPI dependency providers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.clients.redis_client import get_redis
from app.services.session_store import SessionStore


def get_session_store() -> SessionStore:
    return SessionStore(redis=get_redis())


SessionStoreDep = Annotated[SessionStore, Depends(get_session_store)]
