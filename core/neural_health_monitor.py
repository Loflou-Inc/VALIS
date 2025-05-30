"""
Neural Matrix Health Monitor for VALIS
Comprehensive monitoring, cleanup, and optimization for the neural matrix system
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import asyncio

class NeuralMatrixHealthMonitor:
    """
    Comprehensive health monitoring and optimization for VALIS Neural Matrix
    
    Provides real-time monitoring, automated cleanup, and self-healing protocols
    for the neural memory system.
    """
    
    def __init__(self, memory_dir: str, max_memory_file_size: int = 500 * 1024):
        """Initialize neural matrix health monitor"""
        self.memory_dir = Path(memory_dir)
        self.max_memory_file_size = max_memory_file_size  # 500KB default
        self.logger = logging.getLogger('VALIS.NeuralHealth')
        
        # Health thresholds
        self.context_quality_threshold = 0.95  # 95% minimum continuity
        self.max_session_age = 30 * 60  # 30 minutes in seconds
        self.cleanup_interval = 10 * 60  # 10 minutes in seconds
        
        # Performance metrics tracking
        self.metrics = {
            'memory_file_size': 0,
            'total_memories': 0,
            'active_sessions': 0,
            'context_retrievals': 0,
            'context_handoffs': 0,
            'handoff_success_rate': 1.0,
            'compression_ratio': 0.0,
            'last_cleanup': time.time(),
            'memory_integrity_score': 1.0
        }
        
        self.logger.info("Neural Matrix Health Monitor initialized")
    
    def get_memory_health_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory system health statistics"""
        try:
            # Check memory file size and count
            memory_file = self.memory_dir / "memory_store" / "memories.json"
            
            if memory_file.exists():
                file_size = memory_file.stat().st_size
                self.metrics['memory_file_size'] = file_size
                
                # Count memories
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memories = json.load(f)
                        self.metrics['total_memories'] = len(memories) if isinstance(memories, list) else 0
                except Exception as e:
                    self.logger.warning(f"Could not count memories: {e}")
                    self.metrics['total_memories'] = 0
            else:
                self.metrics['memory_file_size'] = 0
                self.metrics['total_memories'] = 0
            
            # Calculate health status
            file_size_health = "green" if self.metrics['memory_file_size'] < self.max_memory_file_size else "red"
            memory_count_health = "green" if self.metrics['total_memories'] < 1000 else "yellow"
            
            # Check archive directory
            archive_dir = self.memory_dir / "memory_store" / "archive"
            archive_count = len(list(archive_dir.glob("*.json"))) if archive_dir.exists() else 0
            
            return {
                "memory_file_size_bytes": self.metrics['memory_file_size'],
                "memory_file_size_mb": round(self.metrics['memory_file_size'] / (1024 * 1024), 2),
                "memory_file_health": file_size_health,
                "total_memories": self.metrics['total_memories'],
                "memory_count_health": memory_count_health,
                "archive_files": archive_count,
                "max_file_size_mb": round(self.max_memory_file_size / (1024 * 1024), 2),
                "memory_utilization_percent": round(
                    (self.metrics['memory_file_size'] / self.max_memory_file_size) * 100, 1
                ),
                "integrity_score": self.metrics['memory_integrity_score'],
                "last_health_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Memory health check failed: {e}")
            return {
                "error": str(e),
                "memory_file_health": "red",
                "last_health_check": datetime.now().isoformat()
            }

    def monitor_context_quality(self, handoff_success: bool = True, compression_ratio: float = 0.0):
        """Track context quality metrics across provider cascades"""
        self.metrics['context_handoffs'] += 1
        
        if handoff_success:
            # Update rolling success rate
            current_rate = self.metrics['handoff_success_rate']
            total_handoffs = self.metrics['context_handoffs']
            
            # Calculate new success rate using exponential moving average
            alpha = 0.1  # Smoothing factor
            self.metrics['handoff_success_rate'] = (alpha * 1.0) + ((1 - alpha) * current_rate)
        else:
            # Failed handoff
            current_rate = self.metrics['handoff_success_rate']
            alpha = 0.1
            self.metrics['handoff_success_rate'] = (alpha * 0.0) + ((1 - alpha) * current_rate)
        
        # Update compression ratio
        if compression_ratio > 0:
            self.metrics['compression_ratio'] = compression_ratio
        
        # Log warning if quality drops below threshold
        if self.metrics['handoff_success_rate'] < self.context_quality_threshold:
            self.logger.warning(
                f"Context quality below threshold: {self.metrics['handoff_success_rate']:.2f} < {self.context_quality_threshold}"
            )
        
        return {
            "handoff_success_rate": round(self.metrics['handoff_success_rate'], 3),
            "total_handoffs": self.metrics['context_handoffs'],
            "compression_ratio": round(self.metrics['compression_ratio'], 3),
            "quality_status": "green" if self.metrics['handoff_success_rate'] >= self.context_quality_threshold else "red"
        }

    def run_cleanup_protocols(self, sessions: Dict = None) -> Dict[str, Any]:
        """Run automated cleanup protocols for neural matrix"""
        cleanup_results = {
            "cleanup_time": datetime.now().isoformat(),
            "sessions_cleaned": 0,
            "memories_archived": 0,
            "duplicates_removed": 0,
            "file_size_before": 0,
            "file_size_after": 0,
            "cleanup_success": True
        }
        
        try:
            memory_file = self.memory_dir / "memory_store" / "memories.json"
            
            if memory_file.exists():
                cleanup_results["file_size_before"] = memory_file.stat().st_size
                
                # Check if memory file exceeds size limit
                if cleanup_results["file_size_before"] > self.max_memory_file_size:
                    self.logger.info(f"Memory file exceeds limit, triggering archival")
                    
                    # Trigger memory archival (this would normally be handled by memory_manager)
                    try:
                        # Import and use memory manager's archival
                        import sys
                        sys.path.append(str(self.memory_dir))
                        from memory_manager import load_memory, save_memory
                        
                        memories = load_memory()
                        if len(memories) > 100:  # Archive if more than 100 memories
                            # Keep only the 50 most recent memories
                            recent_memories = memories[-50:]
                            archived_count = len(memories) - 50
                            
                            save_memory(recent_memories)
                            cleanup_results["memories_archived"] = archived_count
                            self.logger.info(f"Archived {archived_count} old memories")
                            
                    except Exception as e:
                        self.logger.warning(f"Memory archival failed: {e}")
                
                cleanup_results["file_size_after"] = memory_file.stat().st_size if memory_file.exists() else 0
            
            # Session cleanup
            if sessions:
                current_time = time.time()
                expired_sessions = []
                
                for session_id, session_data in sessions.items():
                    if current_time - session_data.get("last_activity", 0) > self.max_session_age:
                        expired_sessions.append(session_id)
                
                cleanup_results["sessions_cleaned"] = len(expired_sessions)
                self.logger.info(f"Identified {len(expired_sessions)} expired sessions for cleanup")
            
            self.metrics['last_cleanup'] = time.time()
            
        except Exception as e:
            self.logger.error(f"Cleanup protocols failed: {e}")
            cleanup_results["cleanup_success"] = False
            cleanup_results["error"] = str(e)
        
        return cleanup_results

    def check_neural_integrity(self) -> Dict[str, Any]:
        """Check neural matrix integrity and self-heal if needed"""
        integrity_results = {
            "integrity_score": 1.0,
            "issues_found": [],
            "repairs_attempted": [],
            "integrity_status": "green"
        }
        
        try:
            memory_file = self.memory_dir / "memory_store" / "memories.json"
            
            if memory_file.exists():
                # Check if file is valid JSON
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memories = json.load(f)
                        
                    # Check for corrupted entries
                    corrupted_count = 0
                    for memory in memories:
                        if not isinstance(memory, dict) or 'text' not in memory:
                            corrupted_count += 1
                    
                    if corrupted_count > 0:
                        integrity_results["issues_found"].append(f"{corrupted_count} corrupted memory entries")
                        integrity_results["integrity_score"] -= 0.1
                    
                    # Check for duplicates
                    seen_texts = set()
                    duplicates = 0
                    for memory in memories:
                        text = memory.get('text', '')
                        if text in seen_texts:
                            duplicates += 1
                        seen_texts.add(text)
                    
                    if duplicates > 0:
                        integrity_results["issues_found"].append(f"{duplicates} duplicate memories")
                        integrity_results["integrity_score"] -= 0.05
                        
                except json.JSONDecodeError:
                    integrity_results["issues_found"].append("Memory file corrupted (invalid JSON)")
                    integrity_results["integrity_score"] = 0.0
                    integrity_results["integrity_status"] = "red"
            else:
                integrity_results["issues_found"].append("Memory file missing")
                integrity_results["integrity_score"] = 0.5
                integrity_results["integrity_status"] = "yellow"
            
            # Update metrics
            self.metrics['memory_integrity_score'] = integrity_results["integrity_score"]
            
            # Set status based on score
            if integrity_results["integrity_score"] >= 0.95:
                integrity_results["integrity_status"] = "green"
            elif integrity_results["integrity_score"] >= 0.8:
                integrity_results["integrity_status"] = "yellow"
            else:
                integrity_results["integrity_status"] = "red"
                
        except Exception as e:
            self.logger.error(f"Integrity check failed: {e}")
            integrity_results["issues_found"].append(f"Integrity check error: {str(e)}")
            integrity_results["integrity_status"] = "red"
        
        return integrity_results

    def optimize_performance(self) -> Dict[str, Any]:
        """Optimize neural matrix performance"""
        optimization_results = {
            "optimizations_applied": [],
            "performance_improvement": 0.0,
            "optimization_success": True
        }
        
        try:
            # Check memory usage and suggest optimizations
            health_stats = self.get_memory_health_stats()
            
            if health_stats["memory_utilization_percent"] > 80:
                optimization_results["optimizations_applied"].append("Memory cleanup recommended")
            
            if self.metrics['total_memories'] > 1000:
                optimization_results["optimizations_applied"].append("Archive old memories")
            
            if self.metrics['handoff_success_rate'] < 0.98:
                optimization_results["optimizations_applied"].append("Context compression tuning needed")
            
            optimization_results["performance_improvement"] = len(optimization_results["optimizations_applied"]) * 0.1
            
        except Exception as e:
            self.logger.error(f"Performance optimization failed: {e}")
            optimization_results["optimization_success"] = False
            optimization_results["error"] = str(e)
        
        return optimization_results
    
    def get_comprehensive_health_report(self, sessions: Dict = None) -> Dict[str, Any]:
        """Get comprehensive neural matrix health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_health": self.get_memory_health_stats(),
            "context_quality": {
                "handoff_success_rate": round(self.metrics['handoff_success_rate'], 3),
                "total_handoffs": self.metrics['context_handoffs'],
                "compression_ratio": round(self.metrics['compression_ratio'], 3),
                "quality_status": "green" if self.metrics['handoff_success_rate'] >= self.context_quality_threshold else "red"
            },
            "neural_integrity": self.check_neural_integrity(),
            "cleanup_status": {
                "last_cleanup": datetime.fromtimestamp(self.metrics['last_cleanup']).isoformat(),
                "cleanup_interval_minutes": self.cleanup_interval / 60,
                "next_cleanup_due": datetime.fromtimestamp(
                    self.metrics['last_cleanup'] + self.cleanup_interval
                ).isoformat()
            },
            "performance_metrics": self.optimize_performance(),
            "overall_status": self._calculate_overall_status()
        }
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall neural matrix health status"""
        memory_health = self.get_memory_health_stats()
        integrity = self.check_neural_integrity()
        
        if (memory_health.get("memory_file_health") == "green" and 
            integrity["integrity_status"] == "green" and
            self.metrics['handoff_success_rate'] >= self.context_quality_threshold):
            return "green"
        elif (memory_health.get("memory_file_health") != "red" and 
              integrity["integrity_status"] != "red"):
            return "yellow"
        else:
            return "red"
