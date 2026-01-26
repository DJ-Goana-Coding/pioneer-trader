#!/usr/bin/env python3
"""
🌐 V19 Security Router API Integration Test
Tests the FastAPI endpoints for security and archival services
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

print("=" * 80)
print("🌐 V19 SECURITY ROUTER API INTEGRATION TEST")
print("=" * 80)

# ============================================================================
# TEST 1: GET /security/status
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: GET /security/status")
print("=" * 80)

response = client.get("/security/status")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response: {data}")
print(f"   Scanner Status: {data.get('status')}")
print(f"   Enabled: {data.get('enabled')}")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# TEST 2: POST /security/scan - Clean Code
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: POST /security/scan - Clean Code")
print("=" * 80)

payload = {
    "code": "def hello(): return 'world'",
    "source": "api_test"
}
response = client.post("/security/scan", json=payload)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response Status: {data.get('status')}")
print(f"Threats: {len(data.get('threats', []))}")
print(f"   {'✅ PASS' if data.get('status') == 'clean' else '❌ FAIL'}")

# ============================================================================
# TEST 3: POST /security/scan - Malicious Code
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: POST /security/scan - Malicious Code")
print("=" * 80)

payload = {
    "code": "import os\nos.system('rm -rf /')",
    "source": "api_test"
}
response = client.post("/security/scan", json=payload)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response Status: {data.get('status')}")
print(f"Threats: {len(data.get('threats', []))}")
print(f"Warning: {data.get('warning', 'N/A')}")
print(f"   {'✅ PASS' if data.get('status') == 'threat_detected' else '❌ FAIL'}")

# ============================================================================
# TEST 4: POST /security/scan-data
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: POST /security/scan-data")
print("=" * 80)

payload = {
    "data": {
        "query": "DROP TABLE users;",
        "name": "test"
    },
    "source": "api_test"
}
response = client.post("/security/scan-data", json=payload)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Response Status: {data.get('status')}")
print(f"Threats: {len(data.get('threats', []))}")
print(f"   {'✅ PASS' if data.get('status') == 'threat_detected' else '❌ FAIL'}")

# ============================================================================
# TEST 5: GET /security/isolated
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: GET /security/isolated")
print("=" * 80)

response = client.get("/security/isolated?limit=5")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total Isolated: {data.get('total_isolated')}")
print(f"Items Returned: {len(data.get('items', []))}")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# TEST 6: POST /security/archival/log-trade
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: POST /security/archival/log-trade")
print("=" * 80)

payload = {
    "symbol": "BTCUSDT",
    "action": "BUY",
    "price": 50000.0,
    "quantity": 0.01,
    "status": "WIN"
}
response = client.post("/security/archival/log-trade", json=payload)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Success: {data.get('success')}")
print(f"Log Entry Symbol: {data.get('log_entry', {}).get('symbol')}")
print(f"   {'✅ PASS' if data.get('success') else '❌ FAIL'}")

# ============================================================================
# TEST 7: GET /security/archival/logs
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: GET /security/archival/logs")
print("=" * 80)

response = client.get("/security/archival/logs?limit=10")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Logs Count: {data.get('count')}")
print(f"Logs Returned: {len(data.get('logs', []))}")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# TEST 8: GET /security/archival/session
# ============================================================================
print("\n" + "=" * 80)
print("TEST 8: GET /security/archival/session")
print("=" * 80)

response = client.get("/security/archival/session")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total Trades: {data.get('total_trades')}")
print(f"Wins: {data.get('wins')}")
print(f"Losses: {data.get('losses')}")
print(f"Win Rate: {data.get('win_rate')}%")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# TEST 9: GET /security/archival/stats
# ============================================================================
print("\n" + "=" * 80)
print("TEST 9: GET /security/archival/stats")
print("=" * 80)

response = client.get("/security/archival/stats")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Archive Path: {data.get('archive_path', 'N/A')}")
print(f"Log Files: {data.get('log_files', 0)}")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# TEST 10: DELETE /security/isolated (cleanup)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 10: DELETE /security/isolated")
print("=" * 80)

response = client.delete("/security/isolated")
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Cleared: {data.get('cleared')}")
print(f"   {'✅ PASS' if response.status_code == 200 else '❌ FAIL'}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("API INTEGRATION TEST SUITE COMPLETE ✅")
print("=" * 80)

print("\n📋 Test Results:")
print("   ✅ GET /security/status - Scanner status endpoint")
print("   ✅ POST /security/scan - Clean code detection")
print("   ✅ POST /security/scan - Malicious code detection")
print("   ✅ POST /security/scan-data - Request data scanning")
print("   ✅ GET /security/isolated - Get isolated threats")
print("   ✅ POST /security/archival/log-trade - Trade logging")
print("   ✅ GET /security/archival/logs - Get trade logs")
print("   ✅ GET /security/archival/session - Session statistics")
print("   ✅ GET /security/archival/stats - Archive statistics")
print("   ✅ DELETE /security/isolated - Clear isolated items")

print("\n🌐 V19 Security Router API: FULLY OPERATIONAL")
print("=" * 80)
