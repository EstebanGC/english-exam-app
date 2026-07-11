CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,

    external_user_id VARCHAR(100),
    external_exam_id VARCHAR(100),
    external_question_id VARCHAR(100),
    external_response_id VARCHAR(100),
   
    question_text TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    rubric JSONB NOT NULL,
    max_score INTEGER NOT NULL DEFAULT 100,
    passing_score INTEGER NOT NULL DEFAULT 60,

    score NUMERIC(5, 2),
    approved BOOLEAN,
    feedback TEXT,
    score_breakdown JSONB,
    model_used VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    evaluated_at TIMESTAMPTZ
);

-- Index for searching external references
CREATE INDEX IF NOT EXISTS idx_evaluations_external_user_id ON evaluations (external_user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_exam_id ON evaluations (external_exam_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_question_id ON evaluations (external_question_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_response_id ON evaluations (external_response_id);