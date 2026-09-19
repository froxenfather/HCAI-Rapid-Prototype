"""Plan sections 41 and 42: placeholder extraction and known-value
substitution.
"""

from app.core.placeholders import (
    PLACEHOLDERS,
    extract_tokens,
    metadata_for_active_tokens,
    substitute_known_values,
    unknown_tokens,
)


def test_extract_tokens_finds_known_tokens_in_order():
    text = "[PATIENT_NAME] is currently at [HOSPITAL_NAME]."
    assert extract_tokens(text) == ["[PATIENT_NAME]", "[HOSPITAL_NAME]"]


def test_extract_tokens_dedupes():
    text = "[PATIENT_NAME] and [PATIENT_NAME] again."
    assert extract_tokens(text) == ["[PATIENT_NAME]"]


def test_unknown_token_is_detected():
    text = "Please welcome [SOME_RANDOM_FIELD] home."
    assert unknown_tokens(text) == ["[SOME_RANDOM_FIELD]"]


def test_known_tokens_are_not_flagged_as_unknown():
    text = "[PATIENT_NAME] is doing well at [HOSPITAL_NAME]."
    assert unknown_tokens(text) == []


def test_known_value_substitution_replaces_exact_token():
    resolved = {key: spec.token for key, spec in PLACEHOLDERS.items()}
    resolved["patient_name"] = "Sarah"

    post = "[PATIENT_NAME] was diagnosed and is doing okay."
    result = substitute_known_values(post, resolved)

    assert result == "Sarah was diagnosed and is doing okay."
    assert "[PATIENT_NAME]" not in extract_tokens(result)


def test_substitution_leaves_unknown_fields_as_placeholders():
    resolved = {key: spec.token for key, spec in PLACEHOLDERS.items()}
    resolved["patient_name"] = "Sarah"

    post = "[PATIENT_NAME] is at [HOSPITAL_NAME]."
    result = substitute_known_values(post, resolved)

    assert result == "Sarah is at [HOSPITAL_NAME]."


def test_metadata_only_includes_active_tokens():
    metadata = metadata_for_active_tokens(["[HOSPITAL_NAME]"])
    assert len(metadata) == 1
    assert metadata[0]["key"] == "hospital_name"
    assert metadata[0]["token"] == "[HOSPITAL_NAME]"
    assert metadata[0]["category"] == "logistics"


def test_required_for_publish_flag_is_set_correctly():
    metadata = metadata_for_active_tokens(["[PATIENT_NAME]", "[FLOWERS_INFORMATION]"])
    by_key = {item["key"]: item for item in metadata}
    assert by_key["patient_name"]["required_for_publish"] is True
    assert by_key["flowers_information"]["required_for_publish"] is False
