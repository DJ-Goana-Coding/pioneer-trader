# 🔥 BERSERKER V6.9 - DEPLOYMENT GUIDE

## MASTER OVERRIDE DIRECTIVE - COMPLETE ✅

Commander, the **Berserker V6.9** hardened trading engine is now operational. All legacy code has been purged. The system is MEXC-exclusive with mandatory safety protocols.

---

## 🎯 WHAT CHANGED

### Legacy Services REMOVED ❌
- **Binance Support** - Completely removed
- **ExchangeService** - Removed (replaced by Vortex)
- **OMS (Order Management System)** - Removed (replaced by Vortex)
- **StrategyEngine** - Removed (replaced by Vortex)
- **/strategy router** - Removed (depended on legacy services)
- **/trade router** - Removed (depended on legacy services)

### Vortex Berserker NOW PRIMARY ✅
- **ONLY Trading Engine** - Vortex is the sole trading system
- **MEXC Exclusive** - Only supports MEXC exchange (ccxt.mexc)
- **Market Orders Only** - No limit orders (eliminates "sitting there" problem)
- **Mandatory Stop-Loss** - 1.5% Ejector Seat on ALL positions (cannot be disabled)

---

## 🔥 BERSERKER V6.9 SPECIFICATIONS

### Trading Parameters (Commander's Mandate)
```
Stake:           $8.00 USDT per trade
Stop-Loss:       1.5% (MANDATORY - Priority 1 check)
Pulse:           8 seconds (aggressive)
Slots:           7 parallel trades
Exchange:        MEXC ONLY
Order Type:      Market orders ONLY
```

### Trading Universe (7 Slots)
1. SOL/USDT  
2. XRP/USDT  
3. DOGE/USDT  
4. ADA/USDT  
5. MATIC/USDT  
6. DOT/USDT  
7. LINK/USDT  

### Strategy Logic
```
Strategy:    RSI(14) + EMA(50)
Entry:       RSI < 30 AND price > EMA50
Exit:        RSI > 70 OR stop-loss triggered
Priority:    Stop-loss check ALWAYS runs first
```

### The "Ejector Seat" - Mandatory Stop-Loss
```python
# This check runs BEFORE any other logic
if drawdown >= 1.5%:
    execute_market_sell()  # IMMEDIATE exit
    # No confirmation, no waiting, no limit orders
```

---

## 🚀 DEPLOYMENT INSTRUCTIONS

### 1. Security First - Revoke Exposed Keys

**IF YOU PASTED KEYS IN CHAT/PUBLIC:**
1. Go to https://www.mexc.com/user/openapi
2. Delete the exposed API key immediately
3. Generate NEW credentials
4. Update your local .env file

### 2. Environment Setup

```bash
# Clone or navigate to repository
cd pioneer-trader

# Copy environment template
cp .env.example .env

# Edit with your REAL credentials
nano .env
```

**Required in .env:**
```bash
# Generate with: openssl rand -hex 32
SECRET_KEY=<your-64-char-hex-string>

# From: https://www.mexc.com/user/openapi
MEXC_API_KEY=<your-mexc-api-key>
MEXC_SECRET_KEY=<your-mexc-secret-key>

# Start in PAPER mode for testing
EXECUTION_MODE=PAPER
```

### 3. Test in PAPER Mode

```bash
# Install dependencies
pip3 install -r requirements.txt

# Start the engine
python -m backend.main
```

**Expected Output:**
```
================================================================================
🔥 BERSERKER V6.9 - Hardened MEXC Trading Engine
Mode: PAPER | UI Theme: OVERKILL
Safety Modulator: 5/10
================================================================================

🔥 Vortex Berserker: ARMED
   Stake: $8.0 USDT per trade
   Ejector Seat: 1.5% stop-loss (MANDATORY)
   Pulse: 8s aggressive interval
   Slots: 7 parallel (7 pairs)
   Exchange: MEXC ONLY (market orders only)

🧠 Phi-3.5 Swarm: 6 drones active
🛡️ Red Flag Malware Scanner: armed
📦 Shadow Archive: /tmp/shadow_archive

================================================================================
✅ BERSERKER V6.9 ONLINE - All systems operational
================================================================================
```

### 4. Verify System Status

```bash
# In another terminal, check the API
curl http://localhost:8000/

# Expected response:
{
  "message": "🔥 Berserker V6.9 Online - Hardened MEXC Trading Engine",
  "mode": "PAPER",
  "exchange": "MEXC",
  "version": "6.9.0",
  "warning": "Market orders only - No limit orders - Mandatory 1.5% stop-loss"
}
```

### 5. Start Vortex Engine

```bash
# Via API
curl -X POST http://localhost:8000/vortex/start

# Or via Python
python3 -c "
import requests
resp = requests.post('http://localhost:8000/vortex/start')
print(resp.json())
"
```

### 6. Monitor Status

```bash
# Check Vortex status
curl http://localhost:8000/vortex/status

# Check telemetry
curl http://localhost:8000/telemetry/vortex
```

---

## ⚠️ LIVE MODE TRANSITION

**ONLY after extensive PAPER mode testing:**

1. **Verify PAPER results are acceptable**
2. **Confirm stop-loss is triggering correctly**
3. **Update .env:**
   ```bash
   EXECUTION_MODE=LIVE
   ```
4. **Restart the engine**
5. **Monitor closely for first 30 minutes**

---

## 🛡️ SAFETY FEATURES

### Multi-Layer Protection

1. **Git Layer** - .gitignore prevents credential commits
2. **Environment Layer** - Credentials in .env only (never in code)
3. **Runtime Layer** - Startup validation rejects placeholders
4. **Trading Layer** - Mandatory 1.5% stop-loss on all positions
5. **Execution Layer** - Market orders only (no stuck orders)

### The "Ejector Seat"
- Checks on EVERY 8-second pulse
- Triggers at 1.5% loss (no exceptions)
- Uses market sell (immediate execution)
- Cannot be disabled or overridden
- Priority 1 check (runs before any other logic)

### No "Sitting There" Problem
- All BUY orders: Market (fills immediately)
- All SELL orders: Market (fills immediately)
- No limit orders = No stuck trades
- No partial fills = No lingering positions

---

## 📊 ARCHITECTURE

```
┌────────────────────────────────────────────┐
│  BERSERKER V6.9 - MEXC EXCLUSIVE           │
└────────────────┬───────────────────────────┘
                 │
┌────────────────┴───────────────────────────┐
│  VORTEX BERSERKER ENGINE (PRIMARY)         │
│  - 7 parallel trading slots                │
│  - $8 stake per trade                      │
│  - 1.5% mandatory stop-loss                │
│  - 8-second pulse                          │
│  - Market orders ONLY                      │
└────────────────┬───────────────────────────┘
                 │
┌────────────────┴───────────────────────────┐
│  MEXC EXCHANGE (ccxt.mexc)                 │
│  - Spot trading only                       │
│  - Real-time price data                    │
│  - Market order execution                  │
└────────────────┬───────────────────────────┘
                 │
┌────────────────┴───────────────────────────┐
│  SUPPORTING SERVICES                       │
│  - Phi-3.5 Swarm (intelligence)            │
│  - Malware Scanner (security)              │
│  - Archival (logging)                      │
└────────────────────────────────────────────┘
```

---

## 🎯 TROUBLESHOOTING

### "Cannot start in LIVE mode with placeholders"
**Solution:** Edit .env file and replace ALL placeholder values with real credentials

### "MEXC exchange initialization failed"
**Solution:** 
1. Verify MEXC_API_KEY and MEXC_SECRET_KEY are correct
2. Check API key permissions (must allow spot trading)
3. Verify API key is not IP-restricted

### "Module not found: fastapi"
**Solution:** Run `pip3 install -r requirements.txt`

### "Connection refused to localhost:8000"
**Solution:** Start the backend first: `python -m backend.main`

---

## 📚 DOCUMENTATION INDEX

- **SECURITY_CHECKLIST.md** - Complete security guide
- **VORTEX_QUICKSTART.md** - Vortex engine guide
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **V19_ARCHITECTURE.md** - Full system architecture
- **BERSERKER_V6.9_DEPLOYMENT.md** - This document

---

## 🔒 SECURITY REMINDERS

1. ✅ **NEVER** paste real API keys in chat, forums, or public locations
2. ✅ **ALWAYS** store credentials in .env file only
3. ✅ **TEST** in PAPER mode before LIVE
4. ✅ **MONITOR** actively when running LIVE (especially first hour)
5. ✅ **REVOKE** keys immediately if exposed

---

## ✅ DEPLOYMENT CHECKLIST

Before going LIVE, verify:

- [ ] MEXC API keys are generated and permissions verified
- [ ] .env file contains REAL credentials (not placeholders)
- [ ] SECRET_KEY is 32+ characters (generated with openssl)
- [ ] Tested extensively in PAPER mode
- [ ] Stop-loss triggers correctly at 1.5%
- [ ] Market orders execute immediately
- [ ] Monitoring system in place
- [ ] Emergency stop procedure understood (`/vortex/stop`)

---

## 🚨 EMERGENCY PROCEDURES

### Stop All Trading Immediately

```bash
# Via API
curl -X POST http://localhost:8000/vortex/stop

# Or kill the process
pkill -f "python -m backend.main"
```

### Close All Positions Manually

```bash
# Login to MEXC web interface
# Go to: https://www.mexc.com/exchange
# Manually close any open positions
```

### Revoke Compromised Keys

```bash
# 1. Go to: https://www.mexc.com/user/openapi
# 2. Find the API key
# 3. Click "Delete"
# 4. Generate new keys
# 5. Update .env file
# 6. Restart the engine
```

---

**Deployment Date:** 2026-02-03  
**Version:** Berserker V6.9  
**Status:** OPERATIONAL ✅  
**Exchange:** MEXC ONLY  
**Safety:** Mandatory 1.5% Stop-Loss  

**Commander, the Berserker is armed and ready. Shall we begin the windfall?** 🔥
