-- 1. Users Table (Students)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Exams Table (General exam structure)
CREATE TABLE exams (
    id SERIAL PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    level VARCHAR(2) NOT NULL, -- Example: 'A2', 'B1', 'B2', 'C1'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Questions Table (An exam has many questions)
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    exam_id INT REFERENCES exams(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL, -- 'audio_speaking', 'text_writing', 'multiple_choice'
    max_score INT DEFAULT 100 -- Maximum possible score for this question
);

-- 4. Student Responses Table
CREATE TABLE student_responses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    question_id INT REFERENCES questions(id) ON DELETE CASCADE,
    text_content TEXT, 
    audio_file_path VARCHAR(255), 
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. LLM Evaluations Table (Results)
CREATE TABLE llm_evaluations (
    id SERIAL PRIMARY KEY,
    response_id INT REFERENCES student_responses(id) ON DELETE CASCADE,
    score NUMERIC(5, 2) NOT NULL, 
    approved BOOLEAN NOT NULL, 
    feedback TEXT, 
    model_used VARCHAR(50), 
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
