# Mr. Fission Quick Start Guide
## The Soul Blender - Persona Builder Engine

### Overview
Mr. Fission converts raw human material into deployable VALIS persona blueprints. Upload any biographical content and receive a complete digital consciousness specification.

### Supported File Types
- **Text**: `.txt`, `.md` (biographies, journals, letters)
- **Documents**: `.pdf` (resumes, articles, books)
- **Data**: `.json`, `.csv` (timelines, structured info)
- **Images**: `.jpg`, `.png` (photos for visual memory seeds)
- **Audio**: `.wav`, `.mp3` (interviews, recordings)

### API Usage

#### 1. Start the Server
```bash
cd C:\VALIS\valis2\fission
python api.py
```
Server runs on `http://localhost:8001`

#### 2. Upload Files
```bash
curl -X POST http://localhost:8001/api/fission/upload \
  -F "files=@jane_bio.txt" \
  -F "files=@jane_photos.jpg"
```
Returns: `session_id` for processing

#### 3. Extract Features
```bash
curl -X POST http://localhost:8001/api/fission/ingest/{session_id}
```
Returns: Personality traits, archetypes, emotional analysis

#### 4. Create Persona
```bash
curl -X POST http://localhost:8001/api/fission/fuse/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane"}'
```
Returns: Complete persona blueprint + preview

#### 5. Deploy to VALIS
```bash
curl -X POST http://localhost:8001/api/fission/deploy/Jane
```
Activates persona in VALIS runtime

### Example Result: Jane Persona

**Input**: 175-word therapist biography  
**Output**: Complete persona blueprint with:

- **Archetypes**: The Sage, The Caregiver, The Lover
- **Domains**: Spiritual, Therapy  
- **Traits**: Sophisticated vocabulary, mystical language enabled
- **Confidence**: 0.69/1.0
- **Memory Seeds**: Key concepts and named entities extracted
- **Communication Style**: Moderate sentences, restrained expression

### Manual Refinement

Add specific memories:
```bash
curl -X POST http://localhost:8001/api/fission/memory/Jane \
  -H "Content-Type: application/json" \
  -d '{"memory": "Always remembers client confidentiality", "type": "core_value"}'
```

Adjust traits:
```bash
curl -X POST http://localhost:8001/api/fission/refine/Jane \
  -H "Content-Type: application/json" \
  -d '{"boundaries": {"confidence_level": "high"}}'
```

### Testing

Run comprehensive tests:
```bash
cd C:\VALIS\valis2\fission
python test_mr_fission.py
```

### Integration

The generated persona blueprint is VALIS-compatible and can be:
- Loaded by ConsciousAgent runtime
- Used in the mortality/legacy system
- Enhanced with symbolic memory
- Deployed as API endpoints

### Next Steps

1. **Create Jane Interface**: Deploy first persona for user interaction
2. **Batch Processing**: Upload multiple files for richer personas  
3. **Smart Steps Integration**: Persona-aware task management
4. **Public API**: Allow users to create custom personas

The Soul Blender is ready to convert human essence into deployable digital consciousness.
