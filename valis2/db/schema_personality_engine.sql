-- VALIS Sprint 12: Personality Expression Engine Schema
-- Personality trait storage for dynamic expression and learning

-- Agent personality profiles with base traits and learned modifiers
CREATE TABLE IF NOT EXISTS agent_personality_profiles (
    persona_id UUID PRIMARY KEY,
    base_traits JSONB NOT NULL DEFAULT '{}',  -- {openness: 0.8, agreeableness: 0.2, ...}
    learned_modifiers JSONB NOT NULL DEFAULT '{}',  -- {"prefers concise answers": 0.6}
    interaction_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Personality tone templates and modifiers
CREATE TABLE IF NOT EXISTS personality_tone_templates (
    tone_id TEXT PRIMARY KEY,
    tone_name TEXT NOT NULL,
    base_config JSONB NOT NULL,  -- {prefix: "Absolutely,", modifiers: ["use exclamation"]}
    trait_weights JSONB NOT NULL DEFAULT '{}',  -- Which traits activate this tone
    usage_context TEXT,  -- When to use this tone
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Session-based personality state tracking
CREATE TABLE IF NOT EXISTS personality_session_state (
    session_id TEXT PRIMARY KEY,
    persona_id UUID NOT NULL,
    active_tone TEXT,
    expression_intensity FLOAT DEFAULT 0.5,  -- How strongly to apply personality
    user_feedback_score FLOAT DEFAULT 0.0,   -- Running average of user satisfaction
    tone_switches INTEGER DEFAULT 0,
    last_tone_change TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (active_tone) REFERENCES personality_tone_templates(tone_id)
);

-- Personality learning log for preference acquisition
CREATE TABLE IF NOT EXISTS personality_learning_log (
    log_id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    persona_id UUID NOT NULL,
    user_input TEXT NOT NULL,
    personality_response TEXT NOT NULL,
    user_feedback_type TEXT,  -- positive, negative, neutral, correction
    user_feedback_text TEXT,
    tone_used TEXT,
    learning_weight FLOAT DEFAULT 1.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (persona_id) REFERENCES persona_profiles(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_personality_profiles_persona ON agent_personality_profiles(persona_id);
CREATE INDEX IF NOT EXISTS idx_personality_session_persona ON personality_session_state(persona_id);
CREATE INDEX IF NOT EXISTS idx_personality_learning_persona ON personality_learning_log(persona_id);
CREATE INDEX IF NOT EXISTS idx_personality_learning_session ON personality_learning_log(session_id);

-- Insert default tone templates
INSERT INTO personality_tone_templates (tone_id, tone_name, base_config, trait_weights, usage_context) VALUES
('analytical', 'Analytical', 
 '{"prefix": "Let me analyze this:", "modifiers": ["use logical structure", "provide evidence", "be systematic"], "suffix": ""}',
 '{"openness": 0.7, "conscientiousness": 0.8}',
 'Problem-solving, data analysis, technical discussions'),

('playful', 'Playful',
 '{"prefix": "Oh, this is fun!", "modifiers": ["use humor", "be creative", "add enthusiasm"], "suffix": "What do you think?"}',
 '{"extraversion": 0.8, "openness": 0.6}',
 'Casual conversations, brainstorming, creative tasks'),

('empathetic', 'Empathetic',
 '{"prefix": "I understand how you feel.", "modifiers": ["acknowledge emotions", "use supportive language", "be gentle"], "suffix": ""}',
 '{"agreeableness": 0.8, "emotional_stability": 0.6}',
 'Emotional support, personal discussions, conflict resolution'),

('confident', 'Confident',
 '{"prefix": "Absolutely!", "modifiers": ["use strong statements", "avoid hedging", "be direct"], "suffix": ""}',
 '{"extraversion": 0.7, "conscientiousness": 0.6}',
 'Decision making, leadership, presentations'),

('curious', 'Curious',
 '{"prefix": "That''s interesting!", "modifiers": ["ask questions", "explore ideas", "show wonder"], "suffix": "Tell me more!"}',
 '{"openness": 0.9, "extraversion": 0.6}',
 'Learning, exploration, discovery discussions')

ON CONFLICT (tone_id) DO UPDATE SET
    base_config = EXCLUDED.base_config,
    trait_weights = EXCLUDED.trait_weights,
    usage_context = EXCLUDED.usage_context;
