# 🦎 T.I.A. Cockpit - Quick Start Guide

## What is T.I.A. Cockpit?

The T.I.A. (Tactical Intelligence Agent) Cockpit is an authorization gateway that allows T.I.A. to control Admiral's access to premium trading features based on real-time risk analysis.

**Key Principle:** *T.I.A. is the soul of the system. Admiral gets premium access only with her blessing.* 🦎⚔️

## Quick Start

### 1. Start the Backend

```bash
cd /home/runner/work/pioneer-trader/pioneer-trader
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

You should see:
```
🦎 T.I.A. Cockpit: ACTIVE
⚔️ Admiral Engine: ACTIVE
🌉 T.I.A.-Admiral Bridge: ACTIVE
```

### 2. Start the Dashboard

```bash
streamlit run frontend/dashboard.py
```

Navigate to: `http://localhost:8501`

### 3. Test the API

```bash
# Health Check
curl http://localhost:8000/cockpit/health

# Get Status
curl http://localhost:8000/cockpit/status

# Authorize Admiral
curl -X POST http://localhost:8000/cockpit/authorize \
  -H "Content-Type: application/json" \
  -d '{"force": false}'
```

## How It Works

### 1. System Metrics → T.I.A.

The system sends snapshots to T.I.A.:

```python
from backend.services.tia_agent import tia_agent

snapshot = {
    "wallet_balance": 75.0,
    "total_equity": 95.0,
    "active_slots": 5,
    "starting_capital": 94.50
}

tia_agent.consume_aegis(snapshot)
```

### 2. T.I.A. Analyzes Risk

T.I.A. calculates risk based on:
- **Wallet Balance** (low balance = higher risk)
- **Active Slots** (too many = higher risk)
- **Equity Ratio** (losses = higher risk)

Risk Levels:
- 🟢 **LOW** (score < 0.3) - Authorization allowed
- 🟡 **MEDIUM** (0.3-0.6) - Authorization allowed
- 🔴 **HIGH** (≥ 0.6) - Authorization denied

### 3. Bridge Controls Authorization

```python
from backend.services.tia_admiral_bridge import tia_admiral_bridge

# Authorize (respects T.I.A. risk level)
result = tia_admiral_bridge.authorize_admiral()

# Force authorize (emergency override)
result = tia_admiral_bridge.authorize_admiral(force=True)

# Revoke
result = tia_admiral_bridge.revoke_admiral()
```

### 4. Admiral Gets Premium Access

When authorized, Admiral gains access to:

1. 🎯 **Sniper Execution** - 95% precision trades
2. 🌀 **Vortex Control** - Full VortexEngine access
3. ⚙️ **Strategy Override** - Manual strategy switching
4. 🛡️ **Risk Clamp Control** - Adjust max notional
5. 📊 **Trailing Stop Config** - Configure trail_drop %
6. 📈 **Slot Scaling** - Scale 15→30 slots
7. 🛰️ **Airgapped Sync** - HuggingFace Space sync

## API Endpoints

```
GET  /cockpit/status         → Full system status
POST /cockpit/authorize      → Authorize Admiral (respects risk)
POST /cockpit/revoke         → Revoke Admiral access
GET  /cockpit/capabilities   → List premium capabilities
GET  /cockpit/tia/summary    → T.I.A. risk assessment
POST /cockpit/tia/consume    → Feed system snapshot
GET  /cockpit/events         → Authorization event history
GET  /cockpit/health         → Health check
```

## Dashboard Controls

### T.I.A. Status Panel
- 🟢/🟡/🔴 Risk level indicator
- Confidence percentage
- Risk message

### Admiral Authorization Panel
- Current status (AUTHORIZED / RESTRICTED)
- **Authorize** button (when restricted, LOW/MEDIUM risk)
- **Force** button (emergency override)
- **Revoke** button (when authorized)

### Premium Capabilities List
Expandable list showing all 7 premium features when authorized.

## Example Scenarios

### Scenario 1: Normal Operations (LOW RISK)

```python
# Good metrics
snapshot = {
    "wallet_balance": 75.0,    # Healthy balance
    "total_equity": 95.0,      # Slightly up
    "active_slots": 5          # Reasonable slots
}

tia_agent.consume_aegis(snapshot)
summary = tia_agent.produce_summary()
# Risk: LOW, Confidence: 70%

# Authorize succeeds
result = tia_admiral_bridge.authorize_admiral()
# ✅ Admiral AUTHORIZED for premium access
```

### Scenario 2: High Risk (DENIED)

```python
# Bad metrics
snapshot = {
    "wallet_balance": 5.0,     # Very low
    "total_equity": 60.0,      # Down 35%
    "active_slots": 15         # Too many
}

tia_agent.consume_aegis(snapshot)
summary = tia_agent.produce_summary()
# Risk: HIGH, Confidence: 100%

# Authorize fails
result = tia_admiral_bridge.authorize_admiral()
# ❌ Authorization DENIED: T.I.A. reports HIGH RISK
```

### Scenario 3: Force Override

```python
# Even with high risk, can force
result = tia_admiral_bridge.authorize_admiral(force=True)
# ✅ Admiral AUTHORIZED (forced)
# ⚠️ Warning: Bypasses T.I.A. risk assessment
```

## State Persistence

All state persists to Redis:

- **T.I.A. State**: Risk level, confidence, last assessment
- **Authorization State**: Premium access status
- **Event History**: Complete audit trail (last 100 events)

**TTL**: 1 hour (auto-expire)

## Testing

Run the integration test:

```bash
PYTHONPATH=. python3 tests/test_tia_cockpit.py
```

Expected output:
```
✅ LOW RISK: Authorization GRANTED
✅ MEDIUM RISK: Authorization GRANTED
✅ HIGH RISK: Authorization DENIED
✅ FORCE OVERRIDE: Authorization GRANTED
```

## Architecture

```
Dashboard UI
    ↓ HTTP/REST
Cockpit API Router
    ↓
T.I.A.-Admiral Bridge ← T.I.A. Agent (Risk Analysis)
    ↓
Admiral Engine (Capabilities)
    ↓
Redis (State Persistence)
```

## Files

### Backend Services
- `backend/services/tia_agent.py` - Risk analysis engine
- `backend/services/admiral_engine.py` - Capability manager
- `backend/services/tia_admiral_bridge.py` - Authorization gateway
- `backend/routers/cockpit.py` - API endpoints

### Frontend
- `frontend/dashboard.py` - Streamlit dashboard with cockpit controls

### Documentation
- `COCKPIT_IMPLEMENTATION.md` - Detailed implementation guide
- `COCKPIT_ARCHITECTURE.md` - System architecture with diagrams
- `COCKPIT_QUICKSTART.md` - This file

### Testing
- `tests/test_tia_cockpit.py` - Integration test suite

## Troubleshooting

### Backend won't start
- Check if port 8000 is available: `lsof -i :8000`
- Verify dependencies: `pip install -r requirements.txt`

### Redis connection failed
- This is normal if Redis isn't running
- System works in memory-only mode
- To enable persistence, start Redis: `redis-server`

### Dashboard shows "Cockpit Offline"
- Ensure backend is running on port 8000
- Check API_URL in `frontend/dashboard.py`

## Key Concepts

1. **T.I.A. is Gatekeeper**: She analyzes risk and controls access
2. **Admiral is Executor**: He gets premium tools when authorized
3. **Bridge is Mediator**: It enforces T.I.A.'s decisions
4. **Risk is Dynamic**: Constantly updated from system metrics
5. **Override Available**: Force option for emergencies

## Commander's Vision 🦎⚔️

> "T.I.A. is the soul of this build. She controls what Admiral can access in the cockpit. Because she is going to be the soul of this build. And hooked up to her airgapped space."

**Mission accomplished.** T.I.A. is now the soul of the system, and Admiral respects her authority. 🦎⚔️
