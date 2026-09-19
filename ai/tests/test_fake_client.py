from app.core.placeholders import build_resolved_context, unknown_tokens
from app.models.requests import GeneratePostRequest
from app.services.fake_client import FakeGeminiClient
from app.services.prompt_builder import build_prompt


def test_fake_client_uses_known_values_and_placeholders_for_unknowns():
    request = GeneratePostRequest.model_validate(
        {"onboarding": {"author_role": "friend", "patient_name": "Sarah"}}
    )
    resolved = build_resolved_context(request)
    system_instruction, user_content = build_prompt(request, resolved, examples=[], anti_pattern_notes=[])

    generation = FakeGeminiClient().generate_post(system_instruction, user_content)

    assert "Sarah" in generation.post
    assert not unknown_tokens(generation.post)
    # patient_name was supplied, so it should NOT show up as a placeholder.
    assert "PATIENT_NAME" not in generation.used_placeholders
    # Everything else was left unspecified, so it remains a placeholder.
    assert "HOSPITAL_NAME" in generation.used_placeholders
    assert "AUTHOR_NAME" in generation.used_placeholders
