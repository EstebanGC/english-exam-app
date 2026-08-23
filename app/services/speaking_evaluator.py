import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from app.services.whisper_transcriber import TranscriptionResult


class SpeakingEvaluator:
    """
    Hybrid evaluator: Whisper (Groq) para STT + LLM (Groq) for evaluation.
    """

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
            max_tokens=4000,
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

        # Construir prompt sin f-string triple problemático
        lines = []
        lines.append("## EXAM CONFIGURATION")
        lines.append(f"Exam Type: {exam_type}")
        lines.append(f"Question: {question}")
        lines.append("")
        lines.append("## AUDIO METADATA")
        lines.append(f"- Duration: {t.duration_seconds:.1f} seconds")
        lines.append(f"- Word count: {t.word_count}")
        lines.append(f"- Speaking rate: {t.words_per_minute:.1f} words per minute")
        lines.append(f"- Language detected: {t.language}")
        lines.append("")
        lines.append("## ENRICHED TRANSCRIPT (with fluency markers)")
        lines.append("```")
        lines.append(t.text)
        lines.append("```")
        lines.append("")
        lines.append("## FLUENCY PATTERN ANALYSIS")
        lines.append("### Long Pauses (>1.5s)")
        lines.append(pause_details)
        lines.append("")
        lines.append("### Repetitions")
        lines.append(rep_details)
        lines.append("")
        lines.append("### Fillers / Hesitation Markers")
        lines.append(filler_details)
        lines.append("")
        lines.append(f"### Self-Corrections / Restarts")
        lines.append(f"{len(t.self_corrections)} instance(s) detected")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## INSTRUCTIONS")
        lines.append(f"Evaluate this speaking response using the {exam_type} rubric.")
        lines.append("")
        lines.append("**CRITICAL INFERENCE RULES** (because we only have ASR text, not native audio):")
        lines.append("1. **Pronunciation**: Infer from words that seem mis-transcribed, truncated, or where the speaker may have struggled.")
        lines.append("2. **Fluency & Coherence**: Use the pause/repetition/filler data directly. Many pauses = lower fluency.")
        lines.append("3. **Intonation & Rhythm**: Infer from punctuation usage, question structures, and emphasis words.")
        lines.append("4. **Grammar & Vocabulary**: Assess from transcript text quality, but be lenient with spoken English slips.")
        lines.append("5. **Task Response**: Did the speaker answer directly? Did they expand appropriately?")
        lines.append("")
        lines.append("**VOCABULARY UPGRADE RULE**:")
        lines.append("Scan the transcript for basic, repetitive, informal, or vague words/phrases the speaker leaned on")
        lines.append("(e.g. 'good', 'bad', 'nice', 'very [adjective]', 'a lot of', 'stuff', 'things', 'said').")
        lines.append("For each one, suggest a more precise, higher-register alternative that fits the exam context,")
        lines.append("and briefly explain why it's stronger. Pick 3-6 of the most impactful swaps — don't list minor filler words.")
        lines.append("Only suggest words that actually appear in the transcript; never invent words the speaker didn't say.")
        lines.append("")
        lines.append("## OUTPUT FORMAT (JSON)")
        lines.append("Return ONLY a JSON object with this exact structure:")
        lines.append("")
        lines.append('{')
        lines.append('  "overall_score": <number>,')
        lines.append('  "band": "<band descriptor>",')
        lines.append('  "cefr_level": "<A1/A2/B1/B2/C1/C2>",')
        lines.append('  "passed": <true/false>,')
        lines.append('  "transcript": "<the transcript text>",')
        lines.append('  "criteria_breakdown": [')
        lines.append('    {')
        lines.append('      "criterion": "<name>",')
        lines.append('      "score": <number>,')
        lines.append('      "max_score": <number>,')
        lines.append('      "weight": <percentage>,')
        lines.append('      "feedback": "<specific feedback>"')
        lines.append('    }')
        lines.append('  ],')
        lines.append('  "vocabulary_suggestions": [')
        lines.append('    {')
        lines.append('      "used": "<word or phrase the speaker actually used>",')
        lines.append('      "suggestion": "<a stronger, more precise alternative>",')
        lines.append('      "reason": "<short explanation of why it sounds more natural/professional>"')
        lines.append('    }')
        lines.append('  ],')
        lines.append('  "priority_improvements": ["<area 1>", "<area 2>", "<area 3>"],')
        lines.append('  "detailed_feedback": "<2-3 paragraphs>",')
        lines.append('  "pronunciation_inference": "<inferred pronunciation notes>",')
        lines.append('  "fluency_notes": "<specific notes on flow, pauses, hesitations>",')
        lines.append('  "intonation_notes": "<inferred intonation and stress patterns>"')
        lines.append('}')
        lines.append("")

        lines.append(f"### Band/Score mapping for {exam_type}:")
        lines.append("")

        if exam_type.upper() == "IELTS":
            lines.append("- Band 9: Expert user (C2) - score 9.0")
            lines.append("- Band 8: Very good user (C1) - score 8.0")
            lines.append("- Band 7: Good user (B2) - score 7.0")
            lines.append("- Band 6: Competent user (B2-) - score 6.0")
            lines.append("- Band 5: Modest user (B1) - score 5.0")
            lines.append("- Band 4: Limited user (A2+) - score 4.0")
            lines.append("- Band 3: Extremely limited (A2) - score 3.0")
            lines.append("- overall_score: 0.0-9.0 (can use .5 increments)")
        elif exam_type.upper() == "FCE":
            lines.append("- Grade A (C1): score 5.0")
            lines.append("- Grade B (B2+): score 4.0")
            lines.append("- Grade C (B2): score 3.0")
            lines.append("- Borderline (B1+): score 2.0")
            lines.append("- Weak (B1): score 1.0")
            lines.append("- overall_score: 1-5")
        elif exam_type.upper() == "KET":
            lines.append("- Distinction (A2+): score 5.0")
            lines.append("- Pass (A2): score 4.0")
            lines.append("- Borderline (A2-): score 3.0")
            lines.append("- Weak (A1+): score 2.0")
            lines.append("- Very weak (A1): score 1.0")
            lines.append("- overall_score: 1-5")

        lines.append("")
        lines.append(f"### Criteria for {exam_type.upper()}:")
        lines.append("")

        if exam_type.upper() == "IELTS":
            lines.append("1. Fluency & Coherence (25%): continuity, logical sequencing, connectors, development")
            lines.append("2. Lexical Resource (25%): vocabulary range, precision, paraphrasing, collocations")
            lines.append("3. Grammatical Range & Accuracy (25%): simple and complex structures, error frequency")
            lines.append("4. Pronunciation (25%): phonological features, stress, intonation, intelligibility")
        elif exam_type.upper() == "FCE":
            lines.append("1. Grammar & Vocabulary (25%): complex structures, collocations, accuracy")
            lines.append("2. Discourse Management (25%): coherence, cohesion, discourse markers")
            lines.append("3. Pronunciation (25%): stress, intonation, rhythm, intelligibility")
            lines.append("4. Interactive Communication (15%): turn-taking, initiation, response")
            lines.append("5. Global Achievement (10%): overall communicative effectiveness")
        elif exam_type.upper() == "KET":
            lines.append("1. Pronunciation (20%): phonemes, stress, intonation, intelligibility")
            lines.append("2. Fluency (20%): flow, hesitation, pausing")
            lines.append("3. Vocabulary (20%): range and precision")
            lines.append("4. Grammar (20%): simple tenses, basic connectors")
            lines.append("5. Interaction/Response (10%): direct answers, expansion")
            lines.append("6. Task Achievement (10%): task completion")

        lines.append("")
        lines.append("Evaluate now and return ONLY the JSON object.")

        return "\n".join(lines)