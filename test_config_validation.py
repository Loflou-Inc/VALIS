#!/usr/bin/env python3
"""Test configuration validation"""

from core.config_schema import VALISConfig, PerformanceConfig
from pydantic import ValidationError

# Test 1: Valid configuration
try:
    config = VALISConfig(performance=PerformanceConfig(max_concurrent_requests=10))
    print("[PASS] Valid config created successfully")
except ValidationError as e:
    print(f"[FAIL] Valid config failed: {e}")

# Test 2: Invalid configuration (too high concurrency)
try:
    config = VALISConfig(performance=PerformanceConfig(max_concurrent_requests=200))
    print("[FAIL] Invalid config created (should have failed)")
except ValidationError as e:
    print("[PASS] Invalid config properly rejected:", str(e).split('\n')[0])

# Test 3: Check default values
config = VALISConfig()
print(f"[INFO] Default values: concurrent={config.performance.max_concurrent_requests}, timeout={config.performance.provider_timeout}")
