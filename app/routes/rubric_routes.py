from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.utils import get_db
from app.models import RubricTemplate
from app.schemas import RubricTemplateCreate, RubricTemplateOut

router = APIRouter(prefix="/rubric-templates", tags=["rubric-templates"])


@router.get("/", response_model=list[RubricTemplateOut])
def list_rubric_templates(db: Session = Depends(get_db)):
    return db.query(RubricTemplate).order_by(RubricTemplate.name).all()


@router.get("/{template_id}", response_model=RubricTemplateOut)
def get_rubric_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(RubricTemplate).filter(RubricTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric template not found")
    return template


@router.post("/", response_model=RubricTemplateOut, status_code=status.HTTP_201_CREATED)
def create_rubric_template(payload: RubricTemplateCreate, db: Session = Depends(get_db)):
    db_template = RubricTemplate(
        name=payload.name,
        description=payload.description,
        criteria=[c.model_dump() for c in payload.criteria],
        max_score=payload.max_score,
        passing_score=payload.passing_score,
        created_at=datetime.now(),
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rubric_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(RubricTemplate).filter(RubricTemplate.id == template_id).first()
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric template not found")
    db.delete(template)
    db.commit()
    return