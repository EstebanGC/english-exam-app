CREATE TABLE IF NOT EXISTS speaking_evaluations (
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
