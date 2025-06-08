"""
Test configuration for VALIS tests - NO DATABASE REQUIRED
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def test_db():
    """
    Test database client that doesn't require actual PostgreSQL connection
    """
    db_mock = Mock()
    
    # Mock common database operations
    db_mock.query.return_value = []
    db_mock.execute.return_value = 1
    db_mock.insert.return_value = "test-uuid-12345"
    
    # Mock connection context manager
    conn_mock = Mock()
    db_mock.get_connection.return_value.__enter__ = Mock(return_value=conn_mock)
    db_mock.get_connection.return_value.__exit__ = Mock(return_value=False)
    
    return db_mock

@pytest.fixture
def mock_db(test_db):
    """
    Alias for test_db fixture for backward compatibility
    """
    return test_db

@pytest.fixture
def sample_persona():
    """Sample persona data for testing"""
    return {
        "id": "test-persona-123",
        "name": "TestPersona",
        "traits": {
            "confidence": 0.7,
            "warmth": 0.6,
            "analytical": 0.8
        },
        "alignment_score": 0.75
    }

@pytest.fixture
def sample_emotion_state():
    """Sample emotion state for testing"""
    return {
        "session_id": "test-session-456", 
        "mood": "happy",
        "arousal_level": 6,
        "emotion_tags": ["positive", "energetic"],
        "valence": 0.7,
        "confidence": 0.8
    }

@pytest.fixture
def mock_tool_feedback():
    """Mock tool feedback for emotion testing"""
    return {
        "all_success": [{"success": True, "tool": "search"}],
        "all_failure": [{"success": False, "tool": "analyze", "error": "timeout"}],
        "mixed": [
            {"success": True, "tool": "search"},
            {"success": False, "tool": "analyze", "error": "timeout"}
        ],
        "empty": []
    }

# Patch the database module to avoid connection issues during testing
def pytest_configure(config):
    """Configure pytest to avoid database connection issues"""
    
    # Mock the database module at import time
    try:
        import memory.db as db_module
        
        # Replace the global db instance with a mock
        mock_db_instance = Mock()
        mock_db_instance.query.return_value = []
        mock_db_instance.execute.return_value = 1
        mock_db_instance.insert.return_value = "test-uuid"
        
        # Replace the DatabaseProxy with our mock
        db_module.db = mock_db_instance
    except ImportError:
        pass  # Module not yet imported, that's fine
