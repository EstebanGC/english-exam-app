import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from app.services.whisper_transcriber import TranscriptionResult


class SpeakingEvaluator:

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
        )
        self.model = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")

    def evaluate(self, question: str, transcription: TranscriptionResult, exam_type: str) -> Dict[str, Any]:
        prompt = self._build_evaluation_prompt(question, transcription, exam_type)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert IELTS/Cambridge English speaking examiner. "
                        "You evaluate spoken English responses. You have access to an ASR transcript "
                        "ENRICHED with fluency markers (pauses, fillers, repetitions, self-corrections). "
                        "IMPORTANT: This is NOT a perfect phonetic transcript. Infer pronunciation, "
                        "fluency, intonation, and rhythm based on the PATTERNS in the transcript, "
                        "not just the words themselves."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        result = json.loads(content)

        result["transcript"] = transcription.text
        result["audio_metrics"] = {
            "duration_seconds": transcription.duration_seconds,
            "word_count": transcription.word_count,
            "words_per_minute": transcription.words_per_minute,
            "fillers_count": transcription.fillers_count,
            "long_pauses_count": len(transcription.long_pauses),
            "repetitions_count": len(transcription.repetitions),
            "self_corrections_count": len(transcription.self_corrections)
        }

        return result

    def _build_evaluation_prompt(self, question, t, exam_type):
        pause_details = "\n".join(
            f"  - {p['between']}: {p['duration_seconds']}s gap"
            for p in t.long_pauses[:10]
        ) or "  - No significant long pauses detected"

        rep_details = "\n".join(
            f"  - '{r['word']}' repeated at {r['at']:.1f}s"
            for r in t.repetitions[:10]
        ) or "  - No repetitions detected"

        filler_words = {"um", "uh", "erm", "ah", "like", "you know", "i mean", "sort of", "kind of", "well", "so"}
        filler_details = "\n".join(
            f"  - '{f['word']}' at {f['start']:.1f}s"
            for f in t.words if f.get("word", "").strip().lower().rstrip(",.!?;") in filler_words
        ) or "  - No fillers detected"

        prompt = f"""## EXAM CONFIGURATION
Exam Type: {exam_type}
Question: {question}

## AUDIO METADATA
- Duration: {t.duration_seconds:.1f} seconds
- Word count: {t.word_count}
- Speaking rate: {t.words_per_minute:.1f} words per minute
- Language detected: {t.language}

## ENRICHED TRANSCRIPT (with fluency markers)