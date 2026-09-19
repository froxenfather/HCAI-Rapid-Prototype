"""Generation orchestrator (plan sections 7 and 57).

Wires together the deterministic pieces (resolved context, example
selection, prompt construction, validation, known-value substitution,
placeholder extraction) around exactly one normal-path call to the
generation client, with at most one repair retry on validation failure.
"""

from __future__ import annotations

from app.core.placeholders import (
    build_resolved_context,
    extract_tokens,
    metadata_for_active_tokens,
    substitute_known_values,
)
from app.models.generation import GeminiGeneration
from app.models.requests import GeneratePostRequest
from app.models.responses import GeneratePostResponse, PlaceholderMetadata
from app.services.errors import GenerationValidationError
from app.services.example_loader import anti_pattern_notes, select_examples
from app.services.gemini_client import GenerationClient
from app.services.prompt_builder import build_prompt
from app.services.validator import validate_generation


def _repair_instruction(errors: list[str]) -> str:
    return (
        "\n\nThe previous response violated the placeholder contract "
        f"({'; '.join(errors)}). Regenerate using only the allowed placeholder "
        "tokens listed above, and make sure the post is non-empty and a "
        "reasonable length."
    )


def _generate_validated(
    client: GenerationClient, system_instruction: str, user_content: str
) -> GeminiGeneration:
    generation = client.generate_post(system_instruction, user_content)
    result = validate_generation(generation.post)
    if result.ok:
        return generation

    # One repair attempt (plan section 57). No infinite loop.
    repaired_content = user_content + _repair_instruction(result.errors)
    generation = client.generate_post(system_instruction, repaired_content)
    result = validate_generation(generation.post)
    if result.ok:
        return generation

    raise GenerationValidationError(
        f"Gemini output failed placeholder/length validation twice: {result.errors}"
    )


def generate_post(
    request: GeneratePostRequest, client: GenerationClient
) -> GeneratePostResponse:
    resolved_context = build_resolved_context(request)
    examples = select_examples(request)
    notes = anti_pattern_notes(request)

    system_instruction, user_content = build_prompt(
        request, resolved_context, examples, notes
    )

    generation = _generate_validated(client, system_instruction, user_content)

    final_post = substitute_known_values(generation.post, resolved_context)
    active_tokens = extract_tokens(final_post)
    placeholder_dicts = metadata_for_active_tokens(active_tokens)

    return GeneratePostResponse(
        post=final_post,
        placeholders=[PlaceholderMetadata.model_validate(p) for p in placeholder_dicts],
        coverage=generation.coverage,
    )
