
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils import get_db
from app.models import Evaluation, User
from app.schemas import EvaluationRequest, EvaluationOut
from app.services.llm_evaluator import evaluate_response
from app.utils.auth import get_current_user

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationOut, status_code=status.HTTP_201_CREATED)
def evaluate_exam_response(payload: EvaluationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rubric_dict = payload.rubric.model_dump()

    try:
        result = evaluate_response(
            question_text=payload.question_text,
            student_answer=payload.student_answer,
            rubric=rubric_dict,
            max_score=payload.max_score,
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    score = result["score"]
    approved = score >= payload.passing_score

    db_evaluation = Evaluation(

        user_id=current_user.id,

        external_user_id=payload.external_user_id,
        external_exam_id=payload.external_exam_id,
        external_question_id=payload.external_question_id,
        external_response_id=payload.external_response_id,

        question_text=payload.question_text,
        student_answer=payload.student_answer,
        rubric=rubric_dict,
        max_score=payload.max_score,
        passing_score=payload.passing_score,

        score=score,
        approved=approved,
        feedback=result["feedback"],
        score_breakdown=result["breakdown"],
        model_used=result["model_used"],
        
        created_at=datetime.now(),
        evaluated_at=datetime.now(),
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)

    return db_evaluation