import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY", "not-needed"),
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
)

MODEL_NAME = os.getenv("LLM_MODEL_NAME")


def build_prompt(question_text: str, student_answer: str, rubric: dict, max_score: int) -> str:
    criteria_lines = "\n".join(
        f"- {c['name']} (max weight: {c['weight']} points): {c.get('description', '')}"
        for c in rubric.get("criteria", [])
    )
    return f"""You are an expert evaluator of English as a Second Language exams.

EXAM QUESTION:
{question_text}

STUDENT ANSWER:
{student_answer}

EVALUATION RUBRIC (total maximum score: {max_score}):
{criteria_lines}

INSTRUCTIONS:
Evaluate the student's answer according to each criterion in the rubric. For each criterion, assign a score between 0 and that criterion's maximum weight. Be objective, basing your evaluation solely on the text of the answer.

Respond ONLY with valid JSON, with no additional text or markdown, using this exact structure:

{{
  "breakdown": [
    {{"criterion": "criterion_name", "score": <number>, "max": <number>, "comment": "<brief justification>"}}
  ],
  "feedback": "<overall feedback for the student, 2-4 sentences>"
}}
"""


def evaluate_response(question_text: str, student_answer: str, rubric: dict, max_score: int = 100) -> dict:
    prompt = build_prompt(question_text, student_answer, rubric, max_score)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an English exam evaluator. You respond only in valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        raw_content = completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error calling the LLM: {e}")

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        raise ValueError(f"The LLM did not return valid JSON: {raw_content}")

    breakdown = parsed.get("breakdown", [])
    total_score = sum(item.get("score", 0) for item in breakdown)

    return {
        "score": total_score,
        "breakdown": breakdown,
        "feedback": parsed.get("feedback", ""),
        "model_used": MODEL_NAME,
    }