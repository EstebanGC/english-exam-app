import os
import tempfile
from typing import List, Dict, Any
from dataclasses import dataclass, field
from openai import OpenAI


@dataclass
class TranscriptionResult:
    text: str
    words: List[Dict[str, Any]] = field(default_factory=list)
    segments: List[Dict[str, Any]] = field(default_factory=list)
    word_count: int = 0
    duration_seconds: float = 0.0
    fillers_count: int = 0
    repetitions: List[Dict[str, Any]] = field(default_factory=list)
    long_pauses: List[Dict[str, Any]] = field(default_factory=list)
    self_corrections: List[Dict[str, Any]] = field(default_factory=list)
    words_per_minute: float = 0.0
    language: str = "en"


class WhisperTranscriber:
    """
    Transcriptor basado en Groq Whisper (OpenAI-compatible).
    Modelos: whisper-large-v3, whisper-large-v3-turbo
    """

    FILLERS = {"um", "uh", "erm", "ah", "like", "you know", "i mean", "sort of", "kind of", "well", "so"}
    PAUSE_THRESHOLD_SECONDS = 1.5

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = os.getenv("WHISPER_MODEL", "whisper-large-v3-turbo")

    async def transcribe(self, audio_bytes: bytes, filename: str = "audio.webm") -> TranscriptionResult:
        suffix = os.path.splitext(filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    file=(filename, audio_file),
                    model=self.model,
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"],
                    language="en",
                    temperature=0.0,
                )
        finally:
            os.unlink(tmp_path)

        text = response.text or ""

        # Convertir objetos Pydantic a diccionarios puros
        words_raw = getattr(response, "words", []) or []
        segments_raw = getattr(response, "segments", []) or []

        words = [self._to_dict(w) for w in words_raw]
        segments = [self._to_dict(s) for s in segments_raw]

        duration = self._calculate_duration(words, segments)
        word_count = len(words)
        wpm = (word_count / duration * 60) if duration > 0 else 0

        fillers = self._detect_fillers(words)
        repetitions = self._detect_repetitions(words)
        pauses = self._detect_long_pauses(words)
        corrections = self._detect_self_corrections(words, text)

        return TranscriptionResult(
            text=text,
            words=words,
            segments=segments,
            word_count=word_count,
            duration_seconds=duration,
            fillers_count=len(fillers),
            repetitions=repetitions,
            long_pauses=pauses,
            self_corrections=corrections,
            words_per_minute=round(wpm, 1),
            language="en"
        )

    def _to_dict(self, obj) -> dict:
        """Convierte objeto Pydantic/BaseModel a dict."""
        if isinstance(obj, dict):
            return obj
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("_") and not callable(getattr(obj, k))}

    def _calculate_duration(self, words, segments):
        if words:
            return max(w.get("end", 0) for w in words)
        if segments:
            return max(s.get("end", 0) for s in segments)
        return 0.0

    def _detect_fillers(self, words):
        fillers = []
        for w in words:
            word_text = w.get("word", "").strip().lower().rstrip(",.!?;")
            if word_text in self.FILLERS:
                fillers.append({"word": word_text, "start": w.get("start"), "end": w.get("end")})
        return fillers

    def _detect_repetitions(self, words):
        reps = []
        for i in range(1, len(words)):
            prev = words[i-1].get("word", "").strip().lower().rstrip(",.!?;")
            curr = words[i].get("word", "").strip().lower().rstrip(",.!?;")
            if prev == curr and len(prev) > 2:
                reps.append({"word": curr, "at": words[i].get("start")})
        return reps

    def _detect_long_pauses(self, words):
        pauses = []
        for i in range(1, len(words)):
            gap = words[i].get("start", 0) - words[i-1].get("end", 0)
            if gap > self.PAUSE_THRESHOLD_SECONDS:
                pauses.append({
                    "between": f"{words[i-1].get('word')} -> {words[i].get('word')}",
                    "start": words[i-1].get("end"),
                    "end": words[i].get("start"),
                    "duration_seconds": round(gap, 2)
                })
        return pauses

    def _detect_self_corrections(self, words, full_text):
        corrections = []
        patterns = ["- ", " i mean ", " rather ", " actually ", " sorry ", " wait "]
        text_lower = full_text.lower()
        for pat in patterns:
            idx = text_lower.find(pat)
            if idx != -1:
                start = max(0, idx - 30)
                end = min(len(full_text), idx + 30)
                corrections.append({"pattern": pat.strip(), "context": full_text[start:end]})
        for i in range(len(words) - 1):
            w1 = words[i].get("word", "").strip()
            w2 = words[i+1].get("word", "").strip()
            if w1.endswith("-") or (len(w1) > 3 and w2.startswith(w1[:-1]) and w1 != w2):
                corrections.append({"pattern": "truncation", "from": w1, "to": w2, "at": words[i].get("start")})
        return corrections