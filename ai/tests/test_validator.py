from app.services.validator import validate_generation


def test_rejects_empty_post():
    result = validate_generation("   ")
    assert not result.ok
    assert "empty_post" in result.errors


def test_rejects_too_short_post():
    result = validate_generation("Hi there.")
    assert not result.ok
    assert "post_too_short" in result.errors


def test_rejects_unknown_placeholder_token():
    text = (
        "Hello [SOME_RANDOM_FIELD], we are so glad you are here reading this "
        "update about the family."
    )
    result = validate_generation(text)
    assert not result.ok
    assert any("unknown_placeholder_tokens" in error for error in result.errors)


def test_accepts_well_formed_post_with_known_tokens():
    text = (
        "[PATIENT_NAME] is doing well and is grateful for your support during "
        "this time of healing and recovery from a recent surgery at "
        "[HOSPITAL_NAME]."
    )
    result = validate_generation(text)
    assert result.ok
    assert result.errors == []


def test_rejects_excessively_long_post():
    text = "word " * 1500  # well over MAX_POST_LENGTH characters
    result = validate_generation(text)
    assert not result.ok
    assert "post_too_long" in result.errors
