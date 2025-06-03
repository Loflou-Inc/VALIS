#!/usr/bin/env python3
"""
QA-302: 10 CONCURRENT CHATS LOAD TEST
Doc Brown's Temporal Concurrency Stress Validation
"""

import asyncio
import aiohttp
import json
import time
import psutil
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class ConcurrentLoadTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.performance_metrics = []
        self.concurrent_sessions = 10
        self.messages_per_session = 5
        
    async def log_test(self, test_name, success, details="", session_id="", duration=0):
        """Log test results with timestamp and performance data"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "details": details,
            "session_id": session_id,
            "duration": duration
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        duration_str = f" ({duration:.3f}s)" if duration > 0 else ""
        print(f"[{timestamp}] {status} {test_name}: {details}{duration_str}")
    
    def monitor_system_resources(self, duration_seconds):
        """Monitor CPU and memory usage during load test"""
        start_time = time.time()
        metrics = []
        
        def collect_metrics():
            while time.time() - start_time < duration_seconds:
                try:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    
                    metric = {
                        'timestamp': time.time() - start_time,
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_used_mb': memory.used / 1024 / 1024
                    }
                    metrics.append(metric)
                    self.performance_metrics.append(metric)
                except:
                    break
        
        thread = threading.Thread(target=collect_metrics)
        thread.daemon = True
        thread.start()
        return thread
    
    async def create_concurrent_chat_session(self, session_index, session_obj):
        """Create a single concurrent chat session with multiple messages"""
        session_id = f"load_test_session_{session_index}_{int(time.time())}"
        session_results = []
        
        # Get available personas
        try:
            async with session_obj.get(f"{self.base_url}/personas") as resp:
                if resp.status == 200:
                    personas = await resp.json()
                    if not personas:
                        await self.log_test(f"Session {session_index} Persona Load", False, "No personas available", session_id)
                        return session_results
                    
                    # Use round-robin persona selection
                    persona = personas[session_index % len(personas)]
                    persona_id = persona.get('id', f'persona_{session_index}')
                    persona_name = persona.get('name', 'Unknown')
                else:
                    await self.log_test(f"Session {session_index} Persona Load", False, f"HTTP {resp.status}", session_id)
                    return session_results
        except Exception as e:
            await self.log_test(f"Session {session_index} Persona Load", False, f"Error: {e}", session_id)
            return session_results
        
        # Send multiple messages in sequence
        conversation_context = f"TestUser{session_index}"
        for msg_index in range(self.messages_per_session):
            start_time = time.time()
            
            # Generate varied test messages
            test_messages = [
                f"Hello {persona_name}, I'm {conversation_context}. Can you introduce yourself?",
                f"I'm working on a project about {session_index}. Can you help me?",
                f"What do you think about the topic we discussed earlier?",
                f"Can you give me some advice based on our conversation?",
                f"Thank you for your help. Any final thoughts?"
            ]
            
            message = test_messages[msg_index % len(test_messages)]
            
            try:
                chat_data = {
                    "persona_id": persona_id,
                    "message": message,
                    "session_id": session_id
                }
                
                async with session_obj.post(f"{self.base_url}/chat", json=chat_data) as resp:
                    duration = time.time() - start_time
                    
                    if resp.status == 200:
                        response_data = await resp.json()
                        response_length = len(response_data.get('response', ''))
                        provider_used = response_data.get('provider_used', 'unknown')
                        
                        session_results.append({
                            'message_index': msg_index,
                            'success': True,
                            'duration': duration,
                            'response_length': response_length,
                            'provider': provider_used
                        })
                        
                        await self.log_test(
                            f"Session {session_index} Message {msg_index+1}",
                            True,
                            f"Response: {response_length} chars, Provider: {provider_used}",
                            session_id,
                            duration
                        )
                    else:
                        session_results.append({
                            'message_index': msg_index,
                            'success': False,
                            'duration': duration,
                            'error': f"HTTP {resp.status}"
                        })
                        
                        await self.log_test(
                            f"Session {session_index} Message {msg_index+1}",
                            False,
                            f"HTTP {resp.status}",
                            session_id,
                            duration
                        )
                        
            except Exception as e:
                duration = time.time() - start_time
                session_results.append({
                    'message_index': msg_index,
                    'success': False,
                    'duration': duration,
                    'error': str(e)
                })
                
                await self.log_test(
                    f"Session {session_index} Message {msg_index+1}",
                    False,
                    f"Error: {e}",
                    session_id,
                    duration
                )
            
            # Small delay between messages in same session to simulate real usage
            await asyncio.sleep(0.5)
        
        return session_results
    
    async def test_session_isolation(self, session_obj):
        """Test that sessions remain isolated under concurrent load"""
        test_session_ids = [f"isolation_test_{i}_{int(time.time())}" for i in range(3)]
        isolation_results = []
        
        # Send distinct messages to different sessions simultaneously
        async def send_isolation_message(session_index, session_id):
            try:
                chat_data = {
                    "persona_id": "jane_thompson",  # Use consistent persona
                    "message": f"My unique identifier is ISOLATION_TEST_{session_index}. Please remember this.",
                    "session_id": session_id
                }
                
                async with session_obj.post(f"{self.base_url}/chat", json=chat_data) as resp:
                    if resp.status == 200:
                        response_data = await resp.json()
                        return {
                            'session_index': session_index,
                            'session_id': session_id,
                            'response': response_data.get('response', ''),
                            'neural_context': response_data.get('neural_context', '')
                        }
            except Exception as e:
                return {'session_index': session_index, 'error': str(e)}
        
        # Send messages concurrently
        tasks = [send_isolation_message(i, sid) for i, sid in enumerate(test_session_ids)]
        isolation_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify isolation by checking for cross-contamination
        for result in isolation_results:
            if isinstance(result, dict) and 'response' in result:
                session_index = result['session_index']
                response = result['response'].lower()
                
                # Check if this response contains identifiers from other sessions
                cross_contamination = any(
                    f"isolation_test_{other_idx}" in response 
                    for other_idx in range(3) 
                    if other_idx != session_index
                )
                
                await self.log_test(
                    f"Session Isolation Test {session_index}",
                    not cross_contamination,
                    f"Cross-contamination: {'Yes' if cross_contamination else 'No'}",
                    result['session_id']
                )
        
        return isolation_results
    
    async def check_ui_state_consistency(self, session_obj):
        """Check that UI-related endpoints remain consistent under load"""
        ui_endpoints = [
            ('/health', 'Health Check'),
            ('/sessions', 'Sessions List'),
            ('/config', 'Configuration'),
            ('/admin/stats', 'System Stats')
        ]
        
        ui_results = []
        
        for endpoint, name in ui_endpoints:
            start_time = time.time()
            try:
                async with session_obj.get(f"{self.base_url}{endpoint}") as resp:
                    duration = time.time() - start_time
                    
                    if resp.status == 200:
                        data = await resp.json()
                        await self.log_test(
                            f"UI Consistency - {name}",
                            True,
                            f"Endpoint responsive",
                            duration=duration
                        )
                        ui_results.append({'endpoint': endpoint, 'success': True, 'duration': duration})
                    else:
                        await self.log_test(
                            f"UI Consistency - {name}",
                            False,
                            f"HTTP {resp.status}",
                            duration=duration
                        )
                        ui_results.append({'endpoint': endpoint, 'success': False, 'duration': duration})
            except Exception as e:
                duration = time.time() - start_time
                await self.log_test(
                    f"UI Consistency - {name}",
                    False,
                    f"Error: {e}",
                    duration=duration
                )
                ui_results.append({'endpoint': endpoint, 'success': False, 'duration': duration})
        
        return ui_results
    
    async def run_load_test(self):
        """Run complete concurrent load test"""
        print("🧪 QA-302: 10 CONCURRENT CHATS LOAD TEST")
        print("=" * 70)
        print("🔬 Doc Brown's Temporal Concurrency Stress Validation")
        print(f"⚡ Testing {self.concurrent_sessions} concurrent sessions with {self.messages_per_session} messages each")
        print("-" * 70)
        
        # Start system resource monitoring
        total_test_duration = 60  # Expected test duration in seconds
        monitor_thread = self.monitor_system_resources(total_test_duration)
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session_obj:
            # Pre-test: Verify system health
            try:
                async with session_obj.get(f"{self.base_url}/health") as resp:
                    if resp.status != 200:
                        print(f"❌ System not healthy (HTTP {resp.status}) - aborting load test")
                        return False
            except:
                print("❌ Cannot connect to system - aborting load test")
                return False
            
            print(f"\n🚀 Starting concurrent load test...")
            load_test_start = time.time()
            
            # Create concurrent chat sessions
            session_tasks = [
                self.create_concurrent_chat_session(i, session_obj) 
                for i in range(self.concurrent_sessions)
            ]
            
            # Run all sessions concurrently
            session_results = await asyncio.gather(*session_tasks, return_exceptions=True)
            
            load_test_duration = time.time() - load_test_start
            
            print(f"\n🧠 Testing session isolation under load...")
            isolation_results = await self.test_session_isolation(session_obj)
            
            print(f"\n🎨 Testing UI consistency under load...")
            ui_results = await self.check_ui_state_consistency(session_obj)
            
        # Analyze results
        total_messages = 0
        successful_messages = 0
        failed_messages = 0
        response_times = []
        provider_usage = defaultdict(int)
        
        for i, result in enumerate(session_results):
            if isinstance(result, list):  # Successful session
                for msg_result in result:
                    total_messages += 1
                    if msg_result.get('success', False):
                        successful_messages += 1
                        response_times.append(msg_result.get('duration', 0))
                        provider_usage[msg_result.get('provider', 'unknown')] += 1
                    else:
                        failed_messages += 1
            else:  # Failed session
                failed_messages += self.messages_per_session
                total_messages += self.messages_per_session
        
        # Calculate performance metrics
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # System resource analysis
        if self.performance_metrics:
            avg_cpu = sum(m['cpu_percent'] for m in self.performance_metrics) / len(self.performance_metrics)
            max_cpu = max(m['cpu_percent'] for m in self.performance_metrics)
            avg_memory = sum(m['memory_percent'] for m in self.performance_metrics) / len(self.performance_metrics)
            max_memory = max(m['memory_percent'] for m in self.performance_metrics)
        else:
            avg_cpu = max_cpu = avg_memory = max_memory = 0
        
        # Generate detailed report
        success_rate = (successful_messages / total_messages * 100) if total_messages > 0 else 0
        
        print(f"\n" + "=" * 70)
        print(f"🎯 QA-302 CONCURRENT LOAD TEST RESULTS:")
        print(f"📊 Total Messages: {total_messages}")
        print(f"✅ Successful: {successful_messages}")
        print(f"❌ Failed: {failed_messages}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Average Response Time: {avg_response_time:.3f}s")
        print(f"⏱️ Response Time Range: {min_response_time:.3f}s - {max_response_time:.3f}s")
        print(f"🖥️ CPU Usage: Avg {avg_cpu:.1f}%, Max {max_cpu:.1f}%")
        print(f"🧠 Memory Usage: Avg {avg_memory:.1f}%, Max {max_memory:.1f}%")
        print(f"⚡ Provider Distribution: {dict(provider_usage)}")
        print(f"🏃 Total Test Duration: {load_test_duration:.1f}s")
        
        # Determine if test passed
        test_passed = (
            success_rate >= 90 and  # At least 90% success rate
            avg_response_time <= 5.0 and  # Average response under 5 seconds
            max_cpu <= 90 and  # CPU doesn't exceed 90%
            max_memory <= 90  # Memory doesn't exceed 90%
        )
        
        if test_passed:
            print(f"\n🚀 CONCURRENT LOAD TEST: PASSED!")
            print(f"🛡️ All temporal concurrency safeguards verified!")
            print(f"⚡ System handles {self.concurrent_sessions} concurrent users successfully!")
        else:
            print(f"\n⚠️ CONCURRENT LOAD TEST: PERFORMANCE ISSUES DETECTED!")
            print(f"🔬 Review metrics for temporal concurrency vulnerabilities!")
        
        return test_passed

async def main():
    """Run QA-302 load test"""
    tester = ConcurrentLoadTest()
    success = await tester.run_load_test()
    
    # Save detailed results
    results_file = Path("C:/VALIS/qa_302_load_test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'test_results': tester.test_results,
            'performance_metrics': tester.performance_metrics
        }, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: {results_file}")
    return success

if __name__ == "__main__":
    asyncio.run(main())
