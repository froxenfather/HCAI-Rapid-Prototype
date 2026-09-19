"""Loads the curated example corpus and selects relevant few-shot examples.

No embeddings, no vector store -- a simple deterministic tag/role scorer is
enough for the six curated examples in this MVP (plan section 16).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.models.examples import ExampleRecord
from app.models.requests import GeneratePostRequest

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "examples.json"


@lru_cache
def load_examples(path: Path = _DATA_PATH) -> list[ExampleRecord]:
    raw = path.read_text(encoding="utf-8")
    import json

    records = json.loads(raw)
    return [ExampleRecord.model_validate(record) for record in records]


def _normalize_tag(text: str) -> str:
    return text.strip().lower()


def _condition_score(condition: str | None, tags: list[str]) -> int:
    if not condition:
        return 0
    condition_norm = _normalize_tag(condition)
    for tag in tags:
        tag_norm = _normalize_tag(tag)
        if tag_norm in condition_norm or condition_norm in tag_norm:
            return 3
    return 0


def select_examples(
    request: GeneratePostRequest,
    examples: list[ExampleRecord] | None = None,
    limit: int = 3,
) -> list[ExampleRecord]:
    """Score and return the most relevant GOOD examples for this request.

    Scoring (plan section 16):
        +3 similar health condition
        +2 matching author role
        +1 matching primary-caregiver status (only when known)
    """
    pool = examples if examples is not None else load_examples()
    good_examples = [record for record in pool if record.quality == "good"]

    onboarding = request.onboarding

    def score(record: ExampleRecord) -> int:
        total = _condition_score(onboarding.health_condition, record.condition_tags)
        if record.author_role == onboarding.author_role:
            total += 2
        if (
            onboarding.is_primary_caregiver is not None
            and onboarding.is_primary_caregiver == record.primary_caregiver
        ):
            total += 1
        return total

    ranked = sorted(good_examples, key=score, reverse=True)
    return ranked[:limit]


def anti_pattern_notes(
    request: GeneratePostRequest,
    examples: list[ExampleRecord] | None = None,
    limit: int = 3,
) -> list[str]:
    """Collect a short, deduplicated list of condition-relevant anti-pattern
    notes drawn from curated BAD examples, to supplement the static
    anti-pattern checklist in the prompt (plan section 18).
    """
    pool = examples if examples is not None else load_examples()
    bad_examples = [record for record in pool if record.quality == "bad"]

    onboarding = request.onboarding
    ranked = sorted(
        bad_examples,
        key=lambda record: _condition_score(onboarding.health_condition, record.condition_tags),
        reverse=True,
    )

    notes: list[str] = []
    for record in ranked:
        for problem in record.problems or []:
            if problem not in notes:
                notes.append(problem)
        if len(notes) >= limit:
            break
    return notes[:limit]
