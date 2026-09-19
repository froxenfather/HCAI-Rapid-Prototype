"""Plan section 44: endpoint tests. Uses the offline fake client via the
`api_client` fixture -- no real Gemini call happens in this file.
"""

from app.api.routes import get_generation_client
from app.core.config import Settings, get_settings
from app.main import app
from app.models.generation import CoverageReport, GeminiGeneration
from app.services.errors import GenerationProviderError


def _coverage_all_true() -> CoverageReport:
    return CoverageReport.model_validate({field: True for field in CoverageReport.model_fields})


def test_valid_request_returns_200_with_expected_keys(api_client, rich_request_payload):
    response = api_client.post("/api/v1/generate-post", json=rich_request_payload)
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"post", "placeholders", "coverage"}
    assert "Jake" in body["post"]
    assert "Maria" in body["post"]


def test_missing_required_author_role_returns_422(api_client):
    response = api_client.post("/api/v1/generate-post", json={"onboarding": {}})
    assert response.status_code == 422


def test_missing_optional_fields_still_generates(api_client, minimal_request_payload):
    response = api_client.post("/api/v1/generate-post", json=minimal_request_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["post"].strip()


def test_provider_error_returns_502(api_client):
    class BrokenClient:
        def generate_post(self, system_instruction, user_content):
            raise GenerationProviderError("simulated provider failure")

    app.dependency_overrides[get_generation_client] = lambda: BrokenClient()
    response = api_client.post(
        "/api/v1/generate-post", json={"onboarding": {"author_role": "friend"}}
    )
    assert response.status_code == 502
    assert response.json() == {
        "error": "generation_failed",
        "message": "Unable to generate a draft right now.",
    }


def test_unknown_placeholder_triggers_repair_then_succeeds(api_client):
    calls = {"n": 0}

    class BadThenGoodClient:
        def generate_post(self, system_instruction, user_content):
            calls["n"] += 1
            if calls["n"] == 1:
                post = (
                    "[SOME_RANDOM_FIELD] is not doing well but we are hopeful "
                    "for a full recovery soon and appreciate your support."
                )
                used = ["SOME_RANDOM_FIELD"]
            else:
                post = (
                    "[PATIENT_NAME] is not doing well but we are hopeful for "
                    "a full recovery soon and appreciate your support."
                )
                used = ["PATIENT_NAME"]
            return GeminiGeneration(post=post, used_placeholders=used, coverage=_coverage_all_true())

    app.dependency_overrides[get_generation_client] = lambda: BadThenGoodClient()
    response = api_client.post(
        "/api/v1/generate-post", json={"onboarding": {"author_role": "friend"}}
    )
    assert response.status_code == 200
    assert calls["n"] == 2


def test_persistent_unknown_placeholder_returns_502(api_client):
    class AlwaysBadClient:
        def generate_post(self, system_instruction, user_content):
            return GeminiGeneration(
                post="[NOT_A_REAL_TOKEN] situation continues without much change today.",
                used_placeholders=["NOT_A_REAL_TOKEN"],
                coverage=_coverage_all_true(),
            )

    app.dependency_overrides[get_generation_client] = lambda: AlwaysBadClient()
    response = api_client.post(
        "/api/v1/generate-post", json={"onboarding": {"author_role": "friend"}}
    )
    assert response.status_code == 502
    assert response.json()["error"] == "generation_failed"


def test_provider_not_configured_returns_503():
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_settings] = lambda: Settings(
        gemini_api_key=None, ai_provider="gemini"
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/generate-post", json={"onboarding": {"author_role": "friend"}}
            )
        assert response.status_code == 503
        assert response.json()["error"] == "provider_not_configured"
    finally:
        app.dependency_overrides.clear()
