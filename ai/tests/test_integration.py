"""Plan section 45: optional integration tests against the real Gemini API.

Not run by default (see pytest.ini). Run explicitly with:

    pytest -m integration

Requires GEMINI_API_KEY to be set (e.g. in the repo root .env); otherwise
these tests are skipped rather than failed, so the default suite and CI stay
green without a key. Assertions intentionally avoid pinning exact wording --
LLM output varies -- and instead check the properties that matter most: no
unknown placeholder tokens (hallucination-shaped risk) and that known facts
actually appear.
"""

from __future__ import annotations

import pytest

from app.core.config import get_settings
from app.core.placeholders import unknown_tokens
from app.models.requests import GeneratePostRequest
from app.services.gemini_client import GeminiClient
from app.services.post_generator import generate_post

pytestmark = pytest.mark.integration


def _client() -> GeminiClient:
    settings = get_settings()
    if not settings.gemini_configured:
        pytest.skip("GEMINI_API_KEY not configured; skipping integration test")
    return GeminiClient(
        api_key=settings.gemini_api_key,  # type: ignore[arg-type]
        model=settings.gemini_model,
        temperature=settings.gemini_temperature,
    )


def test_known_facts_are_used_and_no_unknown_tokens_appear():
    client = _client()
    request = GeneratePostRequest.model_validate(
        {
            "onboarding": {
                "patient_name": "Jake",
                "health_condition": "traumatic brain injury",
                "author_role": "friend",
                "author_name": "Alex",
                "relationship_to_patient": "close friend",
                "is_primary_caregiver": False,
                "primary_caregiver_name": "Maria",
            },
            "details": {
                "event_or_symptom_context": "Jake was in a car accident Wednesday night",
                "diagnosis_details": "traumatic brain injury",
                "treatment_plan": "Doctors are monitoring swelling after surgery",
                "next_medical_step": "The team will reassess over the next 48 to 72 hours",
                "visiting_information": "We are not able to have visitors right now",
                "next_update_timing": "after I speak with Maria tomorrow",
            },
        }
    )

    response = generate_post(request, client)

    assert response.post.strip()
    assert "Jake" in response.post
    assert "Maria" in response.post
    assert not unknown_tokens(response.post)


def test_almost_no_information_does_not_invent_facts():
    """The hallucination trap (plan section 83)."""
    client = _client()
    request = GeneratePostRequest.model_validate(
        {"onboarding": {"author_role": "caregiver", "health_condition": "cancer"}}
    )

    response = generate_post(request, client)

    assert response.post.strip()
    assert not unknown_tokens(response.post)
