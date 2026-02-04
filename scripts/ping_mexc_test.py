#!/usr/bin/env python3
# ================================================================
# 🎯 MEXC PING TEST - Verify API Handshake After Render Deploy
# ================================================================
# Tests the MEXC connection without executing trades
# Run this after Render deployment to verify credentials
# ================================================================

import os
import asyncio
import ccxt.async_support as ccxt
from datetime import datetime

def ping_mexc():
    """Test MEXC API connection and credentials"""
    
    print("=" * 60)
    print("🎯 MEXC HANDSHAKE TEST - T.I.A. Verification Protocol")
    print("=" * 60)
    
    # Load credentials from environment
    api_key = os.getenv('MEXC_API_KEY')
    secret = os.getenv('MEXC_SECRET')
    
    if not api_key or not secret:
        print("❌ FATAL: MEXC_API_KEY or MEXC_SECRET not found in environment")
        print("   Set these in your .env file or Render environment variables")
        return False
    
    print(f"✅ Credentials loaded (API Key: {api_key[:8]}...)\n")
    
    # Initialize MEXC exchange
    exchange = ccxt.mexc({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Test 1: Load markets
        print("\n[TEST 1] Loading MEXC markets...")
        await exchange.load_markets()
        print(f"✅ Markets loaded: {len(exchange.markets)} trading pairs available")
        
        # Test 2: Fetch server time
        print("\n[TEST 2] Checking server connectivity...")
        server_time = await exchange.fetch_time()
        print(f"✅ Server time: {datetime.fromtimestamp(server_time/1000).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Test 3: Fetch ticker for test symbol
        test_symbol = 'BTC/USDT'
        print(f"\n[TEST 3] Fetching ticker for {test_symbol}...")
        ticker = await exchange.fetch_ticker(test_symbol)
        print(f"✅ {test_symbol} Last Price: ${ticker['last']:,.2f}")
        
        # Test 4: Fetch account balance (requires valid API key)
        print("\n[TEST 4] Fetching account balance (AUTH TEST)...")
        balance = await exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        print(f"✅ USDT Balance: ${usdt_balance:.2f}")
        
        # Test 5: Check trading pairs in Vortex universe
        print("\n[TEST 5] Verifying Vortex universe pairs...")
        vortex_universe = ['SOL/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT', 'PEPE/USDT']
        for symbol in vortex_universe:
            if symbol in exchange.markets:
                ticker = await exchange.fetch_ticker(symbol)
                print(f"✅ {symbol}: ${ticker['last']:.6f}")
            else:
                print(f"⚠️ {symbol}: NOT AVAILABLE on MEXC")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED - MEXC HANDSHAKE SUCCESSFUL")
        print("=" * 60)
        print("🚀 VortexBerserker is READY TO ENGAGE")
        print("=" * 60)
        
        await exchange.close()
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED: {e}")
        print("   → Check your MEXC_API_KEY and MEXC_SECRET")
        print("   → Verify API permissions in MEXC account settings")
        await exchange.close()
        return False
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        await exchange.close()
        return False

if __name__ == "__main__":
    print("\n🦎 T.I.A. initiating MEXC connection test...\n")
    success = asyncio.run(ping_mexc())
    exit(0 if success else 1)