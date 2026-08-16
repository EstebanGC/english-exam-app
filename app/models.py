from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    NUMERIC,
    Boolean,
    TIMESTAMP,
    LargeBinary,
    Float,
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from app.utils.config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    name = Column(
        String(150),
        nullable=True
    )

    role = Column(
        String(30),
        nullable=False,
        default="student"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)

    # User authenticated in our platform
    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    # References to external systems
    external_user_id = Column(String(100), index=True, nullable=True)
    external_exam_id = Column(String(100), index=True, nullable=True)
    external_question_id = Column(String(100), index=True, nullable=True)
    external_response_id = Column(String(100), index=True, nullable=True)

    question_text = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)

    rubric = Column(JSONB, nullable=False)

    max_score = Column(
        Integer,
        nullable=False,
        default=100
    )

    passing_score = Column(
        Integer,
        nullable=False,
        default=60
    )

    score = Column(
        NUMERIC(5, 2),
        nullable=True
    )

    approved = Column(
        Boolean,
        nullable=True
    )

    feedback = Column(
        Text,
        nullable=True
    )

    score_breakdown = Column(
        JSONB,
        nullable=True
    )

    model_used = Column(
        String(50),
        nullable=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )

    evaluated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True
    )


class RubricTemplate(Base):
    __tablename__ = "rubric_templates"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(150),
        nullable=False,
        index=True
    )

    description = Column(
        Text,
        nullable=True
    )

    criteria = Column(
        JSONB,
        nullable=False
    )

    max_score = Column(
        Integer,
        nullable=False,
        default=100
    )

    passing_score = Column(
        Integer,
        nullable=False,
        default=60
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )


class SpeakingEvaluation(Base):
    __tablename__ = "speaking_evaluations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Authenticated platform user
    user_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    # External/student identifier
    student_id = Column(
        String(100),
        nullable=True
    )

    exam_type = Column(
        String(20),
        nullable=False
    )

    question = Column(
        Text,
        nullable=False
    )

    audio_data = Column(
        LargeBinary,
        nullable=False
    )

    audio_filename = Column(
        String(255),
        nullable=True
    )

    transcript = Column(
        Text,
        nullable=True
    )

    overall_score = Column(
        Float,
        nullable=True
    )

    band = Column(
        String(50),
        nullable=True
    )

    cefr_level = Column(
        String(10),
        nullable=True
    )

    passed = Column(
        Boolean,
        default=False
    )

    criteria_breakdown = Column(
        JSONB,
        nullable=True
    )

    priority_improvements = Column(
        JSONB,
        nullable=True
    )

    detailed_feedback = Column(
        Text,
        nullable=True
    )

    audio_metrics = Column(
        JSONB,
        nullable=True
    )

    pronunciation_inference = Column(
        Text,
        nullable=True
    )

    fluency_notes = Column(
        Text,
        nullable=True
    )

    intonation_notes = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )