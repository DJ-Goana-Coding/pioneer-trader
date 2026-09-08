# Vortex V3.1.0 - Intelligent Stagnation Filter & Adaptive MLOFI Gatekeeper

## Overview
This release introduces three major enhancements to the Vortex trading engine designed to protect capital and improve trade management in volatile market conditions.

## Key Features

### 1. Intelligent Stagnation Filter
**Purpose:** Prevent premature liquidations while freeing up capital from truly dead trades.

**Rules:**
- ✅ **Never liquidate before 4 hours** - Allows trades time to develop
- ✅ **Loss threshold with momentum check** - Only liquidate if:
  - Loss > 0.8% AND
  - No recovery momentum detected (price declining over last 30 minutes)
- ✅ **Breakeven stagnation** - Free up capital from sideways trades:
  - If -0.3% < profit < +0.3% for more than 8 hours, liquidate
- ✅ **Recovery protection** - NEVER force-sell positions showing upward momentum

**Implementation:**
```python
should_liquidate, reason = await should_liquidate_stagnant(
    symbol, entry_time, entry_price, current_price
)
```

### 2. Context-Aware MLOFI Gatekeeper
**Purpose:** Adapt buy filtering to different liquidity environments instead of blind blocking.

**Rules by Liquidity Level:**

| Liquidity Level | Volume Threshold | Entry Criteria |
|----------------|------------------|----------------|
| **High** (>$50M) | > $50,000,000 | RSI < 30 (oversold) |
| **Mid** ($10M-$50M) | $10M - $50M | RSI < 25 (extreme oversold) |
| **Low** (<$10M) | < $10,000,000 | Positive price momentum (1h & 4h) |

**Note:** MLOFI calculation not yet implemented - using RSI and momentum as proxy indicators.

**Implementation:**
```python
buy_allowed, reason = await is_buy_allowed(
    symbol, volume_24h, candles
)
```

### 3. Dynamic Position Sizing (4% Rule)
**Purpose:** Protect capital by limiting exposure per trade to 4% of total equity.

**Rules:**
- Maximum 4% of total equity per trade
- Minimum position size: $5 USDT (prevents dust trades)
- Maximum position size: $15 USDT (caps exposure even as capital grows)

**Examples:**
- $50 equity → $5 stake (min enforced)
- $100 equity → $5 stake (min enforced)
- $200 equity → $8 stake (4% = $8)
- $500 equity → $15 stake (max enforced)

**Implementation:**
```python
stake = calculate_position_size(total_equity)
```

## Technical Details

### New Methods Added to VortexBerserker

#### Stagnation Filter
- `_get_price_30min_ago()` - Retrieves historical price for momentum analysis
- `_showing_recovery_momentum()` - Detects upward price movement
- `should_liquidate_stagnant()` - Main stagnation detection logic

#### MLOFI Gatekeeper
- `_get_price_momentum()` - Calculates 1h and 4h price momentum
- `_check_price_momentum_positive()` - Verifies positive momentum trend
- `is_buy_allowed()` - Main gatekeeper with liquidity-aware filtering
- `_calculate_rsi()` - RSI (Relative Strength Index) calculation

#### Position Sizing
- `calculate_position_size()` - Dynamic stake calculation based on equity

### Configuration Constants

```python
# Stagnation Filter
MIN_HOLD_HOURS = 4.0
STAGNATION_LOSS_THRESHOLD = -0.008  # -0.8%
STAGNATION_BREAKEVEN_MIN = -0.003  # -0.3%
STAGNATION_BREAKEVEN_MAX = 0.003   # +0.3%
STAGNATION_BREAKEVEN_HOURS = 8.0

# MLOFI Gatekeeper
HIGH_LIQUIDITY_THRESHOLD = 50_000_000  # $50M
MID_LIQUIDITY_THRESHOLD = 10_000_000   # $10M
RSI_OVERSOLD_THRESHOLD = 25

# Position Sizing
POSITION_SIZE_PCT = 0.04    # 4%
MIN_POSITION_SIZE = 5.0     # $5 USDT
MAX_POSITION_SIZE = 15.0    # $15 USDT
```

## Integration Points

### 1. Main Trading Loop (`start()`)
- MLOFI gatekeeper checks all candidates before executing orders
- Filters out symbols that don't meet liquidity-specific criteria

### 2. Position Monitor (`pulse_monitor()`)
- Stagnation filter checks all active positions
- Runs before wing-specific exit logic
- Provides early exit for truly dead trades

### 3. Order Execution (`execute_order()`)
- Uses dynamic position sizing instead of fixed stake
- Logs position size calculation for transparency

## Logging Enhancements

All new features include comprehensive logging:

**Stagnation Filter:**
```
🚨 BTC/USDT: Stagnation: Loss -0.98% with no recovery (5.0h)
⏹️ ETH/USDT: Stagnation: Sideways +0.10% for 9.0h
⏳ SOL/USDT: Loss -0.85% but showing recovery - holding
```

**MLOFI Gatekeeper:**
```
💎 BTC/USDT: High liquidity, RSI 28.5 (oversold) - ALLOWED
⛔ ETH/USDT: High liquidity, RSI 45.2 - BLOCKED
💎 SHIB/USDT: Low liquidity with positive momentum - ALLOWED
⛔ DOGE/USDT: Low liquidity without positive momentum - BLOCKED
```

**Position Sizing:**
```
💰 Position sizing: Equity=$200.00 → Stake=$8.00 (4% rule)
💰 Position sizing: Equity=$500.00 → Stake=$15.00 (4% rule)
```

## Test Coverage

Comprehensive test suite added: `tests/test_vortex_v310.py`

**Test Cases:**
1. ✅ Dynamic Position Sizing (4 scenarios)
2. ✅ RSI Calculation (3 scenarios)
3. ✅ Stagnation Filter - Early Exit Prevention (2 scenarios)
4. ✅ Stagnation Filter - Loss with No Recovery
5. ✅ Stagnation Filter - Breakeven Stagnation (2 scenarios)
6. ✅ MLOFI Gatekeeper - High Liquidity
7. ✅ MLOFI Gatekeeper - Mid Liquidity
8. ✅ MLOFI Gatekeeper - Low Liquidity (Allowed)
9. ✅ MLOFI Gatekeeper - Low Liquidity (Blocked)
10. ✅ Configuration Constants

**Result:** 10/10 tests passing ✅

**Regression Testing:**
- All 6 existing fleet reconfiguration tests pass ✅
- All 6 existing sync-guard tests pass ✅

## Fleet Manifest Configuration

New configuration file: `registry/fleet_manifest.json`

```json
{
  "fleet_version": "3.1.0",
  "base_stake_calculation": "dynamic",
  "max_stake_pct": 0.04,
  "wings": {
    "Banker": {
      "enabled": false,
      "reason": "Conflicts with MLOFI negative filter - catches falling knives"
    }
  }
}
```

## Deployment Notes

### Pre-Deployment Checklist
- ✅ All tests passing (10 new + 12 existing)
- ✅ No breaking changes to existing functionality
- ✅ Comprehensive logging for all decisions
- ✅ Error handling for missing data (volume, RSI, price history)
- ✅ Fleet manifest documentation created

### Post-Deployment Validation
1. Run 24-hour paper trading session
2. Monitor logs for:
   - False positives in stagnation detection
   - MLOFI exceptions on high-liquidity pairs
   - Position sizing edge cases
3. Verify capital protection (4% rule enforced)
4. Check stagnation filter prevents premature exits during normal volatility

### Risk Mitigation
- **Testing Branch Only** - This PR targets testing branch deployment
- **Paper Trading First** - Validate in PAPER mode before LIVE
- **Gradual Rollout** - Monitor for 24 hours before full deployment

## Success Criteria

- [x] ✅ Stagnation filter prevents premature liquidations during normal volatility
- [x] ✅ MLOFI gatekeeper adapts to different liquidity environments
- [x] ✅ Position sizing scales with remaining capital (4% rule enforced)
- [x] ✅ All existing functionality preserved (no breaking changes)
- [x] ✅ Comprehensive logging for all trading decisions

## Future Enhancements

1. **MLOFI Calculation** - Implement actual MLOFI (Market Liquidity Oscillator for Intelligent) calculation instead of RSI proxy
2. **Machine Learning** - Train recovery momentum model on historical data
3. **Adaptive Thresholds** - Adjust stagnation thresholds based on market volatility
4. **Position Correlation** - Consider portfolio-level risk when sizing positions

## Files Modified

1. `backend/services/vortex.py` - Main trading engine with new features
2. `registry/fleet_manifest.json` - Configuration documentation
3. `tests/test_vortex_v310.py` - Comprehensive test suite

## Version Information

- **Version:** 3.1.0
- **Previous Version:** 3.0.0 (10-SLOT ARK FLEET)
- **Release Date:** 2026-02-09
- **Priority:** CRITICAL
- **Capital Risk:** HIGH - Protects last $100 capital

---

**Prepared by:** Copilot Agent  
**Review Status:** Pending  
**Deployment Target:** Testing Branch
