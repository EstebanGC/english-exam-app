from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.utils import get_db
from app.models import SpeakingEvaluation
from app.schemas import SpeakingEvaluationOut
from app.services.whisper_transcriber import WhisperTranscriber
from app.services.speaking_evaluator import SpeakingEvaluator
from app.services.speaking_evaluator import evaluate_speaking
from app.services.exam_rubrics import get_rubric
import json

router = APIRouter()

MAX_AUDIO_BYTES = 20 * 1024 * 1024


@router.post("/evaluate-speaking", response_model=SpeakingEvaluationOut, status_code=status.HTTP_201_CREATED)
async def evaluate_speaking_response(
    audio: UploadFile = File(..., description="Audio file of the student's spoken response"),
    exam_type: str = Form(..., description="KET, FCE, IELTS, or CUSTOM"),
    question_text: str = Form(..., min_length=10, max_length=5000),
    external_user_id: Optional[str] = Form(None),
    external_exam_id: Optional[str] = Form(None),
    external_question_id: Optional[str] = Form(None),
    external_response_id: Optional[str] = Form(None),
    custom_rubric: Optional[str] = Form(None, description="JSON string with criteria (only for CUSTOM)"),
    max_score: Optional[float] = Form(None),
    passing_score: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    exam_type_upper = exam_type.upper()
    if exam_type_upper not in {"KET", "FCE", "IELTS", "CUSTOM"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exam_type must be one of: KET, FCE, IELTS, CUSTOM"
        )

    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file exceeds {MAX_AUDIO_BYTES // (1024*1024)} MB limit"
        )

    rubric = get_rubric(exam_type_upper)
    if rubric:
        rubric_dict = rubric
        effective_max = rubric["max_score"]
        effective_passing = rubric["passing_score"]
    else:
        if not custom_rubric:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_rubric is required when exam_type is CUSTOM"
            )
        try:
            rubric_dict = json.loads(custom_rubric)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_rubric must be valid JSON"
            )
        effective_max = max_score or 100
        effective_passing = passing_score or (effective_max * 0.6)

    try:
        result = evaluate_speaking(
            audio_bytes=audio_bytes,
            audio_mime_type=audio.content_type or "audio/wav",
            question_text=question_text,
            exam_type=exam_type_upper,
            max_score=effective_max if exam_type_upper == "CUSTOM" else None,
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    overall_score = result["score"]
    approved = overall_score >= result["passing_score"]

    db_eval = SpeakingEvaluation(
        external_user_id=external_user_id,
        external_exam_id=external_exam_id,
        external_question_id=external_question_id,
        external_response_id=external_response_id,
        exam_type=exam_type_upper,
        question_text=question_text,
        audio_data=audio_bytes,
        audio_mime_type=audio.content_type,
        rubric=rubric_dict,
        max_score=result["max_score"],
        passing_score=result["passing_score"],
        overall_score=overall_score,
        overall_band=str(result.get("overall_band", overall_score)),
        cefr_level=result.get("cefr_level", ""),
        approved=approved,
        feedback=result.get("feedback", ""),
        score_breakdown=result.get("breakdown", []),
        transcript=result.get("transcript", ""),
        priority_improvements=result.get("priority_improvements", []),
        model_used=result.get("model_used", ""),
        created_at=datetime.now(),
        evaluated_at=datetime.now(),
    )
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)

    return db_eval
