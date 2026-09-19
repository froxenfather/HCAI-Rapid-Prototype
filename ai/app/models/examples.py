"""Schema for curated few-shot example records (plan section 15)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ExampleRecord(BaseModel):
    id: str
    quality: Literal["good", "bad"]
    condition_tags: list[str]
    author_role: Literal["patient", "caregiver", "friend", "family", "other"]
    primary_caregiver: bool
    post: str
    problems: list[str] | None = None
