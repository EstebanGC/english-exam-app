from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils import get_db
from app.models import Exam, Question
from app.schemas import ExamCreate, ExamUpdate, ExamOut, ExamsResponse

router = APIRouter()


@router.get("/exams/", response_model=ExamsResponse)
def read_exams(db: Session = Depends(get_db)):
    exams = db.query(Exam).all()
    return {"exams": exams}  # FastAPI convierte cada Exam a ExamOut automáticamente


@router.post("/exams/", status_code=status.HTTP_201_CREATED, response_model=ExamOut)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    db_exam = Exam(**exam.model_dump())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam


@router.get("/exams/{exam_id}", response_model=ExamOut)
def read_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam


@router.put("/exams/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, exam: ExamUpdate, db: Session = Depends(get_db)):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    update_data = exam.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_exam, key, value)

    db.commit()
    db.refresh(db_exam)
    return db_exam


@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    db.delete(db_exam)
    db.commit()
    return