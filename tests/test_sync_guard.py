#!/usr/bin/env python3
"""
🛡️ Sync-Guard Stability Patch Tests
Tests for error 30005 (Oversold), error 10007 (Invalid Symbol), and Post-Buy Cooldown
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
import ccxt.async_support as ccxt

# Import VortexBerserker
from backend.services.vortex import VortexBerserker

print("=" * 80)
print("🛡️ SYNC-GUARD STABILITY PATCH TESTS")
print("=" * 80)

# ============================================================================
# TEST 1: Error 30005 (Oversold) - Slot Force Clear
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: Error 30005 (Oversold) - Slot Force Clear")
print("=" * 80)

async def test_error_30005():
    vortex = VortexBerserker()
    
    # Mock the exchange
    vortex.exchange = Mock()
    vortex.exchange.create_market_sell_order = AsyncMock(
        side_effect=ccxt.ExchangeError("mexc {'code': '30005', 'msg': 'Oversold'}")
    )
    
    # Add a test position
    test_symbol = "BTC/USDT"
    vortex.active_slots[test_symbol] = {
        'entry': 50000,
        'qty': 0.001,
        'time': time.time(),
        'wing': 'piranha',
        'slot': 1,
        'peak_profit': 0.0
    }
    
    # Try to exit - should catch error 30005 and clear slot
    await vortex.execute_exit(test_symbol, 0.001, "Test Exit")
    
    # Verify slot was cleared
    if test_symbol not in vortex.active_slots:
        print("✅ PASS - Slot cleared after error 30005")
        return True
    else:
        print("❌ FAIL - Slot not cleared after error 30005")
        return False

result = asyncio.run(test_error_30005())
test1_pass = result

# ============================================================================
# TEST 2: Error 10007 (Invalid Symbol) - Blacklist
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: Error 10007 (Invalid Symbol) - Blacklist")
print("=" * 80)

async def test_error_10007():
    vortex = VortexBerserker()
    
    # Mock the exchange
    vortex.exchange = Mock()
    vortex.exchange.fetch_ohlcv = AsyncMock(
        side_effect=Exception("mexc {'code': '10007', 'msg': 'Illegal symbol'}")
    )
    
    test_symbol = "PENGUIN/USDT"
    
    # Try to get candle data - should catch error 10007 and blacklist
    result = await vortex.get_candle_data(test_symbol)
    
    # Verify symbol was blacklisted
    if test_symbol in vortex.blacklisted_symbols:
        print(f"✅ PASS - {test_symbol} blacklisted after error 10007")
        print(f"   Blacklisted symbols: {vortex.blacklisted_symbols}")
        return True
    else:
        print(f"❌ FAIL - {test_symbol} not blacklisted after error 10007")
        return False

result = asyncio.run(test_error_10007())
test2_pass = result

# ============================================================================
# TEST 3: Blacklist Filter in Market Scan
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Blacklist Filter in Market Scan")
print("=" * 80)

async def test_blacklist_filter():
    vortex = VortexBerserker()
    
    # Add symbols to blacklist
    vortex.blacklisted_symbols.add("PENGUIN/USDT")
    vortex.blacklisted_symbols.add("SCAM/USDT")
    
    # Mock the exchange
    vortex.exchange = Mock()
    vortex.exchange.fetch_tickers = AsyncMock(return_value={
        'BTC/USDT': {
            'last': 50000,
            'quoteVolume': 1000000,
            'percentage': 5.0
        },
        'PENGUIN/USDT': {
            'last': 1.0,
            'quoteVolume': 600000,
            'percentage': 10.0
        },
        'ETH/USDT': {
            'last': 3000,
            'quoteVolume': 800000,
            'percentage': 3.0
        },
        'SCAM/USDT': {
            'last': 0.5,
            'quoteVolume': 700000,
            'percentage': 15.0
        }
    })
    
    # Fetch market data
    market_data = await vortex.fetch_global_market()
    
    # Extract symbols from market data
    symbols = [ticker['symbol'] for ticker in market_data]
    
    # Verify blacklisted symbols are not in results
    if 'PENGUIN/USDT' not in symbols and 'SCAM/USDT' not in symbols:
        print("✅ PASS - Blacklisted symbols filtered from market scan")
        print(f"   Market symbols: {symbols}")
        return True
    else:
        print("❌ FAIL - Blacklisted symbols still in market scan")
        print(f"   Market symbols: {symbols}")
        return False

result = asyncio.run(test_blacklist_filter())
test3_pass = result

# ============================================================================
# TEST 4: Post-Buy Cooldown (5 seconds)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Post-Buy Cooldown (5 seconds)")
print("=" * 80)

async def test_post_buy_cooldown():
    vortex = VortexBerserker()
    
    # Mock the exchange
    vortex.exchange = Mock()
    vortex.exchange.fetch_tickers = AsyncMock(return_value={
        'BTC/USDT': {
            'last': 51000  # 2% profit
        }
    })
    vortex.exchange.create_market_sell_order = AsyncMock()
    
    # Add a position that was just bought (less than 5 seconds ago)
    test_symbol = "BTC/USDT"
    vortex.active_slots[test_symbol] = {
        'entry': 50000,
        'qty': 0.001,
        'time': time.time() - 2.0,  # Only 2 seconds ago
        'wing': 'piranha',
        'slot': 1,
        'peak_profit': 0.0
    }
    
    # Try to monitor - should skip due to cooldown
    await vortex.pulse_monitor()
    
    # Verify sell was NOT called (cooldown active)
    if not vortex.exchange.create_market_sell_order.called:
        print("✅ PASS - Sell blocked during cooldown period")
        
        # Now test after cooldown expires
        vortex.active_slots[test_symbol]['time'] = time.time() - 6.0  # 6 seconds ago
        await vortex.pulse_monitor()
        
        if vortex.exchange.create_market_sell_order.called:
            print("✅ PASS - Sell allowed after cooldown expires")
            return True
        else:
            print("❌ FAIL - Sell not allowed even after cooldown")
            return False
    else:
        print("❌ FAIL - Sell executed during cooldown period")
        return False

result = asyncio.run(test_post_buy_cooldown())
test4_pass = result

# ============================================================================
# TEST 5: Verify Sync-Guard Constants
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Verify Sync-Guard Constants")
print("=" * 80)

vortex = VortexBerserker()

# Check that POST_BUY_COOLDOWN is set to 5 seconds
if vortex.POST_BUY_COOLDOWN == 5.0:
    print(f"✅ PASS - POST_BUY_COOLDOWN = {vortex.POST_BUY_COOLDOWN}s")
    test5_pass = True
else:
    print(f"❌ FAIL - POST_BUY_COOLDOWN = {vortex.POST_BUY_COOLDOWN}s (expected 5.0)")
    test5_pass = False

# Check that blacklisted_symbols set exists
if hasattr(vortex, 'blacklisted_symbols') and isinstance(vortex.blacklisted_symbols, set):
    print(f"✅ PASS - blacklisted_symbols initialized as set")
else:
    print(f"❌ FAIL - blacklisted_symbols not properly initialized")
    test5_pass = False

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("SYNC-GUARD TEST SUITE SUMMARY")
print("=" * 80)

all_tests = [
    ("Error 30005 Handling", test1_pass),
    ("Error 10007 Blacklist", test2_pass),
    ("Blacklist Filter", test3_pass),
    ("Post-Buy Cooldown", test4_pass),
    ("Sync-Guard Constants", test5_pass)
]

passed = sum(1 for _, result in all_tests if result)
total = len(all_tests)

print(f"\n📊 Test Results: {passed}/{total} passed")
for test_name, result in all_tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"   {status} - {test_name}")

if passed == total:
    print("\n🛡️ Sync-Guard Stability Patch: ALL TESTS PASSED")
    print("=" * 80)
    sys.exit(0)
else:
    print("\n⚠️ Some tests failed - review implementation")
    print("=" * 80)
    sys.exit(1)
