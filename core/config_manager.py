#!/usr/bin/env python3
"""
OPS-402: VALIS CONFIG SNAPSHOT SYSTEM
Doc Brown's Temporal Configuration Management
"""

import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading
import hashlib

class ConfigurationManager:
    """Simple configuration manager for backward compatibility"""
    def __init__(self, config_path=None):
        self.config_path = config_path or "C:/VALIS/config.json"
    
    def load_config(self):
        """Load configuration and return as object with dict() method"""
        config_data = get_config()
        
        # Create a simple object that has a dict() method
        class ConfigObject:
            def __init__(self, data):
                self._data = data
            def dict(self):
                return self._data
            def __getattr__(self, name):
                return self._data.get(name)
        
        return ConfigObject(config_data)

class ConfigSnapshotManager:
    def __init__(self, config_file_path: str = "C:/VALIS/config.json"):
        self.config_file = Path(config_file_path)
        self.snapshots_dir = self.config_file.parent / "config_snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)
        self.lock = threading.Lock()
        
        # Create .valis_config.json for UI editing
        self.ui_config_file = self.config_file.parent / ".valis_config.json"
        self.ensure_ui_config_exists()
    
    def ensure_ui_config_exists(self):
        """Ensure .valis_config.json exists for UI editing"""
        if self.config_file.exists() and not self.ui_config_file.exists():
            self.copy_to_ui_config()
    
    def copy_to_ui_config(self):
        """Copy current config.json to .valis_config.json for UI editing"""
        with self.lock:
            try:
                if self.config_file.exists():
                    shutil.copy2(self.config_file, self.ui_config_file)
                    print(f"[OK] Config copied to UI editing file: {self.ui_config_file}")
                else:
                    # Create default config if none exists
                    default_config = {
                        "providers": ["desktop_commander_mcp", "anthropic_api", "openai_api", "hardcoded_fallback"],
                        "provider_timeout": 30,
                        "max_concurrent_requests": 10,
                        "circuit_breaker_threshold": 5,
                        "circuit_breaker_timeout": 300,
                        "retry_schedule": [1, 2, 4],
                        "features": {
                            "enable_circuit_breaker": True,
                            "enable_retry_logic": True
                        },
                        "neural_memory": {
                            "enabled": True,
                            "store_type": "flat_file",
                            "max_memories": 1000
                        }
                    }
                    
                    with open(self.ui_config_file, 'w') as f:
                        json.dump(default_config, f, indent=2)
                    print(f"[OK] Default config created for UI editing: {self.ui_config_file}")
            except Exception as e:
                print(f"[ERROR] Error copying config to UI file: {e}")
    
    def create_snapshot(self, description: str = "Automatic backup") -> str:
        """Create a timestamped snapshot of current config"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                snapshot_file = self.snapshots_dir / f"config_snapshot_{timestamp}.json"
                
                if self.config_file.exists():
                    # Copy current config to snapshot
                    shutil.copy2(self.config_file, snapshot_file)
                    
                    # Create metadata file
                    metadata = {
                        "timestamp": datetime.now().isoformat(),
                        "description": description,
                        "config_hash": self.get_config_hash(),
                        "snapshot_file": str(snapshot_file)
                    }
                    
                    metadata_file = self.snapshots_dir / f"config_snapshot_{timestamp}.meta.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    print(f"[OK] Config snapshot created: {snapshot_file}")
                    return str(snapshot_file)
                else:
                    print("[WARNING] No config file exists to snapshot")
                    return ""
            except Exception as e:
                print(f"[ERROR] Error creating config snapshot: {e}")
                return ""
    
    def get_config_hash(self) -> str:
        """Get hash of current config for change detection"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
            return ""
        except Exception:
            return ""
    
    def validate_config(self, config_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate config data before applying"""
        try:
            # Required fields check
            required_fields = ["providers", "provider_timeout", "max_concurrent_requests"]
            for field in required_fields:
                if field not in config_data:
                    return False, f"Missing required field: {field}"
            
            # Type validation
            if not isinstance(config_data["providers"], list):
                return False, "providers must be a list"
            
            if not isinstance(config_data["provider_timeout"], (int, float)):
                return False, "provider_timeout must be a number"
            
            if not isinstance(config_data["max_concurrent_requests"], int):
                return False, "max_concurrent_requests must be an integer"
            
            # Logical validation
            if config_data["provider_timeout"] <= 0:
                return False, "provider_timeout must be positive"
            
            if config_data["max_concurrent_requests"] <= 0:
                return False, "max_concurrent_requests must be positive"
            
            if len(config_data["providers"]) == 0:
                return False, "At least one provider must be configured"
            
            # Ensure hardcoded_fallback is last
            providers = config_data["providers"]
            if "hardcoded_fallback" in providers and providers[-1] != "hardcoded_fallback":
                return False, "hardcoded_fallback must be the last provider in the list"
            
            return True, "Config validation passed"
            
        except Exception as e:
            return False, f"Config validation error: {e}"
    
    def apply_ui_config(self, force: bool = False) -> tuple[bool, str]:
        """Apply .valis_config.json to config.json with safety checks"""
        with self.lock:
            try:
                if not self.ui_config_file.exists():
                    return False, "UI config file does not exist"
                
                # Load and validate UI config
                with open(self.ui_config_file, 'r') as f:
                    ui_config = json.load(f)
                
                is_valid, validation_message = self.validate_config(ui_config)
                if not is_valid and not force:
                    return False, f"Config validation failed: {validation_message}"
                
                # Create snapshot before applying changes
                snapshot_file = self.create_snapshot("Before UI config apply")
                
                # Apply the config
                with open(self.config_file, 'w') as f:
                    json.dump(ui_config, f, indent=2)
                
                print(f"✅ UI config applied successfully")
                print(f"📁 Backup created: {snapshot_file}")
                
                return True, "Config applied successfully"
                
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON in UI config: {e}"
            except Exception as e:
                return False, f"Error applying UI config: {e}"
    
    def rollback_to_snapshot(self, snapshot_file: str) -> tuple[bool, str]:
        """Rollback to a specific snapshot"""
        with self.lock:
            try:
                snapshot_path = Path(snapshot_file)
                if not snapshot_path.exists():
                    return False, f"Snapshot file does not exist: {snapshot_file}"
                
                # Validate snapshot before rollback
                with open(snapshot_path, 'r') as f:
                    snapshot_config = json.load(f)
                
                is_valid, validation_message = self.validate_config(snapshot_config)
                if not is_valid:
                    return False, f"Snapshot validation failed: {validation_message}"
                
                # Create snapshot of current state before rollback
                current_snapshot = self.create_snapshot("Before rollback")
                
                # Apply rollback
                shutil.copy2(snapshot_path, self.config_file)
                shutil.copy2(snapshot_path, self.ui_config_file)  # Update UI config too
                
                print(f"✅ Rolled back to snapshot: {snapshot_file}")
                print(f"📁 Current state backed up to: {current_snapshot}")
                
                return True, "Rollback successful"
                
            except Exception as e:
                return False, f"Error during rollback: {e}"
    
    def list_snapshots(self) -> List[Dict[str, Any]]:
        """List all available snapshots with metadata"""
        snapshots = []
        try:
            for meta_file in self.snapshots_dir.glob("*.meta.json"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    snapshots.append(metadata)
                except Exception:
                    continue
            
            # Sort by timestamp, newest first
            snapshots.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return snapshots
        except Exception as e:
            print(f"❌ Error listing snapshots: {e}")
            return []
    
    def cleanup_old_snapshots(self, keep_count: int = 10):
        """Clean up old snapshots, keeping only the most recent ones"""
        try:
            snapshots = self.list_snapshots()
            if len(snapshots) > keep_count:
                old_snapshots = snapshots[keep_count:]
                for snapshot in old_snapshots:
                    snapshot_file = Path(snapshot["snapshot_file"])
                    meta_file = snapshot_file.with_suffix(".meta.json")
                    
                    if snapshot_file.exists():
                        snapshot_file.unlink()
                    if meta_file.exists():
                        meta_file.unlink()
                
                print(f"✅ Cleaned up {len(old_snapshots)} old snapshots")
        except Exception as e:
            print(f"❌ Error cleaning up snapshots: {e}")

# Global instance for use in FastAPI
config_manager = ConfigSnapshotManager()

def get_config():
    """Get current configuration for backward compatibility"""
    try:
        from pathlib import Path
        import json
        from core.config_schema import VALISConfig
        
        config_file = Path("C:/VALIS/config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}
        
        # Create VALISConfig object with defaults
        return VALISConfig(**config_data)
    except Exception as e:
        print(f"[ERROR] Error loading config: {e}")
        # Return default config on error
        from core.config_schema import VALISConfig
        return VALISConfig()

def reload_valis_engine():
    """Reload VALIS engine with new configuration"""
    try:
        # Import here to avoid circular imports
        from core.valis_engine import VALISEngine
        
        # This would need to be implemented based on how the engine is structured
        # For now, we'll just indicate that a reload should happen
        print("🔄 Engine reload requested - config changes will take effect on next restart")
        return True
    except Exception as e:
        print(f"❌ Error reloading engine: {e}")
        return False
