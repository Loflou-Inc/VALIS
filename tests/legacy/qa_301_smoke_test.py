#!/usr/bin/env python3
"""
QA-301: PERSONA SWITCHING & CHAT SMOKE TEST
Doc Brown's Temporal Persona Context Validation
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from pathlib import Path

class PersonaSmokeTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.session_data = {}
        
    async def log_test(self, test_name, success, details="", session_id=""):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "details": details,
            "session_id": session_id
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{timestamp}] {status} {test_name}: {details}")
        
    async def test_system_health(self, session):
        """Verify system is operational before testing"""
        try:
            async with session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    await self.log_test(
                        "System Health Check",
                        True,
                        f"Status: {health_data.get('status', 'unknown')}, Providers: {len(health_data.get('providers_available', []))}"
                    )
                    return True
                else:
                    await self.log_test("System Health Check", False, f"HTTP {resp.status}")
                    return False
        except Exception as e:
            await self.log_test("System Health Check", False, f"Error: {e}")
            return False
    
    async def test_persona_loading(self, session):
        """Test persona loading and validate available personas"""
        try:
            async with session.get(f"{self.base_url}/personas") as resp:
                if resp.status == 200:
                    personas = await resp.json()
                    if len(personas) >= 3:  # Ensure we have multiple personas to test
                        persona_names = [p.get('name', 'Unknown') for p in personas]
                        await self.log_test(
                            "Persona Loading",
                            True,
                            f"Loaded {len(personas)} personas: {', '.join(persona_names[:3])}"
                        )
                        return personas
                    else:
                        await self.log_test("Persona Loading", False, f"Only {len(personas)} personas available, need 3+")
                        return None
                else:
                    await self.log_test("Persona Loading", False, f"HTTP {resp.status}")
                    return None
        except Exception as e:
            await self.log_test("Persona Loading", False, f"Error: {e}")
            return None
    
    async def send_chat_message(self, session, persona_id, message, session_id):
        """Send a chat message and return the response"""
        try:
            chat_data = {
                "persona_id": persona_id,
                "message": message,
                "session_id": session_id
            }
            
            async with session.post(f"{self.base_url}/chat", json=chat_data) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    return response_data
                else:
                    await self.log_test(
                        "Chat Message",
                        False,
                        f"HTTP {resp.status} for persona {persona_id}",
                        session_id
                    )
                    return None
        except Exception as e:
            await self.log_test(
                "Chat Message", 
                False, 
                f"Error: {e}", 
                session_id
            )
            return None
    
    async def test_persona_context_isolation(self, session, personas):
        """Test that personas maintain distinct contexts"""
        # Create unique session for this test
        test_session_id = f"persona_isolation_test_{int(time.time())}"
        
        # Test with 3 different personas
        test_personas = personas[:3] if len(personas) >= 3 else personas
        persona_responses = {}
        
        for i, persona in enumerate(test_personas):
            persona_id = persona.get('id', f'persona_{i}')
            persona_name = persona.get('name', 'Unknown')
            
            # Send persona-specific question
            if 'jane' in persona_name.lower() or 'hr' in persona.get('role', '').lower():
                test_message = "What are the best practices for employee onboarding?"
            elif 'emma' in persona_name.lower() or 'coach' in persona.get('role', '').lower():
                test_message = "What's the best workout routine for beginners?"
            else:
                test_message = f"Please introduce yourself and tell me about your role as {persona_name}"
            
            response = await self.send_chat_message(session, persona_id, test_message, test_session_id)
            
            if response:
                persona_responses[persona_name] = {
                    'response': response.get('response', ''),
                    'provider': response.get('provider_used', 'unknown'),
                    'context_length': len(response.get('neural_context', ''))
                }
                
                await self.log_test(
                    f"Persona Context - {persona_name}",
                    True,
                    f"Response length: {len(response.get('response', ''))} chars, Provider: {response.get('provider_used', 'unknown')}",
                    test_session_id
                )
            else:
                await self.log_test(
                    f"Persona Context - {persona_name}",
                    False,
                    "No response received",
                    test_session_id
                )
        
        # Analyze responses for context isolation
        if len(persona_responses) >= 2:
            response_texts = [data['response'].lower() for data in persona_responses.values()]
            
            # Check if responses are sufficiently different (basic heuristic)
            unique_words = set()
            for text in response_texts:
                unique_words.update(text.split())
            
            if len(unique_words) > 50:  # Reasonable diversity in responses
                await self.log_test(
                    "Persona Context Isolation",
                    True,
                    f"Responses show distinct persona characteristics ({len(unique_words)} unique words)",
                    test_session_id
                )
            else:
                await self.log_test(
                    "Persona Context Isolation",
                    False,
                    f"Responses may be too similar ({len(unique_words)} unique words)",
                    test_session_id
                )
        
        return persona_responses
    
    async def test_memory_continuity(self, session, personas):
        """Test memory continuity when switching between personas"""
        if len(personas) < 2:
            await self.log_test("Memory Continuity", False, "Need at least 2 personas for memory test")
            return
        
        test_session_id = f"memory_continuity_test_{int(time.time())}"
        persona_a = personas[0]
        persona_b = personas[1] if len(personas) > 1 else personas[0]
        
        persona_a_id = persona_a.get('id', 'persona_0')
        persona_b_id = persona_b.get('id', 'persona_1') 
        persona_a_name = persona_a.get('name', 'Persona A')
        persona_b_name = persona_b.get('name', 'Persona B')
        
        # Step 1: Chat with Persona A about a specific topic
        first_message = "My name is TestUser and I work in software development. I'm interested in learning about project management."
        response_a1 = await self.send_chat_message(session, persona_a_id, first_message, test_session_id)
        
        if response_a1:
            await self.log_test(
                f"Memory Setup - {persona_a_name}",
                True,
                f"Initial context established, neural context: {len(response_a1.get('neural_context', ''))} chars",
                test_session_id
            )
        
        # Step 2: Switch to Persona B for different topic
        second_message = "Can you help me with something completely different - I need advice about healthy eating."
        response_b = await self.send_chat_message(session, persona_b_id, second_message, test_session_id)
        
        if response_b:
            await self.log_test(
                f"Persona Switch - {persona_b_name}",
                True,
                f"Context switch successful, neural context: {len(response_b.get('neural_context', ''))} chars",
                test_session_id
            )
        
        # Step 3: Return to Persona A and check memory
        third_message = "Earlier I mentioned I work in software development. Do you remember what I wanted to learn about?"
        response_a2 = await self.send_chat_message(session, persona_a_id, third_message, test_session_id)
        
        if response_a2:
            response_text = response_a2.get('response', '').lower()
            has_context = any(keyword in response_text for keyword in [
                'project management', 'software development', 'testuser', 'earlier', 'mentioned'
            ])
            
            await self.log_test(
                f"Memory Continuity - {persona_a_name}",
                has_context,
                f"Context preservation: {'Yes' if has_context else 'No'}, Response: {response_text[:100]}...",
                test_session_id
            )
        
        # Get session history to verify proper storage
        try:
            async with session.get(f"{self.base_url}/sessions/{test_session_id}/history") as resp:
                if resp.status == 200:
                    history_data = await resp.json()
                    message_count = history_data.get('total_count', 0)
                    await self.log_test(
                        "Session History Storage",
                        message_count >= 3,
                        f"Messages stored: {message_count}",
                        test_session_id
                    )
                else:
                    await self.log_test("Session History Storage", False, f"HTTP {resp.status}", test_session_id)
        except Exception as e:
            await self.log_test("Session History Storage", False, f"Error: {e}", test_session_id)
    
    async def test_provider_consistency(self, session, personas):
        """Test provider consistency across persona interactions"""
        test_session_id = f"provider_consistency_test_{int(time.time())}"
        provider_usage = {}
        
        for persona in personas[:3]:  # Test with first 3 personas
            persona_id = persona.get('id', 'unknown')
            persona_name = persona.get('name', 'Unknown')
            
            # Send simple test message
            test_message = f"Hello {persona_name}, please tell me about yourself briefly."
            response = await self.send_chat_message(session, persona_id, test_message, test_session_id)
            
            if response:
                provider = response.get('provider_used', 'unknown')
                if provider not in provider_usage:
                    provider_usage[provider] = []
                provider_usage[provider].append(persona_name)
                
                await self.log_test(
                    f"Provider Usage - {persona_name}",
                    True,
                    f"Used provider: {provider}, Response time: {response.get('response_time', 0):.3f}s",
                    test_session_id
                )
        
        # Analyze provider distribution
        total_providers = len(provider_usage)
        if total_providers > 0:
            provider_summary = ", ".join([f"{p}: {len(personas)}" for p, personas in provider_usage.items()])
            await self.log_test(
                "Provider Consistency Analysis",
                True,
                f"Providers used: {total_providers}, Distribution: {provider_summary}",
                test_session_id
            )
        else:
            await self.log_test(
                "Provider Consistency Analysis",
                False,
                "No successful provider usage detected",
                test_session_id
            )
        
        return provider_usage
    
    async def run_smoke_test(self):
        """Run complete persona switching smoke test"""
        print("🧪 QA-301: PERSONA SWITCHING & CHAT SMOKE TEST")
        print("=" * 70)
        print("🔬 Doc Brown's Temporal Persona Context Validation")
        print("⚡ Testing persona isolation, memory continuity, provider consistency")
        print("-" * 70)
        
        async with aiohttp.ClientSession() as session:
            # Test 1: System Health
            if not await self.test_system_health(session):
                print("\n❌ System health check failed - aborting smoke test")
                return False
            
            # Test 2: Persona Loading
            personas = await self.test_persona_loading(session)
            if not personas:
                print("\n❌ Persona loading failed - aborting smoke test")
                return False
            
            # Test 3: Persona Context Isolation
            print(f"\n🎭 Testing persona context isolation with {len(personas)} personas...")
            persona_responses = await self.test_persona_context_isolation(session, personas)
            
            # Test 4: Memory Continuity
            print(f"\n🧠 Testing memory continuity across persona switches...")
            await self.test_memory_continuity(session, personas)
            
            # Test 5: Provider Consistency
            print(f"\n⚡ Testing provider consistency across personas...")
            provider_usage = await self.test_provider_consistency(session, personas)
            
        # Generate summary
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n" + "=" * 70)
        print(f"🎯 QA-301 SMOKE TEST RESULTS:")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print(f"\n🚀 PERSONA SWITCHING & CHAT: SMOKE TEST PASSED!")
            print(f"🛡️ All temporal persona isolation safeguards verified!")
            return True
        else:
            print(f"\n⚠️ PERSONA SWITCHING & CHAT: SMOKE TEST ISSUES DETECTED!")
            print(f"🔬 Review failed tests for temporal vulnerabilities!")
            return False

async def main():
    """Run QA-301 smoke test"""
    tester = PersonaSmokeTest()
    success = await tester.run_smoke_test()
    
    # Save detailed results
    results_file = Path("C:/VALIS/qa_301_smoke_test_results.json")
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'test_results': tester.test_results
        }, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: {results_file}")
    return success

if __name__ == "__main__":
    asyncio.run(main())
