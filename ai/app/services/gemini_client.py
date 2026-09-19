"""Gemini provider wrapper (plan sections 5 and 28).

This is the ONLY module that imports the ``google-genai`` SDK. Everything
else in the application talks to a ``GenerationClient`` (structurally, via
duck typing / ``Protocol``), so tests can swap in ``FakeGeminiClient``
without touching real network calls, and the SDK can change without
rippling through the rest of the codebase.
"""

from __future__ import annotations

import time
from typing import Protocol

from app.models.generation import GeminiGeneration
from app.services.errors import GenerationProviderError

# HTTP/gRPC-ish status codes worth a short retry: the request itself was
# fine, the provider was momentarily unavailable or rate-limiting us.
# Anything else (bad request, auth, schema mismatch, etc.) fails immediately
# -- retrying those would just waste time and quota.
_RETRYABLE_CODES = {429, 503}
_MAX_ATTEMPTS = 3
_BACKOFF_SECONDS = (1, 2)  # sleep before attempt 2, then before attempt 3


class GenerationClient(Protocol):
    def generate_post(self, system_instruction: str, user_content: str) -> GeminiGeneration:
        ...


class GeminiClient:
    """Thin wrapper around ``google.genai.Client`` using structured output."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.4) -> None:
        # Imported lazily so environments without the SDK installed (or
        # without a key) can still import this module cheaply, and so any
        # SDK-specific errors are contained to construction/generation time.
        from google import genai

        self._genai = genai
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._temperature = temperature

    def generate_post(self, system_instruction: str, user_content: str) -> GeminiGeneration:
        from google.genai import errors, types

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=GeminiGeneration,
            temperature=self._temperature,
        )

        response = None
        last_error: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=user_content,
                    config=config,
                )
                last_error = None
                break
            except errors.APIError as exc:
                last_error = exc
                is_last_attempt = attempt == _MAX_ATTEMPTS - 1
                if exc.code not in _RETRYABLE_CODES or is_last_attempt:
                    raise GenerationProviderError(f"Gemini request failed: {exc}") from exc
                time.sleep(_BACKOFF_SECONDS[attempt])
            except Exception as exc:  # noqa: BLE001 - anything else fails immediately
                raise GenerationProviderError(f"Gemini request failed: {exc}") from exc

        if response is None:  # pragma: no cover - defensive, loop always returns or raises
            raise GenerationProviderError(f"Gemini request failed: {last_error}")

        text = getattr(response, "text", None)
        if not text:
            raise GenerationProviderError("Gemini returned an empty response")

        try:
            return GeminiGeneration.model_validate_json(text)
        except Exception as exc:  # noqa: BLE001
            raise GenerationProviderError(
                f"Gemini response did not match the expected schema: {exc}"
            ) from exc
