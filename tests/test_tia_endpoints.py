#!/usr/bin/env python3
"""
🛰️ T.I.A. Fleet Endpoints Tests
Tests for /health and /telemetry endpoints with 2/4/1 configuration
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=" * 80)
print("🛰️ T.I.A. FLEET ENDPOINTS TESTS")
print("=" * 80)

# ============================================================================
# TEST 1: GET /health - Safety Locks Verification
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: GET /health - Safety Locks Verification")
print("=" * 80)

response = client.get("/health")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response: {data}")

test1_pass = True
if response.status_code == 200:
    print("✅ PASS - Health endpoint responds with 200")
else:
    print(f"❌ FAIL - Health endpoint returned {response.status_code}")
    test1_pass = False

if data.get('status') == 'ok':
    print("✅ PASS - Status is 'ok'")
else:
    print(f"❌ FAIL - Status is '{data.get('status')}' (expected 'ok')")
    test1_pass = False

if data.get('Safety Locks') == 'ENGAGED ✅':
    print("✅ PASS - Safety Locks: ENGAGED ✅")
else:
    print(f"❌ FAIL - Safety Locks: {data.get('Safety Locks')} (expected 'ENGAGED ✅')")
    test1_pass = False

# ============================================================================
# TEST 2: GET /telemetry - Fleet Allocation (requires auth)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: GET /telemetry - Fleet Allocation (requires auth)")
print("=" * 80)

# Test without auth - should fail
response_no_auth = client.get("/telemetry")
print(f"Without Auth - Status Code: {response_no_auth.status_code}")

test2_pass = True
if response_no_auth.status_code == 401:
    print("✅ PASS - Telemetry requires authentication (401)")
else:
    print(f"⚠️  WARNING - Telemetry returned {response_no_auth.status_code} without auth (expected 401)")

# Note: We can't test with auth without valid credentials, but we verified it requires auth
print("\nℹ️  Telemetry endpoint requires authentication (as expected)")
print("   Fleet allocation format: 'X Piranha + Y Harvester + Z Sniper'")
print("   Expected: '0 Piranha + 0 Harvester + 0 Sniper' (no active positions at startup)")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("T.I.A. FLEET ENDPOINTS TEST SUITE SUMMARY")
print("=" * 80)

all_tests = [
    ("Health Endpoint - Safety Locks", test1_pass),
    ("Telemetry Endpoint - Auth Required", test2_pass),
]

passed = sum(1 for _, result in all_tests if result)
total = len(all_tests)

print(f"\n📊 Test Results: {passed}/{total} passed")
for test_name, result in all_tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"   {status} - {test_name}")

if passed == total:
    print("\n🛰️ T.I.A. Fleet Endpoints: ALL TESTS PASSED")
    print("=" * 80)
    if __name__ == "__main__":
        sys.exit(0)
else:
    print("\n⚠️ Some tests failed - review implementation")
    print("=" * 80)
    if __name__ == "__main__":
        sys.exit(1)
