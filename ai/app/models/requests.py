"""Request schemas for the generate-post endpoint (plan section 9)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

_NAME_MAX = 100
_SHORT_MAX = 300
_MEDIUM_MAX = 2000


def _strip_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class OnboardingInfo(BaseModel):
    patient_name: str | None = Field(default=None, max_length=_NAME_MAX)
    health_condition: str | None = Field(default=None, max_length=_SHORT_MAX)

    author_role: Literal["patient", "caregiver", "friend", "family", "other"]
    author_name: str | None = Field(default=None, max_length=_NAME_MAX)

    relationship_to_patient: str | None = Field(default=None, max_length=_SHORT_MAX)

    is_primary_caregiver: bool | None = None
    primary_caregiver_name: str | None = Field(default=None, max_length=_NAME_MAX)

    _normalize = field_validator(
        "patient_name",
        "health_condition",
        "author_name",
        "relationship_to_patient",
        "primary_caregiver_name",
        mode="after",
    )(_strip_or_none)


class UserAddedDetails(BaseModel):
    event_or_symptom_context: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    diagnosis_details: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    hospital_name: str | None = Field(default=None, max_length=_SHORT_MAX)

    treatment_plan: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    next_medical_step: str | None = Field(default=None, max_length=_MEDIUM_MAX)

    visiting_information: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    flowers_information: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    phone_text_preferences: str | None = Field(default=None, max_length=_MEDIUM_MAX)

    support_needs: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    fundraiser_information: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    food_information: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    transportation_support: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    child_or_pet_care_support: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    other_support: str | None = Field(default=None, max_length=_MEDIUM_MAX)

    sharing_preference: str | None = Field(default=None, max_length=_MEDIUM_MAX)
    next_update_timing: str | None = Field(default=None, max_length=_SHORT_MAX)

    _normalize = field_validator(
        "event_or_symptom_context",
        "diagnosis_details",
        "hospital_name",
        "treatment_plan",
        "next_medical_step",
        "visiting_information",
        "flowers_information",
        "phone_text_preferences",
        "support_needs",
        "fundraiser_information",
        "food_information",
        "transportation_support",
        "child_or_pet_care_support",
        "other_support",
        "sharing_preference",
        "next_update_timing",
        mode="after",
    )(_strip_or_none)


class GenerationPreferences(BaseModel):
    tone: Literal["warm", "neutral", "hopeful", "direct", "gentle"] = "warm"
    length: Literal["short", "medium", "long"] = "medium"
    style: Literal["personal", "concise", "informative"] = "personal"


class GeneratePostRequest(BaseModel):
    onboarding: OnboardingInfo
    details: UserAddedDetails = Field(default_factory=UserAddedDetails)
    preferences: GenerationPreferences = Field(default_factory=GenerationPreferences)
