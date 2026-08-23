from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Authentication
# ============================================================

class UserRegister(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = Field(None, max_length=150)


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class RubricCriterion(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    weight: int = Field(..., gt=0, le=100)
    description: Optional[str] = None


class Rubric(BaseModel):
    criteria: List[RubricCriterion] = Field(..., min_length=1)


class CriterionResult(BaseModel):
    criterion: str
    score: float
    max: float
    comment: Optional[str] = None


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


class SpeakingEvaluationOut(BaseModel):
    id: int
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    exam_type: str
    question_text: str
    overall_score: float
    overall_band: Optional[str] = None
    cefr_level: Optional[str] = None
    approved: bool
    feedback: Optional[str] = None
    score_breakdown: Optional[List[CriterionResult]] = None
    transcript: Optional[str] = None
    priority_improvements: Optional[List[str]] = None
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

class EvaluationHistoryItem(BaseModel):
    id: int
    question_text: str
    score: float
    max_score: int
    passing_score: int
    approved: bool
    model_used: Optional[str] = None
    evaluated_at: Optional[datetime] = None
 
    model_config = ConfigDict(from_attributes=True)
 
 
class SpeakingEvaluationHistoryItem(BaseModel):
    id: int
    exam_type: str
    question: str
    overall_score: float
    band: Optional[str] = None
    cefr_level: Optional[str] = None
    passed: bool
    created_at: Optional[datetime] = None
 
    model_config = ConfigDict(from_attributes=True)
 
 
class HistorySummary(BaseModel):
    total_evaluations: int
    total_speaking_evaluations: int
    average_score: Optional[float] = None
    average_speaking_score: Optional[float] = None