import pytest
from fastapi.testclient import TestClient

from app.api.routes import get_generation_client
from app.main import app
from app.services.fake_client import FakeGeminiClient


@pytest.fixture
def fake_client() -> FakeGeminiClient:
    return FakeGeminiClient()


@pytest.fixture
def api_client():
    """TestClient with the generation client forced to the offline fake,
    regardless of what GEMINI_API_KEY is set in the environment/.env -- the
    default test suite must never call the real API (plan section 38).
    """
    app.dependency_overrides[get_generation_client] = lambda: FakeGeminiClient()
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def minimal_request_payload() -> dict:
    return {"onboarding": {"author_role": "friend"}}


@pytest.fixture
def rich_request_payload() -> dict:
    return {
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
            "hospital_name": None,
            "treatment_plan": "Doctors are monitoring swelling after surgery",
            "next_medical_step": "The team will reassess over the next 48 to 72 hours",
            "visiting_information": "We are not able to have visitors right now",
            "next_update_timing": "after I speak with Maria tomorrow",
        },
        "preferences": {"tone": "warm", "length": "medium", "style": "personal"},
    }
