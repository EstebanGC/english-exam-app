from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RubricCriterion(BaseModel):
    name: str
    weight: int
    description: Optional[str] = None


class Rubric(BaseModel):
    criteria: List[RubricCriterion]


class EvaluationRequest(BaseModel):
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    question_text: str
    student_answer: str
    rubric: Rubric
    max_score: int = 100
    passing_score: int = 60


class CriterionResult(BaseModel):
    criterion: str
    score: float
    max: float
    comment: Optional[str] = None


class EvaluationOut(BaseModel):
    id: int
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    score: float
    approved: bool
    feedback: Optional[str] = None
    score_breakdown: Optional[List[CriterionResult]] = None
    model_used: Optional[str] = None
    evaluated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)