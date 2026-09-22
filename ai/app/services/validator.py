"""Post-generation validation (plan section 22).

Gemini's output is schema-constrained, but schema compliance does not
guarantee semantic correctness. This module re-checks the parts of the
contract that must hold deterministically:

- Every bracket token in the post is in the canonical registry.
- The post is non-empty and within reasonable length bounds.

Placeholder metadata and known-value substitution are handled separately in
``app.core.placeholders`` (the post text is authoritative there, not the
model's self-reported ``used_placeholders`` list -- plan section 22.2).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.placeholders import known_fields, missing_known_facts, unknown_tokens

MIN_POST_LENGTH = 80
MAX_POST_LENGTH = 5000

# Minimum character counts per requested length preference. These are
# deliberately lenient (well below the actual paragraph guidance given to
# the model in prompt_builder._LENGTH_GUIDANCE) -- the goal is only to catch
# a draft that is dramatically shorter than what was asked for, not to
# police prose length precisely.
LENGTH_MIN_CHARS = {
    "short": 150,
    "medium": 350,
    "long": 600,
}

# If more than this fraction of the known (non-placeholder) facts supplied
# by the user are entirely absent from the post text, treat the draft as
# having dropped too much of the supplied context to ship as-is.
MAX_MISSING_FACT_RATIO = 0.4


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_generation(
    post: str,
    *,
    length: str | None = None,
    resolved_context: dict[str, str] | None = None,
) -> ValidationResult:
    errors: list[str] = []

    if not post or not post.strip():
        errors.append("empty_post")
        return ValidationResult(ok=False, errors=errors)

    post_length = len(post.strip())
    if post_length < MIN_POST_LENGTH:
        errors.append("post_too_short")
    if post_length > MAX_POST_LENGTH:
        errors.append("post_too_long")

    if length is not None and post_length < LENGTH_MIN_CHARS[length]:
        errors.append("post_too_short_for_requested_length")

    bad_tokens = unknown_tokens(post)
    if bad_tokens:
        errors.append(f"unknown_placeholder_tokens:{','.join(bad_tokens)}")

    if resolved_context is not None:
        total_known = len(known_fields(resolved_context))
        missing = missing_known_facts(post, resolved_context)
        if total_known > 0 and len(missing) / total_known > MAX_MISSING_FACT_RATIO:
            errors.append(f"missing_known_facts:{','.join(sorted(missing))}")

    return ValidationResult(ok=not errors, errors=errors)
