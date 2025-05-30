"""Neural Matrix Health Monitoring Test - Task 2.4"""
import sys, os, asyncio, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from valis_engine import VALISEngine

async def test_neural_health():
    print("=== NEURAL MATRIX HEALTH MONITORING TEST ===")
    
    engine = VALISEngine()
    
    # Test 1: Check health monitor availability
    health_available = engine.neural_health_monitor is not None
    print(f"1. Neural Health Monitor: {'AVAILABLE' if health_available else 'UNAVAILABLE'}")
    
    if not health_available:
        print("   Skipping advanced tests - monitor not available")
        return False
    
    # Test 2: Basic health dashboard
    print("2. Testing Health Dashboard...")
    dashboard = engine.get_neural_health_dashboard()
    overall_status = dashboard.get('overall_status', 'unknown')
    print(f"   Overall Status: {overall_status}")
    
    # Test 3: Create activity and test metrics
    print("3. Testing Activity Tracking...")
    session_id = f"test_{int(time.time())}"
    
    for i in range(2):
        result = await engine.get_persona_response("jane", f"Test message {i+1}", session_id)
        print(f"   Interaction {i+1}: {result.get('success')}")
        await asyncio.sleep(0.3)
    
    # Test 4: Check health metrics
    print("4. Checking Health Metrics...")
    updated_dashboard = engine.get_neural_health_dashboard()
    context_quality = updated_dashboard.get('context_quality', {})
    print(f"   Handoff Success Rate: {context_quality.get('handoff_success_rate', 0):.3f}")
    print(f"   Total Handoffs: {context_quality.get('total_handoffs', 0)}")
    
    # Test 5: Test system health integration
    print("5. Testing System Health Integration...")
    system_health = engine.health_check()
    system_status = system_health.get('status', 'unknown')
    neural_status = system_health.get('neural_matrix_health', {}).get('overall_status', 'unknown')
    print(f"   System Status: {system_status}")
    print(f"   Neural Matrix Status: {neural_status}")
    
    # Success criteria
    success = (
        health_available and
        overall_status in ['green', 'yellow'] and
        context_quality.get('handoff_success_rate', 0) >= 0.9
    )
    
    print(f"\n{'='*50}")
    print(f"NEURAL HEALTH MONITORING: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
    
    if success:
        print("SUCCESS: Neural Matrix Health Monitoring OPERATIONAL!")
    
    return success

asyncio.run(test_neural_health())
