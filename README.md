# English Evaluator — Backend

AI-powered English assessment backend built with **FastAPI, PostgreSQL, SQLAlchemy, Whisper and LLM-based evaluation**.

> **Product vision:** a reusable evaluation engine for education, recruitment, corporate training and language-assessment platforms.

## Overview

The backend evaluates written and spoken English responses against configurable rubrics, produces structured scores and feedback, and persists evaluations.

```text
                    ┌──────────────────────┐
                    │      Frontend        │
                    └──────────┬───────────┘
                               │ REST
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    └──────────┬───────────┘
                               │
               ┌───────────────┼────────────────┐
               ▼               ▼                ▼
          Evaluation       Speaking          Rubrics
               │               │
               │        ┌──────┴──────┐
               │        ▼             ▼
               │     Whisper       Audio metrics
               │        │             │
               └────────┴──────┬──────┘
                               ▼
                         LLM Evaluator
                               │
                               ▼
                         PostgreSQL
```

## Main capabilities

### Written evaluation

Evaluates an English response against a rubric and returns criterion-level scores, feedback and an overall result.

Typical criteria include:

- Grammar
- Vocabulary
- Coherence
- Task achievement
- Fluency
- Custom criteria

The LLM performs language evaluation, while application code validates the structure and applies deterministic business rules.

### Speaking evaluation

Accepts recorded audio and processes it through a speech-evaluation pipeline:

- audio upload
- Whisper transcription
- transcript analysis
- duration
- word count
- words per minute
- filler detection
- repetition detection
- self-correction detection
- long-pause detection
- rubric-based LLM scoring
- structured feedback

The current system uses Whisper as the transcription component.

> **Important:** transcript-derived observations about pronunciation, stress and intonation are inferences, not equivalent to dedicated acoustic/prosody analysis. A future production version can add specialized audio models for stronger speaking assessment.

### Rubric templates

The backend supports reusable rubrics and predefined exam-style configurations. The architecture can support:

- IELTS-style assessments
- KET-style assessments
- FCE-style assessments
- custom organizational rubrics

The engine is therefore not tied to a single examination.

---

## Project structure

```text
app/
├── routes/
│   ├── evaluation_routes.py
│   ├── rubric_routes.py
│   └── speaking_routes.py
│
├── services/
│   ├── audio_evaluator.py
│   ├── exam_rubrics.py
│   ├── llm_evaluator.py
│   ├── speaking_evaluator.py
│   └── whisper_transcriber.py
│
├── main.py
├── models.py
└── schemas.py

db-script.sql
requirements.txt
README.md
```

### Routes

- `evaluation_routes.py` — written evaluation API.
- `speaking_routes.py` — speaking/audio evaluation API.
- `rubric_routes.py` — rubric template management.

### Services

- `llm_evaluator.py` — prompt construction, LLM invocation and result handling.
- `speaking_evaluator.py` — speaking evaluation orchestration.
- `whisper_transcriber.py` — speech-to-text.
- `audio_evaluator.py` — audio and fluency-related metrics.
- `exam_rubrics.py` — predefined rubric definitions.

### Core files

- `models.py` — SQLAlchemy database models.
- `schemas.py` — Pydantic API contracts.
- `main.py` — FastAPI application entry point.

---

## Written evaluation flow

Conceptually:

```text
Request
  ↓
Validate input
  ↓
Build rubric-aware prompt
  ↓
LLM evaluation
  ↓
Normalize model output
  ↓
Validate with Pydantic
  ↓
Calculate/validate final score
  ↓
Persist evaluation
  ↓
Return structured result
```

Example request shape:

```json
{
  "question": "Describe your daily routine.",
  "response": "I usually wake up at seven...",
  "rubric": {
    "criteria": [
      { "name": "Grammar", "weight": 25 },
      { "name": "Vocabulary", "weight": 25 }
    ]
  }
}
```

---

## Speaking evaluation flow

```text
Browser recording
      │
      ▼
audio/webm
      │
      ▼
FastAPI
      │
      ├──► Whisper transcription
      │
      ├──► audio metrics
      │
      └──► LLM evaluation
                │
                ▼
          rubric criteria
                │
                ▼
         normalized result
                │
                ▼
           PostgreSQL
```

The speaking result can contain:

- transcript
- overall score
- band/proficiency
- CEFR level
- criterion breakdown
- feedback
- priority improvements
- audio/fluency metrics

---

## Rubric architecture

Evaluation is **rubric-driven rather than hard-coded to one test**.

A rubric can define:

```text
Criterion
Weight
Description
Score range
Evaluation instructions
```

For example:

```text
Fluency & Coherence   25%
Lexical Resource      25%
Grammar               25%
Pronunciation         25%
```

An organization could instead define:

```text
Customer Support English

Communication        30%
Vocabulary            20%
Grammar               20%
Fluency               20%
Professional tone    10%
```

The same evaluation engine can serve both.

---

## LLM output normalization

LLMs can return slightly different field names. The backend normalizes them before Pydantic validation.

For example:

```text
max_score → max
feedback  → comment
```

This provides a stable internal contract.

The LLM should be treated as an evaluation component, **not as the authority over application structure or business rules**.

---

## Database

PostgreSQL stores evaluation information such as:

- exam type
- question
- transcript
- score
- band
- CEFR level
- pass status
- criterion breakdown
- feedback
- improvement suggestions
- speaking metrics
- evaluation metadata

SQLAlchemy manages persistence.

The database engine uses connection-health settings:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

`pool_pre_ping` helps prevent stale pooled connections from causing failures.

### Audio storage

The current MVP can persist audio with an evaluation record. For production, object storage is preferable:

```text
PostgreSQL
    └── audio_url

Object Storage
    └── response.webm
```

This keeps large multimedia files out of the relational database.

---

## Configuration

Use environment variables for credentials and deployment configuration.

Example:

```env
DATABASE_URL=
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=
```

Never commit:

- `.env`
- database passwords
- API keys
- private tokens
- service credentials

Provide an `.env.example` containing placeholders instead.

---

## LLM provider flexibility

The evaluation layer uses an OpenAI-compatible client pattern, making it possible to work with compatible hosted providers, gateways or local inference servers.

The evaluator should remain provider-agnostic where practical.

---

## API surface

Conceptually:

```text
/evaluate
    Written evaluation

/evaluate-speaking
    Speaking/audio evaluation

/rubrics
    Rubric template management
```

Request and response contracts are defined in `schemas.py`.

API consumers should depend on those contracts rather than internal SQLAlchemy models.

---

## Error handling

The API should distinguish between:

- invalid requests
- unsupported exam types
- invalid rubrics
- transcription errors
- LLM errors
- malformed LLM output
- database errors
- unexpected application errors

Model output must be validated before it is persisted or returned.

---

## Deployment

The backend is suitable for cloud deployment on platforms such as Render or similar Python hosting environments.

Typical workflow:

```text
git push
   ↓
GitHub
   ↓
Cloud deployment
   ↓
FastAPI
   ├── PostgreSQL
   ├── LLM provider
   └── transcription/audio services
```

Secrets belong in the deployment platform's environment configuration.

---

# Product positioning

The backend can power:

### Educational platforms
Automated English exams and learner progress.

### Language schools
Teacher-assisted or automated assessment.

### Corporate training
Employee English assessment and progress tracking.

### Recruitment
Automated English screening.

### Custom assessment
Organization-specific rubrics and scoring.

### Embedded API
Existing LMS, HR or education systems can consume the evaluator without adopting the reference frontend.

---

# Roadmap

## Current MVP

- FastAPI API
- PostgreSQL persistence
- written evaluation
- speaking evaluation
- Whisper transcription
- speaking metrics
- configurable rubrics
- structured Pydantic responses
- predefined exam-style rubrics
- custom rubric foundation
- cloud deployment compatibility

## Recommended production work

1. **Authentication and authorization**
2. **Multi-tenancy**
3. **Object storage for audio**
4. **Evaluation history and analytics**
5. **Asynchronous evaluation jobs**
6. **Structured logging and monitoring**
7. **LLM usage/cost tracking**
8. **Dedicated acoustic analysis**

Future speaking analysis can cover:

- pronunciation
- phoneme accuracy
- pitch
- stress
- rhythm
- intonation
- speech rate
- voice quality

---

## Design principles

1. **LLM-assisted, not LLM-controlled**
2. **Rubric-driven evaluation**
3. **Provider flexibility**
4. **API-first architecture**
5. **Deterministic application logic**
6. **Separation of concerns**

---

## License

Add the project's chosen license before public distribution.

## Disclaimer

Third-party examination names, rubrics and proficiency terminology may be protected intellectual property or trademarks. Describe third-party examinations as compatible with or inspired by public criteria unless the appropriate authorization or licensing has been obtained.
