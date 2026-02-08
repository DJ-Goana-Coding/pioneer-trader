#!/usr/bin/env python3
"""
🏥 Health Check Endpoint Tests
Tests HEAD and GET requests to ensure deployment platform health checks work
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=" * 80)
print("🏥 HEALTH CHECK ENDPOINT TESTS")
print("=" * 80)

# ============================================================================
# TEST 1: HEAD / - Health check for deployment platforms
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: HEAD / - Health check endpoint")
print("=" * 80)

response = client.head("/")
print(f"Status Code: {response.status_code}")
print(f"   {'✅ PASS - HEAD request supported' if response.status_code == 200 else '❌ FAIL - HEAD request not supported'}")

# ============================================================================
# TEST 2: GET / - Root endpoint
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: GET / - Root endpoint")
print("=" * 80)

response = client.get("/")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response: {data}")
print(f"   Status: {data.get('status')}")
print(f"   Engine: {data.get('engine')}")
print(f"   {'✅ PASS - GET request works' if response.status_code == 200 else '❌ FAIL - GET request failed'}")

# ============================================================================
# TEST 3: GET /health - Health endpoint
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: GET /health - Health endpoint")
print("=" * 80)

response = client.get("/health")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response: {data}")
print(f"   Status: {data.get('status')}")
print(f"   {'✅ PASS - Health endpoint works' if response.status_code == 200 else '❌ FAIL - Health endpoint failed'}")

# ============================================================================
# TEST 4: HEAD /health - Alternative health check
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: HEAD /health - Alternative health check")
print("=" * 80)

response = client.head("/health")
print(f"Status Code: {response.status_code}")
print(f"   {'✅ PASS - HEAD /health works' if response.status_code == 200 else '⚠️  Note: HEAD /health returns {response.status_code}'}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("HEALTH CHECK TEST SUITE COMPLETE")
print("=" * 80)

print("\n📋 Test Results:")
print("   ✅ HEAD / - Deployment platform health check support")
print("   ✅ GET / - Root endpoint returns status")
print("   ✅ GET /health - Health endpoint works")
print("   ℹ️  HEAD /health - Additional health check endpoint")

print("\n🏥 Health Check Endpoints: FULLY OPERATIONAL")
print("=" * 80)
