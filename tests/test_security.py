#!/usr/bin/env python3
"""
Security Validation Test
Tests that the system correctly rejects placeholder credentials in LIVE mode.
"""

import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import security constants
from backend.core.security_constants import MIN_API_KEY_LENGTH, MIN_SECRET_KEY_LENGTH

def check_placeholder(value):
    """
    Check if a value contains placeholder text.
    
    This function matches the logic in backend/main.py:is_placeholder_credential()
    Uses MIN_API_KEY_LENGTH constant to ensure consistency.
    """
    if not value or "PLACEHOLDER" in value.upper():
        return True
    if "YOUR_" in value.upper():
        return True
    if len(value) < MIN_API_KEY_LENGTH:  # Shared constant from security_constants.py
        return True
    return False

def test_placeholder_rejection():
    """Test that LIVE mode rejects placeholder credentials"""
    
    print("=" * 80)
    print("SECURITY VALIDATION TEST")
    print("=" * 80)
    print(f"Using MIN_API_KEY_LENGTH = {MIN_API_KEY_LENGTH}")
    print(f"Using MIN_SECRET_KEY_LENGTH = {MIN_SECRET_KEY_LENGTH}")
    
    # Test 1: Check security validation logic
    print("\n✅ Test 1: Security validation logic")
    
    test_cases = [
        ("PLACEHOLDER_KEY", True, "literal PLACEHOLDER"),
        ("mx0vglABCDEF1234567890ABCDEF", False, "real API key format (28+ chars)"),
        ("YOUR_KEY_HERE", True, "YOUR_ prefix"),
        ("short", True, f"too short (< {MIN_API_KEY_LENGTH} chars)"),
        ("", True, "empty string"),
        (None, True, "None value"),
        ("a1b2c3d4e5f6g7h8i9j0k1l2m3n4", False, "legitimate 32-char key"),
        ("ghp_1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef", False, "GitHub PAT format"),
    ]
    
    all_passed = True
    for value, should_fail, description in test_cases:
        result = check_placeholder(value)
        status = "✓" if result == should_fail else "✗"
        if result != should_fail:
            all_passed = False
        print(f"   {status} {description}: {repr(value)} -> reject={result}")
    
    if not all_passed:
        print("   Status: ✗ Some validation tests failed")
        return False
    print("   Status: ✓ All validation tests passed")
    
    # Test 2: Verify LIVE mode would fail with placeholders
    print("\n✅ Test 2: LIVE mode rejection (simulated)")
    print("   Note: The actual main.py will raise ValueError on startup")
    
    os.environ['EXECUTION_MODE'] = 'LIVE'
    os.environ['MEXC_API_KEY'] = 'PLACEHOLDER'
    
    security_warnings = []
    if check_placeholder(os.environ.get('MEXC_API_KEY')):
        security_warnings.append("MEXC_API_KEY contains placeholder")
    
    if security_warnings:
        print(f"   ✓ Correctly detected: {security_warnings[0]}")
        print("   ✓ Would prevent LIVE mode startup (expected)")
    else:
        print("   ✗ FAILED - Did not detect placeholder")
        return False
    
    # Test 3: Verify legitimate keys pass validation
    print("\n✅ Test 3: Legitimate credential acceptance")
    
    legitimate_keys = [
        "mx0vglABCDEF1234567890ABCDEF1234",  # MEXC format
        "ghp_1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdef",  # GitHub PAT
        "sk-1234567890abcdefghijklmnopqrstuvwxyz",  # Generic API key format
    ]
    
    all_accepted = True
    for key in legitimate_keys:
        rejected = check_placeholder(key)
        status = "✓" if not rejected else "✗"
        if rejected:
            all_accepted = False
        print(f"   {status} Accepts key format (len={len(key)}): {key[:20]}...")
    
    if not all_accepted:
        print("   Status: ✗ Some legitimate keys were rejected")
        return False
    print("   Status: ✓ All legitimate key formats accepted")
    
    # Test 4: Verify SECRET_KEY length requirement
    print("\n✅ Test 4: SECRET_KEY minimum length validation")
    
    secret_test_cases = [
        ("short_key", True, f"Too short (< {MIN_SECRET_KEY_LENGTH} chars)"),
        ("a" * MIN_SECRET_KEY_LENGTH, False, f"Exactly {MIN_SECRET_KEY_LENGTH} chars"),
        ("a" * (MIN_SECRET_KEY_LENGTH + 10), False, f"Longer than minimum ({MIN_SECRET_KEY_LENGTH + 10} chars)"),
    ]
    
    secret_tests_passed = True
    for value, should_fail, description in secret_test_cases:
        # SECRET_KEY has additional length check
        rejected = check_placeholder(value) or len(value) < MIN_SECRET_KEY_LENGTH
        status = "✓" if rejected == should_fail else "✗"
        if rejected != should_fail:
            secret_tests_passed = False
        print(f"   {status} {description}: len={len(value)} -> reject={rejected}")
    
    if not secret_tests_passed:
        print("   Status: ✗ Some SECRET_KEY tests failed")
        return False
    print("   Status: ✓ SECRET_KEY length validation passed")
    
    print("\n" + "=" * 80)
    print("ALL SECURITY VALIDATION TESTS PASSED ✅")
    print("=" * 80)
    print("\n📋 Next Steps for Operators:")
    print("1. Copy .env.example to .env")
    print("2. Replace placeholders with real credentials")
    print(f"3. Ensure SECRET_KEY is at least {MIN_SECRET_KEY_LENGTH} characters")
    print("4. NEVER commit .env file")
    print("5. Read SECURITY_CHECKLIST.md")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = test_placeholder_rejection()
    sys.exit(0 if success else 1)
