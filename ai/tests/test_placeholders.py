"""Plan section 39: registry invariants."""

from app.core.placeholders import PLACEHOLDERS, TOKEN_PATTERN


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
