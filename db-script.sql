-- ============================================================
-- English Exam Evaluator — Database schema
-- Run against your PostgreSQL database to (re)create all tables.
-- Safe to re-run: every statement uses IF NOT EXISTS.
-- ============================================================

-- ---------------------------------------------------------
-- Table: evaluations
-- Stores the history of every graded exam response.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS evaluations (
    id SERIAL PRIMARY KEY,

    -- References to the external system (traceability only, not real foreign keys)
    external_user_id VARCHAR(100),
    external_exam_id VARCHAR(100),
    external_question_id VARCHAR(100),
    external_response_id VARCHAR(100),

    -- Data received in the request
    question_text TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    rubric JSONB NOT NULL,
    max_score INTEGER NOT NULL DEFAULT 100 CHECK (max_score > 0),
    passing_score INTEGER NOT NULL DEFAULT 60 CHECK (passing_score >= 0),

    -- Evaluation result
    score NUMERIC(5, 2) CHECK (score >= 0),
    approved BOOLEAN,
    feedback TEXT,
    score_breakdown JSONB,
    model_used VARCHAR(50),

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    evaluated_at TIMESTAMPTZ
);

-- Indexes for searching evaluations by external reference
CREATE INDEX IF NOT EXISTS idx_evaluations_external_user_id ON evaluations (external_user_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_exam_id ON evaluations (external_exam_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_question_id ON evaluations (external_question_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_external_response_id ON evaluations (external_response_id);


-- ---------------------------------------------------------
-- Table: rubric_templates
-- Stores reusable grading rubrics, selectable from the client
-- instead of rebuilding the same criteria on every evaluation.
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS rubric_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    criteria JSONB NOT NULL,
    max_score INTEGER NOT NULL DEFAULT 100 CHECK (max_score > 0),
    passing_score INTEGER NOT NULL DEFAULT 60 CHECK (passing_score >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for searching rubric templates by name
CREATE INDEX IF NOT EXISTS idx_rubric_templates_name ON rubric_templates (name);