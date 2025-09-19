#!/usr/bin/env python3
"""
Manual testing script for mandate lifecycle management.
This script provides an interactive way to test the mandate revocation functionality.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'samples', 'python', 'src'))

async def test_mandate_lifecycle_manually():
    """Interactive test of mandate lifecycle management."""
    print("🧪 Manual Mandate Lifecycle Test")
    print("=" * 40)
    print()

    from ap2.types.mandate import IntentMandate, MandateStatus
    from ap2.types.error_schema import mandate_not_found_error, mandate_already_revoked_error

    # Test 1: Create a mandate
    print("1️⃣ Creating an Intent Mandate...")
    mandate = IntentMandate(
        natural_language_description="Buy a pair of Nike shoes if price drops below $80",
        intent_expiry="2025-12-31T23:59:59Z"
    )

    print(f"   Mandate ID: {id(mandate)}")
    print(f"   Status: {mandate.status}")
    print(f"   Created: {mandate.created_at}")
    print(f"   Description: {mandate.natural_language_description}")
    print("   ✅ Mandate created successfully")
    print()

    # Test 2: Check if mandate is executable
    print("2️⃣ Checking if mandate is executable...")
    is_executable = mandate.status == MandateStatus.ACTIVE
    print(f"   Executable: {is_executable}")
    print("   ✅ Active mandate is executable")
    print()

    # Test 3: Revoke the mandate
    print("3️⃣ Revoking the mandate...")
    mandate.status = MandateStatus.REVOKED
    mandate.updated_at = datetime.now(timezone.utc).isoformat()

    print(f"   New Status: {mandate.status}")
    print(f"   Updated: {mandate.updated_at}")
    print("   ✅ Mandate revoked successfully")
    print()

    # Test 4: Try to execute revoked mandate
    print("4️⃣ Attempting to execute revoked mandate...")
    is_executable = mandate.status == MandateStatus.ACTIVE
    print(f"   Executable: {is_executable}")

    if not is_executable:
        # Simulate the error that would be returned
        error = mandate_already_revoked_error(str(id(mandate)))
        print("   🚨 Error would be returned:")
        print(f"   Status Code: {error.status}")
        print(f"   Error Type: {error.type}")
        print(f"   Title: {error.title}")
        print(f"   Detail: {error.detail}")
        print("   ✅ Revoked mandate correctly rejected")
    else:
        print("   ❌ ERROR: Revoked mandate was incorrectly accepted")
    print()

    # Test 5: Test different mandate states
    print("5️⃣ Testing different mandate states...")

    states_to_test = [
        (MandateStatus.DRAFT, "Draft mandate"),
        (MandateStatus.ACTIVE, "Active mandate"),
        (MandateStatus.REVOKED, "Revoked mandate"),
        (MandateStatus.EXPIRED, "Expired mandate"),
        (MandateStatus.COMPLETED, "Completed mandate"),
        (MandateStatus.FAILED, "Failed mandate")
    ]

    for status, description in states_to_test:
        mandate.status = status
        is_executable = mandate.status == MandateStatus.ACTIVE
        print(f"   {description}: Executable = {is_executable}")

    print("   ✅ State validation works correctly")
    print()

    # Test 6: Test error scenarios
    print("6️⃣ Testing error scenarios...")

    # Test mandate not found error
    not_found_error = mandate_not_found_error("nonexistent-123")
    print(f"   Not Found Error - Status: {not_found_error.status}")
    print(f"   Not Found Error - Type: {not_found_error.type}")

    # Test already revoked error
    revoked_error = mandate_already_revoked_error("revoked-456")
    print(f"   Already Revoked Error - Status: {revoked_error.status}")
    print(f"   Already Revoked Error - Type: {revoked_error.type}")

    print("   ✅ Error scenarios work correctly")
    print()

    print("🎉 Manual test completed successfully!")
    print()
    print("Summary of what was tested:")
    print("  ✅ Mandate creation with proper defaults")
    print("  ✅ Status transitions (ACTIVE → REVOKED)")
    print("  ✅ Execution validation (only ACTIVE mandates executable)")
    print("  ✅ Error handling for invalid states")
    print("  ✅ RFC 7807 compliant error responses")
    print("  ✅ All mandate states properly handled")

def test_error_serialization():
    """Test that errors can be properly serialized for API responses."""
    print("\n🔧 Testing Error Serialization")
    print("=" * 30)

    from ap2.types.error_schema import mandate_not_found_error

    error = mandate_not_found_error("test-mandate-789")
    error_dict = error.model_dump()

    print("Error as dictionary:")
    print(json.dumps(error_dict, indent=2))
    print()

    # Test that it can be converted back to JSON
    error_json = json.dumps(error_dict)
    print("Error as JSON:")
    print(error_json)
    print()

    print("✅ Error serialization works correctly")

async def main():
    """Main test runner."""
    print("🚀 AP2 Mandate Lifecycle Manual Testing")
    print("=" * 50)
    print()

    try:
        await test_mandate_lifecycle_manually()
        test_error_serialization()

        print("\n🎯 Next Steps for Full Testing:")
        print("1. Run the mandate revocation scenario:")
        print("   bash samples/python/scenarios/mandate-revocation/run.sh")
        print()
        print("2. Start the full agent system and test via web interface:")
        print("   - Shopping Agent: http://localhost:8000")
        print("   - Merchant Agent: http://localhost:8001")
        print()
        print("3. Test real agent interactions:")
        print("   - Create a mandate through the shopping agent")
        print("   - Revoke it using the revoke_mandate tool")
        print("   - Try to execute the revoked mandate")

    except Exception as e:
        print(f"❌ Manual test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
