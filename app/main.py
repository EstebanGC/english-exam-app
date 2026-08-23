from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.routes import auth_routes, evaluation_routes, history, rubric_routes, speaking_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://enlgish-exam-client-lilac.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(evaluation_routes.router)
app.include_router(history_routes.router)
app.include_router(rubric_routes.router)
app.include_router(speaking_routes.router)


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Welcome to the English Exam Evaluation API"
