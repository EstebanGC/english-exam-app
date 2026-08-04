# app/services/speaking_evaluator.py
import os
import json
import tempfile
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from app.services.exam_rubrics import get_rubric, build_rubric_prompt

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def evaluate_speaking(
    audio_bytes: bytes,
    audio_mime_type: str,
    question_text: str,
    exam_type: str,
    max_score: Optional[float] = None,
) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=GEMINI_API_KEY)

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

    # Determine file extension from mime type
    ext_map = {
        "audio/webm": ".webm",
        "audio/mp4": ".mp4",
        "audio/wav": ".wav",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
    }
    ext = ext_map.get(audio_mime_type, ".webm")

    # Write to temp file for Gemini upload
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # Upload file to Gemini
        audio_file = genai.upload_file(path=tmp_path, mime_type=audio_mime_type)

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )

        response = model.generate_content([
            "You are a certified English Speaking examiner. Respond only in valid JSON.",
            audio_file,
            prompt,
        ])

        raw_text = response.text

    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Parse JSON
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
        "model_used": GEMINI_MODEL,
    }