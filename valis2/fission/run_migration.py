"""
Run Soul Stratification database migration
"""
import sys
sys.path.append('C:\\VALIS\\valis2')

from memory.db import db

# Create persona_documents table
try:
    db.execute("""
        CREATE TABLE IF NOT EXISTS persona_documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            persona_id UUID NOT NULL,
            session_id UUID,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            file_type TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            canon_status TEXT NOT NULL DEFAULT 'core',
            life_phase TEXT,
            tags JSONB DEFAULT '[]',
            metadata JSONB DEFAULT '{}',
            content_hash TEXT NOT NULL,
            file_size INTEGER,
            upload_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            processed_timestamp TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("[OK] persona_documents table created")
    
    # Create indexes
    db.execute("CREATE INDEX IF NOT EXISTS idx_persona_documents_persona_id ON persona_documents(persona_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_persona_documents_doc_type ON persona_documents(doc_type)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_persona_documents_canon_status ON persona_documents(canon_status)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_persona_documents_life_phase ON persona_documents(life_phase)")
    print("[OK] Indexes created")
    
    print("Soul Stratification database migration completed successfully!")

except Exception as e:
    print(f"Migration failed: {e}")
