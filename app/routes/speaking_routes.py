import os
import json
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.utils import get_db
from app.models import SpeakingEvaluation
from app.schemas import SpeakingEvaluationOut, CriterionResult
from app.services.whisper_transcriber import WhisperTranscriber
from app.services.speaking_evaluator import SpeakingEvaluator

router = APIRouter(prefix="/evaluate-speaking", tags=["speaking"])


def _normalize_criterion(c: dict) -> dict:
    """Normaliza campos del LLM: max -> max_score si es necesario."""
    if "max" in c and "max_score" not in c:
        c["max_score"] = c.pop("max")
    return c


@router.post("", response_model=SpeakingEvaluationOut)
async def evaluate_speaking(
    audio: UploadFile = File(..., description="Audio file (webm, mp3, wav, etc.)"),
    question: str = Form(..., description="Exam question/prompt"),
    exam_type: str = Form(..., description="Exam type: KET, FCE, or IELTS"),
    student_id: Optional[str] = Form(None, description="Optional student identifier"),
    db: Session = Depends(get_db)
):
    exam_type = exam_type.upper().strip()
    if exam_type not in {"KET", "FCE", "IELTS"}:
        raise HTTPException(status_code=400, detail="Invalid exam_type. Must be one of: KET, FCE, IELTS")

    audio_bytes = await audio.read()
    if len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small or empty")

    max_size = 25 * 1024 * 1024
    if len(audio_bytes) > max_size:
        raise HTTPException(status_code=400, detail=f"Audio file too large: {len(audio_bytes)/(1024*1024):.1f}MB. Max: 25MB")

    try:
        transcriber = WhisperTranscriber()
        transcription = await transcriber.transcribe(audio_bytes, filename=audio.filename)

        if not transcription.text or transcription.text.strip() == "":
            raise HTTPException(status_code=400, detail="Could not transcribe audio. Please speak clearly and try again.")

        evaluator = SpeakingEvaluator()
        evaluation = evaluator.evaluate(question=question, transcription=transcription, exam_type=exam_type)

        raw_breakdown = evaluation.get("criteria_breakdown", [])
        normalized_breakdown = [_normalize_criterion(c) for c in raw_breakdown]

        db_eval = SpeakingEvaluation(
            student_id=student_id,
            exam_type=exam_type,
            question=question,
            audio_data=audio_bytes,
            audio_filename=audio.filename,
            transcript=transcription.text,
            overall_score=evaluation.get("overall_score", 0),
            band=evaluation.get("band", ""),
            cefr_level=evaluation.get("cefr_level", ""),
            passed=evaluation.get("passed", False),
            criteria_breakdown=json.dumps(normalized_breakdown),
            priority_improvements=json.dumps(evaluation.get("priority_improvements", [])),
            detailed_feedback=evaluation.get("detailed_feedback", ""),
            audio_metrics=json.dumps(evaluation.get("audio_metrics", {})),
            pronunciation_inference=evaluation.get("pronunciation_inference", ""),
            fluency_notes=evaluation.get("fluency_notes", ""),
            intonation_notes=evaluation.get("intonation_notes", "")
        )

        db.add(db_eval)
        db.commit()
        db.refresh(db_eval)

        return SpeakingEvaluationOut(
            id=db_eval.id,
            student_id=db_eval.student_id,
            exam_type=db_eval.exam_type,
            question=db_eval.question,
            transcript=db_eval.transcript,
            overall_score=db_eval.overall_score,
            band=db_eval.band,
            cefr_level=db_eval.cefr_level,
            passed=db_eval.passed,
            criteria_breakdown=[CriterionResult(**c) for c in json.loads(db_eval.criteria_breakdown)],
            priority_improvements=json.loads(db_eval.priority_improvements),
            detailed_feedback=db_eval.detailed_feedback,
            audio_metrics=json.loads(db_eval.audio_metrics),
            pronunciation_inference=db_eval.pronunciation_inference,
            fluency_notes=db_eval.fluency_notes,
            intonation_notes=db_eval.intonation_notes,
            created_at=db_eval.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")