from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import UserOut
from app.utils.config import get_db
from app.routes import exam_routes
from app.utils.auth_utils import get_current_user

app = FastAPI()

# Include routes
app.include_router(exam_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the English Exam Evaluation API"}

@app.get("/users/me/", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user