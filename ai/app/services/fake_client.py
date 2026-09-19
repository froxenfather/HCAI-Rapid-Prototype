"""Deterministic stand-in for ``GeminiClient`` (plan sections 38 and 71).

Used by default in tests (no network calls, no API quota spent) and
optionally in local dev via ``AI_PROVIDER=fake`` so the frontend team can
integrate against a stable contract before/without a Gemini key.

It reads the same RESOLVED_CONTEXT JSON block the real prompt embeds, so
its output actually reflects known values vs. placeholders, rather than
being a static string.
"""

from __future__ import annotations

import json
import re

from app.models.generation import CoverageReport, GeminiGeneration
from app.services.prompt_builder import RESOLVED_CONTEXT_END, RESOLVED_CONTEXT_START

_BLOCK_PATTERN = re.compile(
    rf"{re.escape(RESOLVED_CONTEXT_START)}\s*(.*?)\s*{re.escape(RESOLVED_CONTEXT_END)}",
    re.DOTALL,
)


def _extract_resolved_context(user_content: str) -> dict[str, str]:
    match = _BLOCK_PATTERN.search(user_content)
    if not match:
        return {}
    return json.loads(match.group(1))


class FakeGeminiClient:
    """Implements the same interface as ``GeminiClient`` without calling out."""

    def generate_post(self, system_instruction: str, user_content: str) -> GeminiGeneration:
        ctx = _extract_resolved_context(user_content)
        get = ctx.get

        post = (
            f"{get('patient_name', '[PATIENT_NAME]')} is currently dealing with "
            f"{get('health_condition', '[HEALTH_CONDITION]')}. "
            f"I am {get('author_name', '[AUTHOR_NAME]')}, "
            f"{get('relationship_to_patient', '[AUTHOR_RELATIONSHIP]')}, and I am setting up "
            f"this page to keep everyone updated. "
            f"{get('event_or_symptom_context', '[EVENT_OR_SYMPTOM_CONTEXT]')} "
            f"{get('diagnosis_details', '[DIAGNOSIS_DETAILS]')} "
            f"{get('treatment_plan', '[TREATMENT_PLAN]')} "
            f"The next step is {get('next_medical_step', '[NEXT_MEDICAL_STEP]')}. "
            f"For visitors, {get('visiting_information', '[VISITING_INFORMATION]')} "
            f"Regarding flowers, {get('flowers_information', '[FLOWERS_INFORMATION]')} "
            f"For calls and texts, {get('phone_text_preferences', '[PHONE_TEXT_PREFERENCES]')} "
            f"If you would like to help, {get('support_needs', '[SUPPORT_NEEDS]')} "
            f"Regarding sharing, {get('sharing_preference', '[SHARING_PREFERENCE]')} "
            f"I will post another update {get('next_update_timing', '[NEXT_UPDATE_TIMING]')}."
        )

        used_placeholders = sorted(
            {
                value.strip("[]")
                for value in ctx.values()
                if isinstance(value, str) and value.startswith("[") and value.endswith("]")
            }
        )

        return GeminiGeneration(
            post=post,
            used_placeholders=used_placeholders,
            coverage=CoverageReport(
                patient_and_health_issue=True,
                author_relationship=True,
                condition_details=True,
                community_information=True,
                support_needs=True,
                privacy_preferences=True,
                next_medical_steps=True,
                next_update=True,
            ),
        )
