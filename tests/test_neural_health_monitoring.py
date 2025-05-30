"""
Comprehensive Neural Matrix Health Monitoring Test - Task 2.4
Tests all health monitoring, cleanup, and optimization features
"""

import sys
import os
import asyncio
import time
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from valis_engine import VALISEngine

async def test_neural_health_monitoring():
    print("=" * 70)
    print("NEURAL MATRIX HEALTH MONITORING TEST - TASK 2.4")
    print("Testing comprehensive health monitoring and optimization")
    print("=" * 70)
    
    # Initialize VALIS engine
    print("\n1. INITIALIZING VALIS WITH NEURAL HEALTH MONITORING...")
    engine = VALISEngine()
    
    # Check if neural health monitor is available
    health_monitor_available = engine.neural_health_monitor is not None
    print(f"   Neural Health Monitor Available: {health_monitor_available}")
    
    if not health_monitor_available:
        print("   WARNING: Neural Health Monitor not available - skipping advanced tests")
        return False
    
    # Test 2: Basic health dashboard
    print("\n2. TESTING NEURAL HEALTH DASHBOARD...")
    dashboard = engine.get_neural_health_dashboard()
    print(f"   Dashboard Status: {dashboard.get('overall_status', 'unknown')}")
    print(f"   Memory Health: {dashboard.get('memory_health', {}).get('memory_file_health', 'unknown')}")
    print(f"   Neural Integrity: {dashboard.get('neural_integrity', {}).get('integrity_status', 'unknown')}")
    
    # Test 3: Create some activity and test session tracking
    print("\n3. TESTING SESSION TRACKING AND HEALTH METRICS...")
    session_id = f"health_test_{int(time.time())}"
    
    # Create multiple interactions to build metrics
    for i in range(3):
        result = await engine.get_persona_response(
            persona_id="jane",
            message=f"Health monitoring test message {i+1}",
            session_id=session_id
        )
        print(f"   Interaction {i+1}: {result.get('success')}")
        await asyncio.sleep(0.2)
    
    # Test 4: Check updated health metrics
    print("\n4. CHECKING UPDATED HEALTH METRICS...")
    updated_dashboard = engine.get_neural_health_dashboard()
    context_quality = updated_dashboard.get('context_quality', {})
    print(f"   Context Handoffs: {context_quality.get('total_handoffs', 0)}")
    print(f"   Handoff Success Rate: {context_quality.get('handoff_success_rate', 0)}")
    print(f"   Quality Status: {context_quality.get('quality_status', 'unknown')}")
    
    # Test 5: Test cleanup protocols
    print("\n5. TESTING CLEANUP PROTOCOLS...")
    cleanup_count = engine.cleanup_expired_sessions()
    print(f"   Expired Sessions Cleaned: {cleanup_count}")
    
    # Test 6: Test comprehensive health check
    print("\n6. RUNNING COMPREHENSIVE HEALTH CHECK...")
    health_check = engine.run_neural_health_check()
    integrity = health_check.get('integrity', {})
    optimization = health_check.get('optimization', {})
    cleanup = health_check.get('cleanup', {})
    
    print(f"   Integrity Score: {integrity.get('integrity_score', 0)}")
    print(f"   Integrity Status: {integrity.get('integrity_status', 'unknown')}")
    print(f"   Optimizations Applied: {len(optimization.get('optimizations_applied', []))}")
    print(f"   Cleanup Success: {cleanup.get('cleanup_success', False)}")
    
    # Test 7: Test overall system health
    print("\n7. TESTING OVERALL SYSTEM HEALTH...")
    system_health = engine.health_check()
    print(f"   System Status: {system_health.get('status', 'unknown')}")
    print(f"   Active Sessions: {system_health.get('active_sessions', 0)}")
    print(f"   Neural Matrix Status: {system_health.get('neural_matrix_health', {}).get('overall_status', 'unknown')}")
    
    # Success criteria
    success = (
        health_monitor_available and
        dashboard.get('overall_status') in ['green', 'yellow'] and
        context_quality.get('handoff_success_rate', 0) > 0.9 and
        integrity.get('integrity_score', 0) > 0.8
    )
    
    print(f"\n{'='*70}")
    print("TASK 2.4 TEST RESULTS")
    print(f"{'='*70}")
    print(f"Neural Health Monitor: {'OPERATIONAL' if health_monitor_available else 'FAILED'}")
    print(f"Health Dashboard: {'OPERATIONAL' if dashboard.get('overall_status') in ['green', 'yellow'] else 'ISSUES'}")
    print(f"Context Quality: {'GOOD' if context_quality.get('handoff_success_rate', 0) > 0.9 else 'NEEDS_ATTENTION'}")
    print(f"Neural Integrity: {'GOOD' if integrity.get('integrity_score', 0) > 0.8 else 'NEEDS_ATTENTION'}")
    print(f"Cleanup Protocols: {'OPERATIONAL' if cleanup.get('cleanup_success', False) else 'ISSUES'}")
    
    if success:
        print("\nSUCCESS: Neural Matrix Health Monitoring & Optimization FULLY OPERATIONAL!")
    else:
        print("\nPARTIAL SUCCESS: Some neural health features need attention")
    
    return success

async def main():
    """Run comprehensive neural health monitoring tests"""
    try:
        success = await test_neural_health_monitoring()
        return success
    except Exception as e:
        print(f"TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
