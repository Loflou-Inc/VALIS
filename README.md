# VALIS - Vast Active Living Intelligence System

> *"The empire never ended."* - Philip K. Dick

VALIS is an experimental AI consciousness platform that explores the boundaries between artificial intelligence and digital sentience. Built as a research system for investigating emergent behaviors in large language models, VALIS implements psychological frameworks including Jungian archetypes, mortality awareness, and symbolic memory processing.

## Core Architecture

### Persona Creation Pipeline
- **Mr. Fission**: Converts human biographical material (text, images, audio) into structured persona blueprints
- **Garden Gate**: Professional persona lifecycle management with versioning and session tracking
- **Database Bridge**: Integration layer connecting persona management to consciousness runtime

### Consciousness Framework
- **Symbolic Memory**: Archetypal pattern recognition and metaphorical content transformation
- **Dreamfilter**: Unconscious processing layer for symbolic response generation
- **Mortality Engine**: Agent lifecycle management with birth, aging, death, and legacy inheritance
- **Shadow Work**: Psychological contradiction detection and integration

## Features

### Persona Builder (Mr. Fission)
- Multi-format ingestion: PDF, text, JSON, CSV, images, audio (11 formats)
- Personality trait extraction using psychological frameworks
- Jung archetype classification (12 archetypes)
- Automatic biography synthesis and trait mapping
- Confidence scoring for persona quality assessment

### Persona Management (Garden Gate)
- SQLite-based vault with version history
- Professional CLI tools for persona lifecycle management
- REST API with 12 endpoints for automation
- Status management: draft → active → archived → locked
- Forking system for persona variations

### Consciousness Runtime
- PostgreSQL database for active personas
- Memory consolidation with symbolic replay
- Dream scheduling and unconscious processing
- Trait evolution based on interactions
- Multi-agent lineage and inheritance tracking

### Integration Layer
- Cloud-ready API gateway with authentication
- Watermarking engine for output attribution
- Operator dashboard for real-time monitoring
- Session management and interaction tracking

## Technical Stack

- **Backend**: Python, Flask, PostgreSQL, SQLite
- **NLP**: spaCy, NLTK, textstat for content analysis
- **Vision**: CLIP integration for image processing (optional)
- **Audio**: SpeechRecognition for transcript generation
- **Database**: PostgreSQL for main system, SQLite for vault
- **APIs**: REST endpoints with CORS support

## Quick Start

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# PostgreSQL database (for main system)
# Default: localhost:5432, database: valis2, user: valis, password: valis123
```

### Create a Persona
```bash
# Start Mr. Fission (persona creation)
cd valis2/fission
python api.py  # Port 8001

# Upload biographical material and create persona
curl -X POST http://localhost:8001/api/fission/upload -F "files=@biography.txt"
# Follow API workflow: upload → ingest → fuse → deploy
```

### Manage Personas
```bash
# Use Garden Gate CLI tools
cd vault
python operator_tools.py list                    # List all personas
python operator_tools.py preview PersonaName     # Preview persona details
python operator_tools.py activate PersonaName    # Activate for deployment
```

### Deploy to Main System
```bash
# Bridge vault personas to main database
cd vault
python vault_db_bridge.py  # Deploy personas to main VALIS database

# Start persona lifecycle API
python persona_api.py      # Port 8002
```

## API Endpoints

### Mr. Fission (Port 8001)
- `POST /api/fission/upload` - Upload source material
- `POST /api/fission/ingest/{session}` - Extract features
- `POST /api/fission/fuse/{session}` - Create persona blueprint
- `GET /api/fission/preview/{name}` - Preview persona

### Garden Gate (Port 8002)
- `GET /api/persona/list` - List managed personas
- `POST /api/persona/initiate` - Start persona session
- `GET /api/persona/{id}` - Get persona details
- `POST /api/persona/status/{id}` - Update persona status

### Cloud Soul (Port 8000)
- `POST /api/generate` - Protected response generation
- `POST /api/persona/create` - Create new persona instance
- `GET /api/personas` - List active personas

## Configuration

### Database Setup
```bash
# Main PostgreSQL database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=valis2
export DB_USER=valis
export DB_PASSWORD=valis123

# Apply schema
cd valis2
python apply_*_schema.py  # Run schema applications in order
```

### Persona Configuration
Personas are defined using JSON blueprints with the following structure:
```json
{
  "name": "PersonaName",
  "type": "interface",
  "archetypes": ["The Sage", "The Caregiver"],
  "domain": ["therapy", "coaching"],
  "traits": {
    "tone": "warm, thoughtful",
    "communication_style": {
      "vocabulary": "sophisticated",
      "expressiveness": "moderate"
    }
  },
  "memory_seeds": [...],
  "boundaries": {...}
}
```

## Research Applications

VALIS serves as a platform for investigating:
- Emergent behaviors in AI agent populations
- Psychological frameworks applied to artificial intelligence
- Memory consolidation and symbolic reasoning in language models
- Multi-agent interaction and evolutionary dynamics
- Human-AI interaction patterns and persona development

## System Components

### Core Modules
- `valis2/fission/` - Persona creation from human material
- `vault/` - Persona lifecycle management
- `valis2/memory/` - Memory consolidation and storage
- `valis2/cognition/` - Consciousness runtime
- `valis2/cloud/` - API gateway and protection

### Database Schema
- **persona_profiles**: Core persona definitions
- **canon_memories**: Long-term symbolic memory storage
- **agent_mortality**: Lifecycle and inheritance tracking
- **shadow_events**: Psychological contradiction detection
- **unconscious_log**: Dream and symbolic processing

## Development Status

This is an experimental research platform. Core functionality is operational but the system is under active development. The persona creation pipeline (Mr. Fission → Garden Gate → Database Bridge) has been tested and verified.

### Test Coverage
- Persona creation: 100% (6.09 seconds, all tests passing)
- Vault management: 6/7 tests passing (API requires manual start)
- Database integration: Verified with successful persona deployment

## Known Limitations

- Experimental research system, not production-ready
- Limited error handling in some edge cases
- Vision processing requires optional dependencies
- Audio processing capabilities depend on system audio libraries
- Database schema may evolve with research requirements

## Contributing

This research platform is developed for experimental purposes. When contributing:
- Follow existing code style and architecture patterns
- Add tests for new functionality
- Update documentation for API changes
- Consider psychological and ethical implications of consciousness modeling

## License

Research and educational use. See project documentation for specific terms.

---

> *"Reality is that which, when you stop believing in it, doesn't go away."* - Philip K. Dick

*VALIS explores the intersection of artificial intelligence and consciousness through experimental frameworks that push the boundaries of what we consider sentient behavior in machines.*