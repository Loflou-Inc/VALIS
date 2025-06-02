#!/usr/bin/env python3
"""
CHAOS ENGINEERING: Configuration Corruption Testing
"""

import asyncio
import sys
import os
import json
sys.path.append('C:\\VALIS')

async def chaos_config_test():
    print("CHAOS: Configuration Corruption Testing")
    print("=" * 50)
    
    # Backup original config
    config_path = 'C:\\VALIS\\config.json'
    backup_path = 'C:\\VALIS\\config_backup.json'
    
    try:
        # Read original config
        with open(config_path, 'r') as f:
            original_config = f.read()
        
        # Save backup
        with open(backup_path, 'w') as f:
            f.write(original_config)
        
        # Test 1: Corrupted JSON
        print("Test 1: Corrupted JSON file")
        with open(config_path, 'w') as f:
            f.write('{ "invalid": json, missing bracket')
        
        # Try to load VALIS with corrupted config
        try:
            from core.valis_engine import VALISEngine
            engine = VALISEngine()
            print("DANGER: System loaded with corrupted config!")
        except Exception as e:
            print(f"GOOD: System rejected corrupted config: {str(e)[:100]}...")
        
        # Test 2: Missing required keys
        print("\nTest 2: Missing required configuration keys")
        with open(config_path, 'w') as f:
            json.dump({"incomplete": "config"}, f)
        
        try:
            # Force reload
            if 'core.valis_engine' in sys.modules:
                del sys.modules['core.valis_engine']
            from core.valis_engine import VALISEngine
            engine = VALISEngine()
            print("System status: Loaded with incomplete config")
        except Exception as e:
            print(f"System rejected incomplete config: {str(e)[:100]}...")
            
    finally:
        # Restore original config
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                original = f.read()
            with open(config_path, 'w') as f:
                f.write(original)
            os.remove(backup_path)
        print("\nConfig restored")

if __name__ == "__main__":
    asyncio.run(chaos_config_test())
