from app.models.requests import GeneratePostRequest
from app.services.example_loader import anti_pattern_notes, load_examples, select_examples


def _request(health_condition: str, author_role: str = "friend") -> GeneratePostRequest:
    return GeneratePostRequest.model_validate(
        {"onboarding": {"author_role": author_role, "health_condition": health_condition}}
    )


def test_load_examples_returns_curated_corpus():
    examples = load_examples()
    assert len(examples) >= 6
    assert {"good", "bad"} <= {example.quality for example in examples}
    ids = {example.id for example in examples}
    assert "cancer_friend_good_01" in ids
    assert "stroke_daughter_good_01" in ids
    assert "tbi_friend_good_01" in ids


def test_select_examples_prefers_matching_condition_and_role():
    request = _request("ovarian cancer", author_role="friend")
    selected = select_examples(request, limit=1)
    assert selected[0].id == "cancer_friend_good_01"


def test_select_examples_only_returns_good_quality():
    request = _request("stroke", author_role="family")
    selected = select_examples(request)
    assert all(example.quality == "good" for example in selected)


def test_select_examples_respects_limit():
    request = _request("cancer")
    assert len(select_examples(request, limit=2)) <= 2


def test_anti_pattern_notes_reflect_matching_condition():
    request = _request("traumatic brain injury")
    notes = anti_pattern_notes(request)
    assert notes
    assert any("hospital" in note or "prognosis" in note or "clinician" in note for note in notes)
