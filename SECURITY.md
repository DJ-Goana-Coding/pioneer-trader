# 🛡️ Security & Deployment Guide

## ⚠️ CRITICAL: Never Commit Secrets

**API keys, tokens, and secrets should NEVER be committed to git.**

This repository uses `.env` files for sensitive configuration. The `.gitignore` file is already configured to exclude:
- `.env` files
- `.venv/` and `venv/` directories
- `__pycache__/` directories

## 🔐 Setting Up Your Environment

### 1. Create Your .env File

Copy the example file and fill in your actual values:

```bash
cp .env.example .env
```

### 2. Generate a Secure SECRET_KEY

For production deployments, generate a strong secret key:

```bash
openssl rand -hex 32
```

Replace the default `SECRET_KEY` in `.env` with this value.

### 3. Configure Exchange API Keys

#### For MEXC (Vortex Engine):

1. Go to [MEXC API Management](https://www.mexc.com/user/openapi)
2. Create a new API key with **Spot Trading** permissions ONLY
3. **NEVER** enable withdrawal permissions
4. Add your IP address to the whitelist if possible
5. Copy the API key and secret to your `.env` file:

```env
MEXC_API_KEY=your_actual_key_here
MEXC_SECRET_KEY=your_actual_secret_here
```

#### For Binance (Legacy Support):

1. Go to [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Create a new API key with **Spot Trading** permissions ONLY
3. **NEVER** enable withdrawal permissions
4. Add to `.env`:

```env
BINANCE_API_KEY=your_actual_key_here
BINANCE_SECRET_KEY=your_actual_secret_here
```

## 🚨 Emergency: API Key Compromise

If you accidentally expose your API keys (commit to git, screenshot, chat log, etc.):

### Immediate Actions (Do these FIRST):

1. **MEXC:** Go to [API Management](https://www.mexc.com/user/openapi) and **DELETE** the compromised key immediately
2. **Binance:** Go to [API Management](https://www.binance.com/en/my/settings/api-management) and **DELETE** the compromised key
3. **GitHub:** Go to [Personal Access Tokens](https://github.com/settings/tokens) and **REVOKE** any exposed tokens
4. **HuggingFace:** Go to [Tokens](https://huggingface.co/settings/tokens) and **REVOKE** any exposed tokens

### After Securing:

1. Generate new API keys
2. Update your local `.env` file
3. **Do NOT commit** the new keys
4. If you committed secrets to git, you must:
   - Remove them from git history (use `git filter-branch` or BFG Repo-Cleaner)
   - Force push to rewrite history
   - Consider the repository contaminated and potentially start fresh

## 🎯 Vortex Engine: The Ejector Seat

The Vortex Berserker Engine implements **mandatory survival protocols**:

### Hard Stop-Loss (1.5%)

- **ALWAYS ACTIVE:** Cannot be disabled
- **PRIORITY #1:** Checked before ANY other trading logic
- **MARKET ORDERS ONLY:** Immediate exit, no waiting
- **Commander's Mandate:** Protects capital above all else

### Configuration

```env
# Recommended conservative settings for testing
EXECUTION_MODE=PAPER              # Start with PAPER mode
VORTEX_STAKE_USDT=8.0            # $8 per trade
VORTEX_STOP_LOSS_PCT=0.015       # 1.5% ejector seat
VORTEX_PULSE_SECONDS=8           # 8-second pulse

# When ready for live trading
EXECUTION_MODE=LIVE              # Switch to LIVE carefully
```

### Trading Universe

Default trading pairs (all vs USDT):
- SOL/USDT
- XRP/USDT
- DOGE/USDT
- ADA/USDT
- MATIC/USDT
- DOT/USDT
- LINK/USDT

## 📊 Execution Modes

### PAPER Mode (Recommended for Testing)

- Simulated execution
- No real trades
- Uses mock market data
- Safe for testing strategies
- No API keys required

```env
EXECUTION_MODE=PAPER
```

### TESTNET Mode

- Some exchanges support testnet (simulated money, real API)
- Depends on exchange support

```env
EXECUTION_MODE=TESTNET
```

### LIVE Mode (Real Money)

**⚠️ USE WITH EXTREME CAUTION**

- Real trades with real money
- Requires funded exchange account
- Start with small amounts
- Monitor constantly
- Respect the stop-loss

```env
EXECUTION_MODE=LIVE
```

## 🔒 Security Best Practices

### API Key Permissions

✅ **DO:**
- Enable SPOT trading only
- Set IP whitelist if possible
- Start with small trading limits
- Monitor API usage regularly
- Rotate keys periodically

❌ **DON'T:**
- Enable withdrawal permissions
- Enable futures/margin unless needed
- Share keys in screenshots/chat
- Commit keys to git
- Use keys from untrusted sources

### Deployment

#### Local Development

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in PAPER mode first
EXECUTION_MODE=PAPER python -m backend.main
```

#### Production Deployment

```bash
# 1. Use environment variables (not .env files)
export SECRET_KEY="your-secure-key"
export MEXC_API_KEY="your-key"
export MEXC_SECRET_KEY="your-secret"
export EXECUTION_MODE="LIVE"

# 2. Run with production settings
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker Deployment

```dockerfile
# Use secrets management (not .env in image)
docker run -d \
  -e SECRET_KEY="${SECRET_KEY}" \
  -e MEXC_API_KEY="${MEXC_API_KEY}" \
  -e MEXC_SECRET_KEY="${MEXC_SECRET_KEY}" \
  -e EXECUTION_MODE="LIVE" \
  pioneer-trader:latest
```

## 🚀 Vortex API Usage

### Start the Engine

```bash
# POST /vortex/start (requires authentication)
curl -X POST http://localhost:8000/vortex/start \
  -H "Authorization: Bearer your_jwt_token"
```

### Check Status

```bash
# GET /vortex/status (no auth required)
curl http://localhost:8000/vortex/status
```

### View Positions

```bash
# GET /vortex/positions (requires authentication)
curl http://localhost:8000/vortex/positions \
  -H "Authorization: Bearer your_jwt_token"
```

### Stop the Engine

```bash
# POST /vortex/stop (requires authentication)
curl -X POST http://localhost:8000/vortex/stop \
  -H "Authorization: Bearer your_jwt_token"
```

## 📝 Monitoring

Monitor these key metrics:

1. **Active Positions:** Number of open trades
2. **Win Rate:** Percentage of profitable trades
3. **Stop-Loss Triggers:** How often 1.5% ejector seat activates
4. **API Rate Limits:** Ensure not exceeding exchange limits
5. **System Resources:** CPU, memory usage

## 🆘 Support & Issues

If you encounter issues:

1. Check logs for error messages
2. Verify `.env` configuration
3. Test in PAPER mode first
4. Ensure API keys have correct permissions
5. Check exchange status (maintenance, API changes)

## ⚖️ Disclaimer

**This software is provided as-is for educational purposes.**

- Trading cryptocurrencies involves significant risk
- You can lose all your invested capital
- Past performance does not guarantee future results
- Always trade responsibly and within your means
- The authors are not responsible for any financial losses

**Trade at your own risk.**
