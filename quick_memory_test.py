#!/usr/bin/env python3
"""
VALIS Memory Test - Quick CLI
Direct test of memory without event loop issues
"""

import sys
from pathlib import Path

# Add VALIS root to path
sys.path.append(str(Path(__file__).parent))

try:
    from valis_inference_pipeline import VALISInferencePipeline
    print("SUCCESS: Pipeline module imported")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)

def quick_test():
    """Quick test with single interaction"""
    try:
        pipeline = VALISInferencePipeline()
        print("SUCCESS: Pipeline initialized")
        
        # Test simple CLI interaction  
        result = pipeline.run_memory_aware_chat(
            persona_id="marty",
            client_id="cli_test",
            user_message="Hello, can you remember this conversation? #working_memory"
        )
        
        print("\\n" + "="*50)
        print("PIPELINE TEST RESULT")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Provider: {result['provider']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Response length: {len(result['response'])} chars")
        print(f"Tags processed: {result['tags_processed']}")
        
        # Check memory usage
        memory = result['memory_used']
        print(f"\\nMemory layers:")
        print(f"- Core biography: {len(memory.get('core_biography', []))} entries")
        print(f"- Canon: {len(memory.get('canonized_identity', []))} entries") 
        print(f"- Client facts: {len(memory.get('client_profile', {}).get('facts', {}))}")
        print(f"- Working memory: {len(memory.get('working_memory', []))} entries")
        
        print(f"\\nFirst 100 chars of response:")
        print(f'"{result["response"][:100]}..."')
        
        return True
        
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    print(f"\\nTest {'PASSED' if success else 'FAILED'}")
