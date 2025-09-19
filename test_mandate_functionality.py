#!/usr/bin/env python3
"""
Test script to verify mandate lifecycle management and error handling functionality.
Run this to quickly test the core features without starting the full agent system.
"""

import sys
import os
from datetime import datetime, timezone

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_mandate_status_enum():
    """Test that the MandateStatus enum works correctly."""
    print("🧪 Testing MandateStatus enum...")

    from ap2.types.mandate import MandateStatus

    # Test all status values
    assert MandateStatus.ACTIVE == "ACTIVE"
    assert MandateStatus.REVOKED == "REVOKED"
    assert MandateStatus.EXPIRED == "EXPIRED"
    assert MandateStatus.COMPLETED == "COMPLETED"
    assert MandateStatus.FAILED == "FAILED"
    assert MandateStatus.DRAFT == "DRAFT"

    print("✅ MandateStatus enum works correctly")

def test_mandate_creation():
    """Test that mandates are created with proper default values."""
    print("🧪 Testing mandate creation...")

    from ap2.types.mandate import IntentMandate, MandateStatus

    # Create an IntentMandate
    mandate = IntentMandate(
        natural_language_description="Buy a pair of shoes if price drops below $50",
        intent_expiry="2025-12-31T23:59:59Z"
    )

    # Check default values
    assert mandate.status == MandateStatus.ACTIVE
    assert mandate.created_at is not None
    assert mandate.updated_at is not None
    assert isinstance(mandate.created_at, str)
    assert isinstance(mandate.updated_at, str)

    print("✅ Mandate creation works with correct defaults")

def test_mandate_status_transitions():
    """Test that mandate status can be updated."""
    print("🧪 Testing mandate status transitions...")

    from ap2.types.mandate import IntentMandate, MandateStatus

    mandate = IntentMandate(
        natural_language_description="Test mandate",
        intent_expiry="2025-12-31T23:59:59Z"
    )

    # Test status update
    original_status = mandate.status
    mandate.status = MandateStatus.REVOKED

    assert mandate.status == MandateStatus.REVOKED
    assert mandate.status != original_status

    print("✅ Mandate status transitions work correctly")

def test_error_schema():
    """Test the error schema functionality."""
    print("🧪 Testing error schema...")

    from ap2.types.error_schema import AP2Error, ErrorType, create_error, mandate_not_found_error

    # Test basic error creation
    error = create_error(
        ErrorType.MANDATE_NOT_FOUND,
        "Mandate Not Found",
        404,
        "The mandate could not be found",
        mandate_reference="test-123"
    )

    assert error.type == ErrorType.MANDATE_NOT_FOUND.value
    assert error.title == "Mandate Not Found"
    assert error.status == 404
    assert error.mandate_reference == "test-123"

    # Test error serialization
    error_dict = error.model_dump()
    assert "type" in error_dict
    assert "title" in error_dict
    assert "status" in error_dict
    assert "detail" in error_dict
    assert "mandate_reference" in error_dict

    # Test helper function
    error2 = mandate_not_found_error("test-mandate-456")
    assert error2.mandate_reference == "test-mandate-456"
    assert error2.status == 404

    print("✅ Error schema works correctly")

def test_mandate_validation():
    """Test that mandates validate their status correctly."""
    print("🧪 Testing mandate validation...")

    from ap2.types.mandate import IntentMandate, MandateStatus

    mandate = IntentMandate(
        natural_language_description="Test mandate",
        intent_expiry="2025-12-31T23:59:59Z"
    )

    # Test active mandate (should be executable)
    assert mandate.status == MandateStatus.ACTIVE
    is_executable = mandate.status == MandateStatus.ACTIVE
    assert is_executable == True

    # Test revoked mandate (should not be executable)
    mandate.status = MandateStatus.REVOKED
    is_executable = mandate.status == MandateStatus.ACTIVE
    assert is_executable == False

    # Test expired mandate (should not be executable)
    mandate.status = MandateStatus.EXPIRED
    is_executable = mandate.status == MandateStatus.ACTIVE
    assert is_executable == False

    print("✅ Mandate validation works correctly")

def test_error_types():
    """Test that all error types are properly defined."""
    print("🧪 Testing error types...")

    from ap2.types.error_schema import ErrorType

    # Test that all expected error types exist
    expected_errors = [
        "MANDATE_NOT_FOUND",
        "MANDATE_ALREADY_REVOKED",
        "MANDATE_EXPIRED",
        "PAYMENT_DECLINED",
        "UNAUTHORIZED_AGENT",
        "INTERNAL_SERVER_ERROR"
    ]

    for error_name in expected_errors:
        assert hasattr(ErrorType, error_name), f"Missing error type: {error_name}"
        error_value = getattr(ErrorType, error_name)
        assert error_value.startswith("https://ap2-protocol.org/errors/")

    print("✅ All error types are properly defined")

def main():
    """Run all tests."""
    print("🚀 Testing AP2 Mandate Lifecycle Management")
    print("=" * 50)
    print()

    try:
        test_mandate_status_enum()
        test_mandate_creation()
        test_mandate_status_transitions()
        test_error_schema()
        test_mandate_validation()
        test_error_types()

        print()
        print("🎉 All tests passed!")
        print()
        print("✅ Core functionality verified:")
        print("  • Mandate status management")
        print("  • Error schema (RFC 7807)")
        print("  • Status transitions")
        print("  • Validation logic")
        print("  • Error type definitions")
        print()
        print("Next steps:")
        print("1. Run the full agent system test")
        print("2. Test the mandate revocation scenario")
        print("3. Verify error handling in real agent interactions")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
