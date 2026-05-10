"""
Configuración global de CiberTeatro.

Centraliza variables de entorno y constantes que actúan como
salvaguardas de los principios no negociables del producto:

    * MAX_DIFFICULTY = 3 (techo pedagógico, nunca "indistinguible")
    * MIN_AGGREGATE_N = 10 (anonimato estadístico para reportes)
"""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Base de datos ---
    database_url: str = Field(
        default="postgresql+psycopg://ciberteatro:ciberteatro@localhost:5432/ciberteatro"
    )

    # --- Anthropic ---
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-sonnet-4-5")

    # --- Seguridad ---
    secret_key: str = Field(default="dev-secret-change-me")
    access_token_expire_minutes: int = Field(default=120)

    # --- CORS ---
    frontend_origins: str = Field(default="http://localhost:3000")

    # --- Reglas de producto codificadas (no negociables) ---
    min_aggregate_n: int = Field(default=10)
    max_difficulty: int = Field(default=3)

    environment: str = Field(default="development")

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.frontend_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
