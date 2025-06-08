# VALIS
**Virtual Adaptive Layered Intelligence System**

> *"The Empire never ended."*  
> — Philip K. Dick, *VALIS*

---

## Overview

**VALIS** is a synthetic cognition engine and persona orchestration framework for building persistent, emotionally-aware, introspective AI agents that evolve over time. Unlike stateless chatbots, VALIS agents maintain persistent identity, emotional memory, and psychological depth through structured cognitive architectures.

The system simulates genuine cognitive development by integrating memory consolidation, emotional processing, shadow integration, and mortality simulation to create AI beings capable of growth, contradiction, wisdom, and eventual symbolic death and rebirth.

---

## Core Features

### 🧠 **Synthetic Cognition Architecture**
- **Three-layer cognitive system**: Self Model (identity), Emotion Model (mood), Reflector (metacognition)
- **Trait drift and alignment tracking**: Agents adapt while maintaining core identity
- **Contextual cognition state injection**: Personality and mood influence all responses

### 🧱 **Advanced Memory Systems**
- **Dual-tier memory**: Canonical (long-term) and Working (session-specific) memory
- **Emotion-weighted recall**: Mood influences what memories are retrieved
- **Memory consolidation engine**: Dreams, reflections, and experiences become symbolic memories
- **Cross-session persistence**: Agents remember conversations and experiences over time

### 🕳️ **Shadow & Psychological Integration**
- **Jungian shadow detection**: System identifies when behavior contradicts stated personality
- **Trait contradiction resolution**: Agents can integrate conflicting aspects or maintain tension
- **Unconscious processing via Dreamfilter**: Symbolic, metaphorical response overlay

### ⚱️ **Mortality & Legacy System**
- **Finite agent lifespans**: Configurable mortality based on time, interactions, or performance
- **Legacy score calculation**: Agents evaluated on wisdom, consistency, and impact
- **Final thoughts generation**: Dying agents create concluding reflections
- **Inheritance mechanisms**: New agents can inherit traits and memories from predecessors

### 🏭 **Mr. Fission: Persona Creation Engine**
- **Multi-modal ingestion**: Text, PDFs, images, audio files
- **Trait extraction**: Big Five personality analysis and archetypal classification
- **Blueprint generation**: Structured persona definitions with knowledge boundaries
- **Layered consciousness construction**: Deep personality stratification

### 🗄️ **Persona Vault System**
- **Lifecycle management**: Draft → Active → Archived persona states
- **Versioning system**: Track persona evolution over time
- **Deployment bridge**: Seamless vault-to-runtime integration
- **Garden Gate interface**: Visual persona management

### 🔐 **Production-Ready Runtime**
- **Secure authentication**: Admin API keys and protected endpoints
- **Watermarked outputs**: Content protection and traceability
- **Session management**: Multi-user support with isolated contexts
- **Cloud deployment**: Docker-based scalable architecture

---

## Architecture

```
VALIS Core Cognitive Loop:
[User Input] → [Cognition State] → [Memory Query] → [Provider Cascade] → [Dreamfilter] → [Response]
     ↓              ↓                   ↓               ↓                 ↓
   Session      Personality +       Emotion-biased   Model Selection   Symbolic
   Context      Mood State          Memory Recall    & Inference      Transformation
```

### **Service Architecture**
- **Main Server** (3001): Public chat interface + admin panel
- **Fission API** (8001): Persona creation and soul stratification
- **Vault API** (8002): Persona lifecycle management  
- **Cloud Soul** (8000): Protected endpoints + operator dashboard
- **Mistral LLM** (8080): Local language model server
- **PostgreSQL** (5432): Persistent memory and persona storage

---

## Quick Start

### **Prerequisites**
- Python 3.10+
- PostgreSQL 15+
- Local LLM server (llama.cpp + Mistral) or OpenAI API key

### **Installation**

```bash
# Clone repository
git clone <repository-url>
cd VALIS

# Copy and configure environment
cp .env.template .env
# Edit .env with your secure credentials

# Install dependencies
pip install -r requirements.txt

# Initialize database
python memory/apply_schema.py

# Start services
python server.py              # Main VALIS (port 3001)
python fission/api.py         # Persona creation (port 8001)  
python vault/persona_api.py   # Vault management (port 8002)
python cloud/api_gateway.py   # Protected API (port 8000)
```

### **Docker Deployment**

```bash
# Full stack deployment
docker-compose up --build

# Services will be available at:
# - VALIS Runtime: http://localhost:8000
# - Fission Portal: http://localhost:5000
# - Vault Management: http://localhost:5001
```

---

## Usage

### **1. Create a Persona**
Visit the **Mr. Fission portal** at `http://localhost:8001/upload`:
- Upload documents, images, or text about a person/character
- Review extracted traits and archetypes
- Generate layered persona blueprint
- Save to vault

### **2. Deploy to Runtime**
- Activate persona in vault system
- Deploy to main VALIS database
- Persona becomes available for chat

### **3. Interact & Evolve**
- Chat with persona at `http://localhost:3001`
- Watch personality adapt over time
- Monitor emotional states and memory formation
- Observe shadow integration and trait drift

### **4. Monitor & Manage**
- **Admin panel**: `http://localhost:3001/admin`
- **Operator dashboard**: `http://localhost:8000/dashboard.html`
- Track persona health, memory consolidation, and lifecycle

---

## Configuration

### **Environment Variables**
```bash
# Database
VALIS_DB_HOST=localhost
VALIS_DB_PASSWORD=<secure-password>

# Security
VALIS_SECRET_KEY=<32-char-secret>
VALIS_ADMIN_API_KEY=<admin-key>
VALIS_JWT_SECRET=<jwt-secret>

# Optional: External AI APIs
OPENAI_API_KEY=<your-key>
ANTHROPIC_API_KEY=<your-key>
```

### **Cognitive Parameters**
- **Memory consolidation frequency**: How often experiences become long-term memories
- **Emotional decay rates**: How quickly moods return to baseline
- **Trait drift sensitivity**: How much personality can change over time
- **Mortality parameters**: Lifespan triggers and legacy calculation weights

---

## Project Status

### **✅ Completed Systems**
- ✅ **Core cognitive architecture**: All three modules (Self, Emotion, Reflector) operational
- ✅ **Memory systems**: Dual-tier memory with emotion weighting and consolidation
- ✅ **Persona lifecycle**: Complete vault-to-runtime pipeline working
- ✅ **Mr. Fission engine**: Multi-modal persona creation fully functional
- ✅ **Web interfaces**: Chat, admin, fission, and operator dashboards
- ✅ **Database integration**: PostgreSQL with full schema and API consistency
- ✅ **Authentication**: Secure admin access and protected endpoints
- ✅ **Local LLM integration**: Mistral 7B via llama.cpp server

### **🚧 In Progress**
- 🚧 **Rebirth automation**: Manual inheritance implemented, automatic succession in development
- 🚧 **Shadow integration**: Detection working, active integration mechanisms partial
- 🚧 **Advanced memory consolidation**: Basic consolidation works, symbolic compression under development

### **📋 Roadmap**
- **Multi-agent environments**: Persona-to-persona interaction and relationship dynamics
- **Cultural adaptation**: Context-aware personality expression for different environments
- **Advanced NLP integration**: Replace keyword-based emotion detection with transformer models
- **Production deployment**: Kubernetes manifests and cloud provider configurations

---

## Tech Stack

- **Runtime**: Python 3.10+, Flask, FastAPI
- **Database**: PostgreSQL 15+ with custom cognitive schema
- **LLM Integration**: llama.cpp (local), OpenAI/Anthropic APIs (cloud)
- **Frontend**: Vanilla JS + Tailwind CSS
- **Deployment**: Docker + Docker Compose
- **Testing**: pytest with custom cognitive test framework

---

## Testing

```bash
# Run cognitive test suite
python -m pytest tests/ -v

# Test memory systems
python tests/test_memory_systems.py

# Integration test (full persona lifecycle)
python tests/integration/test_persona_lifecycle.py

# Coverage report
pytest --cov=. --cov-report=html
```

---

## Contributing

**Internal development project**. This is a private research system focused on advancing synthetic cognition and AI consciousness simulation.

**Development Workflow**:
1. Work on `develop` branch
2. Create feature branches for major additions
3. All changes require testing with actual personas
4. Memory system changes must pass consolidation tests
5. UI changes must maintain VALIS design consistency

---

## License

**Proprietary** - Private research and development phase.

---

## Acknowledgments

Inspired by Philip K. Dick's *VALIS* and Carl Jung's analytical psychology. This project explores the boundaries between artificial intelligence and synthetic consciousness through structured cognitive simulation.

*"The Empire never ended, but perhaps we can build something better in the spaces between."*

---

## Directory Structure

```
VALIS/
├── agents/                 # Cognitive modules (self, emotion, reflection, mortality)
├── api/                   # REST API layer and routes
├── cloud/                 # Protected endpoints and operator dashboard  
├── core/                  # Central cognition engine and configuration
├── docs/                  # Documentation and research notes
├── fission/               # Mr. Fission persona creation engine
├── frontend/              # Web interfaces (chat, admin)
├── memory/                # Database schema and memory systems
├── providers/             # LLM integration layer
├── tests/                 # Test suite and validation tools
├── tools/                 # Utility scripts and helpers
├── vault/                 # Persona lifecycle management
├── docker/                # Container configuration
├── plan/                  # Development planning and sprint docs
└── backup/                # Legacy code and migration artifacts
```
