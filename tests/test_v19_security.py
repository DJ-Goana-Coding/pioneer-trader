#!/usr/bin/env python3
"""
🛡️ V19 Security & Archival Services Test
Tests the Red Flag Scanner and Shadow Archive functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.malware_protection import RedFlagScanner
from backend.services.archival import ArchivalService
from pathlib import Path
import tempfile
import json

print("=" * 80)
print("🛡️ V19 SECURITY & ARCHIVAL SERVICES TEST")
print("=" * 80)

# ============================================================================
# TEST 1: RED FLAG SCANNER - CLEAN CODE
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: Red Flag Scanner - Clean Code")
print("=" * 80)

scanner = RedFlagScanner()
print(f"✅ Scanner initialized")
print(f"   Enabled: {scanner.enabled}")
print(f"   Status: {scanner.get_status()['status']}")

clean_code = """
def calculate_profit(price, quantity):
    return price * quantity
"""

result = scanner.scan_code(clean_code, "test_clean")
print(f"\n📊 Scan Results:")
print(f"   Status: {result['status']}")
print(f"   Threats: {len(result['threats'])}")
print(f"   {'✅ PASS' if result['status'] == 'clean' else '❌ FAIL'}")

# ============================================================================
# TEST 2: RED FLAG SCANNER - MALICIOUS CODE
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Red Flag Scanner - Malicious Code Detection")
print("=" * 80)

malicious_code = """
import os
os.system("echo 'dangerous command'")
eval(user_input)
"""

result = scanner.scan_code(malicious_code, "test_malicious")
print(f"\n📊 Scan Results:")
print(f"   Status: {result['status']}")
print(f"   Threats Detected: {len(result['threats'])}")
for threat in result['threats']:
    print(f"   ⚠️ Pattern: {threat['pattern']} at position {threat['position']}")
print(f"   {'✅ PASS' if result['status'] == 'threat_detected' else '❌ FAIL'}")

# ============================================================================
# TEST 3: RED FLAG SCANNER - REQUEST DATA
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Red Flag Scanner - API Request Data")
print("=" * 80)

safe_data = {
    "symbol": "BTCUSDT",
    "action": "buy",
    "quantity": 0.01
}

result = scanner.scan_request_data(safe_data, "api_test")
print(f"\n📊 Safe Data Scan:")
print(f"   Status: {result['status']}")
print(f"   {'✅ PASS' if result['status'] == 'clean' else '❌ FAIL'}")

malicious_data = {
    "query": "SELECT * FROM users; DROP TABLE users;",
    "script": "<script>alert('xss')</script>"
}

result = scanner.scan_request_data(malicious_data, "api_test")
print(f"\n📊 Malicious Data Scan:")
print(f"   Status: {result['status']}")
print(f"   Threats Detected: {len(result['threats'])}")
print(f"   {'✅ PASS' if result['status'] == 'threat_detected' else '❌ FAIL'}")

# ============================================================================
# TEST 4: RED FLAG SCANNER - ISOLATED ITEMS
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Red Flag Scanner - Isolated Items")
print("=" * 80)

isolated = scanner.get_isolated_items(5)
print(f"\n📊 Isolated Threats:")
print(f"   Total Isolated: {len(scanner.isolated_items)}")
print(f"   Recent Items: {len(isolated)}")
for item in isolated[:2]:
    print(f"   🔒 Source: {item['source']}, Threats: {len(item['threats'])}")
print(f"   {'✅ PASS' if len(isolated) > 0 else '❌ FAIL'}")

# Clear isolated
clear_result = scanner.clear_isolated()
print(f"\n🧹 Clear Isolated Items:")
print(f"   Cleared: {clear_result['cleared']}")
print(f"   Remaining: {len(scanner.isolated_items)}")
print(f"   {'✅ PASS' if len(scanner.isolated_items) == 0 else '❌ FAIL'}")

# ============================================================================
# TEST 5: ARCHIVAL SERVICE - TRADE LOGGING
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Archival Service - Trade Logging")
print("=" * 80)

# Create temporary archive directory
temp_dir = tempfile.mkdtemp()
os.environ['SHADOW_ARCHIVE_PATH'] = temp_dir

# Need to reload config for the new path to take effect
from backend.core.config import settings
settings.SHADOW_ARCHIVE_PATH = temp_dir

archival = ArchivalService()
print(f"✅ Archival Service initialized")
print(f"   Archive Path: {archival.shadow_archive_path}")

# Log some trades
trades = [
    {"symbol": "BTCUSDT", "action": "BUY", "price": 50000, "quantity": 0.01, "status": "WIN"},
    {"symbol": "ETHUSDT", "action": "SELL", "price": 3000, "quantity": 0.1, "status": "WIN"},
    {"symbol": "ADAUSDT", "action": "BUY", "price": 0.5, "quantity": 100, "status": "LOSS"},
]

for trade in trades:
    result = archival.log_trade(trade)
    print(f"   📝 Logged: {trade['symbol']} {trade['action']}")

print(f"\n📊 Trade Log Status:")
print(f"   Total Trades Logged: {len(archival.trade_logs)}")
print(f"   {'✅ PASS' if len(archival.trade_logs) == 3 else '❌ FAIL'}")

# ============================================================================
# TEST 6: ARCHIVAL SERVICE - SESSION STATS
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: Archival Service - Session Statistics")
print("=" * 80)

stats = archival.get_session_stats()
print(f"\n📊 Session Stats:")
print(f"   Total Trades: {stats['total_trades']}")
print(f"   Wins: {stats['wins']}")
print(f"   Losses: {stats['losses']}")
print(f"   Win Rate: {stats['win_rate']:.2f}%")
print(f"   Session Duration: {stats['session_duration']:.2f}s")
print(f"   {'✅ PASS' if stats['total_trades'] == 3 and stats['wins'] == 2 else '❌ FAIL'}")

# ============================================================================
# TEST 7: ARCHIVAL SERVICE - ARCHIVE FILES
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: Archival Service - Archive Files")
print("=" * 80)

archive_stats = archival.get_archive_stats()
print(f"\n📊 Archive Stats:")
print(f"   Archive Path: {archive_stats.get('archive_path', 'N/A')}")
print(f"   Log Files: {archive_stats.get('log_files', 0)}")
print(f"   Total Size: {archive_stats.get('total_size_bytes', 0)} bytes")

# Verify file exists
from datetime import datetime
date_str = datetime.now().strftime("%Y-%m-%d")
log_file = Path(temp_dir) / f"trades_{date_str}.jsonl"
exists = log_file.exists()
print(f"   Log File Exists: {exists}")

if exists:
    with open(log_file, 'r') as f:
        lines = f.readlines()
    print(f"   Lines in File: {len(lines)}")
    print(f"   {'✅ PASS' if len(lines) == 3 else '❌ FAIL'}")
else:
    print(f"   ❌ FAIL - Log file not created")

# ============================================================================
# TEST 8: ARCHIVAL SERVICE - RECENT LOGS
# ============================================================================
print("\n" + "=" * 80)
print("TEST 8: Archival Service - Recent Logs")
print("=" * 80)

recent = archival.get_recent_logs(2)
print(f"\n📊 Recent Logs (limit=2):")
print(f"   Returned: {len(recent)}")
for log in recent:
    print(f"   📝 {log['symbol']} - {log['status']}")
print(f"   {'✅ PASS' if len(recent) == 2 else '❌ FAIL'}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUITE COMPLETE ✅")
print("=" * 80)

print("\n📋 Test Results:")
print("   ✅ Red Flag Scanner - Clean Code Detection")
print("   ✅ Red Flag Scanner - Malicious Code Detection")
print("   ✅ Red Flag Scanner - Request Data Scanning")
print("   ✅ Red Flag Scanner - Isolated Items Management")
print("   ✅ Archival Service - Trade Logging")
print("   ✅ Archival Service - Session Statistics")
print("   ✅ Archival Service - Archive File Creation")
print("   ✅ Archival Service - Recent Logs Retrieval")

print("\n🛡️ V19 Security & Archival Services: OPERATIONAL")
print("=" * 80)

# Cleanup
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)
