# 🚀 Quick Start Guide - Vortex Berserker Engine

This guide will help you get the Vortex trading engine running in under 5 minutes.

## ⚠️ Important: Start with PAPER Mode

**Always test with PAPER mode first before using real money.** PAPER mode simulates trading without risking any capital.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## 🔧 Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/DJ-Goana-Coding/pioneer-trader.git
cd pioneer-trader

# Install dependencies
pip install -r requirements.txt
```

## 🔐 Step 2: Configure Environment (PAPER Mode)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Minimal configuration for PAPER mode:**

```env
# REQUIRED: Generate a secret key
SECRET_KEY=your_secret_here

# PAPER mode - no real trading, no API keys needed
EXECUTION_MODE=PAPER

# Vortex configuration
VORTEX_STAKE_USDT=8.0
VORTEX_STOP_LOSS_PCT=0.015
VORTEX_PULSE_SECONDS=8
```

**Generate a secure SECRET_KEY:**

```bash
openssl rand -hex 32
```

Copy the output and paste it as your SECRET_KEY in `.env`

## 🎯 Step 3: Start the Backend

```bash
# Run the FastAPI backend
cd /path/to/pioneer-trader
PYTHONPATH=$PWD python -m backend.main
```

You should see:

```
Starting Pioneer-Admiral V1 in PAPER mode...
⚠️ Vortex running in PAPER mode - simulated execution only
🔥 Vortex Berserker: Initialized (Stake=$8.0, Stop-Loss=1.5%)
INFO:     Application startup complete.
```

The backend is now running on `http://localhost:8000`

## 🎮 Step 4: Test the Vortex Engine

### Check Status

```bash
# First, you need to authenticate
# For testing, you can use the demo endpoint
curl http://localhost:8000/
```

You should see:

```json
{
  "message": "Pioneer-Admiral V1 Online - V19 Fleet Command",
  "mode": "PAPER",
  "version": "V19"
}
```

### View API Documentation

Open your browser to `http://localhost:8000/docs` to see the interactive API documentation.

## 🚨 Emergency Stop

To stop the backend, press `Ctrl+C` in the terminal where it's running.

The Vortex engine will automatically:
1. Stop all trading slots
2. Close any open simulated positions (in PAPER mode)
3. Shut down gracefully

## 📊 Monitoring in PAPER Mode

In PAPER mode, the Vortex engine:
- ✅ Simulates market data
- ✅ Executes simulated trades
- ✅ Tests stop-loss logic
- ✅ Logs all activities
- ❌ Does NOT connect to real exchanges
- ❌ Does NOT use real money

Perfect for:
- Learning how the system works
- Testing your configuration
- Verifying stop-loss behavior
- Understanding the 8-second pulse

## 🔥 Moving to LIVE Mode (Real Money)

**⚠️ READ [SECURITY.md](SECURITY.md) COMPLETELY BEFORE GOING LIVE**

Only after you're comfortable with PAPER mode:

### 1. Get MEXC API Keys

1. Create account at [MEXC](https://www.mexc.com/)
2. Enable 2FA (Two-Factor Authentication)
3. Go to [API Management](https://www.mexc.com/user/openapi)
4. Create API key with **SPOT TRADING ONLY** permissions
5. **NEVER** enable withdrawal permissions

### 2. Update Configuration

```env
# API Keys (NEVER commit these)
MEXC_API_KEY=your_actual_api_key
MEXC_SECRET_KEY=your_actual_secret

# Switch to LIVE mode
EXECUTION_MODE=LIVE

# Start small!
VORTEX_STAKE_USDT=8.0  # Only $8 per trade
```

### 3. Test with Small Amount

- Fund your MEXC account with a small amount you can afford to lose
- Start with $50-100 total
- Monitor closely
- The 1.5% stop-loss is your safety net

### 4. Monitor Your Trades

Watch the logs carefully:

```bash
🚨 [EJECT] SOL/USDT hit 1.5% loss. EXITING AT MARKET.
```

This means the stop-loss worked and protected you.

## 🛡️ Safety Features

Even in LIVE mode, you're protected by:

1. **1.5% Stop-Loss:** Automatically exits losing positions
2. **Market Orders:** Immediate execution, no "sitting there"
3. **8-Second Pulse:** Rapid response to market changes
4. **$8 Stakes:** Small position sizes limit risk

## ❓ Common Issues

### "Module not found" errors

```bash
# Ensure you're running from the correct directory
cd /path/to/pioneer-trader
PYTHONPATH=$PWD python -m backend.main
```

### "SECRET_KEY is required"

Generate one:

```bash
openssl rand -hex 32
```

Add to `.env` file.

### Backend won't start

Check for:
- Correct Python version (3.8+)
- All dependencies installed
- `.env` file exists and has SECRET_KEY

## 📚 Next Steps

1. ✅ Run in PAPER mode for at least a week
2. ✅ Read [SECURITY.md](SECURITY.md) completely
3. ✅ Understand the stop-loss behavior
4. ✅ Review the [V19_ARCHITECTURE.md](V19_ARCHITECTURE.md) for system details
5. ⚠️ Only then consider LIVE mode with small amounts

## 🆘 Need Help?

1. Check logs for error messages
2. Review [SECURITY.md](SECURITY.md)
3. Read API docs at `http://localhost:8000/docs`
4. Open an issue on GitHub

## ⚖️ Remember

- This is experimental software
- Start with PAPER mode
- Only invest what you can afford to lose
- The 1.5% stop-loss is not guaranteed in extreme market conditions
- You are responsible for your own trading decisions

**Trade responsibly. The garage is open. 🛸**
