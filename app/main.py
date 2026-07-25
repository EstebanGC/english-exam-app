from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.routes import evaluation_routes, rubric_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "enlgish-exam-client-8xori9dav-english-evaluator-exam.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(evaluation_routes.router)
app.include_router(rubric_routes.router)


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Welcome to the English Exam Evaluation API"