# English Exam Evaluator

Microservice built with **FastAPI** that receives English exam responses (question, student answer, and grading rubric) and automatically scores them using an LLM, returning a score, an approval status, and detailed feedback per criterion.

This service is **not a full exam platform**: it does not manage users, exams, or questions. Its only responsibility is to receive the data needed to evaluate a response, grade it, and keep a history of evaluations. Exams, questions, and users live in an external system that consumes this API.

## Features

- Automatic evaluation of exam responses via LLM, based on a configurable rubric sent with each request.
- Deterministic approval calculation (`approved`) handled in the backend, not delegated to the LLM.
- Feedback broken down by evaluation criterion.
- Evaluation history persisted in PostgreSQL (native `JSONB` types for the rubric and result breakdown).
- Compatible with any LLM provider that exposes an OpenAI-compatible API: Groq, local models served with LM Studio, Ollama, OpenAI, etc. The provider is configured via environment variables, with no code changes required.
- Strict input validation (minimum/maximum length, rubric weights) to prevent evaluations on empty or invalid data.

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Pydantic v2** — validation and schemas
- **OpenAI SDK** — client compatible with any OpenAI-style provider

## Prerequisites

- Python 3.11+
- PostgreSQL running
- Access to an OpenAI-API-compatible LLM provider (a hosted API key, or a model running locally)

## Installation

```bash
git clone <repository-url>
cd english-evaluator

python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root (this file should never be committed to version control):

```env
# Database
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>
DB_HOST=<your_db_host>
DB_PORT=5432
DB_NAME=<your_db_name>

# LLM provider (OpenAI-API-compatible)
LLM_BASE_URL=<provider_base_url>
LLM_API_KEY=<your_llm_api_key>
LLM_MODEL_NAME=<model_identifier>
```

Example for a local provider (e.g. LM Studio, default settings):

```env
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=not-needed
LLM_MODEL_NAME=<model_identifier_as_shown_by_provider>
```

Example for a hosted provider (e.g. Groq):

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=<your_api_key>
LLM_MODEL_NAME=<model_name>
```

## Database

Run the `db-script.sql` script included in the repository against your PostgreSQL database to create the `evaluations` table:

```bash
psql -U <your_db_user> -d <your_db_name> -f db-script.sql
```

## Running the app

```bash
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`, and the interactive documentation (Swagger) at `http://127.0.0.1:8000/docs`.

## Usage

### `POST /evaluate`

Receives an exam response and returns its evaluation.

**Request:**

```json
{
  "external_user_id": "<external-user-reference>",
  "external_exam_id": "<external-exam-reference>",
  "external_question_id": "<external-question-reference>",
  "external_response_id": "<external-response-reference>",
  "question_text": "Describe your daily routine using present simple tense.",
  "student_answer": "I wake up at 7 am. I goes to work by bus. After work I cooking dinner.",
  "rubric": {
    "criteria": [
      { "name": "grammar", "weight": 25, "description": "Correct use of present simple" },
      { "name": "vocabulary", "weight": 25, "description": "Range and accuracy of vocabulary" },
      { "name": "coherence", "weight": 25, "description": "Logical flow of ideas" },
      { "name": "task_achievement", "weight": 25, "description": "Covers a full daily routine" }
    ]
  },
  "max_score": 100,
  "passing_score": 60
}
```

**Response (`201 Created`):**

```json
{
  "id": 1,
  "external_user_id": "<external-user-reference>",
  "external_exam_id": "<external-exam-reference>",
  "external_question_id": "<external-question-reference>",
  "external_response_id": "<external-response-reference>",
  "score": 73.0,
  "approved": true,
  "feedback": "Your response is clear and covers a good portion of your daily routine...",
  "score_breakdown": [
    {
      "criterion": "grammar",
      "score": 15.0,
      "max": 25.0,
      "comment": "The student made a grammatical error in 'I goes to work by bus'..."
    }
  ],
  "model_used": "<model_identifier>",
  "evaluated_at": "2026-07-11T15:37:29.213841-05:00"
}
```

## Project structure

```
app/
├── main.py                          # Application entry point
├── models.py                        # SQLAlchemy models
├── schemas.py                       # Pydantic schemas (request/response)
├── routes/
│   └── evaluation_routes.py         # POST /evaluate endpoint
├── services/
│   └── llm_evaluator.py             # Prompt building and LLM call logic
└── utils/
    ├── config.py                    # Database connection
    └── __init__.py
db-script.sql                        # evaluations table creation script
```

## Design notes

- The **approval status** (`approved`) is calculated in the backend by comparing `score` against `passing_score`; the decision is not delegated to the LLM. This keeps the business rule deterministic and auditable.
- The **rubric** travels with each request; this service does not store its own rubrics, since the exam, the question, and its evaluation criteria are the responsibility of the external system consuming this API.
- The `external_*_id` fields are for reference/traceability only — they are not real foreign keys, since they point to entities that live in another system.

## Next steps

- Authentication for the `/evaluate` endpoint (a dedicated API key for API clients).
- Associate evaluations with an account/API client.
- More granular error handling depending on the type of LLM failure (timeout, model unavailable, malformed response).