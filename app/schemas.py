from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class ExamCreate(BaseModel):
    title: str
    level: str
    description: str

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None

class ExamOut(BaseModel):
    id: int
    title: str
    level: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class ExamResponse(BaseModel):
    exam: ExamOut

class ExamsResponse(BaseModel):
    exams: List[ExamOut]  