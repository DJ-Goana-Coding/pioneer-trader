#!/usr/bin/env python3
"""
🌊 Vortex V3.1.0 Tests - Intelligent Stagnation Filter & Adaptive MLOFI Gatekeeper
Tests for intelligent stagnation detection, context-aware MLOFI filtering, and dynamic position sizing
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

# Test Constants
SECONDS_PER_5MIN = 300  # 5 minutes in seconds

print("=" * 80)
print("🌊 VORTEX V3.1.0 - INTELLIGENT TRADING TESTS")
print("=" * 80)

# ============================================================================
# TEST 1: Dynamic Position Sizing (4% Rule)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: Dynamic Position Sizing (4% Rule)")
print("=" * 80)

def test_position_sizing():
    vortex = VortexBerserker()
    
    # Test with $100 capital (should get $4 = 4%)
    stake = vortex.calculate_position_size(100.0)
    if stake == 5.0:  # Min $5 enforced
        print(f"✅ PASS - $100 equity → ${stake:.2f} stake (min $5 enforced)")
        test1a = True
    else:
        print(f"❌ FAIL - $100 equity → ${stake:.2f} stake (expected $5.00)")
        test1a = False
    
    # Test with $200 capital (should get $8 = 4%)
    stake = vortex.calculate_position_size(200.0)
    if stake == 8.0:
        print(f"✅ PASS - $200 equity → ${stake:.2f} stake (4% rule)")
        test1b = True
    else:
        print(f"❌ FAIL - $200 equity → ${stake:.2f} stake (expected $8.00)")
        test1b = False
    
    # Test with $500 capital (should get $15 = max cap)
    stake = vortex.calculate_position_size(500.0)
    if stake == 15.0:  # Max $15 enforced
        print(f"✅ PASS - $500 equity → ${stake:.2f} stake (max $15 enforced)")
        test1c = True
    else:
        print(f"❌ FAIL - $500 equity → ${stake:.2f} stake (expected $15.00)")
        test1c = False
    
    # Test with $50 capital (should get $5 = min)
    stake = vortex.calculate_position_size(50.0)
    if stake == 5.0:  # Min $5 enforced
        print(f"✅ PASS - $50 equity → ${stake:.2f} stake (min $5 enforced)")
        test1d = True
    else:
        print(f"❌ FAIL - $50 equity → ${stake:.2f} stake (expected $5.00)")
        test1d = False
    
    return test1a and test1b and test1c and test1d

test1_pass = test_position_sizing()

# ============================================================================
# TEST 2: RSI Calculation
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: RSI Calculation")
print("=" * 80)

def test_rsi_calculation():
    vortex = VortexBerserker()
    
    # Test with simulated price data (trending up)
    prices_up = [100, 102, 104, 103, 105, 107, 106, 108, 110, 109, 111, 113, 112, 114, 116]
    rsi_up = vortex._calculate_rsi(prices_up, period=14)
    
    if rsi_up is not None and 50 < rsi_up < 100:
        print(f"✅ PASS - Uptrend RSI = {rsi_up:.2f} (expected 50-100)")
        test2a = True
    else:
        print(f"❌ FAIL - Uptrend RSI = {rsi_up} (expected 50-100)")
        test2a = False
    
    # Test with simulated price data (trending down)
    prices_down = [100, 98, 96, 97, 95, 93, 94, 92, 90, 91, 89, 87, 88, 86, 84]
    rsi_down = vortex._calculate_rsi(prices_down, period=14)
    
    if rsi_down is not None and 0 < rsi_down < 50:
        print(f"✅ PASS - Downtrend RSI = {rsi_down:.2f} (expected 0-50)")
        test2b = True
    else:
        print(f"❌ FAIL - Downtrend RSI = {rsi_down} (expected 0-50)")
        test2b = False
    
    # Test with insufficient data
    prices_short = [100, 102, 104]
    rsi_short = vortex._calculate_rsi(prices_short, period=14)
    
    if rsi_short is None:
        print(f"✅ PASS - Insufficient data returns None")
        test2c = True
    else:
        print(f"❌ FAIL - Insufficient data returned {rsi_short} (expected None)")
        test2c = False
    
    return test2a and test2b and test2c

test2_pass = test_rsi_calculation()

# ============================================================================
# TEST 3: Intelligent Stagnation Filter - Early Exit Prevention
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: Intelligent Stagnation Filter - Early Exit Prevention")
print("=" * 80)

async def test_stagnation_early_exit():
    vortex = VortexBerserker()
    
    # Mock exchange for candle data
    vortex.exchange = Mock()
    
    test_symbol = "BTC/USDT"
    entry_price = 50000.0
    current_price = 49600.0  # -0.8% loss
    
    # Test Case 1: Position held for only 2 hours (should NOT liquidate)
    entry_time_2h = time.time() - (2 * 3600)
    
    should_liquidate, reason = await vortex.should_liquidate_stagnant(
        test_symbol, entry_time_2h, entry_price, current_price
    )
    
    if not should_liquidate:
        print(f"✅ PASS - 2 hours old with -0.8% loss: NOT liquidated (min 4h rule)")
        test3a = True
    else:
        print(f"❌ FAIL - 2 hours old with -0.8% loss: Liquidated (should wait 4h)")
        test3a = False
    
    # Test Case 2: Position held for 3.5 hours (should NOT liquidate)
    entry_time_3h = time.time() - (3.5 * 3600)
    
    should_liquidate, reason = await vortex.should_liquidate_stagnant(
        test_symbol, entry_time_3h, entry_price, current_price
    )
    
    if not should_liquidate:
        print(f"✅ PASS - 3.5 hours old with -0.8% loss: NOT liquidated (min 4h rule)")
        test3b = True
    else:
        print(f"❌ FAIL - 3.5 hours old with -0.8% loss: Liquidated (should wait 4h)")
        test3b = False
    
    return test3a and test3b

test3_pass = asyncio.run(test_stagnation_early_exit())

# ============================================================================
# TEST 4: Intelligent Stagnation Filter - Loss with No Recovery
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Intelligent Stagnation Filter - Loss with No Recovery")
print("=" * 80)

async def test_stagnation_loss_no_recovery():
    vortex = VortexBerserker()
    
    # Mock exchange
    vortex.exchange = Mock()
    
    # Mock get_candle_data to return declining prices
    # Simulate 5-minute candles showing price decline over 30 minutes
    mock_candles = []
    base_price = 50000
    for i in range(50):
        # Declining prices - end at 49510 (50000 - 490)
        price = base_price - (i * 10)
        mock_candles.append([
            time.time() - (50-i) * SECONDS_PER_5MIN,  # timestamp (5 min intervals)
            price,  # open
            price + 5,  # high
            price - 5,  # low
            price,  # close
            1000  # volume
        ])
    
    vortex.exchange.fetch_ohlcv = AsyncMock(return_value=mock_candles)
    
    test_symbol = "BTC/USDT"
    entry_price = 50000.0
    current_price = 49510.0  # -0.98% loss (below -0.8% threshold)
    entry_time = time.time() - (5 * 3600)  # 5 hours old
    
    should_liquidate, reason = await vortex.should_liquidate_stagnant(
        test_symbol, entry_time, entry_price, current_price
    )
    
    if should_liquidate and "no recovery" in reason.lower():
        print(f"✅ PASS - 5h old, -0.98% loss, declining: LIQUIDATED")
        print(f"   Reason: {reason}")
        return True
    else:
        print(f"❌ FAIL - Should liquidate stagnant position with no recovery")
        print(f"   Result: {should_liquidate}, Reason: {reason}")
        return False

test4_pass = asyncio.run(test_stagnation_loss_no_recovery())

# ============================================================================
# TEST 5: Intelligent Stagnation Filter - Breakeven Stagnation
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Intelligent Stagnation Filter - Breakeven Stagnation")
print("=" * 80)

async def test_stagnation_breakeven():
    vortex = VortexBerserker()
    
    test_symbol = "BTC/USDT"
    entry_price = 50000.0
    current_price = 50050.0  # +0.1% (within breakeven range)
    
    # Test Case 1: 5 hours old (should NOT liquidate - need 8h)
    entry_time_5h = time.time() - (5 * 3600)
    
    should_liquidate, reason = await vortex.should_liquidate_stagnant(
        test_symbol, entry_time_5h, entry_price, current_price
    )
    
    if not should_liquidate:
        print(f"✅ PASS - 5h breakeven position: NOT liquidated (need 8h)")
        test5a = True
    else:
        print(f"❌ FAIL - 5h breakeven position: Liquidated (should wait 8h)")
        test5a = False
    
    # Test Case 2: 9 hours old (should liquidate - free up capital)
    entry_time_9h = time.time() - (9 * 3600)
    
    should_liquidate, reason = await vortex.should_liquidate_stagnant(
        test_symbol, entry_time_9h, entry_price, current_price
    )
    
    if should_liquidate and "sideways" in reason.lower():
        print(f"✅ PASS - 9h breakeven position: LIQUIDATED (free up capital)")
        print(f"   Reason: {reason}")
        test5b = True
    else:
        print(f"❌ FAIL - 9h breakeven position should be liquidated")
        print(f"   Result: {should_liquidate}, Reason: {reason}")
        test5b = False
    
    return test5a and test5b

test5_pass = asyncio.run(test_stagnation_breakeven())

# ============================================================================
# TEST 6: MLOFI Gatekeeper - High Liquidity
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: MLOFI Gatekeeper - High Liquidity")
print("=" * 80)

async def test_mlofi_high_liquidity():
    vortex = VortexBerserker()
    
    # Mock exchange
    vortex.exchange = Mock()
    
    # Create mock candles with oversold RSI (prices declining)
    mock_candles = []
    base_price = 100
    for i in range(50):
        price = base_price - (i * 0.5)  # Declining prices
        mock_candles.append([
            time.time() - (50-i) * SECONDS_PER_5MIN,
            price, price + 1, price - 1, price, 1000
        ])
    
    vortex.exchange.fetch_ohlcv = AsyncMock(return_value=mock_candles)
    
    test_symbol = "BTC/USDT"
    volume_high = 60_000_000  # $60M volume (high liquidity)
    
    # Should be allowed due to oversold RSI
    allowed, reason = await vortex.is_buy_allowed(test_symbol, volume_high)
    
    if allowed:
        print(f"✅ PASS - High liquidity with oversold RSI: ALLOWED")
        print(f"   Reason: {reason}")
        return True
    else:
        print(f"❌ FAIL - High liquidity with oversold should be allowed")
        print(f"   Reason: {reason}")
        return False

test6_pass = asyncio.run(test_mlofi_high_liquidity())

# ============================================================================
# TEST 7: MLOFI Gatekeeper - Mid Liquidity with Extreme Oversold
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: MLOFI Gatekeeper - Mid Liquidity with Extreme Oversold")
print("=" * 80)

async def test_mlofi_mid_liquidity():
    vortex = VortexBerserker()
    
    # Mock exchange
    vortex.exchange = Mock()
    
    # Create mock candles with extreme oversold RSI
    mock_candles = []
    base_price = 100
    for i in range(50):
        price = base_price - (i * 1.0)  # Strong decline for low RSI
        mock_candles.append([
            time.time() - (50-i) * SECONDS_PER_5MIN,
            price, price + 1, price - 1, price, 1000
        ])
    
    vortex.exchange.fetch_ohlcv = AsyncMock(return_value=mock_candles)
    
    test_symbol = "ETH/USDT"
    volume_mid = 20_000_000  # $20M volume (mid liquidity)
    
    # Should be allowed due to extreme oversold
    allowed, reason = await vortex.is_buy_allowed(test_symbol, volume_mid)
    
    if allowed and "extreme oversold" in reason.lower():
        print(f"✅ PASS - Mid liquidity with extreme oversold: ALLOWED")
        print(f"   Reason: {reason}")
        return True
    else:
        print(f"❌ FAIL - Mid liquidity with extreme oversold should be allowed")
        print(f"   Result: {allowed}, Reason: {reason}")
        return False

test7_pass = asyncio.run(test_mlofi_mid_liquidity())

# ============================================================================
# TEST 8: MLOFI Gatekeeper - Low Liquidity with Positive Momentum
# ============================================================================
print("\n" + "=" * 80)
print("TEST 8: MLOFI Gatekeeper - Low Liquidity with Positive Momentum")
print("=" * 80)

async def test_mlofi_low_liquidity():
    vortex = VortexBerserker()
    
    # Mock exchange
    vortex.exchange = Mock()
    
    # Create mock candles with positive momentum (prices rising)
    mock_candles = []
    base_price = 100
    for i in range(50):
        price = base_price + (i * 0.5)  # Rising prices
        mock_candles.append([
            time.time() - (50-i) * SECONDS_PER_5MIN,
            price, price + 1, price - 1, price, 1000
        ])
    
    vortex.exchange.fetch_ohlcv = AsyncMock(return_value=mock_candles)
    
    test_symbol = "SHIB/USDT"
    volume_low = 5_000_000  # $5M volume (low liquidity)
    
    # Should be allowed due to positive momentum
    allowed, reason = await vortex.is_buy_allowed(test_symbol, volume_low)
    
    if allowed and "positive momentum" in reason.lower():
        print(f"✅ PASS - Low liquidity with positive momentum: ALLOWED")
        print(f"   Reason: {reason}")
        return True
    else:
        print(f"❌ FAIL - Low liquidity with positive momentum should be allowed")
        print(f"   Result: {allowed}, Reason: {reason}")
        return False

test8_pass = asyncio.run(test_mlofi_low_liquidity())

# ============================================================================
# TEST 9: MLOFI Gatekeeper - Low Liquidity without Momentum (Blocked)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 9: MLOFI Gatekeeper - Low Liquidity without Momentum (Blocked)")
print("=" * 80)

async def test_mlofi_low_liquidity_blocked():
    vortex = VortexBerserker()
    
    # Mock exchange
    vortex.exchange = Mock()
    
    # Create mock candles with negative momentum (prices declining)
    mock_candles = []
    base_price = 100
    for i in range(50):
        price = base_price - (i * 0.3)  # Declining prices
        mock_candles.append([
            time.time() - (50-i) * SECONDS_PER_5MIN,
            price, price + 1, price - 1, price, 1000
        ])
    
    vortex.exchange.fetch_ohlcv = AsyncMock(return_value=mock_candles)
    
    test_symbol = "DOGE/USDT"
    volume_low = 3_000_000  # $3M volume (low liquidity)
    
    # Should be blocked due to negative momentum
    allowed, reason = await vortex.is_buy_allowed(test_symbol, volume_low)
    
    if not allowed and "without positive momentum" in reason.lower():
        print(f"✅ PASS - Low liquidity without momentum: BLOCKED")
        print(f"   Reason: {reason}")
        return True
    else:
        print(f"❌ FAIL - Low liquidity without momentum should be blocked")
        print(f"   Result: {allowed}, Reason: {reason}")
        return False

test9_pass = asyncio.run(test_mlofi_low_liquidity_blocked())

# ============================================================================
# TEST 10: Configuration Constants
# ============================================================================
print("\n" + "=" * 80)
print("TEST 10: Configuration Constants")
print("=" * 80)

def test_configuration():
    vortex = VortexBerserker()
    
    # Verify stagnation filter constants
    if vortex.MIN_HOLD_HOURS == 4.0:
        print(f"✅ PASS - MIN_HOLD_HOURS = {vortex.MIN_HOLD_HOURS}")
        test10a = True
    else:
        print(f"❌ FAIL - MIN_HOLD_HOURS = {vortex.MIN_HOLD_HOURS} (expected 4.0)")
        test10a = False
    
    if vortex.STAGNATION_LOSS_THRESHOLD == -0.008:
        print(f"✅ PASS - STAGNATION_LOSS_THRESHOLD = {vortex.STAGNATION_LOSS_THRESHOLD}")
        test10b = True
    else:
        print(f"❌ FAIL - STAGNATION_LOSS_THRESHOLD = {vortex.STAGNATION_LOSS_THRESHOLD} (expected -0.008)")
        test10b = False
    
    # Verify MLOFI constants
    if vortex.HIGH_LIQUIDITY_THRESHOLD == 50_000_000:
        print(f"✅ PASS - HIGH_LIQUIDITY_THRESHOLD = ${vortex.HIGH_LIQUIDITY_THRESHOLD:,}")
        test10c = True
    else:
        print(f"❌ FAIL - HIGH_LIQUIDITY_THRESHOLD = {vortex.HIGH_LIQUIDITY_THRESHOLD}")
        test10c = False
    
    # Verify position sizing constants
    if vortex.POSITION_SIZE_PCT == 0.04:
        print(f"✅ PASS - POSITION_SIZE_PCT = {vortex.POSITION_SIZE_PCT} (4%)")
        test10d = True
    else:
        print(f"❌ FAIL - POSITION_SIZE_PCT = {vortex.POSITION_SIZE_PCT} (expected 0.04)")
        test10d = False
    
    if vortex.MIN_POSITION_SIZE == 5.0 and vortex.MAX_POSITION_SIZE == 15.0:
        print(f"✅ PASS - Position size range: ${vortex.MIN_POSITION_SIZE} - ${vortex.MAX_POSITION_SIZE}")
        test10e = True
    else:
        print(f"❌ FAIL - Position size range incorrect")
        test10e = False
    
    return test10a and test10b and test10c and test10d and test10e

test10_pass = test_configuration()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("VORTEX V3.1.0 TEST SUITE SUMMARY")
print("=" * 80)

all_tests = [
    ("Dynamic Position Sizing (4% Rule)", test1_pass),
    ("RSI Calculation", test2_pass),
    ("Stagnation Filter - Early Exit Prevention", test3_pass),
    ("Stagnation Filter - Loss with No Recovery", test4_pass),
    ("Stagnation Filter - Breakeven Stagnation", test5_pass),
    ("MLOFI Gatekeeper - High Liquidity", test6_pass),
    ("MLOFI Gatekeeper - Mid Liquidity", test7_pass),
    ("MLOFI Gatekeeper - Low Liquidity Allowed", test8_pass),
    ("MLOFI Gatekeeper - Low Liquidity Blocked", test9_pass),
    ("Configuration Constants", test10_pass)
]

passed = sum(1 for _, result in all_tests if result)
total = len(all_tests)

print(f"\n📊 Test Results: {passed}/{total} passed")
for test_name, result in all_tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"   {status} - {test_name}")

if passed == total:
    print("\n🌊 Vortex V3.1.0: ALL TESTS PASSED")
    print("=" * 80)
    sys.exit(0)
else:
    print("\n⚠️ Some tests failed - review implementation")
    print("=" * 80)
    sys.exit(1)
