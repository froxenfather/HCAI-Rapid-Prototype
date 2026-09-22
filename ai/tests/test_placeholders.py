"""Plan section 39: registry invariants."""

from app.core.placeholders import PLACEHOLDERS, TOKEN_PATTERN, missing_known_facts


def test_every_token_is_unique():
    tokens = [spec.token for spec in PLACEHOLDERS.values()]
    assert len(tokens) == len(set(tokens))


def test_every_token_matches_canonical_pattern():
    for spec in PLACEHOLDERS.values():
        assert TOKEN_PATTERN.fullmatch(spec.token), spec.token


def test_every_key_has_a_label():
    for spec in PLACEHOLDERS.values():
        assert spec.label.strip()


def test_every_key_has_a_category():
    for spec in PLACEHOLDERS.values():
        assert spec.category.strip()


def test_no_token_contains_spaces():
    for spec in PLACEHOLDERS.values():
        assert " " not in spec.token


def test_every_token_begins_and_ends_with_brackets():
    for spec in PLACEHOLDERS.values():
        assert spec.token.startswith("[")
        assert spec.token.endswith("]")


def test_registry_key_matches_dict_key():
    for key, spec in PLACEHOLDERS.items():
        assert spec.key == key


def test_missing_known_facts_tolerates_paraphrasing():
    # The model is expected to reword multi-word facts, not quote them
    # verbatim -- a first-name-only or a relationship-as-synonym reference
    # should still count as covered.
    resolved_context = {
        "patient_name": "Ryan Freese",
        "relationship_to_patient": "Dad",
        "author_name": "John Freese",
    }
    post = (
        "Hi everyone, I'm John, and I'm writing on behalf of Ryan, my son, "
        "to keep you updated."
    )
    missing = missing_known_facts(post, resolved_context)
    assert "patient_name" not in missing
    assert "author_name" not in missing


def test_missing_known_facts_flags_wholesale_omission():
    resolved_context = {
        "treatment_plan": "surgery next Tuesday at Mercy General",
        "fundraiser_information": "GoFundMe raised ten thousand dollars",
    }
    post = "Hi everyone, thank you all for the kind words and support so far."
    missing = missing_known_facts(post, resolved_context)
    assert set(missing) == {"treatment_plan", "fundraiser_information"}
