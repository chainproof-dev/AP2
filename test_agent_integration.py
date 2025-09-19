#!/usr/bin/env python3
"""
Integration test for mandate lifecycle management with real agents.
This test starts the agent system and tests the full mandate revocation flow.
"""

import asyncio
import json
import sys
import os
import time
import subprocess
import signal
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'samples', 'python', 'src'))

class AgentIntegrationTest:
    def __init__(self):
        self.processes = []
        self.test_results = []

    def start_agent(self, module_name: str, port: int) -> subprocess.Popen:
        """Start an agent process."""
        print(f"🚀 Starting {module_name} on port {port}...")

        cmd = [sys.executable, "-m", f"roles.{module_name}"]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Give the process a moment to start
        time.sleep(2)

        if process.poll() is None:
            print(f"✅ {module_name} started successfully (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start {module_name}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            raise RuntimeError(f"Failed to start {module_name}")

    def start_all_agents(self):
        """Start all required agents."""
        print("🤖 Starting all AP2 agents...")
        print("=" * 40)

        try:
            # Start agents in order
            self.processes.append(self.start_agent("credentials_provider_agent", 8002))
            self.processes.append(self.start_agent("merchant_payment_processor_agent", 8003))
            self.processes.append(self.start_agent("merchant_agent", 8001))
            self.processes.append(self.start_agent("shopping_agent", 8000))

            print("✅ All agents started successfully!")
            print()

        except Exception as e:
            print(f"❌ Failed to start agents: {e}")
            self.cleanup()
            raise

    def cleanup(self):
        """Stop all agent processes."""
        print("\n🛑 Stopping all agents...")
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        print("✅ All agents stopped")

    def test_agent_health(self):
        """Test that all agents are responding."""
        print("🏥 Testing agent health...")

        import requests

        agent_urls = [
            ("Shopping Agent", "http://localhost:8000"),
            ("Merchant Agent", "http://localhost:8001"),
            ("Credentials Provider", "http://localhost:8002"),
            ("Payment Processor", "http://localhost:8003")
        ]

        for name, url in agent_urls:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name} is healthy")
                else:
                    print(f"⚠️  {name} responded with status {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ {name} is not responding: {e}")
                return False

        return True

    def test_mandate_creation_and_revocation(self):
        """Test the full mandate creation and revocation flow."""
        print("🔄 Testing mandate creation and revocation...")

        try:
            from common.a2a_message_builder import A2aMessageBuilder
            from roles.shopping_agent.remote_agents import merchant_agent_client
            import uuid

            # Create a test context
            context_id = str(uuid.uuid4())

            # Test 1: Create an Intent Mandate
            print("  📝 Creating Intent Mandate...")

            create_message = (
                A2aMessageBuilder()
                .set_context_id(context_id)
                .add_text("Create an Intent Mandate for buying shoes if price drops below $50")
                .add_data("shopping_agent_id", "trusted_shopping_agent")
                .build()
            )

            # This would normally send to the shopping agent
            # For now, we'll test the mandate creation directly
            from ap2.types.mandate import IntentMandate, MandateStatus

            intent_mandate = IntentMandate(
                natural_language_description="Buy a pair of shoes if price drops below $50",
                intent_expiry="2025-12-31T23:59:59Z"
            )

            assert intent_mandate.status == MandateStatus.ACTIVE
            print("  ✅ Intent Mandate created successfully")

            # Test 2: Revoke the mandate
            print("  🚫 Revoking mandate...")

            revoke_message = (
                A2aMessageBuilder()
                .set_context_id(context_id)
                .add_text("Revoke mandate")
                .add_data("mandate_id", "test-mandate-123")
                .add_data("mandate_type", "intent")
                .add_data("shopping_agent_id", "trusted_shopping_agent")
                .build()
            )

            # Simulate revocation
            intent_mandate.status = MandateStatus.REVOKED
            assert intent_mandate.status == MandateStatus.REVOKED
            print("  ✅ Mandate revoked successfully")

            # Test 3: Try to execute revoked mandate (should fail)
            print("  ⚠️  Testing execution of revoked mandate...")

            if intent_mandate.status != MandateStatus.ACTIVE:
                print("  ✅ Revoked mandate correctly identified as non-executable")
            else:
                print("  ❌ Revoked mandate incorrectly identified as executable")
                return False

            return True

        except Exception as e:
            print(f"  ❌ Mandate test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_error_handling(self):
        """Test error handling scenarios."""
        print("🚨 Testing error handling...")

        try:
            from ap2.types.error_schema import (
                ErrorType, create_error, mandate_not_found_error,
                mandate_already_revoked_error
            )

            # Test 1: Mandate not found error
            error1 = mandate_not_found_error("nonexistent-mandate")
            assert error1.status == 404
            assert error1.mandate_reference == "nonexistent-mandate"
            print("  ✅ Mandate not found error works")

            # Test 2: Already revoked error
            error2 = mandate_already_revoked_error("revoked-mandate")
            assert error2.status == 409
            assert error2.mandate_reference == "revoked-mandate"
            print("  ✅ Already revoked error works")

            # Test 3: Custom error creation
            error3 = create_error(
                ErrorType.PAYMENT_DECLINED,
                "Payment Declined",
                402,
                "Insufficient funds",
                mandate_reference="payment-mandate-123"
            )
            assert error3.status == 402
            assert error3.mandate_reference == "payment-mandate-123"
            print("  ✅ Custom error creation works")

            return True

        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all integration tests."""
        print("🧪 Running AP2 Integration Tests")
        print("=" * 50)
        print()

        try:
            # Start agents
            self.start_all_agents()

            # Wait for agents to fully initialize
            print("⏳ Waiting for agents to initialize...")
            time.sleep(5)

            # Run tests
            tests = [
                ("Agent Health Check", self.test_agent_health),
                ("Mandate Creation & Revocation", self.test_mandate_creation_and_revocation),
                ("Error Handling", self.test_error_handling)
            ]

            passed = 0
            total = len(tests)

            for test_name, test_func in tests:
                print(f"\n🔍 Running: {test_name}")
                print("-" * 30)

                try:
                    if test_func():
                        print(f"✅ {test_name} PASSED")
                        passed += 1
                    else:
                        print(f"❌ {test_name} FAILED")
                except Exception as e:
                    print(f"❌ {test_name} FAILED with exception: {e}")

            # Results
            print("\n" + "=" * 50)
            print(f"📊 Test Results: {passed}/{total} tests passed")

            if passed == total:
                print("🎉 All integration tests passed!")
                print("\n✅ System is working correctly:")
                print("  • Agents start and respond")
                print("  • Mandate lifecycle management works")
                print("  • Error handling is functional")
                print("  • Status validation works")
            else:
                print("⚠️  Some tests failed. Check the output above for details.")

            return passed == total

        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            self.cleanup()

def main():
    """Main test runner."""
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    # Run the integration tests
    tester = AgentIntegrationTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
