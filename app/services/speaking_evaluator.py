# app/services/speaking_evaluator.py
import os
import json
import base64
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import dashscope
from dashscope import MultiModalConversation
from app.services.exam_rubrics import get_rubric, build_rubric_prompt

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_AUDIO_MODEL", "qwen-audio-asr-flash")


def evaluate_speaking(
    audio_bytes: bytes,
    audio_mime_type: str,
    question_text: str,
    exam_type: str,
    max_score: Optional[float] = None,
) -> dict:
    if not DASHSCOPE_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY environment variable is not set")

    dashscope.api_key = DASHSCOPE_API_KEY

    rubric = get_rubric(exam_type)
    if rubric:
        prompt = build_rubric_prompt(rubric, question_text)
        effective_max = rubric["max_score"]
        effective_passing = rubric["passing_score"]
    else:
        effective_max = max_score or 100
        effective_passing = max_score * 0.6 if max_score else 60
        prompt = f"""You are an expert English Speaking evaluator.

The student was asked: "{question_text}"

Listen to the attached audio recording and evaluate the student's spoken English.

Assess the following dimensions and score each 0-{int(effective_max)}:
- Pronunciation & Phonetics (accent, stress, intonation, rhythm)
- Fluency & Coherence (flow, hesitation, linking, discourse markers)
- Lexical Resource (vocabulary range, precision, collocations)
- Grammatical Range & Accuracy (structures, errors, complexity)
- Interactive Communication (turn-taking, responding, expanding)

For each criterion, assign a score and provide a 2-sentence justification referencing specific audio evidence.

Respond ONLY with valid JSON:
{{
  "breakdown": [
    {{"criterion": "name", "score": <number>, "max": <number>, "comment": "..."}}
  ],
  "overall_band": <number>,
  "cefr_level": "<A1/A2/B1/B2/C1/C2>",
  "feedback": "...",
  "priority_improvements": ["...", "..."],
  "transcript": "..."
}}
"""

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_data_uri = f"data:{audio_mime_type};base64,{audio_b64}"

    messages = [
        {
            "role": "system",
            "content": [
                {"text": "You are a certified English Speaking examiner. You respond only in valid JSON."}
            ],
        },
        {
            "role": "user",
            "content": [
                {"audio": audio_data_uri},
                {"text": prompt},
            ],
        },
    ]

    try:
        response = MultiModalConversation.call(
            model=DASHSCOPE_MODEL,
            messages=messages,
            timeout=120,
        )
    except Exception as e:
        raise RuntimeError(f"DashScope API call failed: {e}")

    if response.status_code != 200:
        raise RuntimeError(
            f"DashScope returned status {response.status_code}: "
            f"{getattr(response, 'message', str(response))}"
        )

    try:
        content = response.output.choices[0].message.content
        if isinstance(content, list):
            raw_text = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
        else:
            raw_text = str(content)
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        raise RuntimeError(f"Unexpected response structure from DashScope: {e}")

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                raise ValueError(f"LLM did not return valid JSON. Raw response:\n{raw_text}")
        else:
            raise ValueError(f"LLM did not return valid JSON. Raw response:\n{raw_text}")

    breakdown = parsed.get("breakdown", [])
    
    if breakdown and all("weight" in b for b in breakdown):
        total_weighted = sum(
            (item.get("score", 0) / item.get("max", 1)) * item.get("weight", 0)
            for item in breakdown
        )
        total_weight = sum(item.get("weight", 0) for item in breakdown)
        overall_score = (total_weighted / total_weight) * effective_max if total_weight > 0 else 0
    else:
        overall_score = sum(item.get("score", 0) for item in breakdown)

    if exam_type.upper() == "IELTS":
        overall_score = round(overall_score * 2) / 2
    else:
        overall_score = round(overall_score)

    return {
        "score": overall_score,
        "max_score": effective_max,
        "passing_score": effective_passing,
        "breakdown": breakdown,
        "feedback": parsed.get("feedback", ""),
        "overall_band": parsed.get("overall_band", overall_score),
        "cefr_level": parsed.get("cefr_level", ""),
        "priority_improvements": parsed.get("priority_improvements", []),
        "transcript": parsed.get("transcript", ""),
        "model_used": DASHSCOPE_MODEL,
    }