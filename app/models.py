# app/models.py
from sqlalchemy import Column, Integer, String, Text, NUMERIC, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from app.utils.config import Base


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)

    external_user_id = Column(String(100), index=True, nullable=True)
    external_exam_id = Column(String(100), index=True, nullable=True)
    external_question_id = Column(String(100), index=True, nullable=True)
    external_response_id = Column(String(100), index=True, nullable=True)

    question_text = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    rubric = Column(JSONB, nullable=False)
    max_score = Column(Integer, nullable=False, default=100)
    passing_score = Column(Integer, nullable=False, default=60)

    score = Column(NUMERIC(5, 2), nullable=True)
    approved = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    score_breakdown = Column(JSONB, nullable=True)
    model_used = Column(String(50), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    evaluated_at = Column(TIMESTAMP(timezone=True), nullable=True)