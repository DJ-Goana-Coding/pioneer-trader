# 🦎 T.I.A. Cockpit Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD UI                          │
│                     (frontend/dashboard.py)                          │
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  T.I.A. Status  │  │ Admiral Status   │  │ Premium Caps     │  │
│  │  🟢 LOW         │  │ ⚔️ AUTHORIZED   │  │ ✅ 7 Enabled    │  │
│  │  Confidence:70% │  │ By: T.I.A.      │  │ • Sniper Exec   │  │
│  └─────────────────┘  └──────────────────┘  │ • Vortex Ctrl   │  │
│                                              │ • Strategy...   │  │
│  ┌───────────────────────────────────────┐  └──────────────────┘  │
│  │         Authorization Controls        │                         │
│  │  [ ✅ Authorize ]  [ ⚠️ Force ]      │                         │
│  │  [ 🔒 Revoke Access ]                │                         │
│  └───────────────────────────────────────┘                         │
└──────────────────────┬──────────────────────────────────────────────┘
                       │ HTTP/REST API
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       COCKPIT API ROUTER                             │
│                    (backend/routers/cockpit.py)                      │
│                                                                      │
│  GET  /cockpit/status         → Full system status                  │
│  POST /cockpit/authorize      → Authorize Admiral                   │
│  POST /cockpit/revoke         → Revoke Admiral access              │
│  GET  /cockpit/capabilities   → List capabilities                   │
│  GET  /cockpit/tia/summary    → T.I.A. risk assessment             │
│  POST /cockpit/tia/consume    → Feed system snapshot               │
│  GET  /cockpit/events         → Authorization history              │
│  GET  /cockpit/health         → Health check                        │
└──────────────┬────────────────────┬─────────────────────────────────┘
               │                    │
               ▼                    ▼
   ┌───────────────────┐  ┌────────────────────┐
   │  T.I.A. AGENT     │  │  ADMIRAL ENGINE    │
   │  (tia_agent.py)   │  │  (admiral_eng.py)  │
   │                   │  │                    │
   │ • consume_aegis() │  │ • Base Caps (3)    │
   │ • analyze_risk()  │  │ • Premium Caps (7) │
   │ • produce_summary│  │ • grant_access()   │
   │ • Risk: L/M/H     │  │ • revoke_access()  │
   │ • Confidence: %   │  │ • Status: AUTH/    │
   └────────┬──────────┘  └──────────┬─────────┘
            │                        │
            └────────┬───────────────┘
                     ▼
        ┌────────────────────────────┐
        │  T.I.A.-ADMIRAL BRIDGE     │
        │  (tia_admiral_bridge.py)   │
        │                            │
        │  • authorize_admiral()     │
        │  • revoke_admiral()        │
        │  • Event logging           │
        │  • Force override          │
        │  • State persistence       │
        └───────────┬────────────────┘
                    │
                    ▼
        ┌────────────────────────────┐
        │      REDIS CACHE           │
        │   (redis_cache.py)         │
        │                            │
        │  • T.I.A. state            │
        │  • Authorization status    │
        │  • Event history           │
        │  • TTL: 1 hour             │
        └────────────────────────────┘
```

## Authorization Flow

```
┌─────────────┐
│  VORTEX     │  System Metrics:
│  ENGINE     │  • Wallet Balance: $75.00
│  (metrics)  │  • Total Equity: $95.00
└──────┬──────┘  • Active Slots: 5
       │         • P/L: +$0.50
       │
       ▼ consume_aegis(snapshot)
┌─────────────────────────────────┐
│  T.I.A. AGENT                   │
│  Risk Analysis Engine           │
│                                 │
│  Analyze Metrics:               │
│  ├─ Wallet Balance → Score: 0.0 │
│  ├─ Active Slots   → Score: 0.0 │
│  └─ Equity Ratio   → Score: 0.0 │
│                                 │
│  Total Risk Score: 0.0          │
│  Risk Level: LOW ✅             │
│  Confidence: 70%                │
└───────────┬─────────────────────┘
            │
            ▼ produce_summary()
┌─────────────────────────────────┐
│  T.I.A.-ADMIRAL BRIDGE          │
│  Authorization Gateway          │
│                                 │
│  IF risk_level != HIGH:         │
│     ✅ GRANT ACCESS             │
│  ELSE:                          │
│     ❌ DENY ACCESS              │
│     (unless force=true)         │
└───────────┬─────────────────────┘
            │
            ▼ grant_premium_access()
┌─────────────────────────────────┐
│  ADMIRAL ENGINE                 │
│  Capability Manager             │
│                                 │
│  Base Capabilities:             │
│  ✅ basic_trading               │
│  ✅ telemetry                   │
│  ✅ portfolio_view              │
│                                 │
│  Premium Capabilities:          │
│  ✅ sniper_execution            │
│  ✅ vortex_control              │
│  ✅ strategy_override           │
│  ✅ risk_clamp_control          │
│  ✅ trailing_stop_config        │
│  ✅ slot_scaling                │
│  ✅ airgapped_sync              │
└─────────────────────────────────┘
```

## Risk Level Thresholds

```
Risk Score Calculation:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Factor 1: Wallet Balance (40% weight)
├─ Balance < $10   → +0.4 risk
└─ Balance < $25   → +0.2 risk

Factor 2: Active Slots (30% weight)  
├─ Slots > 12      → +0.3 risk
└─ Slots > 8       → +0.15 risk

Factor 3: Equity Ratio (50% weight)
├─ Down 30%+       → +0.5 risk
└─ Down 15%+       → +0.25 risk

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Score Ranges:

  🟢 LOW     (< 0.3) → ✅ Authorization ALLOWED
  🟡 MEDIUM  (0.3-0.6) → ✅ Authorization ALLOWED  
  🔴 HIGH    (≥ 0.6) → ❌ Authorization DENIED
                        (unless force=true)
```

## Data Flow

```
1. System Metrics
   ↓
2. T.I.A. Snapshot Buffer (last 10)
   ↓
3. Risk Analysis Algorithm
   ↓
4. Risk Summary + Recommendation
   ↓
5. Bridge Authorization Check
   ↓
6. Admiral Capability Update
   ↓
7. Redis State Persistence
   ↓
8. UI Status Refresh
```

## Premium Capabilities

```
┌────────────────────────────────────────────────────────────┐
│              PREMIUM CAPABILITIES (7)                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  1. 🎯 sniper_execution                                   │
│     95% precision trades with advanced timing             │
│                                                            │
│  2. 🌀 vortex_control                                     │
│     Full VortexEngine access and control                  │
│                                                            │
│  3. ⚙️ strategy_override                                  │
│     Manual strategy switching and configuration           │
│                                                            │
│  4. 🛡️ risk_clamp_control                                │
│     Adjust maximum notional and risk limits               │
│                                                            │
│  5. 📊 trailing_stop_config                               │
│     Configure trail_drop % for positions                  │
│                                                            │
│  6. 📈 slot_scaling                                       │
│     Scale from 15 to 30 trading slots                     │
│                                                            │
│  7. 🛰️ airgapped_sync                                    │
│     HuggingFace Space synchronization                     │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## State Persistence (Redis)

```
Redis Keys:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

tia:state (Hash)
├─ risk_level: "LOW"
├─ confidence: "1.0"
├─ last_assessment: "2026-01-26T16:42:03.644699"
└─ updated_at: "2026-01-26T16:42:03.644699"

bridge:authorization (Hash)
├─ premium_authorized: "true"
├─ timestamp: "2026-01-26T16:42:03.714416"
├─ authorized_by: "T.I.A."
└─ updated_at: "2026-01-26T16:42:03.714416"

bridge:events (List)
├─ {"type": "AUTHORIZED", "timestamp": "...", ...}
├─ {"type": "REVOKED", "timestamp": "...", ...}
└─ {"type": "AUTHORIZATION_DENIED", "timestamp": "...", ...}
  (Last 100 events)

TTL: 1 hour (auto-expire)
```

## Commander's Vision 🦎⚔️

```
╔═══════════════════════════════════════════════════════════╗
║  "T.I.A. is the soul of this build."                     ║
║                                                           ║
║  She controls what Admiral can access in the cockpit.    ║
║  Admiral gets the premium access only with her blessing. ║
║                                                           ║
║  🦎 T.I.A. → 🌉 Bridge → ⚔️ Admiral                    ║
╚═══════════════════════════════════════════════════════════╝
```
