"""Configuration loaded from environment.

The constants `SESSION_TTL_SECONDS` and `AGGREGATION_MIN_N` encode two
non-negotiable principles. Overrides are intentionally restricted: tests may
shorten the TTL but production deploys must keep these defaults.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Hard ceilings — referenced from runtime guards, not just docs.
ABSOLUTE_MAX_SESSION_TTL = 30 * 60
ABSOLUTE_MIN_AGGREGATION_N = 10


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-6", alias="CIBERSPAR_MODEL")
    model_fast: str = Field(
        default="claude-haiku-4-5-20251001", alias="CIBERSPAR_MODEL_FAST"
    )

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    postgres_dsn: str = Field(
        default="postgresql+asyncpg://ciberspar:ciberspar@localhost:5432/ciberspar",
        alias="POSTGRES_DSN",
    )

    env: Literal["dev", "test", "prod"] = Field(default="dev", alias="CIBERSPAR_ENV")
    cors_origins: str = Field(
        default="http://localhost:3000", alias="CIBERSPAR_CORS_ORIGINS"
    )

    session_ttl_seconds: int = Field(
        default=ABSOLUTE_MAX_SESSION_TTL, alias="SESSION_TTL_SECONDS"
    )
    aggregation_min_n: int = Field(
        default=ABSOLUTE_MIN_AGGREGATION_N, alias="AGGREGATION_MIN_N"
    )

    @field_validator("session_ttl_seconds")
    @classmethod
    def _enforce_ttl_ceiling(cls, v: int, info) -> int:
        # Tests may shorten the TTL; prod cannot exceed the ceiling.
        env = info.data.get("env", "dev")
        if v > ABSOLUTE_MAX_SESSION_TTL:
            raise ValueError(
                f"SESSION_TTL_SECONDS={v} exceeds the 30-minute ceiling. "
                "This is a non-negotiable principle."
            )
        if env == "prod" and v < ABSOLUTE_MAX_SESSION_TTL:
            raise ValueError(
                "Production must use the full 30-minute TTL ceiling."
            )
        return v

    @field_validator("aggregation_min_n")
    @classmethod
    def _enforce_aggregation_floor(cls, v: int, info) -> int:
        env = info.data.get("env", "dev")
        if env == "prod" and v < ABSOLUTE_MIN_AGGREGATION_N:
            raise ValueError(
                "Production must keep AGGREGATION_MIN_N >= 10."
            )
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
