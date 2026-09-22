"""FastAPI application entrypoint.

Run locally with:

    uvicorn app.main:app --reload

from inside the `ai/` directory.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.services.errors import AppHTTPError


# - Matthew's stuff
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models.requests import GeneratePostRequest
from app.services.errors import (
    GenerationProviderError,
    GenerationValidationError,
)
from app.services.fake_client import FakeGeminiClient
from app.services.post_generator import generate_post
# ---


logging.basicConfig(level=logging.INFO)

settings = get_settings()

app = FastAPI(
    title="CaringBridge AI Backend",
    description="Generates first-post drafts for CaringBridge from onboarding "
    "information, with unresolved details represented as canonical placeholders.",
    version="0.1.0",
)


# - Matthew's stuff
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


@app.get("/")
async def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")


def build_client():
    settings = get_settings()

    if settings.ai_provider == "fake":
        return FakeGeminiClient()

    if not settings.gemini_configured:
        return FakeGeminiClient()

    from app.services.gemini_client import GeminiClient

    return GeminiClient(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        temperature=settings.gemini_temperature,
    )


@app.post("/api/generate")
async def generate(request: GeneratePostRequest):
    client = build_client()

    try:
        response = generate_post(request, client)
        return response

    except (
        GenerationProviderError,
        GenerationValidationError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )
# ---


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppHTTPError)
async def app_http_error_handler(request: Request, exc: AppHTTPError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "message": exc.message},
    )


app.include_router(router)