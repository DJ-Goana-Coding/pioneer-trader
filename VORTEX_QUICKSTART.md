# 🔥 Vortex Berserker Engine - Quick Start Guide

## Overview

The Vortex Berserker Engine is a hardened, aggressive trading system with mandatory safety protocols. It implements an 8-second pulse trading strategy with a non-negotiable 1.5% stop-loss ("Ejector Seat") on all positions.

## 🛡️ Security First - CRITICAL

**Before you do ANYTHING else, read this:**

1. **NEVER** paste your API keys in:
   - Chat conversations
   - Public forums
   - Code comments
   - Git commits

2. **If you've already exposed keys:**
   - Stop reading this
   - Go immediately to:
     - MEXC: https://www.mexc.com/user/openapi → DELETE the exposed key
     - GitHub: https://github.com/settings/tokens → REVOKE the token
   - Generate NEW keys
   - Continue below

3. **Read the full security checklist:**
   ```bash
   cat SECURITY_CHECKLIST.md
   ```

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment

```bash
# Clone repository (if you haven't)
git clone https://github.com/DJ-Goana-Coding/pioneer-trader.git
cd pioneer-trader

# Copy environment template
cp .env.example .env

# Edit .env file and replace ALL placeholders
nano .env
```

### Step 2: Configure Credentials

In your `.env` file, set these REQUIRED variables:

```bash
# MEXC Exchange (get from https://www.mexc.com/user/openapi)
MEXC_API_KEY=your_actual_mexc_api_key_here    # NOT "PLACEHOLDER"
MEXC_SECRET_KEY=your_actual_mexc_secret_here  # NOT "PLACEHOLDER"

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32   # Run: openssl rand -hex 32

# Start in PAPER mode for testing
EXECUTION_MODE=PAPER
```

### Step 3: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 4: Test Security Validation

```bash
# Run security validation test
python3 tests/test_security.py

# You should see: "ALL SECURITY VALIDATION TESTS PASSED ✅"
```

### Step 5: Start in PAPER Mode

```bash
# Start the backend
python -m backend.main

# You should see:
# "Starting Pioneer-Admiral V1 in PAPER mode..."
# "🔥 Vortex Berserker: Initialized (Stake=$8.0, Stop-Loss=1.5%)"
```

### Step 6: Verify Operation

```bash
# In another terminal, test the API
curl http://localhost:8000/

# You should see JSON response with mode="PAPER"
```

## 📊 Vortex Engine Configuration

### Trading Parameters (in .env)

```bash
# Trading stake per position
VORTEX_STAKE_USDT=8.0          # Default: $8 USDT per trade

# Stop-loss percentage (Ejector Seat)
VORTEX_STOP_LOSS_PCT=0.015     # Default: 1.5% (0.015)

# Trading pulse interval
VORTEX_PULSE_SECONDS=8         # Default: 8 seconds

# Safety modulator (0-10 scale)
SAFETY_MODULATOR=5             # Default: 5 (moderate risk)
```

### Trading Universe

The Vortex engine trades these pairs simultaneously:
- SOL/USDT
- XRP/USDT
- DOGE/USDT
- ADA/USDT
- MATIC/USDT
- DOT/USDT
- LINK/USDT

Each pair runs in its own "slot" with independent position management.

## 🎯 Trading Strategy

### Entry Conditions
- RSI < 30 (oversold)
- Price > EMA50 (trend filter)
- No existing position in slot

### Exit Conditions

**Priority 1 - The Ejector Seat (Stop-Loss)**
- Loss >= 1.5% from entry
- **Immediate market sell** (no delays)
- Cannot be disabled
- Checked BEFORE any other logic

**Priority 2 - Take Profit**
- RSI > 70 (overbought)
- Immediate market sell

### Order Types

**All orders are MARKET ORDERS:**
- No limit orders that can "sit there"
- Immediate execution
- Guaranteed fills (at market price)

## 🔧 Control & Monitoring

### Start/Stop Vortex

```bash
# Via API
curl -X POST http://localhost:8000/vortex/start
curl -X POST http://localhost:8000/vortex/stop

# Via Streamlit UI
streamlit run streamlit_app/app.py
# Navigate to Vortex controls
```

### Check Status

```bash
# Get vortex status
curl http://localhost:8000/vortex/status

# Response includes:
# - running: true/false
# - mode: PAPER/LIVE
# - active_positions: count
# - positions: [...details...]
# - configuration: {...params...}
```

### View Logs

```bash
# Watch live logs
tail -f *.log

# Look for:
# 🎯 Slot activated
# 📉 Oversold entry
# 📈 Overbought exit
# 🚨 [EJECT] Stop-loss hit
```

## ⚠️ Transitioning to LIVE Mode

**Only do this after thoroughly testing in PAPER mode:**

### Pre-Flight Checklist

- [ ] Tested in PAPER mode for at least 24 hours
- [ ] Reviewed all entry/exit logic
- [ ] Confirmed stop-loss triggers correctly
- [ ] Checked MEXC API key has correct permissions
- [ ] Set appropriate VORTEX_STAKE_USDT (start small!)
- [ ] Read SECURITY_CHECKLIST.md completely
- [ ] Prepared to monitor actively

### Enable LIVE Mode

```bash
# 1. Stop the system
curl -X POST http://localhost:8000/vortex/stop

# 2. Edit .env
nano .env

# 3. Change mode
EXECUTION_MODE=LIVE

# 4. Restart
python -m backend.main

# 5. Verify live mode
curl http://localhost:8000/vortex/status
# Check: "mode": "LIVE"
```

### First Live Trade

1. **Monitor continuously** for first hour
2. **Start with small stake** (e.g., $5-10)
3. **Watch for entry signals** in logs
4. **Verify orders execute** on MEXC
5. **Test stop-loss** triggers correctly
6. **Gradually increase** stake if comfortable

## 🐛 Troubleshooting

### "Invalid credentials" error on startup

**Problem**: System refuses to start in LIVE mode

**Solution**:
```bash
# Check your .env file
grep PLACEHOLDER .env

# If you see PLACEHOLDER, replace with real keys
# Verify keys are valid on MEXC website
```

### "Failed to fetch data" errors

**Problem**: Exchange connection issues

**Solution**:
```bash
# 1. Check internet connection
ping mexc.com

# 2. Verify API key permissions on MEXC
# Needs: Read, Trade permissions

# 3. Check rate limits
# Wait 1 minute and restart
```

### Positions not closing

**Problem**: Market orders not executing

**Solution**:
```bash
# 1. Check MEXC account balance
# Need sufficient balance for trade

# 2. Verify trading pair is active
# Check if MEXC has suspended the pair

# 3. Review logs for specific error
tail -100 *.log | grep ERROR
```

### Stop-loss not triggering

**Problem**: Concerned about stop-loss

**Solution**:
- Stop-loss is MANDATORY and cannot be disabled
- Check logs for "🚨 [EJECT]" messages
- Verify VORTEX_STOP_LOSS_PCT is set correctly
- Test in PAPER mode with simulated price drops

## 📚 Additional Resources

- **Full Security Guide**: `SECURITY_CHECKLIST.md`
- **V19 Architecture**: `V19_ARCHITECTURE.md`
- **General Quickstart**: `QUICKSTART.md`
- **API Documentation**: http://localhost:8000/docs (when running)

## 🆘 Emergency Stop

If something goes wrong:

```bash
# 1. Stop vortex immediately
curl -X POST http://localhost:8000/vortex/stop

# 2. Stop backend
# Press Ctrl+C in terminal

# 3. Manually close positions on MEXC if needed
# Log into MEXC web interface
# Go to Spot Trading → Open Orders → Cancel All
```

## 💡 Tips

1. **Always test in PAPER mode first** - No exceptions
2. **Start with small stakes** - Increase gradually
3. **Monitor actively** - Especially first 24 hours in LIVE
4. **Keep logs** - Helpful for troubleshooting
5. **Don't panic** - Ejector Seat protects you at 1.5% loss
6. **Scale slowly** - Prove strategy works before scaling up

## ⚡ The Commander's Mandate

- **Stake**: $8 USDT per trade (configurable)
- **Stop-Loss**: 1.5% mandatory (the "Ejector Seat")
- **Pulse**: 8 seconds (aggressive)
- **Slots**: 7 simultaneous pairs
- **Orders**: Market only (no sitting)

Remember: **The Ejector Seat is your friend.** It's designed to protect your capital by cutting losses quickly.

---

**Ready to begin?**

```bash
# Security first
cat SECURITY_CHECKLIST.md

# Then start in PAPER mode
cp .env.example .env
nano .env  # Replace placeholders
python -m backend.main
```

**Questions? Issues?**

Check `SECURITY_CHECKLIST.md` and `V19_ARCHITECTURE.md` first.
