"""HTTP routes (plan sections 25, 26, 27).

Route handlers stay thin: validate via Pydantic (automatic), resolve which
generation client to use, delegate to the orchestrator, and translate
internal exceptions into the documented `{"error", "message"}` shape.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.models.requests import GeneratePostRequest
from app.models.responses import GeneratePostResponse
from app.services.errors import AppHTTPError, GenerationProviderError, GenerationValidationError
from app.services.fake_client import FakeGeminiClient
from app.services.gemini_client import GenerationClient
from app.services.post_generator import generate_post

logger = logging.getLogger("carebridge_ai")

router = APIRouter()


def get_generation_client(settings: Settings = Depends(get_settings)) -> GenerationClient:
    if settings.ai_provider == "fake":
        return FakeGeminiClient()

    if not settings.gemini_configured:
        # Raised during dependency resolution, before the route handler body
        # runs -- so this must be an AppHTTPError directly (registered at
        # the app level) rather than an internal exception the handler body
        # would otherwise translate.
        raise AppHTTPError(
            503,
            "provider_not_configured",
            "The AI drafting service is not configured right now.",
        )

    from app.services.gemini_client import GeminiClient

    return GeminiClient(
        api_key=settings.gemini_api_key,  # type: ignore[arg-type]
        model=settings.gemini_model,
        temperature=settings.gemini_temperature,
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/v1/generate-post", response_model=GeneratePostResponse)
def generate_post_endpoint(
    payload: GeneratePostRequest,
    client: GenerationClient = Depends(get_generation_client),
) -> GeneratePostResponse:
    request_id = uuid.uuid4().hex[:12]
    logger.info("generation_request_received request_id=%s", request_id)

    try:
        response = generate_post(payload, client)
    except GenerationProviderError as exc:
        logger.error("gemini_generation_error request_id=%s", request_id)
        raise AppHTTPError(
            502, "generation_failed", "Unable to generate a draft right now."
        ) from exc
    except GenerationValidationError as exc:
        logger.error("generation_validation_error request_id=%s", request_id)
        raise AppHTTPError(
            502, "generation_failed", "Unable to generate a draft right now."
        ) from exc

    logger.info("generation_completed request_id=%s", request_id)
    return response
