"""FastAPI application entry."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.redis_client import close_redis
from app.config import get_settings
from app.db.session import dispose_engine
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis()
    await dispose_engine()


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
    return app


app = create_app()
