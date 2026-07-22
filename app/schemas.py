from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RubricCriterion(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    weight: int = Field(..., gt=0, le=100)
    description: Optional[str] = None


class Rubric(BaseModel):
    criteria: List[RubricCriterion] = Field(..., min_length=1)


class EvaluationRequest(BaseModel):
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    question_text: str = Field(..., min_length=10, max_length=5000)
    student_answer: str = Field(..., min_length=10, max_length=10000)
    rubric: Rubric
    max_score: int = Field(default=100, gt=0)
    passing_score: int = Field(default=60, ge=0)


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

class RubricTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    criteria: List[RubricCriterion] = Field(..., min_length=1)
    max_score: int = Field(default=100, gt=0)
    passing_score: int = Field(default=60, ge=0)


class RubricTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    criteria: List[RubricCriterion]
    max_score: int
    passing_score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)