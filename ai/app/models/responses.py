"""Response schemas returned to the frontend (plan sections 13 and 25)."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.generation import CoverageReport


class PlaceholderMetadata(BaseModel):
    key: str
    token: str
    label: str
    category: str
    required_for_publish: bool


class GeneratePostResponse(BaseModel):
    post: str
    placeholders: list[PlaceholderMetadata]
    coverage: CoverageReport


class ErrorResponse(BaseModel):
    error: str
    message: str
