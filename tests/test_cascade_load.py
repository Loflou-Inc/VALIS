"""
Temporal Cascade Load Testing
Tests the VALIS provider cascade under various failure scenarios
"""

import asyncio
import time
import json
from pathlib import Path
import sys

# Add VALIS to path
sys.path.append(str(Path(__file__).parent.parent))

from core.valis_engine import VALISEngine

class CascadeLoadTester:
    def __init__(self):
        self.engine = VALISEngine()
        self.results = []
    
    async def test_single_request(self, persona_id: str, message: str, test_name: str):
        """Test a single request and record results"""
        start_time = time.time()
        
        try:
            result = await self.engine.get_persona_response(persona_id, message)
            end_time = time.time()
            
            test_result = {
                "test_name": test_name,
                "persona_id": persona_id,
                "success": result.get("success", False),
                "provider_used": result.get("provider_used", "unknown"),
                "response_time": end_time - start_time,
                "error": result.get("error", None)
            }
            
            self.results.append(test_result)
            print(f"SUCCESS: {test_name}: {result.get('success')} via {result.get('provider_used')} ({test_result['response_time']:.2f}s)")
            
        except Exception as e:
            end_time = time.time()
            test_result = {
                "test_name": test_name,
                "persona_id": persona_id,
                "success": False,
                "provider_used": "exception",
                "response_time": end_time - start_time,
                "error": str(e)
            }
            self.results.append(test_result)
            print(f"ERROR: {test_name}: EXCEPTION - {e}")
    
    async def test_concurrent_requests(self, count: int = 5):
        """Test multiple concurrent requests"""
        print(f"\n>> Testing {count} concurrent requests...")
        
        tasks = []
        for i in range(count):
            task = self.test_single_request(
                "jane", 
                f"Concurrent test message {i+1}", 
                f"concurrent_test_{i+1}"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def test_all_personas(self):
        """Test all available personas"""
        print("\n>> Testing all personas...")
        
        personas = self.engine.get_available_personas()
        for persona in personas:
            await self.test_single_request(
                persona["id"],
                "Hello, can you help me with a quick test?",
                f"persona_test_{persona['id']}"
            )
    
    async def test_provider_cascade(self):
        """Test that the provider cascade works properly"""
        print("\n>> Testing provider cascade...")
        
        # Test normal operation
        await self.test_single_request("jane", "Normal operation test", "cascade_normal")
        
        # Test with invalid persona (should fail gracefully)
        await self.test_single_request("invalid_persona", "Test message", "cascade_invalid_persona")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("TEMPORAL CASCADE LOAD TEST RESULTS")
        print("="*60)
        
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Provider usage stats
        provider_stats = {}
        for result in self.results:
            if result["success"]:
                provider = result["provider_used"]
                provider_stats[provider] = provider_stats.get(provider, 0) + 1
        
        print(f"\n>> Provider Usage:")
        for provider, count in provider_stats.items():
            print(f"  {provider}: {count} requests")
        
        # Average response times
        successful_results = [r for r in self.results if r["success"]]
        if successful_results:
            avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
            print(f"\n>> Average Response Time: {avg_response_time:.2f}s")
        
        # Failed tests details
        failed_results = [r for r in self.results if not r["success"]]
        if failed_results:
            print(f"\n>> Failed Tests:")
            for result in failed_results:
                print(f"  {result['test_name']}: {result['error']}")
        
        # Save detailed results
        with open("cascade_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n>> Detailed results saved to: cascade_test_results.json")

async def main():
    """Run the full cascade load test suite"""
    print(">> INITIALIZING TEMPORAL CASCADE LOAD TESTING...")
    
    tester = CascadeLoadTester()
    
    # Run all tests
    await tester.test_provider_cascade()
    await tester.test_all_personas()
    await tester.test_concurrent_requests(3)
    await tester.test_concurrent_requests(10)
    
    # Generate final report
    tester.generate_report()
    
    print("\n>> TEMPORAL CASCADE TESTING COMPLETE!")
    print("Review the results above and cascade_test_results.json for detailed analysis.")

if __name__ == "__main__":
    asyncio.run(main())
