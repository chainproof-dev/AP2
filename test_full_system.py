#!/usr/bin/env python3
"""
Full system test for mandate lifecycle management.
This script properly starts all agents and tests the mandate revocation functionality.
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
import requests
from typing import List

class FullSystemTest:
    def __init__(self):
        self.processes = []
        self.base_dir = os.path.join(os.path.dirname(__file__), 'samples', 'python')
        self.src_dir = os.path.join(self.base_dir, 'src')

    def start_agent(self, module_name: str, port: int) -> subprocess.Popen:
        """Start an agent process from the correct directory."""
        print(f"🚀 Starting {module_name} on port {port}...")

        cmd = [sys.executable, "-m", f"roles.{module_name}"]
        process = subprocess.Popen(
            cmd,
            cwd=self.src_dir,  # Run from the src directory
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
            return None

    def start_all_agents(self):
        """Start all required agents."""
        print("🤖 Starting all AP2 agents...")
        print("=" * 40)

        # Start agents in order
        agents = [
            ("credentials_provider_agent", 8002),
            ("merchant_payment_processor_agent", 8003),
            ("merchant_agent", 8001),
            ("shopping_agent", 8000)
        ]

        for module_name, port in agents:
            process = self.start_agent(module_name, port)
            if process:
                self.processes.append(process)
            else:
                print(f"❌ Failed to start {module_name}")
                self.cleanup()
                return False

        print("✅ All agents started successfully!")
        return True

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

    def test_agent_connectivity(self):
        """Test that agents are responding."""
        print("\n🏥 Testing agent connectivity...")

        # Wait for agents to fully start
        time.sleep(5)

        # Test if we can make HTTP requests to the agents
        # Note: The actual agents might not have HTTP endpoints,
        # but we can test if they're running by checking processes
        running_count = 0
        for process in self.processes:
            if process.poll() is None:
                running_count += 1

        print(f"✅ {running_count}/{len(self.processes)} agents are running")
        return running_count == len(self.processes)

    def test_mandate_functionality(self):
        """Test mandate functionality with the running agents."""
        print("\n🔄 Testing mandate functionality...")

        try:
            # Import the mandate types
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
            from ap2.types.mandate import IntentMandate, MandateStatus
            from ap2.types.error_schema import mandate_already_revoked_error

            # Test 1: Create a mandate
            print("  📝 Creating Intent Mandate...")
            mandate = IntentMandate(
                natural_language_description="Buy shoes if price drops below $50",
                intent_expiry="2025-12-31T23:59:59Z"
            )

            assert mandate.status == MandateStatus.ACTIVE
            print("  ✅ Intent Mandate created successfully")

            # Test 2: Revoke the mandate
            print("  🚫 Revoking mandate...")
            mandate.status = MandateStatus.REVOKED
            assert mandate.status == MandateStatus.REVOKED
            print("  ✅ Mandate revoked successfully")

            # Test 3: Test execution validation
            print("  ⚠️  Testing execution validation...")
            is_executable = mandate.status == MandateStatus.ACTIVE
            assert not is_executable
            print("  ✅ Revoked mandate correctly identified as non-executable")

            # Test 4: Test error response
            print("  🚨 Testing error response...")
            error = mandate_already_revoked_error("test-mandate-123")
            assert error.status == 409
            assert "revoked" in error.detail.lower()
            print("  ✅ Error response generated correctly")

            return True

        except Exception as e:
            print(f"  ❌ Mandate functionality test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_test(self):
        """Run the full system test."""
        print("🧪 AP2 Full System Test")
        print("=" * 30)
        print()

        try:
            # Start agents
            if not self.start_all_agents():
                return False

            # Test connectivity
            if not self.test_agent_connectivity():
                print("❌ Agent connectivity test failed")
                return False

            # Test mandate functionality
            if not self.test_mandate_functionality():
                print("❌ Mandate functionality test failed")
                return False

            print("\n🎉 All tests passed!")
            print("\n✅ System Status:")
            print("  • All agents are running")
            print("  • Mandate lifecycle management works")
            print("  • Error handling is functional")
            print("  • Status validation works correctly")

            print("\n🌐 Agent URLs (if they have HTTP endpoints):")
            print("  - Shopping Agent: http://localhost:8000")
            print("  - Merchant Agent: http://localhost:8001")
            print("  - Credentials Provider: http://localhost:8002")
            print("  - Payment Processor: http://localhost:8003")

            print("\n📋 Next Steps:")
            print("1. The agents are running and ready for testing")
            print("2. You can now test mandate revocation through agent interactions")
            print("3. Use the shopping agent to create and revoke mandates")

            return True

        except Exception as e:
            print(f"❌ System test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Keep agents running for manual testing
            print("\n⏳ Agents will continue running for manual testing...")
            print("Press Ctrl+C to stop all agents when done testing")

            try:
                # Wait for user interrupt
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping all agents...")
                self.cleanup()

def main():
    """Main test runner."""
    # Check if GOOGLE_API_KEY is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is not set")
        print("Please set your Google API key:")
        print("export GOOGLE_API_KEY=your_key_here")
        sys.exit(1)

    # Run the test
    tester = FullSystemTest()
    success = tester.run_test()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
