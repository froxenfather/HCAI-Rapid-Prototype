"""Plan section 40: resolved-context resolution cases."""

from app.core.placeholders import PLACEHOLDERS, build_resolved_context
from app.models.requests import GeneratePostRequest


def _request(onboarding: dict | None = None, details: dict | None = None) -> GeneratePostRequest:
    return GeneratePostRequest.model_validate(
        {
            "onboarding": {"author_role": "friend", **(onboarding or {})},
            "details": details or {},
        }
    )


def test_known_patient_name_is_used_directly():
    ctx = build_resolved_context(_request(onboarding={"patient_name": "Jake"}))
    assert ctx["patient_name"] == "Jake"


def test_unknown_patient_name_becomes_placeholder():
    ctx = build_resolved_context(_request())
    assert ctx["patient_name"] == PLACEHOLDERS["patient_name"].token


def test_known_primary_caregiver_is_used_directly():
    ctx = build_resolved_context(_request(onboarding={"primary_caregiver_name": "Maria"}))
    assert ctx["primary_caregiver_name"] == "Maria"


def test_unknown_visiting_information_becomes_placeholder():
    ctx = build_resolved_context(_request())
    assert ctx["visiting_information"] == PLACEHOLDERS["visiting_information"].token


def test_whitespace_only_value_is_treated_as_missing():
    ctx = build_resolved_context(_request(onboarding={"patient_name": "   "}))
    assert ctx["patient_name"] == PLACEHOLDERS["patient_name"].token


def test_every_registry_key_present_in_resolved_context():
    ctx = build_resolved_context(_request())
    assert set(ctx.keys()) == set(PLACEHOLDERS.keys())
