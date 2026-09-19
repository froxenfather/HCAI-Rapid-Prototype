"""Dummy CLI for the CaringBridge AI backend.

Prompts for onboarding info with plain `input()` calls, builds a
GeneratePostRequest, and runs it through the same generation pipeline the
HTTP API uses -- no server needed. Meant purely as a quick manual demo/
sanity check, not a real UI.

Run from inside `ai/` (with the venv active):

    python cli_demo.py

Respects the same environment variables as the server: set AI_PROVIDER=fake
to skip Gemini entirely, or leave it on "gemini" with GEMINI_API_KEY set for
a real draft.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.models.requests import (
    GeneratePostRequest,
    GenerationPreferences,
    OnboardingInfo,
    UserAddedDetails,
)
from app.services.errors import GenerationProviderError, GenerationValidationError
from app.services.fake_client import FakeGeminiClient
from app.services.gemini_client import GenerationClient
from app.services.post_generator import generate_post

AUTHOR_ROLES = ["patient", "caregiver", "friend", "family", "other"]
TONES = ["warm", "neutral", "hopeful", "direct", "gentle"]
LENGTHS = ["short", "medium", "long"]
STYLES = ["personal", "concise", "informative"]


def ask(prompt: str) -> str | None:
    """Plain optional text prompt. Blank input -> None."""
    value = input(f"{prompt} (press Enter to skip): ").strip()
    return value or None


def ask_choice(prompt: str, choices: list[str], default: str | None = None) -> str:
    """Prompt until the user types one of `choices` (case-insensitive).
    Blank input uses `default` if given.
    """
    choices_text = "/".join(choices)
    while True:
        raw = input(f"{prompt} [{choices_text}]" + (f" (default: {default})" if default else "") + ": ").strip().lower()
        if not raw and default:
            return default
        if raw in choices:
            return raw
        print(f"  Please type one of: {choices_text}")


def ask_yes_no(prompt: str) -> bool | None:
    raw = input(f"{prompt} (y/n, press Enter if unknown): ").strip().lower()
    if raw in ("y", "yes"):
        return True
    if raw in ("n", "no"):
        return False
    return None


def collect_onboarding() -> OnboardingInfo:
    print("\n--- Onboarding (required questions) ---")
    author_role = ask_choice("Who is writing this page?", AUTHOR_ROLES)

    print("\n--- Onboarding (optional -- leave blank if unknown) ---")
    patient_name = ask("Patient's name")
    health_condition = ask("Health condition (e.g. 'ovarian cancer', 'stroke', 'TBI')")
    author_name = ask("Your name (the author)")
    relationship_to_patient = ask("Your relationship to the patient (e.g. 'close friend')")
    is_primary_caregiver = ask_yes_no("Are you the primary caregiver?")
    primary_caregiver_name = ask("Primary caregiver's name (if that's someone else)")

    return OnboardingInfo(
        patient_name=patient_name,
        health_condition=health_condition,
        author_role=author_role,
        author_name=author_name,
        relationship_to_patient=relationship_to_patient,
        is_primary_caregiver=is_primary_caregiver,
        primary_caregiver_name=primary_caregiver_name,
    )


def collect_details() -> UserAddedDetails:
    print("\n--- Additional details (all optional -- leave blank if unknown) ---")
    return UserAddedDetails(
        event_or_symptom_context=ask("What happened / symptoms that led here"),
        diagnosis_details=ask("Diagnosis details"),
        hospital_name=ask("Hospital or care location"),
        treatment_plan=ask("Treatment plan"),
        next_medical_step=ask("Next medical step"),
        visiting_information=ask("Visiting information"),
        flowers_information=ask("Flowers information"),
        phone_text_preferences=ask("Phone/text preferences"),
        support_needs=ask("What support would help"),
        fundraiser_information=ask("Fundraiser information"),
        food_information=ask("Food/meal support info"),
        transportation_support=ask("Transportation support needed"),
        child_or_pet_care_support=ask("Child or pet care support needed"),
        other_support=ask("Other support needed"),
        sharing_preference=ask("Sharing preference (who can this page be shared with?)"),
        next_update_timing=ask("When to expect the next update"),
    )


def collect_preferences() -> GenerationPreferences:
    print("\n--- Style preferences ---")
    tone = ask_choice("Tone", TONES, default="warm")
    length = ask_choice("Length", LENGTHS, default="medium")
    style = ask_choice("Style", STYLES, default="personal")
    return GenerationPreferences(tone=tone, length=length, style=style)


def build_client() -> GenerationClient:
    settings = get_settings()
    if settings.ai_provider == "fake":
        print("\n[Using AI_PROVIDER=fake -- no real Gemini call will be made]")
        return FakeGeminiClient()

    if not settings.gemini_configured:
        print(
            "\nNo GEMINI_API_KEY configured (and AI_PROVIDER is not 'fake')."
            "\nFalling back to the fake generator so you can still see the contract."
        )
        return FakeGeminiClient()

    from app.services.gemini_client import GeminiClient

    print(f"\n[Calling real Gemini model: {settings.gemini_model}]")
    return GeminiClient(
        api_key=settings.gemini_api_key,  # type: ignore[arg-type]
        model=settings.gemini_model,
        temperature=settings.gemini_temperature,
    )


def main() -> None:
    print("CaringBridge AI backend -- dummy CLI demo")
    print("=" * 50)

    onboarding = collect_onboarding()
    details = collect_details()
    preferences = collect_preferences()

    request = GeneratePostRequest(onboarding=onboarding, details=details, preferences=preferences)
    client = build_client()

    print("\nGenerating draft...\n")
    try:
        response = generate_post(request, client)
    except (GenerationProviderError, GenerationValidationError) as exc:
        print(f"Generation failed: {exc}")
        return

    print("=" * 50)
    print("GENERATED POST")
    print("=" * 50)
    print(response.post)

    if response.placeholders:
        print("\n" + "=" * 50)
        print("UNRESOLVED PLACEHOLDERS")
        print("=" * 50)
        for placeholder in response.placeholders:
            required = " (required to publish)" if placeholder.required_for_publish else ""
            print(f"  {placeholder.token} -- {placeholder.label}{required}")
    else:
        print("\n(No unresolved placeholders -- every field was supplied.)")

    print("\n" + "=" * 50)
    print("COVERAGE")
    print("=" * 50)
    for category, covered in response.coverage.model_dump().items():
        mark = "yes" if covered else "no"
        print(f"  {category}: {mark}")


if __name__ == "__main__":
    main()
