# Pioneer Trader — Comprehensive Knowledge Document

> **Audience:** Librarian AI (Mapping & Inventory Hub), developers, and future agents.
> **Purpose:** Structured, navigable findings covering architecture, status, known issues, and connectivity.
> **Last Audited:** 2026-04-19

---

## 1. Identity & Purpose

| Field | Value |
|-------|-------|
| **Project Name** | Pioneer Trader |
| **Codename** | CGAL Omega Trader |
| **Type** | FastAPI algorithmic trading backend |
| **Node Role** | Citadel Ecosystem — Trading Execution Node |
| **GitHub Org** | `DJ-Goana-Coding` (single-n; intentional GitHub handle) |
| **GitHub Repo** | `DJ-Goana-Coding/pioneer-trader` |
| **HF Space** | `DJ-Goana-Coding/pioneer-trader` |
| **HF Space URL** | `https://huggingface.co/spaces/DJ-Goana-Coding/pioneer-trader` |
| **API Base URL** | `https://dj-goana-coding-pioneer-trader.hf.space` |
| **Connected Hub** | `DJ-Goana-Coding/mapping-and-inventory` |
| **Frontend HUD** | `https://citadel-nexus-private.vercel.app` (Vercel) |
| **Default Port** | 10000 |
| **Default Mode** | PAPER (safe — no real money moves unless `EXECUTION_MODE=LIVE`) |

---

## 2. Technology Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.12 |
| Framework | FastAPI 0.109 + Uvicorn |
| Exchange | CCXT 4.2 → MEXC Spot |
| Data | pandas + pandas-ta |
| Auth | JWT (python-jose HS256) |
| Cache | Redis (graceful fallback to in-memory) |
| Container | Docker (python:3.12-slim) |
| CI/CD | GitHub Actions → HuggingFace Spaces |
| Frontend | Web Components (src/) — UI Stencil Pack |

---

## 3. Directory Map

```
pioneer-trader/
│
├── backend/                        ← Python FastAPI application
│   ├── main.py                     ← App entry point; mounts all routers
│   ├── __init__.py
│   ├── core/
│   │   ├── config.py               ← Pydantic Settings (reads .env / secrets)
│   │   ├── security.py             ← JWT helpers; get_current_admin / get_current_user
│   │   ├── logging_config.py       ← Centralized logger setup
│   │   ├── personas.py             ← Persona registry: TIA, GOANNA, VOID, HIPPY
│   │   ├── iso20022_parser.py      ← ISO 20022 structural parser stub
│   │   └── yield_engine.py         ← Remote-area yield calculator (coeff-driven)
│   ├── routers/
│   │   ├── auth.py                 ← /auth/login, /auth/me
│   │   ├── telemetry.py            ← /telemetry/health, /telemetry/status
│   │   ├── cockpit.py              ← /cockpit/* — T.I.A. + Admiral command center
│   │   ├── security.py             ← /security/* — Red Flag Scanner + Archive
│   │   ├── finance.py              ← /v1/finance/analyze — ISO20022 + Yield
│   │   ├── hub_router.py           ← /v1/ingest, /v1/query → Mapping Hub
│   │   ├── brain.py                ← /brain/knowledge — static KB
│   │   ├── trade.py                ← /trade/order (needs app.state.oms)
│   │   └── strategy.py             ← /strategy/analyze/{symbol}
│   └── services/
│       ├── vortex.py               ← VortexOmega — lightweight sync MEXC wrapper
│       ├── exchange.py             ← ExchangeService — async MEXC (paper/live)
│       ├── strategy_engine.py      ← StrategyEngine "Frankfurt" — MEXC telemetry
│       ├── brain.py                ← SkinWalkerBrain — persona + knowledge
│       ├── knowledge.py            ← KnowledgeBase — JSON file at encyclopedia/
│       ├── tia_agent.py            ← TIAAgent — risk analysis (LOW/MEDIUM/HIGH)
│       ├── admiral_engine.py       ← AdmiralEngine — base/premium capability gating
│       ├── tia_admiral_bridge.py   ← Bridge: T.I.A. authorises Admiral access
│       ├── garage_manager.py       ← Genesis Garage — dynamic strategy loader
│       ├── malware_protection.py   ← RedFlagScanner — regex threat detection
│       ├── archival.py             ← ArchivalService — JSONL shadow archive
│       ├── redis_cache.py          ← RedisCache — portfolio, peaks, trade history
│       ├── oms.py                  ← OMS — order management with risk clamp
│       └── tia_admiral_bridge.py   ← Authorization bridge
│
├── src/                            ← UI Stencil Pack (web components)
│   ├── adaptors/                   ← REST, WS, mock data connectors
│   ├── agents/                     ← Scout, Hound, Sniper, Stylist, Cartographer
│   ├── core/                       ← Core web components and layouts
│   ├── dashboards/                 ← Trading, Monitoring, Governance dashboards
│   ├── metrics/                    ← DeltaMeter, StateIndicator
│   └── themes/                     ← Cyberpunk, Rainforest, Terminal CSS themes
│
├── tests/                          ← pytest + JS test suite
│   ├── test_*.py                   ← 25+ Python unit/integration tests
│   └── *.test.js                   ← 3 JS tests (delta-meter, rest-adaptor, scout)
│
├── config/
│   └── ato_coefficients.json       ← ATO yield coefficients (currently empty stub)
│
├── encyclopedia/
│   └── knowledge_base.json         ← Runtime knowledge base (auto-created)
│
├── scripts/
│   ├── push_to_huggingface.sh      ← Manual HF push script
│   ├── connect_mapping_inventory.sh
│   └── sync_mapping_to_huggingface.sh
│
├── .github/workflows/
│   ├── hf_sync.yml                 ← Pushes main → HF Space on commit; syncs M&I
│   └── codex_sync.yml
│
├── Dockerfile                      ← python:3.12-slim, exposes 10000
├── requirements.txt                ← fastapi, uvicorn, ccxt, pandas, pydantic, httpx
├── .env.example                    ← Template for all env vars
├── render.yaml                     ← Render.com deployment config
└── README.md                       ← HF Space metadata + project documentation
```

---

## 4. API Endpoints (Complete)

### Public (no auth)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Process liveness: `{"status":"ONLINE"}` |
| GET | `/ready` | Deep probe: touches MEXC, returns USDT balance |
| GET | `/v1/system/status` | **Standardised QGTNL telemetry contract** — node identity, routers loaded, service init state, hub URL |
| GET | `/v1/hub/health` | Reports which Hub URL this node is connected to |
| GET | `/cockpit/health` | Cockpit component health |
| GET | `/cockpit/status` | T.I.A. + Admiral + Vortex status |
| GET | `/cockpit/capabilities` | Admiral capability list |
| GET | `/cockpit/tia/summary` | T.I.A. risk assessment |
| GET | `/cockpit/garage/status` | Genesis Garage bay status |
| GET | `/cockpit/events` | Authorization event history |
| POST | `/cockpit/authorize` | Authorize Admiral (T.I.A. gate) |
| POST | `/cockpit/revoke` | Revoke Admiral access |
| POST | `/cockpit/tia/consume` | Feed AEGIS snapshot to T.I.A. |
| POST | `/cockpit/garage/select` | Select Ferrari strategy bay |
| POST | `/cockpit/garage/reload` | Reload garage engine cache |
| POST | `/cockpit/garage/execute` | Execute active strategy |
| POST | `/auth/login` | Get JWT token (`{username, password}`) |
| GET | `/telemetry/health` | Telemetry health |
| GET | `/security/status` | Red Flag Scanner status |
| POST | `/security/scan` | Scan code for malicious patterns |
| POST | `/security/scan-data` | Scan data dict for threats |
| GET | `/security/isolated` | List isolated threats |
| DELETE | `/security/isolated` | Clear isolated threats |
| GET | `/security/archival/stats` | Shadow archive file stats |
| GET | `/security/archival/logs` | Recent trade logs |
| GET | `/security/archival/session` | Session win/loss stats |
| POST | `/security/archival/log-trade` | Log a trade entry |
| POST | `/security/archival/export-github-pages` | Export logs for GitHub Pages |

### JWT-Protected (requires Bearer token from `/auth/login`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/auth/me` | Current authenticated user |
| GET | `/telemetry/status` | System status + execution mode |
| POST | `/strike` | Manual trade execution (audit-logged) |
| POST | `/start/{symbol}` | Start background market monitoring (audit-logged) |
| POST | `/trade/order` | Place order via OMS with risk clamp |
| GET | `/strategy/analyze/{symbol}` | Run a named strategy (`p25_momentum`, `golden_cross`) on the symbol |
| POST | `/v1/ingest` | Forward RAG payload to Mapping Hub |
| POST | `/v1/query` | Forward RAG query to Mapping Hub |
| POST | `/v1/finance/analyze` | Parse ISO 20022 + compute yield |

---

## 5. Key Services Explained

### VortexOmega (`backend/services/vortex.py`)
- Lightweight **synchronous** CCXT wrapper used by `backend/main.py`
- Exposes: `get_balance()`, `execute_trade()`, `monitor_market()`
- Uses env var `MEXC_API_KEY` / `MEXC_SECRET`
- Note: runs in a background task via FastAPI's `BackgroundTasks`

### ExchangeService (`backend/services/exchange.py`)
- **Async** CCXT wrapper used by OMS and StrategyEngine
- Supports PAPER / TESTNET (falls back to PAPER) / LIVE modes
- LIVE mode validates that credentials are set before initialising
- Paper mode returns fake orders without touching the exchange

### TIAAgent (`backend/services/tia_agent.py`)
- **T.I.A. = Tactical Intelligence Agent**
- Analyzes risk from AEGIS snapshots (wallet balance, equity, slots)
- Risk levels: LOW / MEDIUM / HIGH
- Persists state to Redis (with graceful in-memory fallback)
- Controls Admiral's premium capability access via the bridge

### AdmiralEngine (`backend/services/admiral_engine.py`)
- Manages **base** (always-on) and **premium** (T.I.A.-gated) capabilities
- Base: basic_trading, telemetry, portfolio_view
- Premium: sniper_execution, vortex_control, strategy_override, risk_clamp_control, trailing_stop_config, slot_scaling, airgapped_sync

### Genesis Garage (`backend/services/garage_manager.py`)
- Dynamically loads trading strategy classes from bay folders
- T.I.A. selects the bay based on risk level
- Bays: 01_ELITE, 02_ATOMIC, 03_SCOUT, 04_CONSERVATIVE

### HubRouter (`backend/routers/hub_router.py`)
- Thin synapse to the Mapping & Inventory Hub
- Default URL: `https://dj-goana-coding-mapping-and-inventory.hf.space`
- Override via `MAPPING_HUB_URL` env var
- Forwards RAG payloads to `/v1/ingest` and queries to `/v1/query`

---

## 6. Configuration Reference

All configuration is read from environment variables (or `.env` file):

| Env Var | Default | Description |
|---------|---------|-------------|
| `MEXC_API_KEY` | `""` | MEXC API key — required for LIVE mode |
| `MEXC_SECRET` | `""` | MEXC secret — required for LIVE mode |
| `EXECUTION_MODE` | `PAPER` | `PAPER` or `LIVE` |
| `VORTEX_STAKE_USDT` | `8.0` | Default trade stake amount |
| `VORTEX_STOP_LOSS_PCT` | `0.015` | Stop-loss percentage (1.5%) |
| `MAX_ORDER_NOTIONAL` | `50.0` | Maximum USDT notional per order |
| `MIN_SLOT_SIZE` | `8.0` | Minimum slot size |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `REDIS_ENABLED` | `True` | Enable/disable Redis |
| `PORT` | `10000` | Uvicorn listen port (Dockerfile: `--port 10000`) |
| `ADMIN_USERNAME` | `admin` | Login username |
| `ADMIN_PASSWORD` | `""` | Login password — MUST be set |
| `SECRET_KEY` | `""` | JWT signing key — MUST be set (≥32 chars) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiry |
| `ENABLE_MALWARE_PROTECTION` | `True` | Enable RedFlagScanner |
| `SHADOW_ARCHIVE_PATH` | `/tmp/shadow_archive` | Trade log storage path |
| `ENABLE_GITHUB_PAGES_EXPORT` | `False` | Export logs to GH Pages format |
| `ALLOWED_ORIGINS` | `""` | Extra CORS origins (comma-separated) |
| `MAPPING_HUB_URL` | HF Space URL | Override Mapping Hub endpoint |
| `MAPPING_HUB_TIMEOUT` | `30` | Hub request timeout (seconds) |
| `ATO_COEFFICIENTS_PATH` | `config/ato_coefficients.json` | Yield engine config |
| `DIAGNOSTIC_MODE` | `True` | Enable verbose diagnostics |

---

## 7. Bugs Found & Fixed (This Audit)

### Bug 1 — `MEXC_KEY` env var typo in `backend/services/vortex.py`
- **Severity:** High — API key never loaded; LIVE trading silently uses `None`
- **File:** `backend/services/vortex.py` line 8
- **Was:** `os.getenv("MEXC_KEY")`
- **Fixed to:** `os.getenv("MEXC_API_KEY")`
- **Status:** ✅ FIXED

### Bug 2 — `get_current_user` missing from `backend/core/security.py`
- **Severity:** High — 4 routers (telemetry, trade, brain, strategy) import a name that didn't exist, causing `ImportError` if those modules were loaded
- **File:** `backend/core/security.py`
- **Fixed by:** Added `get_current_user = get_current_admin` alias
- **Status:** ✅ FIXED

### Bug 3 — Auth router not mounted in `backend/main.py`
- **Severity:** High — The OAuth2 scheme declares `tokenUrl="/auth/login"` but the auth router was never included in the app, making login impossible
- **File:** `backend/main.py`
- **Fixed by:** Added `app.include_router(auth_router)` with import guard
- **Status:** ✅ FIXED

### Bug 4 — Telemetry, Cockpit, Security routers not mounted
- **Severity:** Medium — Routers were fully implemented but unreachable (not mounted)
- **File:** `backend/main.py`
- **Fixed by:** Registered telemetry, cockpit, and security routers with import guards
- **Status:** ✅ FIXED

### Bug 5 — README describes wrong project ("UI Stencil Pack")
- **Severity:** Medium — README described a front-end component library instead of the trading backend; HF Space metadata was incorrect (`app_port: 7860` instead of `10000`)
- **File:** `README.md`
- **Fixed by:** Replaced README with accurate Pioneer Trader documentation
- **Status:** ✅ FIXED

---

## 8. Known Issues & Incomplete Items

### Issue 1 — `trade.py` and `strategy.py` routers not mounted ✅ RESOLVED (Session 2)
- **Resolution:** Added FastAPI `lifespan` handler in `main.py` that initialises `ExchangeService`, `OMS`, and `StrategyLogic` into `app.state`. Both routers are now mounted with import guards.
- **Strategy router fix:** Replaced calls to non-existent `StrategyEngine.calculate_indicators()` / `check_signal()` with a `StrategyLogic`-driven dispatcher supporting `p25_momentum` and `golden_cross`.

### Issue 2 — `config/ato_coefficients.json` is an empty stub
- **File:** `config/ato_coefficients.json`
- **Impact:** `/v1/finance/analyze` always returns `status: PENDING_COEFFICIENTS` for yield
- **Fix Needed:** Populate with real ATO postcode zone data

### Issue 3 — `iso20022_parser.py` validation is a stub
- **Impact:** XML payloads are stored raw without parsing; no XSD schema validation
- **Fix Needed:** Implement proper ISO 20022 XML parsing (pain.*, pacs.*, camt.*)

### Issue 4 — `brain.py` router uses a static in-memory knowledge base
- **Impact:** Knowledge base is not persisted beyond the `knowledge.py` JSON file; `brain.py` router's knowledge base is a hardcoded dict, disconnected from `KnowledgeBase`
- **Fix Needed:** Wire `brain.py` router to use `knowledge_base` from `backend.services.knowledge`

### Issue 5 — `PORT` config variable mismatch
- **Config default:** `PORT = 7860` (in config.py)
- **Dockerfile CMD:** `--port 10000`
- **Impact:** If code reads `settings.PORT` for the uvicorn port, it would use 7860 instead of 10000
- **Fix Needed:** Set `PORT = 10000` as default in `config.py` (already correct in Dockerfile)

### Issue 6 — `VortexOmega` uses synchronous CCXT in an async FastAPI app
- **Impact:** Blocking calls (`fetch_balance`, `create_order`, `fetch_ticker`) block the event loop
- **Fix Needed:** Replace sync CCXT with `ccxt.async_support` and `await` calls (as already done correctly in `exchange.py`)

### Issue 7 — Redis `hgetall` returns bytes vs strings inconsistency
- **File:** `backend/services/tia_agent.py` line 51
- **Impact:** `state.get("risk_level", "LOW")` — if Redis returns bytes (non-`decode_responses` client), this fails. The `redis_cache.py` sets `decode_responses=True`, but `tia_agent.py` creates its own direct client reference.
- **Actual status:** Low risk because `redis_cache.client` does set `decode_responses=True`.

---

## 9. Personas

| ID | Name | Role | Style | Triggers |
|----|------|------|-------|---------|
| `TIA` | T.I.A. | Captain | green | status, report, tia, system |
| `GOANNA` | DJ Goanna | DJ | purple | bass, vibe, play |
| `VOID` | The Void | Oracle | red | truth, dark, prediction |
| `HIPPY` | Hippy | Guide | blue | peace, chill, love |

> **Note on naming:** The GitHub org is `DJ-Goana-Coding` (single-n). The persona/character name is "DJ Goanna" (double-n). This is intentional — the GitHub handle uses a single-n abbreviation.

---

## 10. CI/CD & Deployment

### GitHub Actions: `hf_sync.yml`
- **Trigger:** Push to `main`, manual dispatch, daily cron (00:00 UTC)
- **Job 1 — sync-pioneer-trader:** Pushes this repo to HF Space via `git push --force`
  - Requires secret: `HF_TOKEN`
- **Job 2 — sync-mapping-and-inventory:** Clones the M&I repo, injects a Gradio `app.py` + Dockerfile, and uploads to `DJ-Goana-Coding/Mapping-and-Inventory` HF Space
  - Requires secret: `HF_TOKEN`

### Required GitHub Secrets
| Secret | Purpose |
|--------|---------|
| `HF_TOKEN` | HuggingFace write token for Space sync |
| `MEXC_API_KEY` | MEXC exchange API key (for LIVE mode) |
| `MEXC_SECRET` | MEXC exchange secret (for LIVE mode) |
| `ADMIN_PASSWORD` | API admin password |
| `SECRET_KEY` | JWT signing key |

### Docker Build
```bash
docker build -t pioneer-trader .
docker run -p 10000:10000 \
  -e MEXC_API_KEY=your_key \
  -e MEXC_SECRET=your_secret \
  -e ADMIN_PASSWORD=your_password \
  -e SECRET_KEY=your_32_char_jwt_key \
  pioneer-trader
```

---

## 11. Testing

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov httpx

# Run all Python tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing

# JS tests
npm test
```

### Test Files
| File | Coverage Area |
|------|--------------|
| `test_health_check.py` | /health, /ready endpoints |
| `test_auth_api.py` | JWT login/auth flow |
| `test_vortex_v310.py` | VortexOmega trading engine |
| `test_tia_agent_unit.py` | T.I.A. risk analysis |
| `test_admiral_engine_unit.py` | AdmiralEngine capabilities |
| `test_exchange_unit.py` | ExchangeService PAPER mode |
| `test_malware_scanner_unit.py` | RedFlagScanner patterns |
| `test_archival_unit.py` | ArchivalService logging |
| `test_redis_cache_unit.py` | RedisCache operations |
| `test_personas_unit.py` | Persona registry + detection |
| `test_config_unit.py` | Settings loading |
| `test_cockpit_api.py` | Cockpit endpoints |
| `test_tia_cockpit.py` | T.I.A. + cockpit integration |
| `test_strategy_engine_unit.py` | StrategyEngine telemetry |
| `test_brain_service.py` | SkinWalkerBrain |
| `test_v19_api.py` | V19 security + archival |
| `test_v19_security.py` | RedFlagScanner API |

---

## 12. Connectivity Map

```
GitHub (DJ-Goana-Coding/pioneer-trader)
    │
    ├──[hf_sync.yml on push]──► HF Space: DJ-Goana-Coding/pioneer-trader
    │                               ↑ FastAPI app at :10000
    │                               │ /v1/ingest, /v1/query
    │                               └──► HF Space: DJ-Goana-Coding/mapping-and-inventory
    │
    ├──[hf_sync.yml daily]──► HF Space: DJ-Goana-Coding/Mapping-and-Inventory
    │                               (Gradio docs browser)
    │
    └──[Vercel HUD]──► https://citadel-nexus-private.vercel.app
                           (CORS-whitelisted; reads /cockpit/status, /health)
```

---

## 13. What the Librarian Can Offer From This Repo

- **Fix paths:** Auth router was missing — fixed; MEXC key typo — fixed; missing router mounts — fixed
- **Missing implementations:** `trade.py` + `strategy.py` need app.state lifecycle; `ato_coefficients.json` needs real data; ISO20022 parser needs XSD validation
- **Connectivity:** Hub bridge is in place at `/v1/ingest` and `/v1/query` — ready for RAG sync
- **Security posture:** JWT auth covers admin endpoints; RedFlagScanner covers content scanning; PAPER mode default prevents accidental live trading
- **Next steps:** Wire `trade.py`/`strategy.py` into lifespan, populate ATO coefficients, implement ISO 20022 XML validation

---

*This document was auto-generated by Copilot during the 2026-04-19 audit session.*
