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


def test_rejects_post_shorter_than_requested_length():
    # Passes the bare MIN_POST_LENGTH floor but is far short of what "long"
    # was supposed to produce.
    text = "Hi everyone, thanks for checking in. More news soon."
    result = validate_generation(text, length="long")
    assert not result.ok
    assert "post_too_short_for_requested_length" in result.errors


def test_accepts_short_post_for_short_length_preference():
    text = (
        "Hi everyone, thanks so much for checking in on us during this time. "
        "We will share more as soon as there is news to share, and we are "
        "grateful for all the kind words so far."
    )
    result = validate_generation(text, length="short")
    assert result.ok


def test_rejects_post_that_drops_most_supplied_facts():
    resolved_context = {
        "patient_name": "Jordan",
        "health_condition": "a hip fracture",
        "author_name": "Sam",
        "relationship_to_patient": "[AUTHOR_RELATIONSHIP]",
        "treatment_plan": "surgery next Tuesday at Mercy General",
        "visiting_information": "no visitors until after surgery",
        "support_needs": "meals for the family",
        "sharing_preference": "close friends and family only",
    }
    # Only mentions one of the six known facts; drops the rest even though
    # the post is long enough to pass the length checks.
    text = (
        "Hi everyone, I'm writing to share that Jordan is going "
        "through a tough time right now. We appreciate all your love and "
        "support from everyone checking in, and we will keep this page "
        "updated as things progress. Thank you all so much."
    )
    result = validate_generation(text, resolved_context=resolved_context)
    assert not result.ok
    assert any(error.startswith("missing_known_facts:") for error in result.errors)


def test_accepts_post_that_covers_most_supplied_facts():
    resolved_context = {
        "patient_name": "Jordan",
        "health_condition": "a hip fracture",
        "author_name": "Sam",
        "relationship_to_patient": "[AUTHOR_RELATIONSHIP]",
        "treatment_plan": "surgery next Tuesday at Mercy General",
        "visiting_information": "no visitors until after surgery",
        "support_needs": "meals for the family",
        "sharing_preference": "close friends and family only",
    }
    text = (
        "Hi everyone, I'm Sam and I'm writing to share that Jordan is going "
        "through a tough time. Jordan has a hip fracture, and the plan is "
        "surgery next Tuesday at Mercy General. Please hold off on visiting: "
        "no visitors until after surgery for now. If you'd like to help, "
        "meals for the family would mean a lot. This page is shared with "
        "close friends and family only, and we'll post more soon."
    )
    result = validate_generation(text, resolved_context=resolved_context)
    assert result.ok
