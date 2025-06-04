# VALIS 2.0 Public Chat - Usage Guide

## Quick Start

1. **Start the VALIS server:**
   ```bash
   cd C:\VALIS\valis2
   python server.py
   ```
   Server will start on http://localhost:3001

2. **Open the frontend:**
   Open `C:\VALIS\valis2\frontend\index.html` in your web browser

3. **Start chatting:**
   - Interface auto-initializes with anonymous session
   - Gets assigned a random persona (Kai, Luna, or Jane)
   - Your session persists across browser refreshes
   - All conversations are stored and remembered

## Features

### Anonymous Persistence
- Each user gets a unique UUID stored in localStorage
- Memory persists across browser sessions
- No login required - just start chatting

### Persona-Aware AI
- **Kai the Coach:** Motivational, goal-focused (balanced mode)
- **Luna the Therapist:** Calm, empathetic (full context mode)
- **Jane Thompson:** Professional HR expert (tight mode)

### Memory System
- Conversations stored in working memory
- Persona-specific knowledge base access
- Client-specific fact learning and retention

## API Endpoints

### Session Management
- `POST /api/init_session` - Initialize or restore session
- `GET /api/available_personas` - List all personas
- `GET /api/persona_info/<id>` - Get persona details

### Chat
- `POST /api/chat` - Send message, get AI response
- Requires: client_id, persona_id, message
- Returns: response, provider_used, metadata

### Health
- `GET /api/health` - Check server status

## Deployment Notes

- Server runs on port 3001 by default
- Frontend uses localhost:3001 for API calls
- CORS enabled for cross-origin requests
- PostgreSQL required for memory persistence

## Architecture

```
Browser (Frontend) -> Flask Server (Backend) -> VALIS Core -> Local LLM/APIs
     |                       |                      |
localStorage              PostgreSQL            Memory System
```

Memory flows: Client ID -> Persona Context -> Working Memory -> LLM -> Response -> Stored
