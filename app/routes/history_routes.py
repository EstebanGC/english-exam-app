from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.utils import get_db
from app.models import Evaluation, SpeakingEvaluation, User
from app.schemas import EvaluationHistoryItem, SpeakingEvaluationHistoryItem, HistorySummary
from app.utils.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/evaluations", response_model=List[EvaluationHistoryItem])
def get_evaluation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated user's written-response evaluation history,
    most recent first.
    """
    return (
        db.query(Evaluation)
        .filter(Evaluation.user_id == current_user.id)
        .order_by(Evaluation.created_at.desc())
        .all()
    )


@router.get("/speaking", response_model=List[SpeakingEvaluationHistoryItem])
def get_speaking_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated user's speaking evaluation history,
    most recent first.
    """
    return (
        db.query(SpeakingEvaluation)
        .filter(SpeakingEvaluation.user_id == current_user.id)
        .order_by(SpeakingEvaluation.created_at.desc())
        .all()
    )


@router.get("/summary", response_model=HistorySummary)
def get_history_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Quick stats for a progress dashboard: totals and averages.
    """
    eval_count = db.query(func.count(Evaluation.id)).filter(
        Evaluation.user_id == current_user.id
    ).scalar() or 0

    eval_avg = db.query(func.avg(Evaluation.score)).filter(
        Evaluation.user_id == current_user.id
    ).scalar()

    speaking_count = db.query(func.count(SpeakingEvaluation.id)).filter(
        SpeakingEvaluation.user_id == current_user.id
    ).scalar() or 0

    speaking_avg = db.query(func.avg(SpeakingEvaluation.overall_score)).filter(
        SpeakingEvaluation.user_id == current_user.id
    ).scalar()

    return HistorySummary(
        total_evaluations=eval_count,
        total_speaking_evaluations=speaking_count,
        average_score=round(float(eval_avg), 2) if eval_avg is not None else None,
        average_speaking_score=round(float(speaking_avg), 2) if speaking_avg is not None else None,
    )