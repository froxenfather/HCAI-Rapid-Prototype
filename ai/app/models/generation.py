"""Schema for the structured output Gemini is required to return.

This is the contract between our prompt and the model (plan section 21).
It intentionally does NOT leave the API response shape -- the orchestrator
re-derives placeholders/coverage deterministically before responding to the
frontend (plan section 22.2), so this model only needs to be "good enough"
for the model to reason about, not authoritative.
"""

from __future__ import annotations

from pydantic import BaseModel


class CoverageReport(BaseModel):
    patient_and_health_issue: bool
    author_relationship: bool
    condition_details: bool
    community_information: bool
    support_needs: bool
    privacy_preferences: bool
    next_medical_steps: bool
    next_update: bool


class GeminiGeneration(BaseModel):
    post: str
    used_placeholders: list[str]
    coverage: CoverageReport
