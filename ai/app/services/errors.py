"""Errors raised by the generation pipeline, mapped to HTTP status codes in
the route layer (plan section 27)."""

from __future__ import annotations


class GenerationProviderError(Exception):
    """The provider (Gemini) call itself failed or returned unusable data."""


class GenerationValidationError(Exception):
    """The provider's output failed validation even after one repair attempt."""


class AppHTTPError(Exception):
    """Carries the exact `{"error", "message"}` shape the API returns on
    failure (plan section 27), independent of the internal exception that
    triggered it.
    """

    def __init__(self, status_code: int, error: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error = error
        self.message = message
