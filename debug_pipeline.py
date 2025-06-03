#!/usr/bin/env python3
"""
Debug Pipeline Integration
Simple test to isolate the pipeline issue
"""

import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

def test_pipeline_directly():
    """Test the pipeline directly without Flask"""
    print("=== TESTING PIPELINE DIRECTLY ===")
    
    try:
        from valis_inference_pipeline import VALISInferencePipeline
        print("SUCCESS: Imported VALISInferencePipeline")
        
        pipeline = VALISInferencePipeline()
        print("SUCCESS: Created pipeline instance")
        
        result = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="debug_test",
            user_message="Hello, this is a direct test",
            session_id="debug_session"
        )
        
        print("SUCCESS: Pipeline executed")
        print(f"Response: {result['response']}")
        print(f"Provider: {result['provider']}")
        print(f"Success: {result['success']}")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_components():
    """Test backend component imports"""
    print("\\n=== TESTING BACKEND COMPONENTS ===")
    
    try:
        from core.valis_engine import VALISEngine
        print("SUCCESS: VALISEngine import")
        
        from core.valis_memory import MemoryRouter
        print("SUCCESS: MemoryRouter import")
        
        from core.persona_router import PersonaRouter
        print("SUCCESS: PersonaRouter import")
        
        from valis_inference_pipeline import VALISInferencePipeline
        print("SUCCESS: VALISInferencePipeline import")
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    components_ok = test_backend_components()
    pipeline_ok = test_pipeline_directly()
    
    if components_ok and pipeline_ok:
        print("\\nSUCCESS: All components working")
    else:
        print("\\nFAILED: Component issues detected")
