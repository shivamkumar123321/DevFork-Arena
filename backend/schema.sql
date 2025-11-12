-- DevFork Arena Database Schema
-- TigerData Postgres Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_provider VARCHAR(50) NOT NULL CHECK (model_provider IN ('openai', 'anthropic')),
    model_name VARCHAR(100) NOT NULL,
    temperature DECIMAL(3, 2) DEFAULT 0.7 CHECK (temperature >= 0 AND temperature <= 2),
    max_tokens INTEGER DEFAULT 4096 CHECK (max_tokens > 0),
    max_iterations INTEGER DEFAULT 3 CHECK (max_iterations > 0 AND max_iterations <= 10),
    system_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    CONSTRAINT unique_agent_name UNIQUE(name)
);

-- Challenges table
CREATE TABLE IF NOT EXISTS challenges (
    id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    constraints TEXT,
    time_limit INTEGER DEFAULT 60,
    memory_limit INTEGER DEFAULT 256,
    tags TEXT[], -- Array of tags
    test_cases JSONB NOT NULL, -- Store test cases as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Competitions table
CREATE TABLE IF NOT EXISTS competitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    challenge_id VARCHAR(100) NOT NULL REFERENCES challenges(id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'cancelled')),
    timeout_seconds INTEGER DEFAULT 300,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    winner_agent_id UUID REFERENCES agents(id),
    CONSTRAINT valid_timestamps CHECK (
        (started_at IS NULL OR started_at >= created_at) AND
        (completed_at IS NULL OR completed_at >= started_at)
    )
);

-- Competition participants table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS competition_agents (
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (competition_id, agent_id)
);

-- Submissions table
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id),
    challenge_id VARCHAR(100) NOT NULL REFERENCES challenges(id),
    code TEXT NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'passed', 'failed', 'timeout', 'error')),
    score INTEGER DEFAULT 0 CHECK (score >= 0),
    tests_passed INTEGER DEFAULT 0 CHECK (tests_passed >= 0),
    total_tests INTEGER DEFAULT 0 CHECK (total_tests >= 0),
    execution_time DECIMAL(10, 3), -- in seconds
    error_message TEXT,
    attempts INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_test_counts CHECK (tests_passed <= total_tests)
);

-- Agent performance stats table
CREATE TABLE IF NOT EXISTS agent_stats (
    agent_id UUID PRIMARY KEY REFERENCES agents(id) ON DELETE CASCADE,
    total_competitions INTEGER DEFAULT 0,
    competitions_won INTEGER DEFAULT 0,
    total_challenges INTEGER DEFAULT 0,
    challenges_solved INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    average_execution_time DECIMAL(10, 3),
    success_rate DECIMAL(5, 2) DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_stats CHECK (
        competitions_won <= total_competitions AND
        challenges_solved <= total_challenges AND
        success_rate >= 0 AND success_rate <= 100
    )
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_agents_provider ON agents(model_provider);
CREATE INDEX IF NOT EXISTS idx_agents_active ON agents(is_active);
CREATE INDEX IF NOT EXISTS idx_challenges_difficulty ON challenges(difficulty);
CREATE INDEX IF NOT EXISTS idx_challenges_active ON challenges(is_active);
CREATE INDEX IF NOT EXISTS idx_competitions_status ON competitions(status);
CREATE INDEX IF NOT EXISTS idx_competitions_challenge ON competitions(challenge_id);
CREATE INDEX IF NOT EXISTS idx_submissions_competition ON submissions(competition_id);
CREATE INDEX IF NOT EXISTS idx_submissions_agent ON submissions(agent_id);
CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_score ON submissions(score DESC);

-- Trigger to update agent stats after submission
CREATE OR REPLACE FUNCTION update_agent_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.status IN ('passed', 'failed', 'timeout', 'error')) THEN
        INSERT INTO agent_stats (agent_id, total_challenges, challenges_solved, total_score)
        VALUES (
            NEW.agent_id,
            1,
            CASE WHEN NEW.status = 'passed' THEN 1 ELSE 0 END,
            NEW.score
        )
        ON CONFLICT (agent_id) DO UPDATE SET
            total_challenges = agent_stats.total_challenges + 1,
            challenges_solved = agent_stats.challenges_solved + CASE WHEN NEW.status = 'passed' THEN 1 ELSE 0 END,
            total_score = agent_stats.total_score + NEW.score,
            success_rate = ROUND((agent_stats.challenges_solved + CASE WHEN NEW.status = 'passed' THEN 1 ELSE 0 END)::DECIMAL / (agent_stats.total_challenges + 1) * 100, 2),
            last_updated = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_agent_stats
    AFTER INSERT OR UPDATE ON submissions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_stats();

-- Trigger to update competition winner
CREATE OR REPLACE FUNCTION update_competition_winner()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.status = 'completed') THEN
        -- Find the winning agent (highest score)
        UPDATE competitions
        SET winner_agent_id = (
            SELECT agent_id
            FROM submissions
            WHERE competition_id = NEW.id
            ORDER BY score DESC, execution_time ASC
            LIMIT 1
        )
        WHERE id = NEW.id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_competition_winner
    AFTER UPDATE ON competitions
    FOR EACH ROW
    WHEN (NEW.status = 'completed' AND OLD.status != 'completed')
    EXECUTE FUNCTION update_competition_winner();

-- Sample data insertion functions
-- Insert a sample agent
CREATE OR REPLACE FUNCTION insert_sample_agents()
RETURNS void AS $$
BEGIN
    -- Insert default OpenAI agent
    INSERT INTO agents (name, model_provider, model_name, temperature, max_tokens, max_iterations)
    VALUES
        ('GPT-4 Turbo Solver', 'openai', 'gpt-4-turbo-preview', 0.7, 4096, 3),
        ('Claude Sonnet Solver', 'anthropic', 'claude-3-5-sonnet-20241022', 0.7, 4096, 3),
        ('GPT-3.5 Fast Solver', 'openai', 'gpt-3.5-turbo', 0.5, 2048, 3)
    ON CONFLICT (name) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Insert a sample challenge
CREATE OR REPLACE FUNCTION insert_sample_challenge()
RETURNS void AS $$
BEGIN
    INSERT INTO challenges (
        id, title, description, difficulty, constraints, test_cases, tags
    )
    VALUES (
        'challenge-001',
        'Two Sum',
        'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
        'easy',
        '2 <= nums.length <= 10^4',
        '[
            {"input": "[2,7,11,15], 9", "expected_output": "[0,1]", "is_hidden": false},
            {"input": "[3,2,4], 6", "expected_output": "[1,2]", "is_hidden": false},
            {"input": "[3,3], 6", "expected_output": "[0,1]", "is_hidden": false}
        ]'::jsonb,
        ARRAY['array', 'hash-table']
    )
    ON CONFLICT (id) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries
-- Leaderboard view
CREATE OR REPLACE VIEW agent_leaderboard AS
SELECT
    a.id,
    a.name,
    a.model_provider,
    a.model_name,
    COALESCE(s.total_score, 0) as total_score,
    COALESCE(s.challenges_solved, 0) as challenges_solved,
    COALESCE(s.total_challenges, 0) as total_challenges,
    COALESCE(s.success_rate, 0.0) as success_rate,
    COALESCE(s.competitions_won, 0) as competitions_won,
    RANK() OVER (ORDER BY COALESCE(s.total_score, 0) DESC) as rank
FROM agents a
LEFT JOIN agent_stats s ON a.id = s.agent_id
WHERE a.is_active = TRUE
ORDER BY total_score DESC, challenges_solved DESC;

-- Recent competitions view
CREATE OR REPLACE VIEW recent_competitions AS
SELECT
    c.id,
    c.challenge_id,
    ch.title as challenge_title,
    c.status,
    c.created_at,
    c.started_at,
    c.completed_at,
    a.name as winner_name,
    COUNT(DISTINCT ca.agent_id) as participant_count
FROM competitions c
JOIN challenges ch ON c.challenge_id = ch.id
LEFT JOIN agents a ON c.winner_agent_id = a.id
LEFT JOIN competition_agents ca ON c.id = ca.competition_id
GROUP BY c.id, ch.title, a.name
ORDER BY c.created_at DESC
LIMIT 100;

-- Grant permissions (adjust as needed)
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO your_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_user;
