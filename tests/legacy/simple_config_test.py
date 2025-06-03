"""Simple test for configurability"""
import sys
from pathlib import Path

# Add VALIS root to path
valis_root = Path(__file__).parent
sys.path.insert(0, str(valis_root))

from core.config_validator import VALISConfigValidator

def test_config():
    print("Testing VALIS Configuration...")
    
    # Load and validate config
    config = VALISConfigValidator.validate_and_load_config('config.json')
    
    print("Configuration loaded successfully!")
    print(f"   Max concurrent requests: {config.get('max_concurrent_requests')}")
    print(f"   Provider timeout: {config.get('provider_timeout')}")
    print(f"   Circuit breaker threshold: {config.get('circuit_breaker_threshold')}")
    print(f"   Circuit breaker timeout: {config.get('circuit_breaker_timeout')}")
    print(f"   Retry schedule: {config.get('retry_schedule')}")
    print(f"   Session timeout: {config.get('session_timeout')}")
    
    print("Task 4 Configuration validation - SUCCESS!")

if __name__ == "__main__":
    test_config()