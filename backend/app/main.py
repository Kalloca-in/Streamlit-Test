"""FastAPI application entry."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.clients.redis_client import close_redis
from app.config import get_settings
from app.db.base import Base
from app.db.session import dispose_engine, get_engine
from app.routers import debrief, demo, facilitator, health, sessions, sparring


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Best-effort schema bootstrap. If Postgres is unavailable in dev,
    # the app still serves Redis-only flows.
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logging.warning("Postgres unavailable on startup (%s); metrics disabled.", type(e).__name__)
    yield
    await close_redis()
    try:
        await dispose_engine()
    except Exception:
        pass


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="CiberSpar API",
        version="0.1.0",
        description=(
            "Adaptive conversational sparring against social engineering. "
            "Sessions are ephemeral by design."
        ),
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(sessions.router)
    app.include_router(sparring.router)
    app.include_router(debrief.router)
    app.include_router(demo.router)
    app.include_router(facilitator.router)
    return app


app = create_app()
