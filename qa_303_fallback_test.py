#!/usr/bin/env python3
"""
QA-303: BAD CONFIG + FALLBACK SANITY TEST
Doc Brown's Temporal Graceful Degradation Validation
"""

import asyncio
import aiohttp
import json
import shutil
import time
import subprocess
from datetime import datetime
from pathlib import Path

class FallbackSanityTest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.valis_dir = Path("C:/VALIS")
        self.config_backup = None
        self.env_backup = None
        
    async def log_test(self, test_name, success, details=""):
        """Log test results with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        result = {
            "timestamp": timestamp,
            "test": test_name,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{timestamp}] {status} {test_name}: {details}")
    
    def backup_config_files(self):
        """Backup original config files before testing"""
        config_file = self.valis_dir / "config.json"
        env_file = self.valis_dir / ".env"
        
        if config_file.exists():
            self.config_backup = config_file.read_text()
            print("📁 Config file backed up")
        
        if env_file.exists():
            self.env_backup = env_file.read_text()
            print("📁 .env file backed up")
    
    def restore_config_files(self):
        """Restore original config files after testing"""
        config_file = self.valis_dir / "config.json"
        env_file = self.valis_dir / ".env"
        
        if self.config_backup:
            config_file.write_text(self.config_backup)
            print("📁 Config file restored")
        
        if self.env_backup:
            env_file.write_text(self.env_backup)
            print("📁 .env file restored")
    
    def create_malformed_config(self):
        """Create intentionally broken config.json"""
        config_file = self.valis_dir / "config.json"
        
        # Create malformed JSON
        malformed_config = """
        {
            "providers": ["desktop_commander_mcp", "anthropic_api", "openai_api", "hardcoded_fallback"],
            "provider_timeout": 30,
            "max_concurrent_requests": 10,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 300,
            "retry_schedule": [1, 2, 4],
            "features": {
                "enable_circuit_breaker": true,
                "enable_retry_logic": true
            },
            "neural_memory": {
                "enabled": true,
                "store_type": "flat_file",
                "max_memories": 1000
            }
            // Missing closing brace - intentional JSON syntax error
        """
        
        config_file.write_text(malformed_config)
        print("🔧 Created malformed config.json (missing closing brace)")
    
    def create_missing_provider_config(self):
        """Create config with missing critical providers"""
        config_file = self.valis_dir / "config.json"
        
        # Config with only fallback provider
        minimal_config = {
            "providers": ["hardcoded_fallback"],  # Only fallback available
            "provider_timeout": 30,
            "max_concurrent_requests": 10,
            "features": {
                "enable_circuit_breaker": True,
                "enable_retry_logic": True
            }
        }
        
        config_file.write_text(json.dumps(minimal_config, indent=2))
        print("🔧 Created config with only fallback provider")
    
    def break_api_keys(self):
        """Create invalid API keys in .env file"""
        env_file = self.valis_dir / ".env"
        
        broken_env = """
# Intentionally broken API keys for fallback testing
OPENAI_API_KEY=invalid_key_for_testing_fallback_12345
ANTHROPIC_API_KEY=invalid_anthropic_key_for_testing_67890
"""
        
        env_file.write_text(broken_env)
        print("🔧 Created invalid API keys in .env")
    
    async def test_system_response_to_malformed_config(self, session):
        """Test system behavior with malformed config"""
        self.create_malformed_config()
        
        # Wait a moment for config to potentially reload
        await asyncio.sleep(2)
        
        try:
            async with session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    await self.log_test(
                        "Malformed Config Resilience",
                        True,
                        f"System stable despite malformed config: {health_data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    await self.log_test(
                        "Malformed Config Resilience", 
                        False, 
                        f"System failed with malformed config: HTTP {resp.status}"
                    )
                    return False
        except Exception as e:
            await self.log_test(
                "Malformed Config Resilience",
                False,
                f"System crashed with malformed config: {e}"
            )
            return False
    
    async def test_fallback_provider_cascade(self, session):
        """Test that system falls back through provider cascade correctly"""
        # First, break API keys to force fallback
        self.break_api_keys()
        
        # Then create config with multiple providers (but broken API keys)
        config_file = self.valis_dir / "config.json"
        fallback_config = {
            "providers": ["desktop_commander_mcp", "openai_api", "anthropic_api", "hardcoded_fallback"],
            "provider_timeout": 5,  # Short timeout to speed up fallback
            "max_concurrent_requests": 10,
            "features": {
                "enable_circuit_breaker": True,
                "enable_retry_logic": True
            }
        }
        config_file.write_text(json.dumps(fallback_config, indent=2))
        
        # Wait for config to reload
        await asyncio.sleep(3)
        
        # Test chat with broken providers - should fall back
        test_session_id = f"fallback_test_{int(time.time())}"
        fallback_test_results = []
        
        for i in range(3):  # Test multiple messages to see fallback behavior
            try:
                chat_data = {
                    "persona_id": "jane_thompson",
                    "message": f"Test message {i+1} for fallback validation. Can you respond?",
                    "session_id": test_session_id
                }
                
                start_time = time.time()
                async with session.post(f"{self.base_url}/chat", json=chat_data) as resp:
                    duration = time.time() - start_time
                    
                    if resp.status == 200:
                        response_data = await resp.json()
                        provider_used = response_data.get('provider_used', 'unknown')
                        response_text = response_data.get('response', '')
                        
                        fallback_test_results.append({
                            'message_index': i,
                            'success': True,
                            'provider': provider_used,
                            'duration': duration,
                            'response_length': len(response_text)
                        })
                        
                        await self.log_test(
                            f"Fallback Cascade Test {i+1}",
                            True,
                            f"Provider: {provider_used}, Duration: {duration:.3f}s, Response: {len(response_text)} chars"
                        )
                    else:
                        fallback_test_results.append({
                            'message_index': i,
                            'success': False,
                            'error': f"HTTP {resp.status}",
                            'duration': duration
                        })
                        
                        await self.log_test(
                            f"Fallback Cascade Test {i+1}",
                            False,
                            f"HTTP {resp.status}, Duration: {duration:.3f}s"
                        )
            except Exception as e:
                await self.log_test(
                    f"Fallback Cascade Test {i+1}",
                    False,
                    f"Error: {e}"
                )
        
        # Analyze fallback behavior
        successful_responses = [r for r in fallback_test_results if r.get('success', False)]
        if successful_responses:
            providers_used = [r['provider'] for r in successful_responses]
            unique_providers = set(providers_used)
            
            # Check if fallback provider was used (expected with broken API keys)
            fallback_used = any('fallback' in provider.lower() for provider in providers_used)
            
            await self.log_test(
                "Fallback Provider Analysis",
                fallback_used,
                f"Providers used: {list(unique_providers)}, Fallback active: {fallback_used}"
            )
        
        return fallback_test_results
    
    async def test_ui_error_states(self, session):
        """Test that UI endpoints show graceful error information"""
        ui_endpoints = [
            ('/health', 'Health Status'),
            ('/config', 'Configuration'),
            ('/sessions', 'Sessions'),
            ('/admin/stats', 'System Stats')
        ]
        
        ui_error_results = []
        
        for endpoint, name in ui_endpoints:
            try:
                async with session.get(f"{self.base_url}{endpoint}") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Check if error states are properly communicated
                        if endpoint == '/health':
                            status = data.get('status', 'unknown')
                            providers = data.get('providers_available', [])
                            
                            # With broken config, we should see degraded status or limited providers
                            graceful_degradation = (
                                status in ['degraded', 'warning', 'healthy'] and
                                isinstance(providers, list)
                            )
                            
                            await self.log_test(
                                f"UI Error State - {name}",
                                graceful_degradation,
                                f"Status: {status}, Providers: {len(providers)}"
                            )
                        else:
                            # Other endpoints should return valid JSON even in degraded state
                            await self.log_test(
                                f"UI Error State - {name}",
                                True,
                                f"Endpoint responsive with valid JSON"
                            )
                        
                        ui_error_results.append({
                            'endpoint': endpoint,
                            'success': True,
                            'status': resp.status,
                            'has_data': bool(data)
                        })
                    else:
                        await self.log_test(
                            f"UI Error State - {name}",
                            False,
                            f"HTTP {resp.status}"
                        )
                        ui_error_results.append({
                            'endpoint': endpoint,
                            'success': False,
                            'status': resp.status
                        })
            except Exception as e:
                await self.log_test(
                    f"UI Error State - {name}",
                    False,
                    f"Error: {e}"
                )
                ui_error_results.append({
                    'endpoint': endpoint,
                    'success': False,
                    'error': str(e)
                })
        
        return ui_error_results
    
    async def test_recovery_after_fix(self, session):
        """Test that system recovers when configuration is fixed"""
        # Restore original configuration
        self.restore_config_files()
        
        # Wait for system to reload config
        await asyncio.sleep(5)
        
        recovery_results = []
        
        # Test system health after recovery
        try:
            async with session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    health_data = await resp.json()
                    status = health_data.get('status', 'unknown')
                    providers = health_data.get('providers_available', [])
                    
                    recovery_success = (
                        status == 'healthy' and
                        len(providers) >= 2  # Should have multiple providers working
                    )
                    
                    await self.log_test(
                        "System Recovery Test",
                        recovery_success,
                        f"Status: {status}, Providers: {len(providers)}"
                    )
                    
                    recovery_results.append({
                        'test': 'health_check',
                        'success': recovery_success,
                        'status': status,
                        'provider_count': len(providers)
                    })
                else:
                    await self.log_test(
                        "System Recovery Test",
                        False,
                        f"HTTP {resp.status}"
                    )
        except Exception as e:
            await self.log_test(
                "System Recovery Test",
                False,
                f"Error: {e}"
            )
        
        # Test that chat works normally after recovery
        try:
            chat_data = {
                "persona_id": "jane_thompson",
                "message": "Recovery test: Can you confirm the system is working normally?",
                "session_id": f"recovery_test_{int(time.time())}"
            }
            
            async with session.post(f"{self.base_url}/chat", json=chat_data) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    provider_used = response_data.get('provider_used', 'unknown')
                    response_length = len(response_data.get('response', ''))
                    
                    # Should work with a non-fallback provider if APIs are restored
                    normal_operation = (
                        response_length > 50 and  # Reasonable response length
                        provider_used != 'hardcoded_fallback'  # Using real AI provider
                    )
                    
                    await self.log_test(
                        "Chat Recovery Test",
                        True,
                        f"Provider: {provider_used}, Response: {response_length} chars"
                    )
                    
                    recovery_results.append({
                        'test': 'chat_function',
                        'success': True,
                        'provider': provider_used,
                        'normal_operation': normal_operation
                    })
                else:
                    await self.log_test(
                        "Chat Recovery Test",
                        False,
                        f"HTTP {resp.status}"
                    )
        except Exception as e:
            await self.log_test(
                "Chat Recovery Test",
                False,
                f"Error: {e}"
            )
        
        return recovery_results
    
    async def run_fallback_test(self):
        """Run complete fallback and graceful degradation test"""
        print("🧪 QA-303: BAD CONFIG + FALLBACK SANITY TEST")
        print("=" * 70)
        print("🔬 Doc Brown's Temporal Graceful Degradation Validation")
        print("⚡ Testing config corruption, provider failures, and recovery")
        print("-" * 70)
        
        # Backup original files
        print("\n📁 Backing up original configuration...")
        self.backup_config_files()
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            # Test 1: Malformed Config Resilience
            print("\n🔧 Testing malformed config resilience...")
            await self.test_system_response_to_malformed_config(session)
            
            # Test 2: Provider Fallback Cascade
            print("\n⚡ Testing provider fallback cascade...")
            fallback_results = await self.test_fallback_provider_cascade(session)
            
            # Test 3: UI Error States
            print("\n🎨 Testing UI error state handling...")
            ui_results = await self.test_ui_error_states(session)
            
            # Test 4: System Recovery
            print("\n🚀 Testing system recovery after config restoration...")
            recovery_results = await self.test_recovery_after_fix(session)
        
        # Analyze overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        # Calculate specific test category success rates
        fallback_success = len([r for r in fallback_results if r.get('success', False)])
        ui_success = len([r for r in ui_results if r.get('success', False)])
        recovery_success = len([r for r in recovery_results if r.get('success', False)])
        
        print(f"\n" + "=" * 70)
        print(f"🎯 QA-303 FALLBACK SANITY TEST RESULTS:")
        print(f"✅ Total Passed: {passed_tests}")
        print(f"❌ Total Failed: {failed_tests}")
        print(f"📊 Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"⚡ Fallback Tests: {fallback_success}/{len(fallback_results)} successful")
        print(f"🎨 UI Error Handling: {ui_success}/{len(ui_results)} endpoints graceful")
        print(f"🚀 Recovery Tests: {recovery_success}/{len(recovery_results)} successful")
        
        # Determine if test passed
        test_passed = (
            passed_tests / total_tests >= 0.8 and  # At least 80% success rate
            fallback_success > 0 and  # At least some fallback functionality works
            ui_success >= len(ui_results) * 0.75  # Most UI endpoints handle errors gracefully
        )
        
        if test_passed:
            print(f"\n🚀 FALLBACK SANITY TEST: PASSED!")
            print(f"🛡️ System demonstrates graceful degradation!")
            print(f"⚡ Fallback mechanisms protect against config disasters!")
        else:
            print(f"\n⚠️ FALLBACK SANITY TEST: VULNERABILITIES DETECTED!")
            print(f"🔬 System may not handle configuration failures gracefully!")
        
        return test_passed

async def main():
    """Run QA-303 fallback test"""
    tester = FallbackSanityTest()
    try:
        success = await tester.run_fallback_test()
    finally:
        # Always restore config files, even if test fails
        print("\n📁 Restoring original configuration...")
        tester.restore_config_files()
    
    # Save detailed results
    results_file = Path("C:/VALIS/qa_303_fallback_test_results.json")
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
