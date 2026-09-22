"""Canonical placeholder registry and deterministic placeholder helpers.

This module is the single source of truth for every bracket token the
system is allowed to emit (e.g. ``[PATIENT_NAME]``). Nothing else in the
codebase should hard-code a token string - see
``CAREBRIDGE_AI_BACKEND_PLAN.md`` section 11.

The registry intentionally owns three kinds of logic that must stay
deterministic and outside the LLM's control:

1. ``PLACEHOLDERS``      - the token/label/category registry itself.
2. ``build_resolved_context`` - "known value OR canonical placeholder" per field.
3. ``extract_tokens`` / placeholder metadata helpers - turning generated text
   back into frontend-facing metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.requests import GeneratePostRequest

TOKEN_PATTERN = re.compile(r"\[[A-Z0-9_]+\]")


@dataclass(frozen=True)
class PlaceholderSpec:
    key: str
    token: str
    label: str
    category: str


PLACEHOLDERS: dict[str, PlaceholderSpec] = {
    "patient_name": PlaceholderSpec("patient_name", "[PATIENT_NAME]", "Patient name", "identity"),
    "health_condition": PlaceholderSpec(
        "health_condition", "[HEALTH_CONDITION]", "Health condition", "medical_context"
    ),
    "author_name": PlaceholderSpec("author_name", "[AUTHOR_NAME]", "Author name", "identity"),
    "relationship_to_patient": PlaceholderSpec(
        "relationship_to_patient",
        "[AUTHOR_RELATIONSHIP]",
        "Relationship to patient",
        "identity",
    ),
    "primary_caregiver_name": PlaceholderSpec(
        "primary_caregiver_name", "[PRIMARY_CAREGIVER]", "Primary caregiver", "identity"
    ),
    "event_or_symptom_context": PlaceholderSpec(
        "event_or_symptom_context",
        "[EVENT_OR_SYMPTOM_CONTEXT]",
        "What led to this update",
        "medical_context",
    ),
    "diagnosis_details": PlaceholderSpec(
        "diagnosis_details", "[DIAGNOSIS_DETAILS]", "Diagnosis details", "medical_context"
    ),
    "hospital_name": PlaceholderSpec(
        "hospital_name", "[HOSPITAL_NAME]", "Hospital or care location", "logistics"
    ),
    "treatment_plan": PlaceholderSpec(
        "treatment_plan", "[TREATMENT_PLAN]", "Treatment plan", "medical_context"
    ),
    "next_medical_step": PlaceholderSpec(
        "next_medical_step", "[NEXT_MEDICAL_STEP]", "Next medical step", "medical_context"
    ),
    "visiting_information": PlaceholderSpec(
        "visiting_information", "[VISITING_INFORMATION]", "Visiting information", "community"
    ),
    "flowers_information": PlaceholderSpec(
        "flowers_information", "[FLOWERS_INFORMATION]", "Flowers information", "community"
    ),
    "phone_text_preferences": PlaceholderSpec(
        "phone_text_preferences",
        "[PHONE_TEXT_PREFERENCES]",
        "Phone and text preferences",
        "community",
    ),
    "support_needs": PlaceholderSpec(
        "support_needs", "[SUPPORT_NEEDS]", "Support needs", "support"
    ),
    "fundraiser_information": PlaceholderSpec(
        "fundraiser_information",
        "[FUNDRAISER_INFORMATION]",
        "Fundraiser information",
        "support",
    ),
    "food_information": PlaceholderSpec(
        "food_information", "[FOOD_INFORMATION]", "Food or meal support", "support"
    ),
    "transportation_support": PlaceholderSpec(
        "transportation_support",
        "[TRANSPORTATION_SUPPORT]",
        "Transportation support",
        "support",
    ),
    "child_or_pet_care_support": PlaceholderSpec(
        "child_or_pet_care_support",
        "[CHILD_OR_PET_CARE_SUPPORT]",
        "Child or pet care support",
        "support",
    ),
    "other_support": PlaceholderSpec(
        "other_support", "[OTHER_SUPPORT]", "Other support", "support"
    ),
    "sharing_preference": PlaceholderSpec(
        "sharing_preference", "[SHARING_PREFERENCE]", "Sharing preference", "privacy"
    ),
    "next_update_timing": PlaceholderSpec(
        "next_update_timing",
        "[NEXT_UPDATE_TIMING]",
        "When to expect another update",
        "follow_up",
    ),
}


REQUIRED_FOR_PUBLISH_KEYS = frozenset(
    {"patient_name", "health_condition", "relationship_to_patient"}
)


TOKEN_TO_KEY: dict[str, str] = {
    spec.token: key for key, spec in PLACEHOLDERS.items()
}

ALL_TOKENS: frozenset[str] = frozenset(TOKEN_TO_KEY.keys())

ALLOWED_TOKEN_LIST_TEXT = "\n".join(sorted(ALL_TOKENS))


def _is_missing(value: str | None) -> bool:
    return value is None or value.strip() == ""


def build_resolved_context(request: GeneratePostRequest) -> dict[str, str]:
    """Build the "known value OR canonical placeholder" context."""

    onboarding = request.onboarding
    details = request.details

    source_values: dict[str, str | None] = {
        "patient_name": onboarding.patient_name,
        "health_condition": onboarding.health_condition,
        "author_name": onboarding.author_name,
        "relationship_to_patient": onboarding.relationship_to_patient,
        "primary_caregiver_name": onboarding.primary_caregiver_name,
        "event_or_symptom_context": details.event_or_symptom_context,
        "diagnosis_details": details.diagnosis_details,
        "hospital_name": details.hospital_name,
        "treatment_plan": details.treatment_plan,
        "next_medical_step": details.next_medical_step,
        "visiting_information": details.visiting_information,
        "flowers_information": details.flowers_information,
        "phone_text_preferences": details.phone_text_preferences,
        "support_needs": details.support_needs,
        "fundraiser_information": details.fundraiser_information,
        "food_information": details.food_information,
        "transportation_support": details.transportation_support,
        "child_or_pet_care_support": details.child_or_pet_care_support,
        "other_support": details.other_support,
        "sharing_preference": details.sharing_preference,
        "next_update_timing": details.next_update_timing,
    }

    resolved: dict[str, str] = {}

    for key, spec in PLACEHOLDERS.items():
        value = source_values.get(key)
        resolved[key] = value.strip() if not _is_missing(value) else spec.token

    return resolved


def known_fields(resolved_context: dict[str, str]) -> dict[str, str]:
    """Subset of the resolved context whose value is NOT a placeholder token."""

    return {
        key: value
        for key, value in resolved_context.items()
        if value != PLACEHOLDERS[key].token
    }


def extract_tokens(text: str) -> list[str]:
    """Return every bracket token in ``text``, in first-appearance order, deduped."""

    seen: list[str] = []

    for match in TOKEN_PATTERN.finditer(text):
        token = match.group(0)

        if token not in seen:
            seen.append(token)

    return seen


def unknown_tokens(text: str) -> list[str]:
    """Tokens present in ``text`` that are not in the canonical registry."""

    return [token for token in extract_tokens(text) if token not in ALL_TOKENS]


def metadata_for_active_tokens(tokens: list[str]) -> list[dict]:
    """Build frontend-facing placeholder metadata for tokens that are still
    present (i.e. unresolved) in the final post text.
    """

    metadata = []

    for token in tokens:
        key = TOKEN_TO_KEY.get(token)

        if key is None:
            continue

        spec = PLACEHOLDERS[key]

        metadata.append(
            {
                "key": spec.key,
                "token": spec.token,
                "label": spec.label,
                "category": spec.category,
                "required_for_publish": spec.key in REQUIRED_FOR_PUBLISH_KEYS,
            }
        )

    return metadata


_WORD_PATTERN = re.compile(r"[a-z0-9]+")

# Fraction of a known value's significant words (length > 2, to skip "a",
# "is", "to", etc.) that must show up somewhere in the post for that fact to
# count as covered. Deliberately loose: the model is expected to paraphrase
# ("Ryan" instead of "Ryan Freese", "her father" instead of "Dad"), not quote
# every field verbatim, so this only needs to catch a fact that is wholesale
# absent, not one that was merely reworded. Lowered from 0.5 -- even the
# word-overlap version was still flagging real Gemini drafts that had
# clearly incorporated a fact but reworded most of its words.
_FACT_COVERAGE_THRESHOLD = 0.3


def missing_known_facts(post: str, resolved_context: dict[str, str]) -> list[str]:
    """Keys of known (non-placeholder) facts that appear to be wholesale
    absent from ``post``, judged by fuzzy word overlap rather than an exact
    substring match (the model is expected to paraphrase, not quote).

    This is a coarse, deterministic stand-in for the model's self-reported
    ``coverage`` field, which is not authoritative (same rationale as
    ``extract_tokens`` above): a model can claim a category is covered while
    having silently dropped the actual supplied fact.
    """

    post_lower = post.lower()
    post_words = set(_WORD_PATTERN.findall(post_lower))

    missing: list[str] = []
    for key, value in known_fields(resolved_context).items():
        value_lower = value.lower()
        if value_lower in post_lower:
            continue

        value_words = [w for w in _WORD_PATTERN.findall(value_lower) if len(w) > 2]
        if not value_words:
            # Trivial value (e.g. "ER", "Dr", "OK") -- too short for
            # word-overlap fuzzy matching to judge reliably, and short
            # answers like this are exactly what real users type. Give it
            # the benefit of the doubt rather than auto-flagging as missing.
            continue

        overlap = sum(1 for w in value_words if w in post_words)
        if overlap / len(value_words) < _FACT_COVERAGE_THRESHOLD:
            missing.append(key)

    return missing


def substitute_known_values(post: str, resolved_context: dict[str, str]) -> str:
    """Deterministically replace any placeholder token whose field is
    actually known with the real value.
    """

    result = post

    for key, value in known_fields(resolved_context).items():
        token = PLACEHOLDERS[key].token

        if token in result:
            result = result.replace(token, value)

    return result