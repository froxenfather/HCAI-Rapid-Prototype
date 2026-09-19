"""Central application configuration.

All environment-dependent values are read here, once, so the rest of the
application never touches ``os.environ`` directly. See
``CAREBRIDGE_AI_BACKEND_PLAN.md`` section 29 for the rationale.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

from dotenv import find_dotenv, load_dotenv

# Walk up from the current working directory to find a .env file. This lets
# the backend be run either from `ai/` (its own .env, if present) or from the
# repository root (where the team's shared .env already lives) without any
# extra configuration.
load_dotenv(find_dotenv(usecwd=True))


def _split_origins(raw: str) -> list[str]:
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_temperature: float = 0.4
    ai_provider: str = "gemini"  # "gemini" or "fake"
    cors_origins: list[str] = field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    cors_raw = os.getenv("CORS_ORIGINS")
    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        gemini_temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.4")),
        ai_provider=os.getenv("AI_PROVIDER", "gemini").strip().lower(),
        cors_origins=_split_origins(os.getenv("CORS_ORIGINS", ""))
        or ["http://localhost:3000", "http://localhost:5173"],
    )
