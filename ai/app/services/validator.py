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

from app.core.placeholders import unknown_tokens

MIN_POST_LENGTH = 80
MAX_POST_LENGTH = 5000


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_generation(post: str) -> ValidationResult:
    errors: list[str] = []

    if not post or not post.strip():
        errors.append("empty_post")
        return ValidationResult(ok=False, errors=errors)

    length = len(post.strip())
    if length < MIN_POST_LENGTH:
        errors.append("post_too_short")
    if length > MAX_POST_LENGTH:
        errors.append("post_too_long")

    bad_tokens = unknown_tokens(post)
    if bad_tokens:
        errors.append(f"unknown_placeholder_tokens:{','.join(bad_tokens)}")

    return ValidationResult(ok=not errors, errors=errors)
