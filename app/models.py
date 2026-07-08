from sqlalchemy import Column, Integer, String, ForeignKey, Text, NUMERIC, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship
from app.utils.config import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.now)

class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    level = Column(String, index=True)
    description = Column(String)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)
    max_score = Column(Integer, default=100)
    exam = relationship("Exam", back_populates="questions")

Exam.questions = relationship("Question", order_by=Question.id, back_populates="exam")

class StudentResponse(Base):
    __tablename__ = "student_responses"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    text_content = Column(Text)
    audio_file_path = Column(String(255))
    submitted_at = Column(TIMESTAMP, default=datetime.now)

class LLMEvaluation(Base):
    __tablename__ = "llm_evaluations"
    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("student_responses.id", ondelete="CASCADE"), nullable=False)
    score = Column(NUMERIC(5, 2), nullable=False)
    approved = Column(Boolean, nullable=False)
    feedback = Column(Text)
    model_used = Column(String(50))
    evaluated_at = Column(TIMESTAMP, default=datetime.now)

StudentResponse.evaluations = relationship("LLMEvaluation", order_by=LLMEvaluation.id, back_populates="response")
LLMEvaluation.response = relationship("StudentResponse", back_populates="evaluations")