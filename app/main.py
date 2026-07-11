from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from app.routes import evaluation_routes

app = FastAPI()

# Include routes
app.include_router(evaluation_routes.router)


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Welcome to the English Exam Evaluation API"