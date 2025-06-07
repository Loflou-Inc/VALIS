-- Sprint 22: Soul Stratification Database Migration
-- Creates persona_documents table for layered consciousness construction

CREATE TABLE IF NOT EXISTS persona_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_id UUID NOT NULL,
    session_id UUID,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    file_type TEXT NOT NULL, -- 'pdf', 'txt', 'image', 'audio', etc.
    doc_type TEXT NOT NULL, -- 'narrative', 'education', 'career', 'personal', 'reference'
    canon_status TEXT NOT NULL DEFAULT 'core', -- 'core', 'secondary', 'noise', 'contradictory'
    life_phase TEXT, -- 'childhood', 'adolescence', 'young_adult', 'adult', 'current'
    tags JSONB DEFAULT '[]', -- ['trauma', 'achievement', 'relationship', etc.]
    metadata JSONB DEFAULT '{}', -- Additional parsing metadata
    content_hash TEXT NOT NULL,
    file_size INTEGER,
    upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_persona_documents_persona_id ON persona_documents(persona_id);
CREATE INDEX IF NOT EXISTS idx_persona_documents_doc_type ON persona_documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_persona_documents_canon_status ON persona_documents(canon_status);
CREATE INDEX IF NOT EXISTS idx_persona_documents_life_phase ON persona_documents(life_phase);
CREATE INDEX IF NOT EXISTS idx_persona_documents_session ON persona_documents(session_id);

-- Add document count trigger for personas
CREATE OR REPLACE FUNCTION update_persona_document_count()
RETURNS TRIGGER AS $$
BEGIN
    -- This would update a document_count field in personas table if it exists
    -- For now, just ensure the trigger framework is in place
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER IF NOT EXISTS persona_documents_update_count
    AFTER INSERT OR DELETE ON persona_documents
    FOR EACH ROW EXECUTE FUNCTION update_persona_document_count();

-- View for document summary by persona
CREATE OR REPLACE VIEW persona_document_summary AS
SELECT 
    persona_id,
    COUNT(*) as total_documents,
    COUNT(CASE WHEN doc_type = 'narrative' THEN 1 END) as narrative_docs,
    COUNT(CASE WHEN doc_type = 'education' THEN 1 END) as education_docs,
    COUNT(CASE WHEN doc_type = 'career' THEN 1 END) as career_docs,
    COUNT(CASE WHEN canon_status = 'core' THEN 1 END) as core_docs,
    COUNT(CASE WHEN canon_status = 'noise' THEN 1 END) as noise_docs,
    ARRAY_AGG(DISTINCT life_phase) FILTER (WHERE life_phase IS NOT NULL) as life_phases_covered,
    MIN(created_at) as earliest_document,
    MAX(created_at) as latest_document
FROM persona_documents
GROUP BY persona_id;
