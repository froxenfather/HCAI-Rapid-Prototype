"""GeminiClient should transparently retry transient provider errors
(429/503) a bounded number of times, but fail immediately on anything else.

These tests never hit the network: they patch the constructed SDK client's
``models.generate_content`` directly and stub out ``time.sleep`` so the
suite stays fast.
"""

from __future__ import annotations

import pytest
from google.genai import errors as genai_errors

from app.services import gemini_client as gemini_client_module
from app.services.errors import GenerationProviderError


class _FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


def _valid_response_text() -> str:
    return (
        '{"post": "Hello there, this is a perfectly fine generated post for '
        'testing purposes and it is long enough.", '
        '"used_placeholders": [], '
        '"coverage": {"patient_and_health_issue": true, "author_relationship": true, '
        '"condition_details": true, "community_information": true, '
        '"support_needs": true, "privacy_preferences": true, '
        '"next_medical_steps": true, "next_update": true}}'
    )


def _make_client(monkeypatch: pytest.MonkeyPatch) -> gemini_client_module.GeminiClient:
    # Avoid real network calls / API key requirements from genai.Client(...).
    monkeypatch.setattr(gemini_client_module, "time", gemini_client_module.time)
    client = gemini_client_module.GeminiClient.__new__(gemini_client_module.GeminiClient)
    client._model = "fake-model"
    client._temperature = 0.4
    return client


def _server_error(code: int, status: str) -> genai_errors.APIError:
    return genai_errors.APIError(code, {"error": {"code": code, "message": "boom", "status": status}})


def test_retries_on_503_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client(monkeypatch)
    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda seconds: None)

    calls = {"n": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls["n"] += 1
            if calls["n"] < 3:
                raise _server_error(503, "UNAVAILABLE")
            return _FakeResponse(_valid_response_text())

    client._client = type("FakeSDKClient", (), {"models": FakeModels()})()

    generation = client.generate_post("system", "user content")

    assert calls["n"] == 3
    assert generation.post.startswith("Hello there")


def test_gives_up_after_max_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client(monkeypatch)
    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda seconds: None)

    calls = {"n": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls["n"] += 1
            raise _server_error(503, "UNAVAILABLE")

    client._client = type("FakeSDKClient", (), {"models": FakeModels()})()

    with pytest.raises(GenerationProviderError):
        client.generate_post("system", "user content")

    assert calls["n"] == gemini_client_module._MAX_ATTEMPTS


def test_does_not_retry_non_retryable_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client(monkeypatch)
    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda seconds: None)

    calls = {"n": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls["n"] += 1
            raise _server_error(400, "INVALID_ARGUMENT")

    client._client = type("FakeSDKClient", (), {"models": FakeModels()})()

    with pytest.raises(GenerationProviderError):
        client.generate_post("system", "user content")

    assert calls["n"] == 1


def test_does_not_retry_unexpected_exceptions(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _make_client(monkeypatch)
    monkeypatch.setattr(gemini_client_module.time, "sleep", lambda seconds: None)

    calls = {"n": 0}

    class FakeModels:
        def generate_content(self, **kwargs):
            calls["n"] += 1
            raise ValueError("something unrelated broke")

    client._client = type("FakeSDKClient", (), {"models": FakeModels()})()

    with pytest.raises(GenerationProviderError):
        client.generate_post("system", "user content")

    assert calls["n"] == 1
