# CaringBridge AI Backend (MVP)

Backend for the "Start from Something Similar" concept: given the standard
CaringBridge onboarding info plus any optional details the user adds, this
service asks Gemini to draft a first-post. Anything the user did not supply
comes back as a standardized bracket placeholder (e.g. `[HOSPITAL_NAME]`)
instead of an invented fact, so the frontend can render it as a clickable,
fillable field.

Full design rationale lives in `../CAREBRIDGE_AI_BACKEND_PLAN.md`. This
README is just the practical "how do I run/test/call this" reference.

## Setup

```bash
cd ai
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the env template and fill in your key (or drop a `.env` at the repo
root instead -- config loading searches upward from the current directory,
so either location works):

```bash
copy .env.example .env
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

Interactive API docs (useful for demos): `http://localhost:8000/docs`

## Quick manual demo (no server needed)

```bash
python cli_demo.py
```

A dummy `input()`-based CLI that asks the onboarding/detail questions one at
a time (blank = skip) and runs them through the same pipeline the HTTP API
uses, printing the generated post, unresolved placeholders, and coverage
report directly to the terminal. Respects `AI_PROVIDER`/`GEMINI_API_KEY` the
same way the server does.

## Running without a Gemini key

Set `AI_PROVIDER=fake` (in `.env` or as an environment variable) to use a
deterministic offline generator instead of calling Gemini. It still
respects the same known-value-vs-placeholder contract, so the frontend can
integrate against a stable API before a key is available.

If `AI_PROVIDER=gemini` (the default) and no `GEMINI_API_KEY` is set, the
server still boots and `/health` still returns `200`, but
`/api/v1/generate-post` returns a `503` with a clear configuration error.

## API contract

### `GET /health`

```json
{"status": "ok"}
```

### `POST /api/v1/generate-post`

Request:

```json
{
  "onboarding": {
    "patient_name": "Jake",
    "health_condition": "traumatic brain injury",
    "author_role": "friend",
    "author_name": "Alex",
    "relationship_to_patient": "close friend",
    "is_primary_caregiver": false,
    "primary_caregiver_name": "Maria"
  },
  "details": {
    "event_or_symptom_context": "Jake was in a car accident Wednesday night",
    "diagnosis_details": "traumatic brain injury",
    "hospital_name": null,
    "treatment_plan": "Doctors are monitoring swelling after surgery",
    "next_medical_step": "The team will reassess over the next 48 to 72 hours",
    "visiting_information": "We are not able to have visitors right now",
    "next_update_timing": "after I speak with Maria tomorrow"
  },
  "preferences": {"tone": "warm", "length": "medium", "style": "personal"}
}
```

`onboarding.author_role` is the only required field. Everything else is
optional -- unsupplied fields become canonical placeholders in the
generated post.

Response:

```json
{
  "post": "Hi everyone. I'm Alex, a close friend of Jake's... He is currently being cared for at [HOSPITAL_NAME]. ...",
  "placeholders": [
    {
      "key": "hospital_name",
      "token": "[HOSPITAL_NAME]",
      "label": "Hospital or care location",
      "category": "logistics",
      "required_for_publish": false
    }
  ],
  "coverage": {
    "patient_and_health_issue": true,
    "author_relationship": true,
    "condition_details": true,
    "community_information": true,
    "support_needs": true,
    "privacy_preferences": true,
    "next_medical_steps": true,
    "next_update": true
  }
}
```

`placeholders` only lists tokens that actually still appear in `post`. The
frontend finds each token by exact string match, renders it as clickable,
and replaces it with the user's typed value -- no further API call needed.

Sample cURL:

```bash
curl -X POST "http://localhost:8000/api/v1/generate-post" \
  -H "Content-Type: application/json" \
  -d '{"onboarding": {"author_role": "caregiver", "health_condition": "cancer"}}'
```

### Error shape

```json
{"error": "generation_failed", "message": "Unable to generate a draft right now."}
```

| Status | error                   | When                                             |
| ------ | ----------------------- | ------------------------------------------------- |
| 422    | (Pydantic default)      | Request failed schema validation                  |
| 502    | `generation_failed`     | Gemini call failed, or output failed validation twice |
| 503    | `provider_not_configured` | `AI_PROVIDER=gemini` but no `GEMINI_API_KEY`     |

## How it works

1. **Normalize + resolve** (`app/core/placeholders.py`): every tracked field
   resolves deterministically to either the user's value or its canonical
   placeholder token (`build_resolved_context`). Python owns this -- Gemini
   never sees a bare `null`.
2. **Select examples** (`app/services/example_loader.py`): 2-3 relevant
   curated "good" examples are chosen by condition/role/caregiver-status
   scoring (no embeddings, no vector store -- six curated examples don't
   need one). A short list of condition-relevant anti-patterns from the
   curated "bad" examples supplements a static anti-pattern checklist.
3. **Build the prompt** (`app/services/prompt_builder.py`): one system
   instruction (stable across requests) states the strict source-of-truth
   rule, the placeholder rule, the full list of allowed tokens, and the
   prompt-injection defense framing for user data. The per-request user
   content embeds the resolved context, examples, anti-patterns, and style
   preferences.
4. **Generate** (`app/services/gemini_client.py` / `fake_client.py`): one
   call to Gemini with structured JSON output constrained to the
   `GeminiGeneration` schema (`post`, `used_placeholders`, `coverage`).
   `FakeGeminiClient` implements the same interface without any network
   call, for tests and `AI_PROVIDER=fake`.
5. **Validate** (`app/services/validator.py`): the post text -- not the
   model's self-reported `used_placeholders` -- is authoritative. Any
   bracket token not in the canonical registry, or an empty/too-short/too-
   long post, triggers exactly one repair regeneration attempt; a second
   failure returns a controlled `502`.
6. **Deterministic repair** (`app/core/placeholders.py:substitute_known_values`):
   if Gemini emits a placeholder for a field the user actually supplied,
   it's swapped back to the real value without another API call.
7. **Respond**: active placeholder tokens are re-extracted from the final
   text and mapped to frontend metadata (label, category,
   `required_for_publish`) deterministically.

The example corpus in `app/data/examples.json` is synthetic -- no real
CaringBridge patient posts were used, per the plan's privacy requirements.

## Tests

```bash
pytest
```

Runs 44 unit + endpoint tests entirely offline (a `FakeGeminiClient` is
injected everywhere -- no network calls, no API quota spent, regardless of
what `GEMINI_API_KEY` is set to).

An optional integration suite calls the real Gemini API and is **not** run
by default:

```bash
pytest -m integration
```

It's skipped automatically if `GEMINI_API_KEY` isn't configured.

## Troubleshooting: "high demand" / 503 / 429 errors

Free-tier Gemini API keys have a **per-model daily request quota** (20
requests/day/model at the time of writing). Two symptoms to know apart:

- A genuinely transient outage (Google's servers are momentarily
  overloaded) shows up as `503 UNAVAILABLE` and is retried automatically up
  to 3 times with backoff (`app/services/gemini_client.py`) before failing.
- **Quota exhaustion** shows up as `429 RESOURCE_EXHAUSTED` with a message
  like `Quota exceeded for metric: ... limit: 20, model: gemini-3.8-flash`
  -- retries won't help here; each model has its *own* quota bucket, so
  switching `GEMINI_MODEL` to a model you haven't used yet works around it
  immediately, or just wait for the daily reset.
- In practice, some 503s reported as "high demand" turned out to actually
  be masking quota exhaustion on the specific model being called -- if
  retries don't help, try a different `GEMINI_MODEL` before assuming it's
  a real outage.

Either way, `AI_PROVIDER=fake` keeps development moving without touching
the API at all.

## Environment variables

| Variable            | Default                                          | Purpose                                   |
| -------------------- | ------------------------------------------------ | ------------------------------------------ |
| `GEMINI_API_KEY`     | (none)                                           | Required for real generation               |
| `GEMINI_MODEL`       | `gemini-3.5-flash-lite`                          | Model name, kept out of application code   |
| `GEMINI_TEMPERATURE` | `0.4`                                            | Generation temperature                     |
| `AI_PROVIDER`        | `gemini`                                         | `gemini` or `fake`                         |
| `APP_ENV`            | `development`                                    | Informational                              |
| `CORS_ORIGINS`       | `http://localhost:3000,http://localhost:5173`    | Comma-separated allowed frontend origins   |
