# 🛡️ SECURITY CHECKLIST FOR OPERATORS

## ⚠️ CRITICAL: API KEY SECURITY

**NEVER expose your API keys!** They control your funds and repositories. Follow this checklist religiously.

## Before First Run

### 1. ✅ Secure Your Credentials

- [ ] **REVOKE** any API keys you may have accidentally pasted in:
  - Chat conversations
  - Public forums
  - Git commit messages
  - Code comments
  - Documentation files

- [ ] **GENERATE** new API keys from secure sources:
  - MEXC: https://www.mexc.com/user/openapi
  - GitHub: https://github.com/settings/tokens
  - HuggingFace: https://huggingface.co/settings/tokens

- [ ] **STORE** keys ONLY in your local `.env` file
  - Copy `.env.example` to `.env`
  - Replace PLACEHOLDER values with your real keys
  - **NEVER** commit the `.env` file to git
  - **NEVER** share your `.env` file

### 2. ✅ Verify Environment Setup

```bash
# Check .env file exists and is gitignored
ls -la .env
git check-ignore .env  # Should output: .env

# Verify .env is NOT tracked
git status  # .env should NOT appear in untracked or staged files
```

### 3. ✅ Test in PAPER Mode First

```bash
# In your .env file, set:
EXECUTION_MODE=PAPER

# Start the system
python -m backend.main

# Verify "PAPER mode" appears in logs
# No real trades will execute
```

## During Operation

### 4. ✅ Monitor for Security Issues

- [ ] Check logs for any credential exposure warnings
- [ ] Verify API keys are working (connection successful)
- [ ] Monitor for unusual activity on your accounts
- [ ] Review trade executions regularly

### 5. ✅ Emergency Procedures

If you suspect a security breach:

1. **IMMEDIATE**: Revoke all API keys
   - MEXC: Delete API key in settings
   - GitHub: Revoke personal access token
   - HuggingFace: Revoke access token

2. **VERIFY**: Check for unauthorized:
   - Trades on your exchange account
   - Commits to your repositories
   - Model uploads to HuggingFace

3. **ROTATE**: Generate new credentials
   - Create new API keys with minimal permissions
   - Update your local `.env` file
   - Test in PAPER mode before LIVE

## Safe Practices

### ✅ DO:
- Store credentials in `.env` file only
- Use PAPER mode for testing
- Set API key permissions to minimum required
- Enable 2FA on all accounts
- Monitor account activity
- Backup your `.env` file securely (encrypted storage only)

### ❌ DON'T:
- Paste API keys in chat/forums/public places
- Commit `.env` file to git
- Share your `.env` file
- Grant API keys more permissions than needed
- Run in LIVE mode without testing in PAPER first
- Leave API keys active when not trading

## Configuration Validation

### Required Environment Variables

```bash
# In your .env file:

# MEXC Exchange (for Vortex engine)
MEXC_API_KEY=your_actual_key_here          # NOT "PLACEHOLDER"
MEXC_SECRET_KEY=your_actual_secret_here    # NOT "PLACEHOLDER"

# Execution Mode
EXECUTION_MODE=PAPER  # Start with PAPER, change to LIVE only when ready

# Vortex Configuration
VORTEX_STAKE_USDT=8.0           # Amount per trade
VORTEX_STOP_LOSS_PCT=0.015      # 1.5% stop-loss
VORTEX_PULSE_SECONDS=8          # Trading interval

# Security
SECRET_KEY=generate_with_openssl_rand_hex_32
```

### Generate Secure Secret Key

```bash
# Use this command to generate a secure SECRET_KEY:
openssl rand -hex 32

# Copy output to .env file
```

## Vortex Engine Specific Security

### The "Ejector Seat" (Stop-Loss)

The Vortex engine implements a **mandatory 1.5% stop-loss** on all positions:

- **Cannot be disabled** - This is a safety feature
- Triggers **before** any other trading logic
- Uses **market orders** for immediate exit
- Prevents "sitting there" with unfilled limit orders

### Risk Parameters

```bash
# Adjust these in .env based on your risk tolerance:

VORTEX_STAKE_USDT=8.0          # Lower = less risk per trade
VORTEX_STOP_LOSS_PCT=0.015     # Higher = more tolerance (0.015 = 1.5%)
SAFETY_MODULATOR=5             # Scale 0-10, affects overall aggression
```

## Audit Trail

Keep a security log of key operations:

```
Date: YYYY-MM-DD
Action: Generated new MEXC API keys
Old Key (last 4): ...Zt
New Key (last 4): ...Xx
Reason: Rotating credentials after testing
```

## Questions or Concerns?

If you're unsure about security:
1. Stay in PAPER mode
2. Review this checklist again
3. Test with small amounts first
4. Monitor carefully before scaling up

**Remember: Your security is YOUR responsibility. The code provides tools, but you must use them safely.**
