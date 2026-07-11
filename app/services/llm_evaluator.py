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
        f"- {c['name']} (peso maximo: {c['weight']} puntos): {c.get('description', '')}"
        for c in rubric.get("criteria", [])
    )
    return f"""Eres un evaluador experto de examenes de ingles como segunda lengua.

PREGUNTA DEL EXAMEN:
{question_text}

RESPUESTA DEL ESTUDIANTE:
{student_answer}

RUBRICA DE EVALUACION (puntaje maximo total: {max_score}):
{criteria_lines}

INSTRUCCIONES:
Evalua la respuesta del estudiante segun cada criterio de la rubrica. Para cada criterio, asigna un puntaje entre 0 y el peso maximo de ese criterio. Se objetivo, basandote unicamente en el texto de la respuesta.

Responde UNICAMENTE con un JSON valido, sin texto adicional ni markdown, con esta estructura exacta:

{{
  "breakdown": [
    {{"criterion": "nombre_del_criterio", "score": <numero>, "max": <numero>, "comment": "<breve justificacion>"}}
  ],
  "feedback": "<retroalimentacion general para el estudiante, 2-4 frases>"
}}
"""


def evaluate_response(question_text: str, student_answer: str, rubric: dict, max_score: int = 100) -> dict:
    prompt = build_prompt(question_text, student_answer, rubric, max_score)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Eres un evaluador de examenes de ingles. Respondes unicamente en JSON valido."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        raw_content = completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error al llamar al LLM: {e}")

    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        raise ValueError(f"El LLM no devolvio un JSON valido: {raw_content}")

    breakdown = parsed.get("breakdown", [])
    total_score = sum(item.get("score", 0) for item in breakdown)

    return {
        "score": total_score,
        "breakdown": breakdown,
        "feedback": parsed.get("feedback", ""),
        "model_used": MODEL_NAME,
    }