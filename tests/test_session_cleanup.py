"""Test session cleanup functionality for Task 2.2"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from valis_engine import VALISEngine
import time

def test_session_cleanup():
    print("Testing session cleanup functionality...")
    
    # Create engine
    engine = VALISEngine()
    
    # Manually create some test sessions
    engine.sessions["test_session_old"] = {
        "created": time.time() - 2000,  # Very old session
        "last_activity": time.time() - 2000,
        "request_count": 5,
        "last_persona": "jane",
        "conversation_summary": []
    }
    
    engine.sessions["test_session_recent"] = {
        "created": time.time() - 60,  # Recent session 
        "last_activity": time.time() - 60,
        "request_count": 2,
        "last_persona": "jane", 
        "conversation_summary": []
    }
    
    print(f"Sessions before cleanup: {len(engine.sessions)}")
    print(f"Session IDs: {list(engine.sessions.keys())}")
    
    # Run cleanup
    expired_count = engine.cleanup_expired_sessions()
    
    print(f"Sessions after cleanup: {len(engine.sessions)}")
    print(f"Expired sessions cleaned: {expired_count}")
    print(f"Remaining session IDs: {list(engine.sessions.keys())}")
    
    # Verify old session was removed and recent one remains
    if "test_session_old" not in engine.sessions and "test_session_recent" in engine.sessions:
        print("SUCCESS: Session cleanup working correctly")
        return True
    else:
        print("ERROR: Session cleanup not working as expected")
        return False

if __name__ == "__main__":
    test_session_cleanup()
