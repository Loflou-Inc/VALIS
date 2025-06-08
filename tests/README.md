# VALIS Test Infrastructure - Sprint 1.1

## Overview
This directory contains the comprehensive test suite for VALIS (Virtual Adaptive Layered Intelligence System), implementing Sprint 1.1 requirements for test infrastructure and baseline coverage.

## Test Structure

### Core Test Files
- `test_synthetic_cognition.py` - Tests for AgentSelfModel, AgentEmotionModel, AgentReflector
- `test_memory_consolidation.py` - Tests for MemoryConsolidationEngine 
- `test_mortality_engine.py` - Tests for MortalityEngine lifecycle functionality
- `test_uuid_fix.py` - UUID handling verification tests

### Configuration
- `conftest.py` - Pytest fixtures and test database setup
- `pytest.ini` - Pytest configuration and coverage settings
- `run_tests.py` - Local test runner script

### Test Data
- `fixtures/test_personas.json` - Sample persona data for testing
- `fixtures/test_memories.json` - Sample memory data for consolidation tests

## Test Categories

### Unit Tests (default)
Fast tests focusing on individual module functionality:
```bash
pytest tests/ -m "not slow"
```

### Integration Tests (marked as 'slow')  
Comprehensive tests involving multiple modules:
```bash
pytest tests/ -m "slow"
```

## Coverage Requirements
- **Minimum Coverage**: 25% (Sprint 1.1 baseline)
- **Target Modules**: agents/, memory/, core/
- **Coverage Reports**: HTML and terminal output

## Running Tests

### Local Development
```bash
# Run all tests with coverage
python tests/run_tests.py

# Run specific test file
pytest tests/test_memory_consolidation.py -v

# Run with coverage report
pytest --cov=agents --cov=memory --cov-report=html
```

### CI/CD
Tests run automatically on:
- Push to main/develop branches
- Pull requests
- Multiple Python versions (3.9, 3.10, 3.11)

## Test Database
- Uses isolated SQLite databases for each test
- Automatic cleanup after each test
- Mocked database operations for unit tests
- Real database integration for slow tests

## Key Testing Principles

1. **Isolation**: Each test runs with fresh database state
2. **Mocking**: External dependencies are mocked appropriately  
3. **Fixtures**: Reusable test data via pytest fixtures
4. **Fast by Default**: Unit tests run quickly, integration tests marked as slow
5. **Coverage Focused**: Tests target critical functionality in core modules

## Sprint 1.1 Deliverables ✓

- [x] Test infrastructure with pytest framework
- [x] Baseline 25% code coverage
- [x] Tests for MemoryConsolidationEngine and MortalityEngine
- [x] CI/CD pipeline via GitHub Actions
- [x] Isolated test database setup
- [x] Test fixtures and sample data
- [x] Local test runner for development

## Next Steps (Sprint 1.2+)
- Expand test coverage to 50%+
- Add integration tests for full agent lifecycle
- Performance testing for memory consolidation
- Security testing for API endpoints
