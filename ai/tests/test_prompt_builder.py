"""Plan section 43: prompt construction contains the required components and
never leaks secrets.
"""

from app.core.placeholders import ALLOWED_TOKEN_LIST_TEXT, build_resolved_context
from app.models.requests import GeneratePostRequest
from app.services.prompt_builder import (
    RESOLVED_CONTEXT_END,
    RESOLVED_CONTEXT_START,
    SYSTEM_INSTRUCTION,
    build_prompt,
)


def test_system_instruction_states_strict_fact_and_placeholder_rules():
    assert "SOURCE-OF-TRUTH RULE" in SYSTEM_INSTRUCTION
    assert "PLACEHOLDER RULE" in SYSTEM_INSTRUCTION
    assert "MEDICAL RULE" in SYSTEM_INSTRUCTION
    assert ALLOWED_TOKEN_LIST_TEXT in SYSTEM_INSTRUCTION


def test_user_content_embeds_resolved_context_and_preferences():
    request = GeneratePostRequest.model_validate(
        {
            "onboarding": {"author_role": "friend", "patient_name": "Jake"},
            "preferences": {"tone": "gentle", "length": "short", "style": "concise"},
        }
    )
    resolved = build_resolved_context(request)
    _, user_content = build_prompt(request, resolved, examples=[], anti_pattern_notes=[])

    assert RESOLVED_CONTEXT_START in user_content
    assert RESOLVED_CONTEXT_END in user_content
    assert '"Jake"' in user_content
    assert "tone: gentle" in user_content
    assert "length: short" in user_content
    assert "style: concise" in user_content


def test_user_content_includes_anti_pattern_notes():
    request = GeneratePostRequest.model_validate({"onboarding": {"author_role": "friend"}})
    resolved = build_resolved_context(request)
    _, user_content = build_prompt(
        request, resolved, examples=[], anti_pattern_notes=["invents a hospital name"]
    )
    assert "invents a hospital name" in user_content


def test_prompt_never_contains_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "totally-secret-value")
    request = GeneratePostRequest.model_validate({"onboarding": {"author_role": "friend"}})
    resolved = build_resolved_context(request)
    system_instruction, user_content = build_prompt(
        request, resolved, examples=[], anti_pattern_notes=[]
    )
    assert "totally-secret-value" not in system_instruction
    assert "totally-secret-value" not in user_content
