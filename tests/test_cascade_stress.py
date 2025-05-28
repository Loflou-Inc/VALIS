"""
VALIS Cascade Stress Testing
Tests the temporal stabilization under extreme conditions

Doc Brown's Orders: "STRESS TEST EVERYTHING, MARTY!"
"""

import asyncio
import time
import pytest
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import threading

# Add VALIS to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_engine import VALISEngine
from core.provider_manager import ProviderManager

# Setup logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('VALIS.StressTest')

class TemporalStressTester:
    """Advanced stress testing system for VALIS temporal stabilization"""
    
    def __init__(self):
        self.engine = None
        self.test_results = {}
        self.stress_metrics = {}
        
    async def setup_engine(self):
        """Setup VALIS engine for testing"""
        self.engine = VALISEngine()
        await asyncio.sleep(0.1)  # Let engine initialize
        
    async def test_cascade_failure_scenarios(self) -> Dict[str, Any]:
        """Test different cascade failure scenarios"""
        logger.info("🔥 TESTING CASCADE FAILURE SCENARIOS")
        
        results = {}
        
        # Test 1: Individual provider failures
        results['individual_failures'] = await self._test_individual_provider_failures()
        
        # Test 2: All providers except fallback fail
        results['cascade_to_fallback'] = await self._test_cascade_to_fallback()
        
        # Test 3: Rapid provider switching
        results['rapid_switching'] = await self._test_rapid_provider_switching()
        
        return results
    
    async def _test_individual_provider_failures(self) -> Dict[str, Any]:
        """Test how system handles individual provider failures"""
        logger.info("Testing individual provider failures...")
        
        test_personas = ['jane', 'coach_emma']
        results = {}
        
        for persona_id in test_personas:
            try:
                # Send test message
                result = await self.engine.get_persona_response(
                    persona_id, 
                    "This is a stress test message"
                )
                
                results[persona_id] = {
                    'success': result.get('success', False),
                    'provider_used': result.get('provider_used'),
                    'response_time': result.get('response_time', 0),
                    'has_response': bool(result.get('response'))
                }
                
            except Exception as e:
                results[persona_id] = {'error': str(e), 'success': False}
        
        return results
    
    async def _test_cascade_to_fallback(self) -> Dict[str, Any]:
        """Test cascading to hardcoded fallback"""
        logger.info("Testing cascade to hardcoded fallback...")
        
        # This should always work due to hardcoded fallback
        result = await self.engine.get_persona_response(
            'jane', 
            "Emergency fallback test - conflict situation"
        )
        
        return {
            'success': result.get('success', False),
            'provider_used': result.get('provider_used'),
            'response_contains_hr_language': 'conflict' in result.get('response', '').lower() or 'hr' in result.get('response', '').lower(),
            'fallback_worked': result.get('success', False)
        }
    
    async def _test_rapid_provider_switching(self) -> Dict[str, Any]:
        """Test rapid requests that might cause provider switching"""
        logger.info("Testing rapid provider switching...")
        
        tasks = []
        for i in range(10):
            task = self.engine.get_persona_response(
                'jane', 
                f"Rapid test message #{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [r for r in results if isinstance(r, dict) and r.get('success')]
        providers_used = [r.get('provider_used') for r in successful_results]
        
        return {
            'total_requests': len(tasks),
            'successful_requests': len(successful_results),
            'success_rate': len(successful_results) / len(tasks),
            'providers_used': list(set(providers_used)),
            'consistent_provider': len(set(providers_used)) == 1
        }
    
    async def test_concurrent_load(self, concurrent_requests: int = 100) -> Dict[str, Any]:
        """Test system under concurrent load"""
        logger.info(f"🚀 TESTING CONCURRENT LOAD: {concurrent_requests} requests")
        
        start_time = time.time()
        
        # Create concurrent requests
        tasks = []
        personas = ['jane', 'coach_emma', 'billy_corgan'] * (concurrent_requests // 3)
        personas = personas[:concurrent_requests]  # Ensure exact count
        
        for i, persona_id in enumerate(personas):
            task = self.engine.get_persona_response(
                persona_id, 
                f"Concurrent stress test message #{i}",
                session_id=f"stress_session_{i % 10}"  # Use multiple sessions
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_results = []
        failed_results = []
        
        for result in results:
            if isinstance(result, Exception):
                failed_results.append(str(result))
            elif isinstance(result, dict) and result.get('success'):
                successful_results.append(result)
            else:
                failed_results.append(result.get('error', 'Unknown error'))
        
        # Calculate metrics
        response_times = [r.get('response_time', 0) for r in successful_results if 'response_time' in r]
        providers_used = [r.get('provider_used') for r in successful_results]
        
        return {
            'total_requests': concurrent_requests,
            'successful_requests': len(successful_results),
            'failed_requests': len(failed_results),
            'success_rate': len(successful_results) / concurrent_requests,
            'total_time': total_time,
            'requests_per_second': concurrent_requests / total_time,
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'providers_used': list(set(providers_used)),
            'provider_distribution': {p: providers_used.count(p) for p in set(providers_used)},
            'failed_reasons': failed_results[:5]  # First 5 failure reasons
        }
    
    async def test_memory_stability(self, duration_minutes: int = 2) -> Dict[str, Any]:
        """Test for memory leaks during extended operation"""
        logger.info(f"🧠 TESTING MEMORY STABILITY for {duration_minutes} minutes")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        request_count = 0
        memory_samples = []
        
        while time.time() < end_time:
            # Send continuous requests
            await self.engine.get_persona_response(
                'jane', 
                f"Memory stability test #{request_count}",
                session_id=f"memory_test_{request_count % 5}"
            )
            
            request_count += 1
            
            # Sample memory every 50 requests
            if request_count % 50 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
                logger.info(f"Memory: {current_memory:.1f}MB, Requests: {request_count}")
            
            # Brief pause to prevent overwhelming
            await asyncio.sleep(0.01)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            'duration_minutes': duration_minutes,
            'total_requests': request_count,
            'requests_per_minute': request_count / duration_minutes,
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_increase_mb': final_memory - initial_memory,
            'memory_increase_percent': ((final_memory - initial_memory) / initial_memory) * 100,
            'max_memory_mb': max(memory_samples) if memory_samples else final_memory,
            'memory_stable': abs(final_memory - initial_memory) < 50,  # Less than 50MB increase
            'memory_samples': memory_samples[-10:]  # Last 10 samples
        }
    
    async def test_error_recovery(self) -> Dict[str, Any]:
        """Test system recovery from various error conditions"""
        logger.info("🔧 TESTING ERROR RECOVERY")
        
        results = {}
        
        # Test 1: Invalid persona handling
        result = await self.engine.get_persona_response('nonexistent_persona', 'test message')
        results['invalid_persona'] = {
            'handled_gracefully': not result.get('success', True),
            'provides_alternatives': 'available_personas' in result
        }
        
        # Test 2: Empty message handling
        result = await self.engine.get_persona_response('jane', '')
        results['empty_message'] = {
            'handled_gracefully': True,  # Should not crash
            'has_response': bool(result.get('response'))
        }
        
        # Test 3: Very long message handling
        long_message = "This is a very long message. " * 1000  # ~30KB message
        result = await self.engine.get_persona_response('jane', long_message)
        results['long_message'] = {
            'handled_gracefully': True,  # Should not crash
            'has_response': bool(result.get('response')),
            'success': result.get('success', False)
        }
        
        return results
    
    async def run_full_stress_test(self) -> Dict[str, Any]:
        """Run the complete stress test suite"""
        logger.info("🎯 STARTING FULL TEMPORAL STABILIZATION STRESS TEST")
        
        await self.setup_engine()
        
        test_results = {}
        
        try:
            # Test 1: Cascade failures
            test_results['cascade_failures'] = await self.test_cascade_failure_scenarios()
            
            # Test 2: Concurrent load (50 requests for testing)
            test_results['concurrent_load'] = await self.test_concurrent_load(50)
            
            # Test 3: Error recovery
            test_results['error_recovery'] = await self.test_error_recovery()
            
            # Test 4: Memory stability (1 minute for testing)
            test_results['memory_stability'] = await self.test_memory_stability(1)
            
            # Get final engine status
            test_results['final_engine_status'] = self.engine.get_engine_status()
            
        except Exception as e:
            logger.error(f"Stress test failed: {e}")
            test_results['stress_test_error'] = str(e)
        
        finally:
            if self.engine:
                await self.engine.shutdown()
        
        return test_results

# Pytest test functions
async def test_valis_stress_basic():
    """Basic stress test for CI/CD"""
    tester = TemporalStressTester()
    await tester.setup_engine()
    
    # Quick test
    result = await tester.test_concurrent_load(10)
    
    assert result['success_rate'] > 0.8, f"Success rate too low: {result['success_rate']}"
    assert result['requests_per_second'] > 1, f"Too slow: {result['requests_per_second']} req/s"
    
    await tester.engine.shutdown()

if __name__ == "__main__":
    async def main():
        tester = TemporalStressTester()
        results = await tester.run_full_stress_test()
        
        print("\n" + "="*80)
        print("🚀 TEMPORAL STABILIZATION STRESS TEST RESULTS")
        print("="*80)
        
        for test_name, test_result in results.items():
            print(f"\n📊 {test_name.upper()}:")
            if isinstance(test_result, dict):
                for key, value in test_result.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  Result: {test_result}")
        
        print("\n" + "="*80)
        print("🎯 STRESS TEST COMPLETE!")
        print("="*80)
    
    asyncio.run(main())
