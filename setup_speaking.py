# setup_speaking.py
# Run: python setup_speaking.py
# This script auto-generates all backend files for the speaking evaluator feature.

import os

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "app/models.py": '''from sqlalchemy import Column, Integer, String, Text, NUMERIC, Boolean, TIMESTAMP, LargeBinary
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


class RubricTemplate(Base):
    __tablename__ = "rubric_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    description = Column(Text, nullable=True)
    criteria = Column(JSONB, nullable=False)
    max_score = Column(Integer, nullable=False, default=100)
    passing_score = Column(Integer, nullable=False, default=60)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False)


class SpeakingEvaluation(Base):
    __tablename__ = "speaking_evaluations"

    id = Column(Integer, primary_key=True, index=True)

    external_user_id = Column(String(100), index=True, nullable=True)
    external_exam_id = Column(String(100), index=True, nullable=True)
    external_question_id = Column(String(100), index=True, nullable=True)
    external_response_id = Column(String(100), index=True, nullable=True)

    exam_type = Column(String(20), nullable=False)
    question_text = Column(Text, nullable=False)
    audio_data = Column(LargeBinary, nullable=True)
    audio_mime_type = Column(String(50), nullable=True)

    rubric = Column(JSONB, nullable=False)
    max_score = Column(NUMERIC(5, 2), nullable=False, default=100)
    passing_score = Column(NUMERIC(5, 2), nullable=False, default=60)

    overall_score = Column(NUMERIC(5, 2), nullable=True)
    overall_band = Column(String(10), nullable=True)
    cefr_level = Column(String(5), nullable=True)
    approved = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    score_breakdown = Column(JSONB, nullable=True)
    transcript = Column(Text, nullable=True)
    priority_improvements = Column(JSONB, nullable=True)
    model_used = Column(String(50), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False)
    evaluated_at = Column(TIMESTAMP(timezone=True), nullable=True)
''',

    "app/schemas.py": '''from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class RubricCriterion(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    weight: int = Field(..., gt=0, le=100)
    description: Optional[str] = None


class Rubric(BaseModel):
    criteria: List[RubricCriterion] = Field(..., min_length=1)


class CriterionResult(BaseModel):
    criterion: str
    score: float
    max: float
    comment: Optional[str] = None


class EvaluationRequest(BaseModel):
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    question_text: str = Field(..., min_length=10, max_length=5000)
    student_answer: str = Field(..., min_length=10, max_length=10000)
    rubric: Rubric
    max_score: int = Field(default=100, gt=0)
    passing_score: int = Field(default=60, ge=0)


class EvaluationOut(BaseModel):
    id: int
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    score: float
    approved: bool
    feedback: Optional[str] = None
    score_breakdown: Optional[List[CriterionResult]] = None
    model_used: Optional[str] = None
    evaluated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SpeakingEvaluationOut(BaseModel):
    id: int
    external_user_id: Optional[str] = None
    external_exam_id: Optional[str] = None
    external_question_id: Optional[str] = None
    external_response_id: Optional[str] = None
    exam_type: str
    question_text: str
    overall_score: float
    overall_band: Optional[str] = None
    cefr_level: Optional[str] = None
    approved: bool
    feedback: Optional[str] = None
    score_breakdown: Optional[List[CriterionResult]] = None
    transcript: Optional[str] = None
    priority_improvements: Optional[List[str]] = None
    model_used: Optional[str] = None
    evaluated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RubricTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    criteria: List[RubricCriterion] = Field(..., min_length=1)
    max_score: int = Field(default=100, gt=0)
    passing_score: int = Field(default=60, ge=0)


class RubricTemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    criteria: List[RubricCriterion]
    max_score: int
    passing_score: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
''',

    "app/main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from app.routes import evaluation_routes, rubric_routes, speaking_routes

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

app.include_router(evaluation_routes.router)
app.include_router(rubric_routes.router)
app.include_router(speaking_routes.router)


@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Welcome to the English Exam Evaluation API"
''',

    "app/routes/speaking_routes.py": '''from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.utils import get_db
from app.models import SpeakingEvaluation
from app.schemas import SpeakingEvaluationOut
from app.services.speaking_evaluator import evaluate_speaking
from app.services.exam_rubrics import get_rubric
import json

router = APIRouter()

MAX_AUDIO_BYTES = 20 * 1024 * 1024


@router.post("/evaluate-speaking", response_model=SpeakingEvaluationOut, status_code=status.HTTP_201_CREATED)
async def evaluate_speaking_response(
    audio: UploadFile = File(..., description="Audio file of the student's spoken response"),
    exam_type: str = Form(..., description="KET, FCE, IELTS, or CUSTOM"),
    question_text: str = Form(..., min_length=10, max_length=5000),
    external_user_id: Optional[str] = Form(None),
    external_exam_id: Optional[str] = Form(None),
    external_question_id: Optional[str] = Form(None),
    external_response_id: Optional[str] = Form(None),
    custom_rubric: Optional[str] = Form(None, description="JSON string with criteria (only for CUSTOM)"),
    max_score: Optional[float] = Form(None),
    passing_score: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    exam_type_upper = exam_type.upper()
    if exam_type_upper not in {"KET", "FCE", "IELTS", "CUSTOM"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exam_type must be one of: KET, FCE, IELTS, CUSTOM"
        )

    audio_bytes = await audio.read()
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file exceeds {MAX_AUDIO_BYTES // (1024*1024)} MB limit"
        )

    rubric = get_rubric(exam_type_upper)
    if rubric:
        rubric_dict = rubric
        effective_max = rubric["max_score"]
        effective_passing = rubric["passing_score"]
    else:
        if not custom_rubric:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_rubric is required when exam_type is CUSTOM"
            )
        try:
            rubric_dict = json.loads(custom_rubric)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="custom_rubric must be valid JSON"
            )
        effective_max = max_score or 100
        effective_passing = passing_score or (effective_max * 0.6)

    try:
        result = evaluate_speaking(
            audio_bytes=audio_bytes,
            audio_mime_type=audio.content_type or "audio/wav",
            question_text=question_text,
            exam_type=exam_type_upper,
            max_score=effective_max if exam_type_upper == "CUSTOM" else None,
        )
    except (RuntimeError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    overall_score = result["score"]
    approved = overall_score >= result["passing_score"]

    db_eval = SpeakingEvaluation(
        external_user_id=external_user_id,
        external_exam_id=external_exam_id,
        external_question_id=external_question_id,
        external_response_id=external_response_id,
        exam_type=exam_type_upper,
        question_text=question_text,
        audio_data=audio_bytes,
        audio_mime_type=audio.content_type,
        rubric=rubric_dict,
        max_score=result["max_score"],
        passing_score=result["passing_score"],
        overall_score=overall_score,
        overall_band=str(result.get("overall_band", overall_score)),
        cefr_level=result.get("cefr_level", ""),
        approved=approved,
        feedback=result.get("feedback", ""),
        score_breakdown=result.get("breakdown", []),
        transcript=result.get("transcript", ""),
        priority_improvements=result.get("priority_improvements", []),
        model_used=result.get("model_used", ""),
        created_at=datetime.now(),
        evaluated_at=datetime.now(),
    )
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)

    return db_eval
''',

    "app/services/exam_rubrics.py": '''from typing import Optional


KET_RUBRIC = {
    "exam_type": "KET",
    "cefr_target": "A2",
    "criteria": [
        {
            "name": "Pronunciation",
            "weight": 20,
            "description": "Phoneme accuracy, word/sentence stress, intonation, and global intelligibility. Native accent is accepted if clear.",
            "scale": "1-5",
            "bands": {
                5: "Generally clear; some errors occur but message is fully understandable.",
                4: "Understandable with effort; occasional strain on listener.",
                3: "Frequent pronunciation errors obscure meaning at times.",
                2: "Pronunciation frequently prevents basic comprehension.",
                1: "Very limited / A1 level."
            }
        },
        {
            "name": "Fluency",
            "weight": 20,
            "description": "Flow of speech, hesitation frequency, and ability to complete sentences without excessive mid-clause pauses.",
            "scale": "1-5",
            "bands": {
                5: "Smooth flow; minimal hesitation; easily completes multi-sentence ideas.",
                4: "Normal A2 hesitation searching for words; completes thoughts without long pauses.",
                3: "Noticeable hesitation; pauses before simple words but maintains basic stream.",
                2: "Frequent long pauses; fragmented speech; struggles to finish simple sentences.",
                1: "Severe hesitation; isolated word production only."
            }
        },
        {
            "name": "Vocabulary",
            "weight": 20,
            "description": "Range and accuracy of everyday vocabulary (family, hobbies, school, food, routines).",
            "scale": "1-5",
            "bands": {
                5: "Uses broad A2 vocabulary; appropriate topic words; attempts simple paraphrasing.",
                4: "Sufficient everyday vocabulary for familiar topics (hobbies, routines).",
                3: "Basic vocabulary; limited variety but adequate for basic answers.",
                2: "Inadequate vocabulary; frequent word searches; relies on prompt words.",
                1: "Extremely restricted vocabulary; isolated words only."
            }
        },
        {
            "name": "Grammar",
            "weight": 20,
            "description": "Structural control of simple tenses (Present Simple/Continuous, Past Simple), be, can/can't, there is/are, and basic connectors (and, but, because).",
            "scale": "1-5",
            "bands": {
                5: "Good control of simple structures; correct verb forms and simple connectors.",
                4: "Clear control of Present/Past simple; minor errors do not block meaning.",
                3: "Basic structural control; errors in tenses/plurals occur but meaning clear.",
                2: "Persistent grammatical errors (verbs, word order) cause confusion.",
                1: "Little to no control of simple grammatical structures."
            }
        },
        {
            "name": "Interaction / Response",
            "weight": 10,
            "description": "Answering prompts directly, expanding with details, turn-taking, and keeping the prompt flow going.",
            "scale": "1-5",
            "bands": {
                5: "Answers directly and expands with reasons/details; natural response flow.",
                4: "Answers prompt directly; minimal expansion; relies on straightforward prompts.",
                3: "Incomplete answers; requires heavy prompt support or repetition.",
                2: "Fails to respond appropriately; off-topic or silent.",
                1: "Very limited interaction."
            }
        },
        {
            "name": "Task / Global",
            "weight": 10,
            "description": "Overall message transmission, task completion, and listener effort required.",
            "scale": "1-5",
            "bands": {
                5: "Full task achievement; communicates clear, effective everyday message.",
                4: "Achieves task goals cleanly; listener understands without difficulty.",
                3: "Achieves essential task requirements; listener needs minor effort.",
                2: "Partial task completion; key information is missing or unclear.",
                1: "Task not achieved; minimal communicative value."
            }
        }
    ],
    "max_score": 5,
    "passing_score": 3,
    "band_to_cefr": {
        "5": "B1",
        "4": "A2",
        "3": "A2",
        "2": "A1",
        "1": "A1"
    }
}

FCE_RUBRIC = {
    "exam_type": "FCE",
    "cefr_target": "B2",
    "criteria": [
        {
            "name": "Grammar & Vocabulary",
            "weight": 25,
            "description": "Range, accuracy, and appropriate usage of complex structures (conditionals, passives, relative clauses, modal deduction) and varied topic vocabulary.",
            "scale": "1-5",
            "bands": {
                5: "Wide range of complex grammar & vocabulary; minor errors do not affect meaning; precise collocations.",
                4: "Good range of simple & complex structures; clear vocabulary; occasional minor slips.",
                3: "Adequate range for B2 tasks; frequent simple errors but complex structures attempted.",
                2: "Limited structural range; relies on simple B1 forms; noticeable vocabulary gaps.",
                1: "Very basic grammar & vocabulary; persistent errors impede expression of complex ideas."
            }
        },
        {
            "name": "Discourse Management",
            "weight": 25,
            "description": "Extended turns, logical coherence, cohesion/linking devices, speech rate, and avoidance of undue hesitation or repetition.",
            "scale": "1-5",
            "bands": {
                5: "Produces extended, well-organized discourse; smooth cohesion; natural discourse markers.",
                4: "Sustains speech comfortably; connects ideas logically using varied linking phrases.",
                3: "Produces extended discourse but with some hesitation, repetition, or basic linkers.",
                2: "Short contributions; noticeable hesitations; limited range of cohesive devices.",
                1: "Fragmented turns; frequent long pauses; lacks logical flow or coherence."
            }
        },
        {
            "name": "Pronunciation",
            "weight": 25,
            "description": "Intelligibility, correct word/sentence stress, intonation patterns conveying emotion/meaning, and natural rhythm.",
            "scale": "1-5",
            "bands": {
                5: "Clear, natural intonation and sentence stress; easy to understand throughout.",
                4: "Generally clear; stress/intonation support meaning; rare listener strain.",
                3: "Intelligible; occasional phoneme errors or non-standard stress require listener focus.",
                2: "Pronunciation errors frequently cause listener strain or misinterpretation.",
                1: "Unclear articulation; frequent errors severely impair communication."
            }
        },
        {
            "name": "Interactive Communication",
            "weight": 15,
            "description": "Active turn-taking, initiating/responding, negotiating outcomes, maintaining conversation flow, and supporting a partner.",
            "scale": "1-5",
            "bands": {
                5: "Initiates and develops interaction effortlessly; negotiates smoothly; supports partner.",
                4: "Maintains interaction well; responds appropriately and invites partner input.",
                3: "Maintains simple interaction; responds directly but initiates infrequently.",
                2: "Struggles to keep interaction going; passive; relies on examiner/partner prompting.",
                1: "Minimal interaction; unable to negotiate or respond effectively."
            }
        },
        {
            "name": "Global Achievement",
            "weight": 10,
            "description": "Overall communicative effectiveness across complex B2 task requirements.",
            "scale": "1-5",
            "bands": {
                5: "Handles all B2 task demands with high effectiveness, nuance, and confidence.",
                4: "Fully satisfies task requirements with clear, coherent B2 communication.",
                3: "Achieves basic communicative purpose across all task types.",
                2: "Fails to fully address task demands; communication lacks depth or clarity.",
                1: "Severe failure to complete tasks; minimal effectiveness."
            }
        }
    ],
    "max_score": 5,
    "passing_score": 3,
    "band_to_cefr": {
        "5": "C1",
        "4": "B2",
        "3": "B2",
        "2": "B1",
        "1": "A2-B1"
    }
}

IELTS_RUBRIC = {
    "exam_type": "IELTS",
    "cefr_target": "B1-C2",
    "criteria": [
        {
            "name": "Fluency & Coherence",
            "weight": 25,
            "description": "Ability to talk with normal levels of continuity, rate and effort and to link ideas and language together to form coherent, connected speech.",
            "scale": "1-9",
            "bands": {
                9: "Fluency is natural and effortless; rare repetition; fully coherent development.",
                8: "Speaks fluently with rare hesitations; develops topics coherently and fully.",
                7: "Speaks at length smoothly; occasional hesitation or self-correction; clear linkers.",
                6: "Willing to speak at length; may lose coherence at times due to hesitation.",
                5: "Maintains flow but relies on repetition, slow rate, and self-correction.",
                4: "Noticeable pauses; slow speech; limited linking words; frequent repetition.",
                3: "Long pauses; speech fragmented; unable to sustain simple answers."
            }
        },
        {
            "name": "Lexical Resource",
            "weight": 25,
            "description": "The range of vocabulary the candidate can use and the precision with which meanings and attitudes can be expressed.",
            "scale": "1-9",
            "bands": {
                9: "Uses vocabulary with full flexibility and precision; idiomatic language natural.",
                8: "Wide vocabulary resource; precise usage; skillful paraphrasing.",
                7: "Flexible vocabulary; uses topic collocations; some inappropriate word choice.",
                6: "Sufficient vocabulary for familiar/abstract topics; attempts paraphrasing.",
                5: "Limited vocabulary for abstract topics; struggles with paraphrasing.",
                4: "Conveys basic meaning on familiar topics; frequent word errors.",
                3: "Simple vocabulary only; inability to express basic concepts."
            }
        },
        {
            "name": "Grammatical Range & Accuracy",
            "weight": 25,
            "description": "The range and accurate use of grammatical structures at sentence and clause level.",
            "scale": "1-9",
            "bands": {
                9: "Full range of structures flexibly and accurately; rare minor slips.",
                8: "Wide range of flexible structures; majority of sentences error-free.",
                7: "Uses range of complex structures; frequent error-free sentences.",
                6: "Mix of simple and complex structures; frequent grammatical errors in complex forms.",
                5: "Basic structures accurate; complex structures rare and frequently faulty.",
                4: "Rely on simple structures; errors predominate in complex sentences.",
                3: "Basic errors dominate; little control over sentence formation."
            }
        },
        {
            "name": "Pronunciation",
            "weight": 25,
            "description": "Ability to produce comprehensible speech using a range of phonological features.",
            "scale": "1-9",
            "bands": {
                9: "Effortless to understand throughout; natural features used effectively.",
                8: "Easy to understand; stress and intonation applied naturally throughout.",
                7: "Generally clear; minor accent interference; stress/intonation mostly good.",
                6: "Understandable overall; mispronunciations occur but do not block general meaning.",
                5: "Requires listener effort; mispronunciations cause intermittent clarity loss.",
                4: "Frequent errors make comprehension difficult; strain required.",
                3: "Pronunciation frequently prevents basic understanding."
            }
        }
    ],
    "max_score": 9,
    "passing_score": 5.5,
    "band_to_cefr": {
        "9": "C2",
        "8.5": "C2",
        "8.0": "C1",
        "7.5": "C1",
        "7.0": "C1",
        "6.5": "B2",
        "6.0": "B2",
        "5.5": "B2",
        "5.0": "B1",
        "4.5": "B1",
        "4.0": "B1",
        "3.5": "A2",
        "3.0": "A2"
    }
}


def get_rubric(exam_type: str) -> Optional[dict]:
    rubrics = {
        "KET": KET_RUBRIC,
        "FCE": FCE_RUBRIC,
        "IELTS": IELTS_RUBRIC,
    }
    return rubrics.get(exam_type.upper())


def build_rubric_prompt(rubric: dict, question_text: str) -> str:
    criteria_blocks = []
    for c in rubric["criteria"]:
        band_lines = "\\n".join(
            f"    Band {band}: {desc}" for band, desc in c["bands"].items()
        )
        criteria_blocks.append(
            f"CRITERION: {c['name']} (weight: {c['weight']}%)\\n"
            f"Description: {c['description']}\\n"
            f"Scale: {c['scale']}\\n"
            f"Band descriptors:\\n{band_lines}"
        )
    
    criteria_text = "\\n\\n".join(criteria_blocks)
    increment = 0.5 if rubric['exam_type'] == 'IELTS' else 1
    
    return f"""You are a certified {rubric['exam_type']} Speaking examiner with 20 years of experience.

The student was asked this question:
\"{question_text}\"

Listen to the attached audio recording of the student's spoken response.

Evaluate the student according to the official {rubric['exam_type']} Speaking Band Descriptors below.

{criteria_text}

INSTRUCTIONS:
1. Listen carefully to the audio. Pay attention to pronunciation, intonation, stress, rhythm, fluency, hesitation patterns, vocabulary choices, grammatical structures, and coherence.
2. For each criterion, assign a score on the scale indicated, in increments of {increment}.
3. Provide a 2-sentence justification for each criterion, referencing specific evidence from the audio.
4. Calculate the overall band/score as the weighted average of all criteria (round to nearest {increment}).
5. Map the overall score to CEFR level using: {rubric['band_to_cefr']}.
6. Provide 2-3 sentences of overall feedback for the student.
7. List 2 specific, actionable priority improvement areas.
8. Include an approximate transcript of what the student said.

Respond ONLY with valid JSON, no markdown, no extra text, using this exact structure:

{{
  \"breakdown\": [
    {{
      \"criterion\": \"criterion_name\",
      \"score\": <number>,
      \"max\": <number>,
      \"comment\": \"<brief justification with audio evidence>\"
    }}
  ],
  \"overall_band\": <number>,
  \"cefr_level\": \"<A1/A2/B1/B2/C1/C2>\",
  \"feedback\": \"<overall feedback>\",
  \"priority_improvements\": [\"<area 1>\", \"<area 2>\"],
  \"transcript\": \"<approximate transcript>\"
}}
"""
''',

    "app/services/speaking_evaluator.py": '''import os
import json
import base64
from typing import Optional
import dashscope
from dashscope import MultiModalConversation
from app.services.exam_rubrics import get_rubric, build_rubric_prompt

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_AUDIO_MODEL", "qwen-audio-asr-flash")


def evaluate_speaking(
    audio_bytes: bytes,
    audio_mime_type: str,
    question_text: str,
    exam_type: str,
    max_score: Optional[float] = None,
) -> dict:
    if not DASHSCOPE_API_KEY:
        raise RuntimeError("DASHSCOPE_API_KEY environment variable is not set")

    dashscope.api_key = DASHSCOPE_API_KEY

    rubric = get_rubric(exam_type)
    if rubric:
        prompt = build_rubric_prompt(rubric, question_text)
        effective_max = rubric["max_score"]
        effective_passing = rubric["passing_score"]
    else:
        effective_max = max_score or 100
        effective_passing = max_score * 0.6 if max_score else 60
        prompt = f"""You are an expert English Speaking evaluator.

The student was asked: \"{question_text}\"

Listen to the attached audio recording and evaluate the student's spoken English.

Assess the following dimensions and score each 0-{int(effective_max)}:
- Pronunciation & Phonetics (accent, stress, intonation, rhythm)
- Fluency & Coherence (flow, hesitation, linking, discourse markers)
- Lexical Resource (vocabulary range, precision, collocations)
- Grammatical Range & Accuracy (structures, errors, complexity)
- Interactive Communication (turn-taking, responding, expanding)

For each criterion, assign a score and provide a 2-sentence justification referencing specific audio evidence.

Respond ONLY with valid JSON:
{{
  \"breakdown\": [
    {{\"criterion\": \"name\", \"score\": <number>, \"max\": <number>, \"comment\": \"...\"}}
  ],
  \"overall_band\": <number>,
  \"cefr_level\": \"<A1/A2/B1/B2/C1/C2>\",
  \"feedback\": \"...\",
  \"priority_improvements\": [\"...\", \"...\"],
  \"transcript\": \"...\"
}}
"""

    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    audio_data_uri = f"data:{audio_mime_type};base64,{audio_b64}"

    messages = [
        {
            "role": "system",
            "content": [
                {"text": "You are a certified English Speaking examiner. You respond only in valid JSON."}
            ],
        },
        {
            "role": "user",
            "content": [
                {"audio": audio_data_uri},
                {"text": prompt},
            ],
        },
    ]

    try:
        response = MultiModalConversation.call(
            model=DASHSCOPE_MODEL,
            messages=messages,
            timeout=120,
        )
    except Exception as e:
        raise RuntimeError(f"DashScope API call failed: {e}")

    if response.status_code != 200:
        raise RuntimeError(
            f"DashScope returned status {response.status_code}: "
            f"{getattr(response, 'message', str(response))}"
        )

    try:
        content = response.output.choices[0].message.content
        if isinstance(content, list):
            raw_text = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
        else:
            raw_text = str(content)
    except (AttributeError, IndexError, KeyError, TypeError) as e:
        raise RuntimeError(f"Unexpected response structure from DashScope: {e}")

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r"```(?:json)?\\s*([\\s\\S]*?)```", raw_text)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                raise ValueError(f"LLM did not return valid JSON. Raw response:\\n{raw_text}")
        else:
            raise ValueError(f"LLM did not return valid JSON. Raw response:\\n{raw_text}")

    breakdown = parsed.get("breakdown", [])
    
    if breakdown and all("weight" in b for b in breakdown):
        total_weighted = sum(
            (item.get("score", 0) / item.get("max", 1)) * item.get("weight", 0)
            for item in breakdown
        )
        total_weight = sum(item.get("weight", 0) for item in breakdown)
        overall_score = (total_weighted / total_weight) * effective_max if total_weight > 0 else 0
    else:
        overall_score = sum(item.get("score", 0) for item in breakdown)

    if exam_type.upper() == "IELTS":
        overall_score = round(overall_score * 2) / 2
    else:
        overall_score = round(overall_score)

    return {
        "score": overall_score,
        "max_score": effective_max,
        "passing_score": effective_passing,
        "breakdown": breakdown,
        "feedback": parsed.get("feedback", ""),
        "overall_band": parsed.get("overall_band", overall_score),
        "cefr_level": parsed.get("cefr_level", ""),
        "priority_improvements": parsed.get("priority_improvements", []),
        "transcript": parsed.get("transcript", ""),
        "model_used": DASHSCOPE_MODEL,
    }
''',

    "requirements.txt": '''annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.14.1
certifi==2026.6.17
cffi==2.1.0
click==8.4.2
colorama==0.4.6
cryptography==49.0.0
dashscope>=1.14.0
distro==1.9.0
fastapi==0.139.0
greenlet==3.5.3
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.18
jiter==0.16.0
openai==2.45.0
psycopg2-binary==2.9.12
pycparser==3.0
pydantic==2.13.4
pydantic_core==2.46.4
python-dotenv==1.2.2
six==1.17.0
sniffio==1.3.1
SQLAlchemy==2.0.51
starlette==1.3.1
tqdm==4.68.4
typing-inspection==0.4.2
typing_extensions==4.16.0
uvicorn==0.50.2
''',

    "db-script.sql": '''CREATE TABLE IF NOT EXISTS speaking_evaluations (
    id SERIAL PRIMARY KEY,
    external_user_id VARCHAR(100),
    external_exam_id VARCHAR(100),
    external_question_id VARCHAR(100),
    external_response_id VARCHAR(100),
    exam_type VARCHAR(20) NOT NULL CHECK (exam_type IN ('KET', 'FCE', 'IELTS', 'CUSTOM')),
    question_text TEXT NOT NULL,
    audio_data BYTEA,
    audio_mime_type VARCHAR(50),
    rubric JSONB NOT NULL,
    max_score NUMERIC(5, 2) NOT NULL DEFAULT 100 CHECK (max_score > 0),
    passing_score NUMERIC(5, 2) NOT NULL DEFAULT 60 CHECK (passing_score >= 0),
    overall_score NUMERIC(5, 2) CHECK (overall_score >= 0),
    overall_band VARCHAR(10),
    cefr_level VARCHAR(5),
    approved BOOLEAN,
    feedback TEXT,
    score_breakdown JSONB,
    transcript TEXT,
    priority_improvements JSONB,
    model_used VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    evaluated_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_speaking_eval_external_user ON speaking_evaluations (external_user_id);
CREATE INDEX IF NOT EXISTS idx_speaking_eval_exam_type ON speaking_evaluations (exam_type);
CREATE INDEX IF NOT EXISTS idx_speaking_eval_cefr ON speaking_evaluations (cefr_level);
''',
}


def main():
    for rel_path, content in FILES.items():
        full_path = os.path.join(BASE, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Created: {rel_path}")

    print("\nDone. Now run:")
    print("  pip install dashscope>=1.14.0")
    print("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()