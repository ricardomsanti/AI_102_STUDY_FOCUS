-- AI-102 Study Guide Database Schema
-- Compatible with PostgreSQL, MySQL, and SQLite (with minor modifications)

-- Drop existing tables if they exist
DROP TABLE IF EXISTS sub_skills CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS topic_areas CASCADE;
DROP TABLE IF EXISTS change_log CASCADE;
DROP TABLE IF EXISTS exam_metadata CASCADE;

-- Exam Metadata Table
CREATE TABLE exam_metadata (
    exam_code VARCHAR(20) PRIMARY KEY,
    exam_title VARCHAR(500) NOT NULL,
    extraction_date TIMESTAMP,
    exam_update_date VARCHAR(100),
    source_url TEXT,
    source_file TEXT
);

-- Topic Areas Table
CREATE TABLE topic_areas (
    topic_id VARCHAR(20) PRIMARY KEY,
    topic_area VARCHAR(500) NOT NULL,
    percentage_weight VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills Table
CREATE TABLE skills (
    skill_id VARCHAR(20) PRIMARY KEY,
    topic_id VARCHAR(20) NOT NULL,
    skill VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topic_areas(topic_id) ON DELETE CASCADE
);

-- Sub-Skills Table (Most granular level)
CREATE TABLE sub_skills (
    sub_skill_id VARCHAR(20) PRIMARY KEY,
    skill_id VARCHAR(20) NOT NULL,
    topic_id VARCHAR(20) NOT NULL,
    sub_skill TEXT NOT NULL,
    reference_links TEXT,
    annotation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topic_areas(topic_id) ON DELETE CASCADE
);

-- Change Log Table
CREATE TABLE change_log (
    change_id VARCHAR(20) PRIMARY KEY,
    change_description TEXT NOT NULL,
    change_date VARCHAR(100),
    change_type VARCHAR(50),
    skill_prior VARCHAR(500),
    skill_current VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study Progress Table (for gamification)
CREATE TABLE study_progress (
    progress_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    sub_skill_id VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'not_started',
    confidence_level INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sub_skill_id) REFERENCES sub_skills(sub_skill_id) ON DELETE CASCADE,
    UNIQUE(user_id, sub_skill_id)
);

-- Quiz Results Table (for tracking quiz performance)
CREATE TABLE quiz_results (
    quiz_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    sub_skill_id VARCHAR(20) NOT NULL,
    question TEXT NOT NULL,
    user_answer TEXT,
    correct_answer TEXT,
    is_correct BOOLEAN,
    time_spent_seconds INTEGER,
    quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sub_skill_id) REFERENCES sub_skills(sub_skill_id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_skills_topic ON skills(topic_id);
CREATE INDEX idx_subskills_skill ON sub_skills(skill_id);
CREATE INDEX idx_subskills_topic ON sub_skills(topic_id);
CREATE INDEX idx_progress_user ON study_progress(user_id);
CREATE INDEX idx_progress_status ON study_progress(status);
CREATE INDEX idx_quiz_user ON quiz_results(user_id);
CREATE INDEX idx_quiz_date ON quiz_results(quiz_date);

-- Create views for common queries

-- View: Complete Skills Hierarchy
CREATE VIEW v_skills_hierarchy AS
SELECT
    t.topic_id,
    t.topic_area,
    t.percentage_weight,
    s.skill_id,
    s.skill,
    ss.sub_skill_id,
    ss.sub_skill,
    ss.reference_links,
    ss.annotation
FROM topic_areas t
LEFT JOIN skills s ON t.topic_id = s.topic_id
LEFT JOIN sub_skills ss ON s.skill_id = ss.skill_id
ORDER BY t.topic_id, s.skill_id, ss.sub_skill_id;

-- View: Study Progress Summary by Topic
CREATE VIEW v_progress_by_topic AS
SELECT
    t.topic_id,
    t.topic_area,
    t.percentage_weight,
    sp.user_id,
    COUNT(DISTINCT ss.sub_skill_id) as total_sub_skills,
    COUNT(DISTINCT CASE WHEN sp.status = 'completed' THEN sp.sub_skill_id END) as completed_count,
    COUNT(DISTINCT CASE WHEN sp.status = 'in_progress' THEN sp.sub_skill_id END) as in_progress_count,
    COUNT(DISTINCT CASE WHEN sp.status = 'mastered' THEN sp.sub_skill_id END) as mastered_count,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN sp.status IN ('completed', 'mastered') THEN sp.sub_skill_id END) /
        NULLIF(COUNT(DISTINCT ss.sub_skill_id), 0),
        2
    ) as completion_percentage
FROM topic_areas t
LEFT JOIN sub_skills ss ON t.topic_id = ss.topic_id
LEFT JOIN study_progress sp ON ss.sub_skill_id = sp.sub_skill_id
GROUP BY t.topic_id, t.topic_area, t.percentage_weight, sp.user_id
ORDER BY t.topic_id;

-- View: Quiz Performance by Topic
CREATE VIEW v_quiz_performance AS
SELECT
    t.topic_id,
    t.topic_area,
    qr.user_id,
    COUNT(*) as total_questions,
    SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) as correct_answers,
    ROUND(100.0 * SUM(CASE WHEN qr.is_correct THEN 1 ELSE 0 END) / COUNT(*), 2) as accuracy_percentage,
    AVG(qr.time_spent_seconds) as avg_time_seconds
FROM topic_areas t
JOIN sub_skills ss ON t.topic_id = ss.topic_id
JOIN quiz_results qr ON ss.sub_skill_id = qr.sub_skill_id
GROUP BY t.topic_id, t.topic_area, qr.user_id
ORDER BY t.topic_id;

-- View: Weak Areas (low performance sub-skills)
CREATE VIEW v_weak_areas AS
SELECT
    t.topic_area,
    s.skill,
    ss.sub_skill,
    sp.user_id,
    sp.confidence_level,
    sp.attempts,
    sp.correct_answers,
    ROUND(100.0 * sp.correct_answers / NULLIF(sp.attempts, 0), 2) as success_rate
FROM sub_skills ss
JOIN skills s ON ss.skill_id = s.skill_id
JOIN topic_areas t ON ss.topic_id = t.topic_id
LEFT JOIN study_progress sp ON ss.sub_skill_id = sp.sub_skill_id
WHERE sp.confidence_level < 3 OR (sp.correct_answers * 100.0 / NULLIF(sp.attempts, 0)) < 70
ORDER BY sp.confidence_level ASC, success_rate ASC;

-- Sample data insertion (metadata)
-- This will be populated by the Python scripts

COMMENT ON TABLE exam_metadata IS 'Stores exam metadata including title, dates, and source information';
COMMENT ON TABLE topic_areas IS 'Main topic areas covered in the AI-102 exam with percentage weights';
COMMENT ON TABLE skills IS 'Skills within each topic area';
COMMENT ON TABLE sub_skills IS 'Detailed sub-skills and learning objectives';
COMMENT ON TABLE change_log IS 'History of changes to the exam content';
COMMENT ON TABLE study_progress IS 'Tracks individual user progress on each sub-skill';
COMMENT ON TABLE quiz_results IS 'Stores quiz results for performance tracking';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai102_user;
-- GRANT SELECT ON ALL VIEWS IN SCHEMA public TO ai102_user;
